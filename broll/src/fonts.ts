import {continueRender, delayRender, staticFile} from 'remotion';

// Fonts are bundled locally: the render browser can't reach Google Fonts through the proxy.
const faces = [
  ['Montserrat', 'Montserrat-var.woff2', 'normal', '100 900'],
  ['Poppins', 'Poppins-normal-400.woff2', 'normal', '400'],
  ['Poppins', 'Poppins-normal-600.woff2', 'normal', '600'],
  ['Poppins', 'Poppins-italic-400.woff2', 'italic', '400'],
  ['Poppins', 'Poppins-italic-500.woff2', 'italic', '500'],
] as const;

const handle = delayRender('Loading fonts');
Promise.all(
  faces.map(([family, file, style, weight]) => {
    const face = new FontFace(family, `url(${staticFile(`fonts/${file}`)})`, {style, weight});
    document.fonts.add(face);
    return face.load();
  }),
).then(() => continueRender(handle));

export const MONT = 'Montserrat';
export const POP = 'Poppins';
