"""
init.py

Starting script to run NetPyNE-based models

"""
from netpyne import sim
from cfg import cfg
from netParams import netParams



def get_epsp(sim): #gets the EPSP data
    """
    after running the simulation, this samples sim.simData for the EPSP
    """
    v = sim.simData['V_soma']['cell_0'].as_numpy()
    start = int(sim.net.params.stimSourceParams['STIM']['start'] / sim.cfg.recordStep)
    return v[start:].max() - v[start-1]

epsp = []
stim = []


for i in range(5):
    weight = 0.3
    cfg.NetStim1['synMechWeightFactor']= i*[weight, weight]
    sim.createSimulateAnalyze(netParams, cfg)
    stim.append(i*weight)
    epsp.append(get_epsp(sim))




plt.figure(figsize=(10,6))
plt.plot(stim, epsp)
plt.title('Epsc / stim')
plt.xlable('Stim')
plt.ylable('Epsc')
plt.grid()
plt.tight_layout()

plt.saveFig(f'Activity_EPSC')