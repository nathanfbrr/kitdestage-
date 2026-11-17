import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve
SR=48000; DUR=40.0; N=int(SR*DUR); B=0.5; rng=np.random.default_rng(11)
L=np.zeros(N); R=np.zeros(N); revL=np.zeros(N); revR=np.zeros(N)
mtof=lambda m:440*2**((m-69)/12)
def put(buf,sig,t,g=1.0):
    i=int(t*SR)
    if i>=N: return
    n=min(len(sig),N-i); buf[i:i+n]+=sig[:n]*g
def add(sig,t,g=1.0,pan=0.0,rev=0.0):
    gl=np.cos((pan+1)*np.pi/4)*np.sqrt(2); gr=np.sin((pan+1)*np.pi/4)*np.sqrt(2)
    put(L,sig,t,g*gl); put(R,sig,t,g*gr)
    if rev: put(revL,sig,t,g*gl*rev); put(revR,sig,t,g*gr*rev)
def tt(d): return np.arange(int(d*SR))/SR
bp=lambda lo,hi:butter(2,[lo,hi],'band',fs=SR,output='sos')
hp=lambda f:butter(2,f,'high',fs=SR,output='sos')
lp=lambda f:butter(2,f,'low',fs=SR,output='sos')
# ---- instruments ----
def kick(g=1.0):
    t=tt(.45); f=48+110*np.exp(-t/.035); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-t/.22); s[:120]+=rng.standard_normal(120)*.25*np.linspace(1,0,120); return np.tanh(s*1.6)*g
def clap():
    t=tt(.3); n=rng.standard_normal(len(t)); env=np.zeros(len(t))
    for o in (0,.011,.022): env+=np.where(t>=o,np.exp(-(t-o)/.012),0)
    env+=np.where(t>=.03,np.exp(-(t-.03)/.11),0)*.7
    return sosfilt(bp(900,4500),n)*env*1.4
def hat(op=False):
    t=tt(.25 if op else .06); return sosfilt(hp(7500),rng.standard_normal(len(t)))*np.exp(-t/(.09 if op else .018))
def saw(f,t,det=(-0.08,0,0.07)):
    s=0
    for d in det:
        ff=f*2**(d/12); s=s+2*((t*ff+rng.random())%1)-1
    return s/len(det)
def stab(notes,d=.32):
    t=tt(d); s=sum(saw(mtof(m),t) for m in notes)/len(notes)
    return sosfilt(lp(3200),s)*np.exp(-t/.12)*np.minimum(1,t/.004)
def bassn(m,d):
    t=tt(d); s=saw(mtof(m),t,(0,))*.7+np.sin(2*np.pi*mtof(m)*t)*.8
    return sosfilt(lp(520),s)*np.minimum(1,t/.004)*np.exp(-t/(d*1.4))
def pluck(m):
    t=tt(.35); return (np.sin(2*np.pi*mtof(m)*t)+.35*np.sin(2*np.pi*mtof(m)*2*t)+.2*np.sin(2*np.pi*mtof(m)*3.01*t))*np.exp(-t/.09)*np.minimum(1,t/.002)
def pad(notes,d):
    t=tt(d+.6); s=sum(saw(mtof(m),t) for m in notes)/len(notes)
    env=np.minimum(1,t/.4)*np.where(t<d,1,np.exp(-(t-d)/.25)); return sosfilt(lp(1500),s)*env
def impact():
    t=tt(1.6); boom=np.sin(2*np.pi*np.cumsum(40+70*np.exp(-t/.06))/SR)*np.exp(-t/.5)
    crash=sosfilt(hp(3000),rng.standard_normal(len(t)))*np.exp(-t/.55)*.35
    return boom*.9+crash
def whoosh(d=.25):
    t=tt(d); n=rng.standard_normal(len(t)); env=np.sin(np.pi*t/d)**2
    return sosfilt(bp(1200,6000),n)*env*.6
def riser(d):
    t=tt(d); n=sosfilt(bp(800,8000),rng.standard_normal(len(t)))*(t/d)**2.2*.5
    tone=np.sin(2*np.pi*np.cumsum(200+1400*(t/d)**2)/SR)*(t/d)**2*.12
    return n+tone
def pop():
    t=tt(.12); return np.sin(2*np.pi*np.cumsum(900+900*np.exp(-t/.02))/SR)*np.exp(-t/.03)
# ---- harmony: F#m – D – A – E, one chord per bar (2 s) ----
PROG=[[54,57,61,66],[50,54,57,62],[57,61,64,69],[52,56,59,64]]; ROOT=[42,38,45,40]
def chord(t): return int(t//2)%4
drums=lambda t:(6<=t<21.75) or (22<=t<36)
# pads: hook + ending
for bar in range(0,3): add(pad(PROG[bar%4],2.0),bar*2,.22,rev=.4)
for t0 in (36,38): add(pad([57,61,64,69,73],2.0),t0,.28,rev=.5)
# hook slams
for h in (0,.5,1.0,2.0,2.5,2.95,4.0): add(kick(1.0),h,.9); add(clap(),h,.35,rev=.3); add(stab(PROG[chord(h)]),h,.45,rev=.3)
for h in (4.35,4.4,4.45): pass
# build 4–6: snare roll + riser
t0=4.5
while t0<6:
    step=.25 if t0<5.25 else .125; g=.15+.45*(t0-4.5)/1.5
    add(clap(),t0,g,pan=.1); t0+=step
add(riser(1.5),4.5,.7)
# main groove
step=.125; i=0; t0=6.0
while t0<36-1e-6:
    if drums(t0):
        b=round((t0-6)/step); beat=b%8==0; off=b%8==4
        if b%4==0: add(kick(),t0,1.0)
        if (b%16)==4 or (b%16)==12: add(clap(),t0,.55,rev=.25)
        add(hat(op=(b%4==2)),t0,.16 if b%4==2 else (.1 if b%2==0 else .06),pan=.3 if b%2 else -.3)
        c=chord(t0)
        if b%2==1: add(bassn(ROOT[c]+(12 if b%4==3 else 0),.12),t0,.55)
        if b%16 in (0,3,6,10,12): add(stab(PROG[c]),t0,.22,pan=-.2 if b%2 else .2,rev=.35)
        if 12<=t0<21.75 or 32<=t0<36:
            arp=[0,2,1,3,2,1,3,2]; m=PROG[c][arp[b%8]]+12; add(pluck(m),t0,.13,pan=.5 if b%2 else -.5,rev=.4)
    t0+=step
# bar chart 'counter' ticks + pops
for a in (24,24.5,25.5,26.5): add(pop(),a,.4)
for i in range(6): add(pop(),21.06+i*.055,.25,pan=-.6+.24*i)
# transitions
CUTS=[2,4,10,12,13.5,15,16.5,18,19.5,21,28,29,30,31]
for c in CUTS: add(whoosh(),c-.22,.55,pan=.4 if int(c*2)%2 else -.4,rev=.2)
for c in (6,22,32,36): add(impact(),c,.8,rev=.4)
add(impact(),27.1,.45); add(riser(1.4),20.6,.45); add(riser(1.5),30.5,.5); add(riser(1.5),34.5,.5)
# ---- sidechain pump on everything but drums would need stems; light global pump instead ----
# reverb
def ir(seed):
    r=np.random.default_rng(seed); n=int(1.6*SR); t=np.arange(n)/SR
    return sosfilt(lp(6000),r.standard_normal(n))*np.exp(-t/.35)
wL=fftconvolve(revL,ir(1))[:N]; wR=fftconvolve(revR,ir(2))[:N]
s=max(np.abs(wL).max(),1e-9); wL/=s; wR/=s
outL=L+wL*np.abs(L).max()*.25; outR=R+wR*np.abs(L).max()*.25
t=np.arange(N)/SR; fade=np.clip((40-t)/1.2,0,1)
out=np.stack([outL*fade,outR*fade],1); out/=np.abs(out).max(); out*=.9
sf.write("dyn/musique-raw.wav",out,SR,subtype='PCM_24'); print("ok")
