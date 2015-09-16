import os
import sys

from pcbnew import *

def gen_data_file(b):
    # We get all layer
    b.SetVisibleAlls()
    ls = b.GetVisibleLayers()
    
    # Use awful black magic things you shouldn't see
    compat = NewApiCompat()
    layers_list = compat._from_LayerSet(ls)
    
    s_layers = "LYR "
    for l in layers_list:
        s_layers = s_layers + l + " "
    
def gen_comp_file(b):
	# Generate the component file and package file
	modules = b.GetModules()
	for m in modules:
		print m.GetName()
		create_package(m)
		create_component(m)

def create_component(m):
	# Create module section in file
	
def create_package(m):
	# Add package entry to EDA file
	# Need to get the footprint name / size / pad
	# Check if already existing
	# If not create it
	# return the dict entry
	return

class NewApiCompat:
    #Please remove this code when new kicad python API will be the standard
    #Please DO NOT USE THIS CLASS IN OTHER SCRIPT WITHOUT ASKING
    #Ask on IRC if not sure.
    def __init__(self):
        self.layer_dict = {BOARD_GetStandardLayerName(n):n for n in range(LAYER_ID_COUNT)}
        self.layer_names = {s:n for n, s in self.layer_dict.iteritems()}
        for l in self.layer_dict:
            print l
        #self.layer_odb_name = 

    def _get_layer(self,s):
        """Get layer id from layer name"""
        return self.layer_dict[s]

    def _to_LayerSet(self,layers):
        """Create LayerSet used for defining pad layers"""
        bitset = 0
        for l in layers:
            bitset |= 1 << self._get_layer(l)
        hexset = '{0:013x}'.format(bitset)
        lset = pcbnew.LSET()
        lset.ParseHex(hexset, len(hexset))
        return lset

    def _from_LayerSet(self,layerset):
        mask = [c for c in layerset.FmtBin() if c in ('0','1')]
        mask.reverse()
        ids = [i for i, c in enumerate(mask) if c == '1']
        return tuple(self.layer_names[i] for i in ids)
