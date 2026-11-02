import sys, wave, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[1], device="cpu", compute_type="int8", cpu_threads=4)
prompt = "Movember. The mo's going. My moustache. My mum. Safety razor. King C. Gillette. Aussie bloke shaving. Nah, I've cut myself. Yeah, yeah."
for spec in sys.argv[2:]:
    wav, a, b = spec.split(":")
    w = wave.open(wav); sr = w.getframerate()
    w.setpos(int(float(a) * sr)); x = np.frombuffer(w.readframes(int((float(b) - float(a)) * sr)), dtype=np.int16).astype(np.float32) / 32768
    for temp_prompt in (None, prompt):
        segs, _ = m.transcribe(x, language="en", beam_size=8, initial_prompt=temp_prompt, vad_filter=False)
        print(f"{spec:22s} {'P' if temp_prompt else '-'} | " + " ".join(s.text.strip() for s in segs), flush=True)
