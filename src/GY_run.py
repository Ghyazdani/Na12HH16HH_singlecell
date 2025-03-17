"""
init.py

Starting script to run NetPyNE-based models
"""

from netpyne import sim
from cfg import cfg
from netParams import netParams
from neuron import h, gui  # Required to display morphology
import matplotlib.pyplot as plt
import numpy as np

#setting cfg parameters, how does Iclamp contribute?
#you can't set location as position 0 or 1 if it needs an ion
cfg.addNetStim = 1 
cfg.NetStim1['sec'], cfg.NetStim1['loc'] = 'dend_49', 0.9
cfg.addIClamp = 1

def get_epsp(sim):
    """
    After running the simulation, this samples sim.simData for the EPSP.
    """
    v = np.array(sim.simData['V_soma']['cell_0'])  # Somatic voltage trace
    start = int(sim.net.params.stimSourceParams['NetStim1']['start'] / sim.cfg.recordStep)
    
    # Calculate the baseline voltage before stimulation
    baseline = np.mean(v[start - int(10 / sim.cfg.recordStep):start])  # Average of 10 ms prior
    
    # Calculate the peak EPSP
    peak_epsp = v[start:].max() - baseline
    print(f"Peak EPSP: {peak_epsp} mV")
    
    return peak_epsp



epsp = []
stim = []

for weight in range(1, 5):#what is the difference between synMechWeightFactor and weight
    #synMechWeightFactor is the relative contributions of each synaptic mechanism (AMPA, NMDA
    cfg.NetStim1['synMechWeightFactor'] = [0.5,0.5] * weight 
    cfg.NetStim1['weight'] = 0.5 * weight
    sim.createSimulateAnalyze(netParams, cfg)
    stim.append(cfg.NetStim1['weight'])
    epsp.append(get_epsp(sim))


print (epsp)
plt.figure(figsize=(10, 6))
plt.plot(stim, epsp, marker='o')
plt.title('EPSP vs Stim')
plt.xlabel('Stim')
plt.ylabel('EPSP')
plt.grid()
plt.tight_layout()
plt.savefig('Activity_EPSC.png')
plt.show()

"""first simulation of cortical column with patch clamp data
aim 1 kcnt1 modeling is with messages
aim2: neuron cultures
how that e

aim 3 organioud
in networks that Adam created and add kcnt1 
fit ammara

aim 1: first make inhibitory and excitatory neurons single neurons 
3 or 4 types of inhibitory

aim2: either mea or cortical column or both

aim3 :identifying therapeutics

in the case of gof kcnt1 what kind of drugs would work"""


"amp vs location and duration of stimulation which can separate the"