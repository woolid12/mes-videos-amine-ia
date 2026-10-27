import json, base64, subprocess, sys, re
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from script_v3 import SEGMENTS, OUTRO
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'uOw88F5bjqRiVuZLhXEA'
SPEED = float(sys.argv[2]) if len(sys.argv) > 2 else 1.06
SAY = [("Aplevia", "Aplévia"), ("bengkung", "benkoung"), ("2 achetées = 1 offerte", "deux achetées, une offerte"),
       ("1000", "mille"), ("29 ans", "vingt-neuf ans"), ("360 degrés", "trois cent soixante degrés"), ("5 étoiles", "cinq étoiles"), ("30 jours", "trente jours")]
def spoken(t):
    for a, b in SAY: t = t.replace(a, b)
    return t
texts = [s[1] for s in SEGMENTS] + OUTRO
for i, t in enumerate(texts):
    body = {"text": spoken(t), "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True, "speed": SPEED},
            "previous_text": spoken(texts[i - 1]) if i else None,
            "next_text": spoken(texts[i + 1]) if i + 1 < len(texts) else None}
    r = subprocess.run(["curl", "-sS", f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128",
                        "-H", "Content-Type: application/json", "-d", json.dumps(body)], capture_output=True, text=True)
    d = json.loads(r.stdout)
    if "audio_base64" not in d: print(i, r.stdout[:300]); sys.exit(1)
    open(f"vo/{i:02d}.mp3", "wb").write(base64.b64decode(d["audio_base64"]))
    json.dump({"text": t, "spoken": spoken(t), "al": d["alignment"]}, open(f"vo/{i:02d}.json", "w"), ensure_ascii=False)
    print(i, "ok", flush=True)
