import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve
SR=48000; DUR=40.0; N=int(SR*DUR)
rng=np.random.default_rng(7)
L=np.zeros(N); R=np.zeros(N)
mtof=lambda m:440*2**((m-69)/12)
def add(sig,start,pan=0.0,gain=1.0):
    i=int(start*SR); n=min(len(sig),N-i)
    if n<=0: return
    gl=np.cos((pan+1)*np.pi/4)*gain; gr=np.sin((pan+1)*np.pi/4)*gain
    L[i:i+n]+=sig[:n]*gl; R[i:i+n]+=sig[:n]*gr

# ---- chords (start, end, midi notes) ----
CH=[(0,7,[50,57,61,64,66]),(7,11,[47,54,57,61,62]),(11,15,[43,50,54,59,61]),
    (15,17.5,[50,57,61,64,66]),(17.5,20,[49,54,57,59,64]),(20,22.5,[47,54,57,61,62]),(22.5,25,[43,50,54,57,59]),
    (25,28.5,[40,47,50,54,55]),(28.5,32,[45,52,54,59,62]),(32,34.5,[43,50,54,57,59]),(34.5,40,[50,57,61,64,66])]

def pad_note(f,dur,att,rel):
    n=int((dur+rel)*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for det in (-0.07,0,0.065):
        ff=f*2**(det/12)
        ph=rng.uniform(0,2*np.pi)
        for k in range(1,9):
            if ff*k>9000: break
            s+=np.sin(2*np.pi*ff*k*t+ph*k)/k**1.7
    env=np.minimum(1,t/att)
    env*=np.where(t<dur,1,np.exp(-(t-dur)/(rel/3)))
    env*=1+0.08*np.sin(2*np.pi*0.23*t+rng.uniform(0,6))
    return s*env/3

padL=np.zeros(N); padR=np.zeros(N)
for ci,(s0,e0,notes) in enumerate(CH):
    att=3.5 if ci==0 else 1.4
    for j,m in enumerate(notes):
        sig=pad_note(mtof(m),e0-s0,att,1.8)*(0.9 if j else 1.0)
        pan=(-0.5+j/(len(notes)-1))*0.7
        i=int(s0*SR); n=min(len(sig),N-i)
        padL[i:i+n]+=sig[:n]*np.cos((pan+1)*np.pi/4); padR[i:i+n]+=sig[:n]*np.sin((pan+1)*np.pi/4)
    # sub bass
    root=notes[0]-12 if notes[0]>=45 else notes[0]
    n=int((e0-s0+1.2)*SR); t=np.arange(n)/SR
    sub=np.sin(2*np.pi*mtof(root)*t)*np.minimum(1,t/(2.5 if ci==0 else .6))*np.where(t<e0-s0,1,np.exp(-(t-(e0-s0))/0.35))
    add(sub*0.32,s0)
sos=butter(2,1600,'low',fs=SR,output='sos')
L+=sosfilt(sos,padL)*0.5; R+=sosfilt(sos,padR)*0.5

# ---- glass bells ----
def bell(f,vel=1.0):
    n=int(2.6*SR); t=np.arange(n)/SR
    s=(np.sin(2*np.pi*f*t)*np.exp(-t/1.1)+0.32*np.sin(2*np.pi*f*2.756*t)*np.exp(-t/0.35)
       +0.12*np.sin(2*np.pi*f*5.404*t)*np.exp(-t/0.12)+0.18*np.sin(2*np.pi*f*2*t)*np.exp(-t/0.7))
    return s*np.minimum(1,t/0.004)*vel*0.16
BEAT=60/84
def chord_at(tt):
    for s0,e0,n in CH:
        if s0<=tt<e0: return n
    return CH[-1][2]
def tones(tt):
    n=chord_at(tt); base=[m for m in n[1:]]
    return sorted([m+12 if m+12>=69 else m+24 for m in base])
pattern=[0,2,1,3,2,4,3,1]
def seq(a,b,step,prob,octup=0):
    k=0; tt=a
    while tt<b-0.05:
        if rng.random()<prob:
            ts=tones(tt); m=ts[pattern[k%len(pattern)]%len(ts)]+octup
            add(bell(mtof(m),rng.uniform(.55,1.0)),tt+rng.normal(0,.006),pan=0.45 if k%2 else -0.45)
        k+=1; tt+=step
seq(1.0,7,BEAT*2,0.9)
seq(7.6,15,BEAT,0.85)
seq(15.3,24.8,BEAT/2,0.82)
seq(25.2,31.8,BEAT,0.85)
seq(32.8,36.5,BEAT*2,0.9)
for f,tt,v in [(mtof(78),33.0,1.1),(mtof(85),36.8,0.9),(mtof(90),36.8,0.5)]: add(bell(f,v),tt)

# ---- transitions: airy swell + soft low impact ----
bp=butter(2,[1800,7000],'band',fs=SR,output='sos')
for tr in (7,15,25,32):
    d=1.6; n=int(d*SR); t=np.arange(n)/SR
    nz=sosfilt(bp,rng.standard_normal(n))*(t/d)**3*0.05
    for ch,g in ((L,1),(R,1)): pass
    add(nz,tr-d,pan=-0.2); add(sosfilt(bp,rng.standard_normal(n))*(t/d)**3*0.05,tr-d,pan=0.2)
    n2=int(1.5*SR); t2=np.arange(n2)/SR
    boom=np.sin(2*np.pi*(46+30*np.exp(-t2/0.05))*t2)*np.exp(-t2/0.45)*0.22
    add(boom,tr)

# ---- reverb ----
def ir(seed):
    r=np.random.default_rng(seed); n=int(3.2*SR); t=np.arange(n)/SR
    return sosfilt(butter(1,5000,'low',fs=SR,output='sos'),r.standard_normal(n))*np.exp(-t/0.75)
wL=fftconvolve(L,ir(1))[:N]; wR=fftconvolve(R,ir(2))[:N]
wL/=np.max(np.abs(wL))+1e-9; wR/=np.max(np.abs(wR))+1e-9
dry=max(np.max(np.abs(L)),np.max(np.abs(R)))
outL=L/dry*0.75+wL*0.38; outR=R/dry*0.75+wR*0.38
# master fades + low cut
t=np.arange(N)/SR
fade=np.minimum(1,t/1.2)*np.clip((40-t)/2.4,0,1)**1.5
hp=butter(2,35,'high',fs=SR,output='sos')
out=np.stack([sosfilt(hp,outL)*fade,sosfilt(hp,outR)*fade],1)
out/=np.max(np.abs(out)); out*=0.89
sf.write("musique-raw.wav",out,SR,subtype='PCM_24')
print("ok")
