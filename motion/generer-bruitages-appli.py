import numpy as np, soundfile as sf
SR=48000; N=40*SR; rng=np.random.default_rng(2)
m,_=sf.read("app/musique-raw.wav"); out=m.copy()*0.55
tt=lambda d:np.arange(int(d*SR))/SR
def add(sig,t,g):
    i=int(t*SR); n=min(len(sig),N-i); out[i:i+n,0]+=sig[:n]*g; out[i:i+n,1]+=sig[:n]*g
def ding(f1,f2):      # two-tone notification chime
    t=tt(.7); a=np.sin(2*np.pi*f1*t)*np.exp(-t/.25)*np.minimum(1,t/.003)
    b=np.zeros_like(t); k=int(.09*SR); tb=t[:-k]; b[k:]=np.sin(2*np.pi*f2*tb)*np.exp(-tb/.3)
    return (a+b+.2*np.sin(2*np.pi*f2*2*t)*np.exp(-t/.1))*.5
def tick():
    t=tt(.08); return np.sin(2*np.pi*(1800-900*t/.08)*t)*np.exp(-t/.018)
def pop():
    t=tt(.12); return np.sin(2*np.pi*np.cumsum(500+700*np.exp(-t/.025))/SR)*np.exp(-t/.035)
def swoosh(d=.3):
    from scipy.signal import butter,sosfilt
    t=tt(d); return sosfilt(butter(2,[900,5000],'band',fs=SR,output='sos'),rng.standard_normal(len(t)))*np.sin(np.pi*t/d)**2*.5
S={'s1':0,'s2':5.6,'s3':9.2,'s4':20.2,'s5':28.6,'s6':33.4}; TICKS=[2.2,3.4,4.5,5.9,7.2,8.6]
for a in (0.9,1.7,2.5): add(ding(880,660),a,.35)          # bad news
add(pop(),3.3,.5)
for k in ('s2','s3','s4','s5','s6'): add(swoosh(),S[k]-.15,.35)
add(swoosh(.5),4.6,.4)                                   # cards swiped away
for i,x in enumerate(TICKS): add(tick(),S['s3']+x,.45); add(pop(),S['s3']+.8+i*.12,.15)
for i in range(4): add(pop(),S['s4']+.8+i*1.05,.3)
add(pop(),S['s4']+5.4,.45)
for a in (1.1,2.0): add(ding(1046,1318),S['s5']+a,.4)  # good news
add(pop(),S['s5']+2.8,.45)
for i in range(5): add(pop(),S['s6']+1.3+i*.1,.2)
add(pop(),S['s6']+2.1,.45)
out/=np.abs(out).max(); sf.write("app/mix-raw.wav",out*.9,SR); print("ok")
