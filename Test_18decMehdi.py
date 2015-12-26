#!/usr/bin/env python
# encoding: utf-8

from pyo import *
import random

##Gamme pour la mélodie en Note midi
scl1=[60,63,65,67,70,72,75,77,79,82]
sc1=midiToHz(scl1)# Conversion en Hertz
###Server Audio
s = Server(sr=44100, nchnls=2, buffersize=512, duplex=0).boot()
s.setAmp(.25)

####Synth Solo
env = AtanTable(slope=0.8) ##envellope
seq=Beat(time=.5, taps=16, w1=[90,80], w2=50, w3=35, poly=2).play()#metro pour un beat avec probabilité
##tr = TrigRand(seq, min=100, max=1500, port=.005)
trig1=TrigChoice(seq,choice=sc1, port=0.005)#Trig pour choisir les note de la melodie

##Metro pour l'envellope du synth (peut etre a remplace par le metro de beat)
mv=Metro(time = .001, poly=2).play()

### les composantes de la melodie= synth + waveguide+ harmonizer et filtres
menv=LinTable([(0, 0.0), (73, 0.9354838709677419), (1609, 0.7096774193548387), (3181, 0.43870967741935485), (4882, 0.6903225806451613), (5577, 0.1870967741935484), (8192, 0.0)])# envellope

tenv2=TrigEnv(mv, table=menv, dur=.05, mul=.3)#trig envlop qui fait dans le waveguide

te = TrigEnv(seq, table=env, dur=.25, mul=.2)#trig envellope pour le synth principle
synth= SumOsc(freq=trig1, ratio=0.75, mul=te).stop()
wg1=Waveguide(synth, freq=trig1, mul=tenv2*.1)
rand_w=Randi(min=950, max=1500, freq=.15)# random sinusoidale
#filtres
wg1f=ButLP(wg1, freq=rand_w).mix(2).out()

synf=ButLP(synth, 3000).mix(2).out()

h1=Harmonizer(wg1f+synf, transpo=12, mul=.1)

cho1=Chorus(h1, depth=2, feedback=rand_w)

shift=FreqShift(cho1, 100)

comph1=Compress(shift, thresh=-70, ratio=10, risetime=.01, falltime=.2, knee=0.5).mix(2).out()


###################################################################
#Section bass

blist=[24,27]
metro=Metro(.5,poly=2).play() # metro propre a la basse
bfrq=midiToHz(blist)
chr =random.uniform(.99,1.01)#chorus (qui en es pas vrm un, a corriger)
envb=LinTable([(0, 0.0), (100, 1.0), (1590, 0.5096774193548387), (2395, 0.4967741935483871), (4736, 0.5032258064516129), (6491, 0.7161290322580646), (8192, 0.0)]) ##meme logique que les trigs et env pour le synth
trig3=TrigChoice(metro, choice=bfrq, port=0.005)
tenv3=TrigEnv(metro, table=envb, dur=1.5, mul=.75)

#######################################################################
lfo = Phasor(.025, .1, .133, .1)# lfo du feedback de bass
Bass=RCOsc(trig3, sharp=lfo, mul=tenv3)
beq=ButLP(Bass,freq=400, mul=1)#eq bass
cho2=Chorus(beq,1,0.5, mul=5)


compb=Mix((Compress(cho2, thresh=-20, ratio=4, risetime=.01, falltime=.2, knee=0.5)),voices=2).out() # compression
####################################################################

#Delay + Reverb

#################################################
rdly=Randi(min=.3,max=.8, freq=.2, mul=.1)
dly=Delay(wg1f+h1+synf,delay=0.75, feedback=rdly, maxdelay=2, mul=.1)
Rev=Freeverb(compb+synf+wg1f+h1+dly, size=[.2,.9], damp=0.70, bal=0.70, mul=0.1)
room=Mix(Rev+dly,voices=2).out()
###Drum#############################################
seqdrum=Beat(time=2, taps=16, w1=100, w2=60, w3=100, poly=1).play()
metdrum=Metro(1).play()


envsn = LinTable(list=[(0, 1.0), (3500, 0.0)], size=8192)

envk=HannTable()
                

ak=Adsr(attack=0.07, decay=0.05, sustain=0.4, release=1.3, dur=0, mul=1, add=0).play()

bsnare=Adsr(attack=0.07, decay=2.35, sustain=0.8, release=3.8, dur=0, mul=1, add=0).play()

tesnare = TrigEnv(seqdrum, table=envsn, dur=.1, mul=bsnare)
sins=Sine(freq=220, mul=tesnare*.5)
sins2=Sine(freq=1100, mul=tesnare*.4)
nsnare= Noise(mul=tesnare*2)

fltsnare=ButHP(nsnare, freq=1500,mul=2)

csnare=Compress(sins+sins2+fltsnare, risetime=0.01, falltime=.1, lookahead=7, knee=0.5, ratio=6, mul=1)


tekick= TrigEnv(metdrum, table=envk, dur=.0125, mul=ak)
sink=Sine(90, mul=tekick)
ck=Compress(sink)
dk=Disto(ck,drive=.7,mul=1)
        
drum=Mix(dk+csnare, voices=2)
######################################################
###Carillon#######################################################################
instenv=CurveTable(list=[(1,0)], size=8192)
ls=[]
datnote=[72, 75,77,79,82,84,87,89,91,94,96]
def changenvl():
    global ls,x2,x3,x4,x5,x6,x7
    x2=random.uniform(1000,3000)
    x3=x2+random.uniform(300,500)
    x4=x3+random.uniform(200,400)
    x5=x4+random.uniform(100,350)
    x6=x5+random.uniform(400,600)
    x7=x6+random.uniform(500,600)
    ls=[(0,1),(x2,0),(x3,.5),(x4,0),(x5,.25),(x6,0),(x7,.125),(8191,0)]
    instenv.replace(ls)
    instenv.setTension(random.uniform(-1,1))
    instenv.setBias(random.uniform(-1,1))

ptv=Pattern(changenvl,.25).play()


iosc = Osc(table=instenv, freq=.25, mul=.5)
datchoice=TrigChoice(input=Metro(.125).play(),choice=midiToHz(datnote))
instcl= LFO(freq=datchoice,mul=iosc)
hrmi1=Harmonizer(instcl, transpo=7.00,mul=1, add=0)
hrmi2=Harmonizer(instcl, transpo=10,mul=1, add=0)
hrmi3=Harmonizer(instcl, transpo=12,mul=1, add=0)
rdd1=Randh(min=.3,max=.6, freq=.2)
rdd2=Randi(min=.6, max=.95, freq=.5)
dly2=Delay(instcl+hrmi1+hrmi2+hrmi3, delay=rdd1, feedback=rdd2, maxdelay=1, mul=1)
verb2=Freeverb(dly2,size=.75, damp=0.50, bal=0.50, mul=.25).mix(2)


##########score

#####################################

def event_0():##bass seule
    pass
    
def event_1():
    pass
def event_2():
    global blist, trig3 # changement de note de bass
    blist=[36,39, 48,51]
    trig3=TrigChoice(metro, choice=(midiToHz(blist)), port=0.005)
    Bass.setFreq(trig3)
def event_3(): # arrivee du synth
    synth.out()
    synth.play()
    print seq.taps, seq.time
def event_4():
    pass
def event_5():
    pass
def event_6(): #changement de pattern rythm de la melodie
    global seq 
    seq.setTaps(9)
    seq.setTime(.25)
    seq.setWeights(w1=80, w2=50, w3=30)
    print seq.taps, seq.time
def event_7(): # arrivée du granulator qui bouffe des ressources !
    seq.new()
def event_8(): # stop du granulator + changemnt de param de seq
    global seq
    print seq.taps, seq.time
    
    
    seq.setTime(.125)
def event_9():
  
    seq.new()
    
  
def event_10(): #arrivé de choir, qui sont des filtres superposé sur un bruit blanc, passes bandes avec un gros Qparam qui donnent voicing d'accords. J'ai fait une progression harmoniques qui vas piger dans 3 listes de notes d'accords, un espece d'écriture a 3 voix
###flts2 et 3, refiltre la premiere voix avec des frequences centrales des 2 autres voix !
    global blist, trig3, flts, flts2,flts3, flts4, fltsx3,fltsx2, choir
    blist=[36,39,41,48,51,53,55,58]
    trig3=TrigChoice(metro, choice=(midiToHz(blist)), port=0.05)
    Bass.setFreq(trig3)
    
    met= Metro(time=3,poly=1).play()
    rnd2=Randi(min=20, max=40, freq=.05)
    rnd3=Randi(min=30, max=40, freq=.1)

    list1=[60,63,65,67]
    l1=midiToHz(list1)

    list2=[67,70,72,75]
    l2=midiToHz(list2)
    list3=[75,77,79,82]
    l3=midiToHz(list3)

    ff1=TrigChoice(met,choice=l1, port=0.005)

    nchord= Noise()
    flt= EQ(nchord, freq=ff1,q=100, type=0,mul=1.6)
    flts=ButBP(flt, freq=ff1, q=100, mul=1)
    ff2=TrigChoice(met,choice=l2, port=0.005)
    flt2= EQ(nchord, freq=ff2, q=100, boost=rnd2, type=0,mul=1.6)
    fltsx2=ButBP(flt2, freq=ff2, q=100, mul=.9)
    flts2=ButBP(flt, freq=ff2, q=100, mul=.4)

    ff3=TrigChoice(met,choice=l3, port=0.005)
    flt3= EQ(nchord, freq=ff3, q=100, boost=rnd3, type=0,mul=1.6)
    fltsx3=ButBP(flt, freq=ff3, q=100, mul=.9)
    flts3=ButBP(flt3, freq=ff3, q=100, mul=.4)
    flts4=ButBP(flt3, freq=ff3, q=100, mul=.4)
    choir=Mix(flts4+flts3+flts2+fltsx3+fltsx2+flts, voices=2,mul=.5).out()
    dly.setInput(wg1f+h1+synf+choir,fadetime=0.05)
    Rev.setInput(compb+synf+fltsx3+fltsx2+wg1f+h1+dly+flts3+flts2+flts, fadetime=.05)
    print "hello"
def event_11():
    synth.stop()
    synf.stop()
    wg1f.stop()
    h1.stop()
    
def event_12():
    dly.setInput(choir,fadetime=0.05)
    Rev.setInput(compb+flts2+flts3+dly+fltsx3+fltsx2+flts, fadetime=.05)
def event_13():
    dly.setInput(fltsx3+fltsx2+flts,fadetime=0.05)
    Rev.setInput(compb+dly+fltsx3+fltsx2+flts, fadetime=.05)
    
def event_14():
    flts3.stop()
    flts2.stop()
    print "oooo"
def event_15():
    pass
    
def event_16():
    synth.out()
    synth.play()
    dly.setInput(synth+fltsx3+fltsx2+flts,fadetime=0.05)
    Rev.setInput(compb+synth+dly+fltsx3+fltsx2+flts, fadetime=.05)
    
def event_17():
    pass
    
def event_18():
    pass
    
def event_19():
    drum.out()
def event_20():
    pass
    
def event_21():
    pass
def event_22():
    global blist, trig3 # changement de note de bass
    blist=[36,39,41,43]
    trig3=TrigChoice(metro, choice=(midiToHz(blist)), port=0.005)
    Bass.setFreq(trig3)
    synth.stop()
    
def event_23():
    verb2.out()
    
def event_24():
    metdrum.setTime(.5)
    seqdrum.setTime(.5)
    
def event_25():
    seqdrum.setW1(30)
    seqdrum.setW2(40)
    seqdrum.setW3(75)
   
    
def event_26():
    pass
def event_27():
    pass
def event_28():
    pass
def event_29():
    pass
    
def event_30():
    pass
    
def event_31():
    pass
    
def event_32():
    choir.stop()
    
def event_33():
    pass
    

#definition du scores et compteurs
metpart = Metro(6).play()
cnt = Counter(metpart, min=0, max=34)
sc = Score(cnt)


s.gui(locals())
