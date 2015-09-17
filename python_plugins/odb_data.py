import os
import sys

from math import *
from pcbnew import *

class ODB_GEN:
	def __init__(self):
		self.packages = []
		self.pkg_n = []
		self.components = []

	# Abandonned function for now
	# Usefull to generate the full copper part
	def gen_data_file(self, b):
		# We get all layer
		b.SetVisibleAlls()
		ls = b.GetVisibleLayers()
		
		# Use awful black magic things you shouldn't see
		compat = NewApiCompat()
		layers_list = compat._from_LayerSet(ls)
		
		s_layers = "LYR "
		for l in layers_list:
			s_layers = s_layers + l + " "
		
	def gen_comp_file(self, b):
		# Generate the component file and package file
		self.b = b
		modules = b.GetModules()
		for m in modules:
			print "Reference: " + m.GetReference()
			print "Value: " + m.GetValue()
			self.add_package(m)
			self.create_component(m)
		self.write_pkg_file()

	def create_component(self, m):
		# Create module section in file
		return

	def add_package(self, m):
		# Add package entry to EDA file
		# Need to get the footprint name / size / pad
		# Check if already existing
		# If not create it
		# return the dict entry
		# To be changed to magic hashing function 
		# so kicad developpers will be happy
		lib_name = self.get_lib_name(m)
		pkg_name = self.get_fp_name(m) + "-" + lib_name
		print self.packages
		print pkg_name
		if (not pkg_name in self.pkg_n):
			pkg = self.create_package(m, pkg_name)
			self.pop_pins(m, pkg)
			self.pkg_n.append(pkg_name)
			self.packages.append(pkg)
		return pkg_name

	# We get the module
	# Copy it
	# Reset rotation
	# Put center 0
	# Easy way to get the package model
	def create_package(self, m, pkg_name):
		m.SetOrientation(0)
		a = wxPoint(0,0)
		m.SetPosition(a)
		pitch = self.get_pitch(m)
		rect = m.GetFootprintRect()
		amin = rect.GetOrigin()
		amax = rect.GetEnd()
		return Package(pkg_name, pitch, ToMils(amin.x)/1000, ToMils(amin.y)/1000, ToMils(amax.x)/1000, ToMils(amax.y)/1000,m)

	# Closest Pair Problem to be optimised for big board !
	def get_pitch(self, m):
		min_distance = 1000 # will be expressed in inches
		pads_list = []
		for p in m.Pads():
			pads_list.append(p)
		for i in range(0, m.GetPadCount()):
			p1x = pads_list[i].GetPosition().x
			p1y = pads_list[i].GetPosition().y
			for j in range(i+1, m.GetPadCount()):
				p2x = pads_list[j].GetPosition().x
				p2y = pads_list[j].GetPosition().y
				distx = ToMils(fabs(p2x - p1x)) / 1000
				disty = ToMils(fabs(p2y - p1y)) / 1000
				if ((distx < min_distance) and (distx != 0)):
					min_distance = distx
				if ((disty < min_distance) and (disty != 0)):
					min_distance = disty
		return min_distance

	def get_fp_name(self, m):
		return m.GetFPID().GetFootprintName()

	def get_lib_name(self, m):
		return m.GetFPID().GetLibNickname()

	def pop_pins(self, m, pkg):
		for p in m.Pads():
			name = p.GetPadName()
			xc = p.GetPosition().x
			yc = p.GetPosition().y
			t = pin_attribute(p.GetAttribute())
			fhs = p.GetDrillSize()
			# Unknown pad type see implementation details
			etype = "U"
			mtype = "U"
			pkg.add_pin(PIN(name,t,xc,yc,fhs,etype,mtype,p))

	def write_pkg_file(self):
		i = 0
		for p in self.packages:
			# write first line
			s = "#\n# PKG %i\n" % i
			s = "%sPKG %s %12.12f %12.12f %12.12f %12.12f %12.12f\n" % (s, p.name, p.pitch, p.xmin, p.ymin, p.xmax, p.ymax)
			# do the outline 
			s = "%sRC %12.12f %12.12f %12.12f %12.12f\n" % (s, p.xmin, p.ymin, p.xmax-p.xmin, p.ymax-p.ymin)
			i = i + 1
			print s

class Package:
	def __init__(self, name, pitch, xmin, ymin, xmax, ymax, pkg):
		self.name = name
		self.pitch = pitch
		self.xmin = xmin
		self.ymin = ymin
		self.xmax = xmax
		self.ymax = ymax
		self.pins = []
		self.pkg = pkg
	
	def add_pin(self, pin):
		self.pins.append(pin)

# See PAGE 88 ODB++ v7 spec
class PIN:
	def __init__(self, number, type, x, y, fhs, etype, mtype, pad):
		self.number = number
		self.type = type
		self.x = x
		self.y = y
		self.fhs = fhs
		self.etype = etype
		self.mtype = mtype
		self.pad = pad

	def add_shape():
		return

# See pad_shapes.h
def pin_attribute(at):
	if(at==0): # Thru hole
		return "T"
	elif(at==1): # SMT
		return "S"
	elif(at==2):
		return "S"
	elif(at==3):
		return "T"
	# B would be blind
	return "T"

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
