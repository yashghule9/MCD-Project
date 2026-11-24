"""Physical dimensions for the HFSS model -> hfss_params.py (read by build_hfss.py)."""
import numpy as np, sys
c0, f1, th = 299792458.0, 500e6, np.pi/5           # theta = pi/(1+k), k = 4
W1, ee1 = 4.831, 1.947                              # Z1 = 30.72 ohm (Hammerstad, em_layout.m)
Wc, Sc = 1.44, 0.48                                 # coupled pair (coupled_sweep.py)
ee_e, ee_o = 1.8879, 1.6910
lam = lambda ee: c0/(f1*np.sqrt(ee))*1e3            # guided wavelength, mm
L1 = th/(2*np.pi)*lam(ee1)
Lc = 0.5*(th/(2*np.pi)*lam(ee_e) + th/(2*np.pi)*lam(ee_o))   # mean of even/odd phase lengths
proj = sys.argv[1] if len(sys.argv) > 1 else 'wilkinson_dualband'
lossy = (sys.argv[2] != 'lossless') if len(sys.argv) > 2 else True
p = dict(h='0.8mm', W1=f'{W1}mm', L1=f'{L1:.3f}mm', Wc=f'{Wc}mm', Sc=f'{Sc}mm', Lc=f'{Lc:.3f}mm',
         W50='2.46mm', Lf='10mm', Ly='6mm', Lx='12mm', t_isl='0.16mm',
         Rv='100ohm', Lv='8.634nH', Cs='2.934pF',     # Cs = C/2 : the two series C's merged
         tand='0.0009' if lossy else '0', lossy=lossy, passes=15, project=proj)
with open('hfss_params.py', 'w') as f:
    for k, v in p.items(): f.write(f'{k} = {v!r}\n')
print(open('hfss_params.py').read())
