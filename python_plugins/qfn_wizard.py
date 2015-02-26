from __future__ import division
import pcbnew
import HelpfulFootprintWizardPlugin as HFPW
import PadArray as PA

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
        self.AddParam("Pads", "Fillet", self.uMM, 0.3);

        self.AddParam("TPad", "tpad", self.uBool, True)
        self.AddParam("TPad", "W", self.uMM, 2.6)
        self.AddParam("TPad", "L", self.uMM, 2.6)

    def CheckParameters(self):
        self.CheckParamInt("Pads", "*nbpads")
        self.CheckParamInt("Pads", "*nbpads", is_multiple_of=4)

    def GetValue(self):
        return "QFN%d_%dx%dmm" % (self.parameters["Pads"]["*nbpads"],pcbnew.ToMM(self.parameters["Pads"]["Width"]),pcbnew.ToMM(self.parameters["Pads"]["Length"]))

    def GetReferencePrefix(self):
        return "U"

    def BuildThisFootprint(self):
        tpad = self.parameters["TPad"]
        pads = self.parameters["Pads"]
        if(tpad["*tpad"]):
            thermal_pad = PA.PadMaker(self.module).SMDPad(tpad["W"], tpad["L"], pcbnew.PAD_RECT)
            origin = pcbnew.wxPoint(0,0);
            #Lazyness !
            array = PA.PadLineArray(thermal_pad, 1, 0, False)
            array.SetFirstPadInArray(pads["*nbpads"]+1)
            array.AddPadsToModule(self.draw)
        nb_pads_row = pads["*nbpads"] / 4;
        line_start = pads["pitch"] * (nb_pads_row - 1) / 2

        #we add 0.3mm to the pad size (to be a parameter)
        #those 0.3mm will be outside of the package
        pad_len = pads["pad length"]
        fillet = pads["Fillet"]
        pad_total = pad_len + fillet
        len_2 = pads["Length"] / 2
        wid_2 = pads["Width"] / 2

        pad_center_l = (len_2 - pad_len + (pad_len+fillet)/2)
        pad_center_w = (wid_2 - pad_len + (pad_len+fillet)/2)

        shape = pcbnew.PAD_OVAL if pads["*oval"] else pcbnew.PAD_RECT

        v_pad = PA.PadMaker(self.module).SMDPad(pads["pad width"], pad_total, shape=shape)
        h_pad = PA.PadMaker(self.module).SMDPad(pad_total, pads["pad width"], shape=shape)

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

        self.draw.BoxWithDiagonalAtCorner(0, 0, pads["Length"], pads["Width"], 1)
        text_size = pcbnew.FromMM(1.2)
        self.draw.Value(0, pads["Width"] + fillet, text_size)
        self.draw.Reference(0, -pads["Width"] - fillet, text_size)

QFNWizard().register()
