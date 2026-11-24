"""Sweep W, S with the FD solver and interpolate to Ze=81.38, Zo=56.00 ohm."""
import numpy as np
from scipy.interpolate import RectBivariateSpline
from scipy.optimize import least_squares
from coupled_synth import Z
Ws = np.array([0.80, 1.00, 1.20, 1.40, 1.60]); Ss = np.array([0.20, 0.36, 0.52, 0.68, 0.84])
ZE = np.zeros((5, 5)); ZO = ZE.copy(); EE = ZE.copy(); EO = ZE.copy()
for a, W in enumerate(Ws):
    for c, S in enumerate(Ss):
        z = Z(W*1e-3, S*1e-3); ZE[a, c], EE[a, c] = z['even']; ZO[a, c], EO[a, c] = z['odd']
        print(f'W={W:.2f} S={S:.2f}  Ze={ZE[a,c]:.2f} Zo={ZO[a,c]:.2f}', flush=True)
sp = {k: RectBivariateSpline(Ws, Ss, v, kx=3, ky=3) for k, v in dict(ZE=ZE, ZO=ZO, EE=EE, EO=EO).items()}
r = least_squares(lambda x: [sp['ZE'](*x)[0,0]-81.38, sp['ZO'](*x)[0,0]-56.00], [1.2, 0.5],
                  bounds=([Ws[0], Ss[0]], [Ws[-1], Ss[-1]]))
W, S = r.x
print(f'RESULT W={W:.3f} mm S={S:.3f} mm  eeff_e={sp["EE"](W,S)[0,0]:.4f} eeff_o={sp["EO"](W,S)[0,0]:.4f}')
z = Z(W*1e-3, S*1e-3); print('verify direct solve:', z)
np.savez('coupled_sweep.npz', Ws=Ws, Ss=Ss, ZE=ZE, ZO=ZO, EE=EE, EO=EO, W=W, S=S)
