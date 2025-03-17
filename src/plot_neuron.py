from neuron import h, gui  # Required for NEURON GUI functionality
h.topology()
# Load the morphology file
"""morphology_file = "/Users/gy/Desktop/Neuron/Synapse/Na12HH16HH_singlecell/cells/Neuron_Model_12HH16HH/morphology/dend-C060114A2_axon-C060114A5.asc"  # Replace with the path to your .asc file
morph_reader = h.Import3d_SWC_read()
morph_reader.input(morphology_file)

# Instantiate the morphology
cell = h.Import3d_GUI(morph_reader)
cell.instantiate(None)

# Visualize the morphology
shape_plot = h.PlotShape()
shape_plot.show(0)  # Display the morphology

# Optional: Add color to specific sections
shape_plot.color(2, sec=h.soma[0])  # Example: Color soma in red (color index 2)
"""

