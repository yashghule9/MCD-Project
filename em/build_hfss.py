# -*- coding: utf-8 -*-
# HFSS (AEDT 2025 R2) model of the Gao/Wu/Tang dual-band Wilkinson divider.
# Run:  ansysedtsv.exe -ng -RunScriptAndExit <path>\build_hfss.py
# Builds the microstrip layout + lumped R/L/C isolation network + 3 lumped
# ports, solves 0.1-2.6 GHz, exports em_results.s3p and saves the project
# wilkinson_dualband.aedt next to this script.  Geometry numbers come from
# hfss_params.py (written by make_params.py).
import os
HERE = r"C:\Users\Karthik\Documents\yash\MCD-Project\em"
P = {}
execfile(os.path.join(HERE, "hfss_params.py"), P)

prj_path = os.path.join(HERE, P.get("project", "wilkinson_dualband") + ".aedt")
for ext in ("", ".lock"):
    if os.path.exists(prj_path + ext):
        os.remove(prj_path + ext)
oProject = oDesktop.NewProject()
oProject.InsertDesign("HFSS", "Wilkinson", "DrivenModal", "")
oDesign = oProject.SetActiveDesign("Wilkinson")
oEditor = oDesign.SetActiveEditor("3D Modeler")
oEditor.SetModelUnits(["NAME:Units Parameter", "Units:=", "mm", "Rescale:=", False])


def var(name, val):
    oDesign.ChangeProperty(["NAME:AllTabs", ["NAME:LocalVariableTab",
        ["NAME:PropServers", "LocalVariables"],
        ["NAME:NewProps", ["NAME:" + name, "PropType:=", "VariableProp",
                           "UserDef:=", True, "Value:=", val]]]])

for k in ["h", "W1", "L1", "Wc", "Sc", "Lc", "W50", "Lf", "Ly", "Lx", "t_isl", "Rv", "Lv", "Cs"]:
    var(k, P[k])


import re
_NV = dict((k, float(P[k].replace("mm", ""))) for k in
           ["h", "W1", "L1", "Wc", "Sc", "Lc", "W50", "Lf", "Ly", "Lx", "t_isl"])
def ev(expr):
    """numeric value (mm string) of a geometry expression - needed for lines."""
    return "%.6fmm" % eval(expr.replace("mm", ""), {}, _NV)


def box(name, x, y, z, dx, dy, dz, mat, color="(128 128 128)", transp=0.0):
    oEditor.CreateBox(["NAME:BoxParameters", "XPosition:=", x, "YPosition:=", y, "ZPosition:=", z,
                       "XSize:=", dx, "YSize:=", dy, "ZSize:=", dz],
                      ["NAME:Attributes", "Name:=", name, "Flags:=", "", "Color:=", color,
                       "Transparency:=", transp, "PartCoordinateSystem:=", "Global",
                       "MaterialValue:=", "\"%s\"" % mat, "SolveInside:=", True])


def rect(name, axis, x, y, z, w, hh):
    oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", x,
                             "YStart:=", y, "ZStart:=", z, "Width:=", w, "Height:=", hh,
                             "WhichAxis:=", axis],
                            ["NAME:Attributes", "Name:=", name, "Flags:=", "", "Color:=", "(255 128 0)",
                             "Transparency:=", 0, "PartCoordinateSystem:=", "Global",
                             "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])


def unite(names):
    oEditor.Unite(["NAME:Selections", "Selections:=", ",".join(names)],
                  ["NAME:UniteParameters", "KeepOriginals:=", False])

# ---- substrate material (RT/duroid 5880 class, as in the paper)
oDefMgr = oProject.GetDefinitionManager()
oDefMgr.AddMaterial(["NAME:sub22", "CoordinateSystemType:=", "Cartesian",
                     ["NAME:AttachedData"], ["NAME:ModifierData"],
                     "permittivity:=", "2.2", "dielectric_loss_tangent:=", P["tand"]])

x0 = "(-(L1+Lf))"            # port-1 plane
x1 = "(Lc+Lx)"             # port-2/3 plane
yb = "(Sc/2+Ly+10mm)"      # half board width
box("Substrate", x0, "-" + yb, "0mm", x1 + "-" + x0, "2*" + yb, "h", "sub22", "(0 128 0)", 0.6)
# air box: open on the port faces' sides by 15 mm margin, 30 mm above / 15 mm below
box("Air", x0 + "-15mm", "-" + yb + "-15mm", "-15mm", x1 + "-" + x0 + "+30mm",
    "2*" + yb + "+30mm", "h+45mm", "air", "(200 200 255)", 0.95)
rect("Ground", "Z", x0, "-" + yb, "0mm", x1 + "-" + x0, "2*" + yb)

# ---- top metal (zero-thickness sheets at z = h)
rect("Top", "Z", x0, "-W50/2", "h", "Lf", "W50")                 # 50-ohm input feed
rect("Trunk", "Z", "-L1", "-W1/2", "h", "L1", "W1")              # Z1 line
rect("CupA", "Z", "0mm", "Sc/2", "h", "Lc", "Wc")                # coupled strip -> port 2
rect("CupB", "Z", "0mm", "-Sc/2-Wc", "h", "Lc", "Wc")            # coupled strip -> port 3
rect("RiseA", "Z", "Lc", "Sc/2", "h", "W50", "Ly")               # 50-ohm riser + run to port 2
rect("OutA", "Z", "Lc", "Sc/2+Ly-W50", "h", "Lx", "W50")
rect("RiseB", "Z", "Lc", "-Sc/2-Ly", "h", "W50", "Ly")           # mirror for port 3
rect("OutB", "Z", "Lc", "-Sc/2-Ly", "h", "Lx", "W50")
unite(["Top", "Trunk", "CupA", "CupB", "RiseA", "OutA", "RiseB", "OutB"])
# small metal island in the gap for the series L - (C/2) branch
rect("Island", "Z", "Lc+W50/2-0.2mm", "-t_isl/2", "h", "0.4mm", "t_isl")

# ---- lumped isolation network in the gap at the coupled-line output end
rect("R_iso", "Z", "Lc+W50-0.6mm", "-Sc/2", "h", "0.6mm", "Sc")
rect("L_iso", "Z", "Lc+W50/2-0.2mm", "t_isl/2", "h", "0.4mm", "Sc/2-t_isl/2")
rect("C_iso", "Z", "Lc+W50/2-0.2mm", "-Sc/2", "h", "0.4mm", "Sc/2-t_isl/2")

oBnd = oDesign.GetModule("BoundarySetup")
if P["lossy"]:
    oBnd.AssignFiniteCond(["NAME:Cu", "Objects:=", ["Top", "Island"], "UseMaterial:=", True,
                           "Material:=", "copper", "UseThickness:=", False, "Roughness:=", "0um",
                           "InfGroundPlane:=", False, "IsTwoSided:=", False, "IsInternal:=", True])
else:
    oBnd.AssignPerfectE(["NAME:Cu", "Objects:=", ["Top", "Island"], "InfGroundPlane:=", False])
oBnd.AssignPerfectE(["NAME:GND", "Objects:=", ["Ground"], "InfGroundPlane:=", False])
oBnd.AssignRadiation(["NAME:Rad", "Objects:=", ["Air"], "IsFssReference:=", False, "IsForPML:=", False])


def rlc(name, obj, xm, ya, yb_, R=None, L=None, C=None):
    a = ["NAME:" + name, "Objects:=", [obj],
         ["NAME:CurrentLine", "Coordinate System:=", "Global",
          "Start:=", [ev(xm), ev(ya), ev("h")], "End:=", [ev(xm), ev(yb_), ev("h")]],
         "RLC Type:=", "Parallel",
         "UseResist:=", R is not None, "UseInduct:=", L is not None, "UseCap:=", C is not None]
    if R: a += ["Resistance:=", R]
    if L: a += ["Inductance:=", L]
    if C: a += ["Capacitance:=", C]
    oBnd.AssignLumpedRLC(a)

rlc("R", "R_iso", "Lc+W50-0.3mm", "Sc/2", "-Sc/2", R="Rv")
rlc("L", "L_iso", "Lc+W50/2", "Sc/2", "t_isl/2", L="Lv")
rlc("C", "C_iso", "Lc+W50/2", "-t_isl/2", "-Sc/2", C="Cs")


def port(name, sheet, x, yc):
    rect(sheet, "X", x, yc + "-W50/2", "0mm", "W50", "h")
    oBnd.AssignLumpedPort(["NAME:" + name, "Objects:=", [sheet], "DoDeembed:=", False,
                           "RenormalizeAllTerminals:=", True,
                           ["NAME:Modes", ["NAME:Mode1", "ModeNum:=", 1, "UseIntLine:=", True,
                                           ["NAME:IntLine", "Coordinate System:=", "Global",
                                            "Start:=", [ev(x), ev(yc), "0mm"], "End:=", [ev(x), ev(yc), ev("h")]],
                                           "AlignmentGroup:=", 0, "CharImp:=", "Zpi",
                                           "RenormImp:=", "50ohm"]],
                           "ShowReporterFilter:=", False, "ReporterFilter:=", [True],
                           "Impedance:=", "50ohm"])

port("P1", "Port1", x0, "0mm")
port("P2", "Port2", x1, "(Sc/2+Ly-W50/2)")
port("P3", "Port3", x1, "(-Sc/2-Ly+W50/2)")

oAn = oDesign.GetModule("AnalysisSetup")
oAn.InsertSetup("HfssDriven", ["NAME:Setup1", "SolveType:=", "Single", "Frequency:=", "2GHz",
                               "MaxDeltaS:=", 0.01, "MaximumPasses:=", P["passes"],
                               "MinimumPasses:=", 3, "MinimumConvergedPasses:=", 2,
                               "PercentRefinement:=", 30, "IsEnabled:=", True, "BasisOrder:=", 1,
                               "DoLambdaRefine:=", True, "DoMaterialLambda:=", True,
                               "SetLambdaTarget:=", False, "Target:=", 0.3333])
oAn.InsertFrequencySweep("Setup1", ["NAME:Sweep1", "IsEnabled:=", True, "RangeType:=", "LinearCount",
                                    "RangeStart:=", "0.1GHz", "RangeEnd:=", "2.6GHz", "RangeCount:=", 251,
                                    "Type:=", "Interpolating", "SaveFields:=", False,
                                    "InterpTolerance:=", 0.5, "InterpMaxSolns:=", 250,
                                    "InterpMinSolns:=", 0, "InterpMinSubranges:=", 1])
oProject.SaveAs(prj_path, True)
oDesign.AnalyzeAll()
oProject.Save()

oSol = oDesign.GetModule("Solutions")
out = os.path.join(HERE, P.get("project", "wilkinson_dualband") + ".s3p")
oSol.ExportNetworkData("", ["Setup1:Sweep1"], 3, out, ["All"], True, 50, "S", -1, 0, 15, True, False, False)
try:
    oSol.ExportConvergence("Setup1", "", os.path.join(HERE, P.get("project", "wilkinson_dualband") + "_conv.txt"))
except Exception:
    pass
oProject.Save()
