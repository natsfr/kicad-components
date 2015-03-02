from __future__ import division
import pcbnew
import HelpfulFootprintWizardPlugin as HFPW
import FootprintWizardDrawingAids as FWDA
import PadArray as PA

import math

class NewApiCompat:
    #Please remove this code when new kicad python API will be the standard
    #Please DO NOT USE THIS CLASS IN OTHER SCRIPT WITHOUT ASKING
    #Ask on IRC if not sure.
    def __init__(self):
        self.layer_dict = {pcbnew.BOARD_GetStandardLayerName(n):n for n in range(pcbnew.LAYER_ID_COUNT)}
        self.layer_names = {s:n for n, s in self.layer_dict.iteritems()}

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

class ThermalViasArray(PA.PadGridArray):
    def NamingFunction(self, x, y):
        return self.firstPadNum

class QFNWizard(HFPW.HelpfulFootprintWizardPlugin):

    def GetName(self):
        return "QFN"

    def GetDescription(self):
        return "QFN Wizard"

    def GenerateParameterList(self):
        self.AddParam("Pads", "nbpads", self.uNatural, 20)
        self.AddParam("Pads", "pitch", self.uMM, 0.5)
        self.AddParam("Pads", "pad width", self.uMM, 0.25)
        self.AddParam("Pads", "pad length", self.uMM, 0.4)
        self.AddParam("Pads", "pitch", self.uMM, 0.5)
        self.AddParam("Pads", "oval", self.uBool, True)
        self.AddParam("Pads", "Width", self.uMM, 4)
        self.AddParam("Pads", "Length", self.uMM, 4)
        self.AddParam("Pads", "Fillet", self.uMM, 0.3)

        self.AddParam("TPad", "tpad", self.uBool, True)
        self.AddParam("TPad", "W", self.uMM, 2.6)
        self.AddParam("TPad", "L", self.uMM, 2.6)
        
        self.AddParam("TPaste", "tpaste", self.uBool, True)
        self.AddParam("TPaste", "box rows", self.uNatural, 4)
        self.AddParam("TPaste", "box cols", self.uNatural, 4)
        self.AddParam("TPaste", "percent", self.uNatural, 50)

        self.AddParam("TVias", "tvias", self.uBool, True)
        self.AddParam("TVias", "rows", self.uNatural, 3)
        self.AddParam("TVias", "cols", self.uNatural, 3)
        self.AddParam("TVias", "drill", self.uMM, 0.3)
        self.AddParam("TVias", "size", self.uMM, 0.6)
        self.AddParam("TVias", "pitch", self.uMM, 1)

    def CheckParameters(self):
        self.CheckParamInt("Pads", "*nbpads")
        self.CheckParamInt("Pads", "*nbpads", is_multiple_of=4)
        self.CheckParamBool("Pads", "*oval")
        self.CheckParamBool("TPad", "*tpad")
        self.CheckParamBool("TVias", "*tvias")
        self.CheckParamBool("TPaste", "*tpaste")

        self.CheckParamInt("TPaste", "*box rows", min_value=2)
        self.CheckParamInt("TPaste", "*box cols", min_value=2)
        self.CheckParamInt("TPaste", "*percent")

    def GetValue(self):
        return "QFN%d_%dx%dmm" % (self.parameters["Pads"]["*nbpads"],pcbnew.ToMM(self.parameters["Pads"]["Width"]),pcbnew.ToMM(self.parameters["Pads"]["Length"]))

    def GetReferencePrefix(self):
        return "U"

    def DrawThermalPadSolderPaste(self, x, y, rows, cols, percent):
        # Calculate the paste area given percentage
        x_total_size = x / (math.sqrt(1/(percent/100)))
        y_total_size = y / (math.sqrt(1/(percent/100)))

        x_box = x_total_size / cols
        y_box = y_total_size / cols

        x_spacer = (x - cols * x_box) / (cols - 1)
        y_spacer = (y - rows * y_box) / (rows - 1)

        x_step = x_spacer + x_box
        y_step = y_spacer + y_box

        # Use PAD as Paste only but Kicad complains
        # Is it a valid use ?
        pastepad = PA.PadMaker(self.module).SMDPad(x_box, y_box, pcbnew.PAD_RECT)
        only_paste = pcbnew.LSET(pcbnew.F_Paste)
        pastepad.SetLayerSet(only_paste)

        array = ThermalViasArray(pastepad, cols, rows, x_step, y_step)
        #array.SetFirstPadInArray(self.parameters["Pads"]["*nbpads"]+1)
        array.SetFirstPadInArray('~')
        array.AddPadsToModule(self.draw)

    def BuildThisFootprint(self):
        tpad = self.parameters["TPad"]
        pads = self.parameters["Pads"]
        tvias = self.parameters["TVias"]
        tpaste = self.parameters["TPaste"]

        if(tpad["*tpad"]):
            thermal_pad = PA.PadMaker(self.module).SMDPad(tpad["W"], tpad["L"], pcbnew.PAD_RECT)

            # Use new kicad python api to have compatible layer set type
            compat = NewApiCompat()
            no_paste_lset = compat._to_LayerSet(('F.Cu', 'F.Mask'))
            thermal_pad.SetLayerSet(no_paste_lset)

            origin = pcbnew.wxPoint(0,0)
            array = PA.PadLineArray(thermal_pad, 1, 0, False)
            array.SetFirstPadInArray(pads["*nbpads"]+1)
            array.AddPadsToModule(self.draw)
            if(tvias["*tvias"]):
                via_size = tvias["size"]
                via_drill = tvias["drill"]
                via_rows = tvias["*rows"]
                via_cols = tvias["*cols"]
                via_pitch = tvias["pitch"]
                thermal_via = PA.PadMaker(self.module).THRoundPad(via_size, via_drill)
                array = ThermalViasArray(thermal_via, via_cols, via_rows, via_pitch, via_pitch)
                array.SetFirstPadInArray(pads["*nbpads"]+1)
                array.AddPadsToModule(self.draw)
                if(tpaste["*tpaste"]):
                    self.DrawThermalPadSolderPaste(tpad["W"], tpad["L"], tpaste["*box rows"], tpaste["*box cols"], tpaste["*percent"])

        nb_pads_row = pads["*nbpads"] / 4;
        line_start = pads["pitch"] * (nb_pads_row - 1) / 2

        pad_len = pads["pad length"]
        fillet = pads["Fillet"]
        pad_total = pad_len + fillet
        len_2 = pads["Length"] / 2
        wid_2 = pads["Width"] / 2

        pad_center_l = (len_2 - pad_len + (pad_len+fillet)/2)
        pad_center_w = (wid_2 - pad_len + (pad_len+fillet)/2)

        pad_shape = pcbnew.PAD_OVAL if pads["*oval"] else pcbnew.PAD_RECT

        v_pad = PA.PadMaker(self.module).SMDPad(pads["pad width"], pad_total, shape=pad_shape)
        h_pad = PA.PadMaker(self.module).SMDPad(pad_total, pads["pad width"], shape=pad_shape)

        pin1pos = pcbnew.wxPoint(-pad_center_l, 0)
        array = PA.PadLineArray(v_pad, nb_pads_row, pads["pitch"], True, pin1pos)
        array.SetFirstPadInArray(1)
        array.AddPadsToModule(self.draw)

        pin1pos = pcbnew.wxPoint(0, pad_center_w)
        array = PA.PadLineArray(h_pad, nb_pads_row, pads["pitch"], False, pin1pos)
        array.SetFirstPadInArray(int(nb_pads_row + 1))
        array.AddPadsToModule(self.draw)

        pin1pos = pcbnew.wxPoint(pad_center_l, 0)
        array = PA.PadLineArray(v_pad, nb_pads_row, -pads["pitch"], True, pin1pos)
        array.SetFirstPadInArray(int(nb_pads_row*2 + 1))
        array.AddPadsToModule(self.draw)

        pin1pos = pcbnew.wxPoint(0, -pad_center_w)
        array = PA.PadLineArray(h_pad, nb_pads_row, -pads["pitch"], False, pin1pos)
        array.SetFirstPadInArray(int(nb_pads_row*3 + 1))
        array.AddPadsToModule(self.draw)

        self.draw.BoxWithDiagonalAtCorner(0, 0, pads["Length"], pads["Width"], pcbnew.FromMM(0.3))
        text_size = pcbnew.FromMM(1.2)
        self.draw.Value(0, pads["Width"] + fillet, text_size)
        self.draw.Reference(0, -pads["Width"] - fillet, text_size)

QFNWizard().register()
