#!/usr/bin/env python3
"""Speaker mattes for the text-behind-speaker window.

BiRefNet-portrait (ONNX, from the rembg GitHub release) on every 3rd frame of renders/base_frames (it takes ~40-60 s a
frame on CPU); the frames in between get the average of their neighbours. Resumable: existing mattes are kept.

    python3 tools/matte.py /path/to/BiRefNet-portrait-epoch_150.onnx   -> renders/masks/m_00001.png ...
"""
import os, sys, time
from pathlib import Path
import numpy as np, onnxruntime as ort
from PIL import Image

HERE = Path(__file__).resolve().parent.parent
SRC, DST = HERE / "renders/base_frames", HERE / "renders/masks"
DST.mkdir(parents=True, exist_ok=True)
frames = sorted(SRC.glob("f_*.png"))
key = list(range(0, len(frames), 3))
if key[-1] != len(frames) - 1: key.append(len(frames) - 1)

so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count()
so.enable_cpu_mem_arena = False; so.enable_mem_pattern = False
sess = ort.InferenceSession(sys.argv[1], so, providers=["CPUExecutionProvider"])
dst = lambda i: DST / f"m_{i + 1:05d}.png"

for i in key:
    if dst(i).exists(): continue
    t = time.time()
    im = Image.open(frames[i]).convert("RGB"); W, H = im.size
    x = np.asarray(im.resize((1024, 1024), Image.BICUBIC), np.float32) / 255
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    o = sess.run(None, {sess.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0]
    o = 1 / (1 + np.exp(-o))
    Image.fromarray((o * 255).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).save(dst(i))
    print(f"{i + 1}/{len(frames)} {time.time() - t:.1f}s", flush=True)

for a, b in zip(key, key[1:]):
    ma = np.asarray(Image.open(dst(a)), np.float32); mb = np.asarray(Image.open(dst(b)), np.float32)
    for i in range(a + 1, b):
        w = (i - a) / (b - a)
        Image.fromarray(((1 - w) * ma + w * mb).astype(np.uint8)).save(dst(i))
print("mattes:", len(list(DST.glob("m_*.png"))))
