#!/usr/bin/env python3
"""Cut a person out of a plain white/light studio background -> RGBA PNG.

Background = near-white pixels connected to the top, left or right edge (not the bottom edge, so a white shirt
that touches the bottom of the frame is kept). Edges get a soft alpha from how far each pixel is from white.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
a = a[6:-6, 6:-6]  # drop the thin grey frame line around the photo
h, w, _ = a.shape

# Distance from the (estimated) background white.
bg = np.median(np.concatenate([a[:20].reshape(-1, 3), a[:, :20].reshape(-1, 3), a[:, -20:].reshape(-1, 3)]), 0)
dist = np.sqrt(((a - bg) ** 2).sum(2))
near = dist < 28
near[-15:] = False  # the bottom strip can't seed or bridge the background (keeps a white shirt intact)

# Erode first so thin near-white bridges (e.g. between collar and backdrop) can't connect a white shirt to the
# background, then grow the edge-connected regions back to their original extent.
core = ndimage.binary_erosion(near, iterations=3)
lab, _ = ndimage.label(core)
edge_labels = set(np.unique(np.concatenate([lab[:6].ravel(), lab[:, :6].ravel(), lab[:, -6:].ravel()]))) - {0}
background = ndimage.binary_dilation(np.isin(lab, list(edge_labels)), iterations=3) & near

# Soft alpha: 0 in the background, ramping up over a few pixels of colour distance near the boundary.
alpha = np.where(background, 0.0, 1.0)
soft = np.clip((dist - 10) / 40, 0, 1)
boundary = ndimage.binary_dilation(background, iterations=4) & ~ndimage.binary_erosion(background, iterations=2)
alpha = np.where(boundary, np.minimum(np.maximum(alpha, soft), 1.0), alpha)
alpha = ndimage.grey_erosion(alpha, size=(3, 3))  # pull the edge in ~1px to drop the white fringe
alpha = ndimage.gaussian_filter(alpha, 0.8)
alpha = np.where(background & (dist < 12), 0, alpha)
# Near-white specks along the side edges (the backdrop peeking past the shoulders) are background too.
side = np.zeros_like(near); side[:, :40] = side[:, -40:] = True
alpha = np.where(side & (dist < 40), 0, alpha)

# Decontaminate edge colour: pull semi-transparent pixels away from the white they were blended with.
k = np.clip(alpha, 0.05, 1)[..., None]
rgb = np.clip((a - bg * (1 - k)) / k, 0, 255)
out = np.dstack([rgb, alpha * 255]).astype(np.uint8)
Image.fromarray(out, "RGBA").save(dst)
print("saved", dst, out.shape)
