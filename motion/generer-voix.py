import sys, numpy as np, soundfile as sf, parselmouth
from kokoro_onnx import Kokoro
k=Kokoro("models/kokoro-v1.0.onnx","models/voices-v1.0.bin")
name,w,sp=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]); pref=sys.argv[4]
st=k.get_voice_style(name)*w+k.get_voice_style("ff_siwis")*(1-w)
L=["Ton premier stage, sans aucune expérience ? Pas de panique !",
"Voici le Kit Premier Stage ! Décroche ton premier stage sans expérience, en quatre semaines.",
"Six fichiers prêts à remplir : mode d'emploi, CV, lettre de motivation, imèles, préparation d'entretien, et suivi des candidatures.",
"La méthode : trente candidatures en quatre semaines. Dix, puis vingt, puis trente !",
"Kit Premier Stage. CV, lettre, imèles, entretien, suivi : tout est prêt. Obtiens le kit !"]
for i,t in enumerate(L):
    a,sr=k.create(t,voice=st,speed=sp,lang="fr-fr")
    sf.write(f"{pref}{i}.wav",a,sr)
    p=parselmouth.Sound(a.astype(np.float64),sr).to_pitch(pitch_floor=60,pitch_ceiling=300).selected_array['frequency']; p=p[p>0]
    print(i,round(len(a)/sr,2),"s  F0 med",round(float(np.median(p))),"Hz  range",round(float(np.percentile(p,90)-np.percentile(p,10))),"Hz")
