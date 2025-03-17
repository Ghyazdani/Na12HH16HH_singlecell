"""
netParams.py

High-level specifications for M1 network model using NetPyNE

"""

from netpyne import specs
import os

try:
    from __main__ import cfg # import SimConfig object with params from parent module
except:
    from src.cfg import cfg



#########################################################################################
#
#NETWORK PARAMETERS
#
#########################################################################################
netParams = specs.NetParams() # Object class NetParams to store network parameters


###############################################################################
# Cell parameters
###############################################################################

#------------------------------------------------------------------------------
# Load cell rules previously saved using netpyne format
#------------------------------------------------------------------------------
loadCellParams = True
saveCellParams = False

# get current path
base_path = os.path.dirname(os.path.abspath(__file__))

# Construct the correct path to the JSON file
file_path = os.path.join(base_path, '../cells/Na12HH16HH_TF.json')

if loadCellParams:
   netParams.loadCellParamsRule(label='PT5B_full', fileName=file_path)

#------------------------------------------------------------------------------
# Includes importing from hoc template or python class, and setting additional params
#------------------------------------------------------------------------------

if not loadCellParams:
    # import cell model from NEURON/Python code
    netParams.importCellParams('PT5B_full', 'cells/Na12HH16HHModel_TF.py', 'Na12Model_TF')

    # rename soma to conform to netpyne standard
    netParams.renameCellParamsSec(label='PT5B_full', oldSec='soma_0', newSec='soma')

    # set variable so easier to work with below
    cellRule = netParams.cellParams['PT5B_full']

    # create some section lists useful to define the locations of synapses
    cellRule['secLists']['alldend'] = [sec for sec in cellRule['secs'] if ('dend' in sec or 'apic' in sec)]  # basal+apical
    cellRule['secLists']['apicdend'] = [sec for sec in cellRule['secs'] if ('apic' in sec)]  # apical
    nonSpiny = ['apic_0', 'apic_1']
    cellRule['secLists']['spiny'] = [sec for sec in cellRule['secLists']['alldend'] if sec not in nonSpiny]

    # set the spike generation location to the axon (default in NEURON is the soma)
    cellRule['secs']['axon_0']['spikeGenLoc'] = 0.5

    # Lowering V threshold since it looks like v in soma is not reaching high voltages when spike occurs
    cellRule['secs']['axon_0']['threshold'] = 0.

    #set weight normalization
    netParams.addCellParamsWeightNorm('PT5B_full', 'conn/PT5B_full_weightNorm.pkl',
                                      threshold=cfg.weightNormThreshold)

    # save to json with all the above modifications so easier/faster to load
    if saveCellParams: netParams.saveCellParamsRule(label='PT5B_full', fileName='cells/Na12HH16HH_TF.json')


###############################################################################
# Population parameters
###############################################################################

netParams.popParams['PT5B'] =	{'cellType': 'PT5B_full', 'numCells': 1}


###############################################################################
# Synaptic Mechanism parameters
###############################################################################

netParams.synMechParams['AMPA'] = {'mod':'MyExp2SynBB', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}
netParams.synMechParams['NMDA'] = {'mod': 'MyExp2SynNMDABB', 'tau1NMDA': 15, 'tau2NMDA': 150, 'e': 0}


###############################################################################
# Stimulation parameters
###############################################################################

# ------------------------------------------------------------------------------
# Current inputs (IClamp)
# ------------------------------------------------------------------------------
if cfg.addIClamp:
    for key in [k for k in dir(cfg) if k.startswith('IClamp')]:
        params = getattr(cfg, key, None)
        [pop, sec, loc, start, dur, amp] = [params[s] for s in ['pop', 'sec', 'loc', 'start', 'dur', 'amp']]

        # add stim source
        netParams.stimSourceParams[key] = {
            'type': 'IClamp', 
            'delay': start, 
            'dur': dur, 
            'amp': amp}

        # connect stim source to target
        netParams.stimTargetParams[key + '_' + pop] = {
            'source': key,
            'conds': {'pop': pop},
            'sec': sec,
            'loc': loc}

# ------------------------------------------------------------------------------
# NetStim inputs
# ------------------------------------------------------------------------------
if cfg.addNetStim:
    for key in [k for k in dir(cfg) if k.startswith('NetStim')]:
        params = getattr(cfg, key, None)
        [pop, sec, loc, synMech, synMechWeightFactor, start, interval, noise, number, weight, delay] = \
            [params[s] for s in
             ['pop', 'sec', 'loc', 'synMech', 'synMechWeightFactor', 'start', 'interval', 'noise', 'number',
              'weight', 'delay']]

        # add stim source
        netParams.stimSourceParams[key] = {
            'type': 'NetStim', 
            'start': start, 
            'interval': interval, 
            'noise': noise,
            'number': number}

        # connect stim source to target
        netParams.stimTargetParams[key + '_' + pop] = {
            'source': key,
            'conds': {'pop': pop},
            'sec': sec,
            'loc': loc,
            'synMech': synMech,
            'weight': weight,
            'synMechWeightFactor': synMechWeightFactor,
            'delay': delay}