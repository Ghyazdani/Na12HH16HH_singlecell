import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import product
from netpyne import sim
from cfg import cfg
from netParams import netParams


def update_json(netParams, na12='na12', na12mut='na12mut', na16='na16', na16mut='na16mut'):
    """
    Updates the NetParams JSON structure by modifying specific ion channel parameters
    (na12, na12mut, na16, na16mut) for all sections.

    Returns:
        netParams: The updated netParams object.
    """
    
    # Load CSV once
    csv_filename = "ion_channel_parameters.csv"
    ion_channel_data = pd.read_csv(csv_filename, index_col=0).to_dict(orient="index")

    # Iterate through all sections and update parameters if specified
    for sec_data in netParams.cellParams['PT5B_full']['secs'].values():
        for mech in ['na12', 'na12mut', 'na16', 'na16mut']:
            try:
                sec_data['mechs'][mech].update(ion_channel_data[mech])
            except KeyError:
                pass  # Skip if the mechanism is missing

    return netParams


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


def compare_models(netParams, cfg, model1, model2, parameter='weight'):
    """
    Compares two models based on a given parameter (e.g., 'weight', 'number', etc.).
    
    Args:
        netParams (object): The network parameters object.
        cfg (object): The simulation configuration object.
        model1 (dict): A dictionary specifying na12, na12mut, na16, and na16mut keys for Model 1.
        model2 (dict): A dictionary specifying na12, na12mut, na16, and na16mut keys for Model 2.
        parameter (str): The parameter to study (default is 'weight').
    
    Returns:
        tuple: Two DataFrames containing the parameter values and corresponding EPSP results.
    """
    
    # Define a range of values for the parameter (scaling from 25% to 150% of the base value)
    
    if parameter == 'loc':
        cfg.NetStim1['sec'] = 'dend_86' #one of the most outer dendrites
        parameter_range =  [0,0.2,0.4,0.6,0.8,1]
    if parameter == 'sec':
        parameter_range = ['dend_86','dend_82', 'dend_73', 'soma_0']
    else:
        parameter_range = [cfg.NetStim1[parameter] * factor for factor in [0.25, 0.5, 0.75, 1, 1.25, 1.5]]

    
    results_model1 = []
    results_model2 = []
    
    for p in parameter_range:
        cfg.NetStim1[parameter] = p
        cfg.addNetStim = 1 
        cfg.addIClamp = 1

        # --- Run simulation for Model 1 ---
        netParams_model1 = update_json(netParams, **model1)
        sim.createSimulateAnalyze(netParams_model1, cfg)
        epsp1 = get_epsp(sim)
        results_model1.append((p, epsp1))
        
        # --- Run simulation for Model 2 ---
        netParams_model2 = update_json(netParams, **model2)
        sim.createSimulateAnalyze(netParams_model2, cfg)
        epsp2 = get_epsp(sim)
        results_model2.append((p, epsp2))
    
    # Convert results to DataFrames
    df_model1 = pd.DataFrame(results_model1, columns=[parameter, 'EPSP'])
    df_model2 = pd.DataFrame(results_model2, columns=[parameter, 'EPSP'])
    
    # Plot the comparison
    plt.figure(figsize=(10, 6))
    plt.plot(df_model1[parameter], df_model1['EPSP'], marker='o', label=f'Model 1: {model1["na12"]}')
    plt.plot(df_model2[parameter], df_model2['EPSP'], marker='o', label=f'Model 2: {model2["na12"]}')
    plt.xlabel(parameter)
    plt.ylabel('EPSP (mV)')
    plt.title(f'Comparison of EPSP vs {parameter}_noIclamp')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'Comparison_EPSP_vs_{parameter}_noIclamp.png')
    plt.show()
    
    return df_model1, df_model2


# Example usage
model1 = {'na12': 'na12_122', 'na12mut': 'na12_13', 'na16': 'na16_99', 'na16mut': 'na16_99'}
model2 = {'na12': 'na12', 'na12mut': 'na12mut', 'na16': 'na16', 'na16mut': 'na16mut'}

df_model1, df_model2 = compare_models(netParams, cfg, model1, model2, parameter='weight') 

