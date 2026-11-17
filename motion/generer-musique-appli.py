import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve
SR=48000; DUR=40.0; N=int(SR*DUR); BPM=90; B=60/BPM; rng=np.random.default_rng(5)
L=np.zeros(N); R=np.zeros(N); RV=np.zeros(N)
mtof=lambda m:440*2**((m-69)/12); tt=lambda d:np.arange(int(d*SR))/SR
lp=lambda f:butter(2,f,'low',fs=SR,output='sos'); hp=lambda f:butter(2,f,'high',fs=SR,output='sos'); bp=lambda a,b:butter(2,[a,b],'band',fs=SR,output='sos')
def add(sig,t,g=1,pan=0,rev=0):
    i=int(t*SR)
    if i>=N or i<0: return
    n=min(len(sig),N-i); gl=np.cos((pan+1)*np.pi/4)*1.41; gr=np.sin((pan+1)*np.pi/4)*1.41
    L[i:i+n]+=sig[:n]*g*gl; R[i:i+n]+=sig[:n]*g*gr
    if rev: RV[i:i+n]+=sig[:n]*g*rev
S2,S5,S6=5.6,28.6,33.4
def kick():
    t=tt(.4); f=45+70*np.exp(-t/.05); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/.18)
def snare():
    t=tt(.35); n=sosfilt(bp(1200,6000),rng.standard_normal(len(t)))*np.exp(-t/.09)
    body=np.sin(2*np.pi*190*t)*np.exp(-t/.06)*.5; return (n*.8+body)
def hat(op=False):
    t=tt(.2 if op else .05); return sosfilt(hp(8000),rng.standard_normal(len(t)))*np.exp(-t/(.07 if op else .015))
def rhodes(m,d):
    t=tt(d+.8); f=mtof(m)
    mod=np.sin(2*np.pi*f*t)*1.2*np.exp(-t/.4)
    s=np.sin(2*np.pi*f*t+mod)+.25*np.sin(2*np.pi*2*f*t)*np.exp(-t/.3)
    env=np.minimum(1,t/.008)*np.exp(-t/1.6)*np.where(t<d,1,np.exp(-(t-d)/.15))
    trem=1+.12*np.sin(2*np.pi*4.5*t); return s*env*trem
def bass(m,d):
    t=tt(d); s=np.sin(2*np.pi*mtof(m)*t)+.2*np.sin(2*np.pi*mtof(m)*2*t)
    return s*np.minimum(1,t/.01)*np.exp(-t/(d*1.2))
def bell(m):
    t=tt(1.2); f=mtof(m); return (np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*f*3.01*t)*np.exp(-t/.2))*np.exp(-t/.6)*np.minimum(1,t/.004)
PROG=[[53,57,60,64],[52,55,59,62],[50,53,57,60],[48,52,55,59]]; ROOT=[41,40,38,36]
BAR=4*B
nb=int(np.ceil(DUR/BAR))
for b in range(nb):
    t0=b*BAR; c=b%4; ch=PROG[c]
    # rhodes chords: on 1 and a pushed hit on the "and" of 2
    for k,(off,d,g) in enumerate([(0,1.6*B,.5),(1.5*B,1.2*B,.32),(3*B,.9*B,.25)]):
        for j,m in enumerate(ch): add(rhodes(m,d),t0+off+j*.012,g*.22,pan=-.3+.2*j,rev=.35)
    if t0>=S2-.01:
        for i in range(8):
            tb=t0+i*B/2+(0.06 if i%2 else 0)   # swing
            if tb>=DUR-1.0: continue
            if i in (0,5): add(kick(),tb,.85)
            if i in (2,6): add(snare(),tb,.38,rev=.2)
            add(hat(op=(i==7)),tb,.10 if i%2==0 else .06,pan=.35)
            if i in (0,3,4): add(bass(ROOT[c]+(0 if i!=3 else 7),B*.9),tb,.5)
    if t0>=S5-.01 and t0<DUR-2:
        mel=[72,74,76,79,76,74,72,69]
        for i,m in enumerate(mel):
            if i%2==0 or rng.random()<.5: add(bell(m+(0 if c<2 else -2)),t0+i*B/2,.12,pan=.5 if i%2 else -.4,rev=.5)
# small riser into the drums and into "ça répond"
for a,d in ((S2-1.2,1.2),(S5-1.0,1.0)):
    t=tt(d); add(sosfilt(bp(500,7000),rng.standard_normal(len(t)))*(t/d)**2.5*.25,a,1,rev=.3)
# vinyl crackle + hiss
cr=np.zeros(N); idx=rng.integers(0,N,2600); cr[idx]=rng.standard_normal(len(idx))*.5
cr=sosfilt(bp(1500,9000),cr)+sosfilt(lp(5000),rng.standard_normal(N))*.006
L+=cr*.5; R+=cr*.5
# reverb + lo-fi tone: low-pass the whole bed, slight wow
def ir(seed):
    r=np.random.default_rng(seed); n=int(2.0*SR); t=np.arange(n)/SR; return sosfilt(lp(4000),r.standard_normal(n))*np.exp(-t/.5)
w=fftconvolve(RV,ir(3))[:N]; w/=np.abs(w).max()+1e-9
m=max(np.abs(L).max(),np.abs(R).max()); L=L/m+w*.12; R=R/m+w*.12
t=np.arange(N)/SR
cut=np.where(t<S2,1400,6500)  # muffled intro, opens when drums enter
outL=np.zeros(N); outR=np.zeros(N); sp=int(S2*SR)
outL[:sp]=sosfilt(lp(1400),L)[:sp]; outR[:sp]=sosfilt(lp(1400),R)[:sp]
outL[sp:]=sosfilt(lp(6500),L)[sp:]; outR[sp:]=sosfilt(lp(6500),R)[sp:]
fade=np.minimum(1,t/.6)*np.clip((DUR-t)/1.8,0,1)
out=np.stack([outL*fade,outR*fade],1); out/=np.abs(out).max(); out*=.9
sf.write("app/musique-raw.wav",out,SR,subtype="PCM_24"); print("ok")
