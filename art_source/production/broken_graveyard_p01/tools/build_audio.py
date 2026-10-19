"""Original editable synthetic Foley/resonance DRAFTS; no sampled recordings."""
from pathlib import Path
import numpy as np
import wave, json
ROOT=Path(__file__).resolve().parents[4]
SR=48000
RNG=np.random.default_rng(9019)

def resonator(duration,frequency,decay=12,noise=.2):
    t=np.arange(int(duration*SR))/SR
    n=RNG.normal(size=t.size)
    # Mixed low-pass/differenced noise makes dull contact instead of a reward ping.
    n=np.convolve(n,np.ones(11)/11,mode='same')
    env=np.minimum(1,t/.003)*np.exp(-t*decay)
    return (np.sin(t*2*np.pi*frequency)+.24*np.sin(t*2*np.pi*frequency*1.71)+noise*n)*env

def taps(length,events):
    y=np.zeros(int(length*SR))
    for start,f,amp,decay in events:
        x=resonator(min(.38,length-start),f,decay,.65)*amp
        a=int(start*SR); y[a:a+len(x)]+=x
    return y

def save(name,y,folder):
    # Remove DC, fade endpoints and cap level without loudness normalization to 0 dBFS.
    y=y-np.mean(y)
    count=min(400,len(y)//3)
    y[:count]*=np.linspace(0,1,count)
    y[-count:]*=np.linspace(1,0,count)
    peak=max(float(np.max(np.abs(y))),1e-6)
    y=y*min(1,.28/peak)
    target=ROOT/'audio'/folder/(name+'.wav'); target.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(target),'wb') as w:
        w.setparams((1,2,SR,len(y),'NONE','not compressed'))
        w.writeframes((y*32767).astype('<i2').tobytes())
    return dict(id=name,path=str(target.relative_to(ROOT)),seconds=len(y)/SR,peak_dbfs=round(20*np.log10(max(abs(y).max(),1e-9)),2),source='original deterministic synthesis; audition candidate, not recorded Foley')

def main():
    entries=[]
    def add(name,y,folder): entries.append(save(name,y,folder))
    scatter=taps(.85,[(.02,530,.16,28),(.13,730,.12,35),(.23,420,.1,30),(.39,920,.07,40),(.54,650,.05,35)])
    add('bone_scatter',scatter,'enemies')
    collapse=taps(1.1,[(.0,145,.18,16),(.06,240,.16,22),(.16,480,.14,25),(.25,680,.1,30),(.45,530,.06,30),(.62,840,.035,40)])
    add('skeleton_collapse',collapse,'enemies')
    t=np.arange(int(.95*SR))/SR
    tension=(np.sin(2*np.pi*(135*t+45*t*t))+.16*np.sin(2*np.pi*460*t))*np.sin(np.pi*t/.95)**3*.075
    add('bone_reassembly_tension',tension,'enemies')
    t=np.arange(int(.66*SR))/SR
    air=np.convolve(RNG.normal(size=len(t)),np.ones(90)/90,mode='same')
    echo=(air*.22+np.sin(2*np.pi*(255*t+30*t*t))*.055)*np.sin(np.pi*t/.66)**2
    add('echo_absorb',echo,'loot')
    add('special_loot_clink',taps(.58,[(.0,1420,.08,22),(.025,740,.045,32),(.055,2280,.017,12)]),'loot')
    add('pickup',taps(.35,[(.0,310,.065,25),(.04,620,.038,26)]),'loot')
    t=np.arange(int(.55*SR))/SR
    focus=(np.sin(2*np.pi*(410*t+60*t*t))*.055+np.sin(2*np.pi*820*t)*.014)*np.sin(np.pi*t/.55)**2
    add('observe_invoke',focus,'words')
    add('shatter_invoke',taps(.65,[(0,180,.16,27),(.025,640,.12,45),(.07,980,.08,55),(.11,410,.055,32)]),'words')
    t=np.arange(int(.85*SR))/SR
    dust=np.convolve(RNG.normal(size=len(t)),np.ones(8)/8,mode='same')
    erode=dust*.09*np.sin(np.pi*t/.85)**2*(.65+.35*np.sin(2*np.pi*11*t))
    add('erode_invoke',erode,'words')
    p=ROOT/'art_source/production/broken_graveyard_p01/audio_manifest.json'
    p.write_text(json.dumps(entries,indent=2)+'\n')
    print('9 original mono 48kHz PCM drafts written.')
if __name__=='__main__': main()
