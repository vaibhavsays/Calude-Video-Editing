# pk_ts.py <model_dir> <wav> <out.tsv> : parakeet TDT recognition in ~10 s windows, every token with its absolute time
import sys, sherpa_onnx, soundfile as sf, numpy as np
d, wav, out = sys.argv[1:4]
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=d+"/encoder.int8.onnx", decoder=d+"/decoder.int8.onnx",
        joiner=d+"/joiner.int8.onnx", tokens=d+"/tokens.txt", model_type="nemo_transducer", num_threads=4)
a, sr = sf.read(wav, dtype="float32")
# windows cut at quiet points near every 10 s
env = np.convolve(np.abs(a), np.ones(1600)/1600, mode="same")
cuts = [0]
while cuts[-1] + 12*sr < len(a):
    lo, hi = cuts[-1] + 8*sr, cuts[-1] + 12*sr
    cuts.append(lo + int(np.argmin(env[lo:hi])))
cuts.append(len(a))
with open(out, "w") as f:
    for s, e in zip(cuts, cuts[1:]):
        st = rec.create_stream(); st.accept_waveform(sr, a[s:e]); rec.decode_stream(st)
        r = st.result
        for tok, t in zip(r.tokens, r.timestamps):
            f.write(f"{s/sr + t:.3f}\t{tok}\n")
        print(f"{s/sr:.2f}-{e/sr:.2f}: {r.text}")
