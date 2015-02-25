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
        fillet = pcbnew.FromMM(0.3)
        size_2 = pads["Length"] / 2

        pad_center = (size_2 - pad_len + (pad_len+fillet)/2)

        v_pad = PA.PadMaker(self.module).SMDPad(pads["pad width"], pads["pad length"], pcbnew.PAD_RECT)
        h_pad = PA.PadMaker(self.module).SMDPad(pads["pad length"], pads["pad width"], pcbnew.PAD_RECT)

        pin1pos = pcbnew.wxPoint(-pad_center, 0)
        array = PA.PadLineArray(v_pad, nb_pads_row, pads["pitch"], True, pin1pos)
        array.SetFirstPadInArray(1)
        array.AddPadsToModule(self.draw)

        pin1pos = pcbnew.wxPoint(0, pad_center)
        array = PA.PadLineArray(h_pad, nb_pads_row, pads["pitch"], False, pin1pos)
        array.SetFirstPadInArray(int(nb_pads_row + 1))
        array.AddPadsToModule(self.draw)

	pin1pos = pcbnew.wxPoint(pad_center, 0)
	array = PA.PadLineArray(v_pad, nb_pads_row, -pads["pitch"], True, pin1pos)
	array.SetFirstPadInArray(int(nb_pads_row*2 + 1))
	array.AddPadsToModule(self.draw)

	pin1pos = pcbnew.wxPoint(0, -pad_center)
        array = PA.PadLineArray(h_pad, nb_pads_row, -pads["pitch"], False, pin1pos)
        array.SetFirstPadInArray(int(nb_pads_row*3 + 1))
        array.AddPadsToModule(self.draw)

QFNWizard().register()
