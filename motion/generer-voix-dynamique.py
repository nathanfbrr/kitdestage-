import numpy as np, soundfile as sf, json
from kokoro_onnx import Kokoro
k=Kokoro("models/kokoro-v1.0.onnx","models/voices-v1.0.bin")
st=k.get_voice_style("im_nicola")*0.75+k.get_voice_style("ff_siwis")*0.25
CUES=[(0.05,"Premier stage ?",1.9),(2.0,"Zéro expérience ?",1.9),(4.0,"Pas de panique !",1.9),
(6.1,"Voici le Kit Premier Stage !",3.8),(10.0,"Ton premier stage, en quatre semaines.",1.95),
(12.05,"Le mode d'emploi.",1.4),(13.55,"Ton CV.",1.4),(15.05,"Ta lettre de motivation.",1.4),(16.55,"Tes imèles.",1.4),
(18.05,"L'entretien.",1.4),(19.55,"Et ton suivi.",1.4),(21.0,"Six fichiers prêts !",1.0),
(22.05,"Trente candidatures en quatre semaines.",2.4),(24.55,"Dix.",0.9),(25.55,"Vingt.",0.9),(26.55,"Trente !",0.9),(27.15,"Et on relance !",0.85),
(28.05,"Une page.",0.9),(29.05,"Dix minutes.",0.9),(30.05,"Zéro faute.",0.9),(31.05,"Et tu relances !",0.9),
(32.05,"Obtiens le Kit Premier Stage !",3.8),(36.1,"Ton premier stage, en quatre semaines.",3.6)]
out=[]
for i,(t,txt,win) in enumerate(CUES):
    sp=1.22
    while True:
        a,sr=k.create(txt,voice=st,speed=sp,lang="fr-fr")
        # trim leading/trailing silence
        idx=np.where(np.abs(a)>0.01)[0]; a=a[max(0,idx[0]-200):idx[-1]+1200]
        d=len(a)/sr
        if d<=win or sp>=1.6: break
        sp+=0.06
    sf.write(f"dyn/v{i:02d}.wav",a,sr); out.append((t,f"dyn/v{i:02d}.wav"))
    print(f"{t:5.2f} {d:4.2f}s/{win} sp={sp:.2f} {txt}")
json.dump(out,open("dyn/cues.json","w"))
