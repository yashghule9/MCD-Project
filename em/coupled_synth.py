"""Quasi-static 2-D finite-difference synthesis of the symmetric coupled
microstrip used for the divider's output branches (er=2.2, h=0.8 mm).
Solves Laplace's equation on the cross-section for even (+1,+1) and odd
(+1,-1) excitation, with and without dielectric:
    C (per strip) from field energy,  Z = 1/(c0*sqrt(C*C_air)),  eeff = C/C_air
then solves for strip width W and gap S giving Ze=81.38 ohm, Zo=56.00 ohm."""
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl
from scipy.optimize import least_squares
c0, e0 = 299792458.0, 8.854187817e-12
er, h, d = 2.2, 0.8e-3, 0.04e-3

def cap(W, S, er_sub, sign):
    half = S/2 + W + 8*h
    nx = 2*int(round(half/d)) + 1; ny = int(round(10*h/d)) + 1
    jh = int(round(h/d)); xc = (np.arange(nx) - nx//2)*d
    V0 = np.full((ny, nx), np.nan)              # nan = unknown
    V0[0, :] = 0; V0[-1, :] = 0; V0[:, 0] = 0; V0[:, -1] = 0
    right = (xc >= S/2) & (xc <= S/2 + W); left = (xc <= -S/2) & (xc >= -S/2 - W)
    V0[jh, right] = 1.0; V0[jh, left] = sign
    eh = np.where(np.arange(ny) < jh, er_sub, 1.0); eh[jh] = (er_sub+1)/2   # x-edges at row j
    ev = np.where(np.arange(ny-1) < jh, er_sub, 1.0)                        # y-edges j..j+1
    unk = np.isnan(V0); num = -np.ones((ny, nx), int); num[unk] = np.arange(unk.sum())
    J, I = np.nonzero(unk); n = num[J, I]
    rows, cols, vals = [], [], []; b = np.zeros(unk.sum()); diag = np.zeros(unk.sum())
    for dj, di, e in ((0, 1, eh[J]), (0, -1, eh[J]), (1, 0, ev[J]), (-1, 0, ev[J-1])):
        Jn, In = J+dj, I+di; diag += e
        nb = num[Jn, In]; isu = nb >= 0
        rows += [n[isu]]; cols += [nb[isu]]; vals += [-e[isu]]
        b[~isu] += e[~isu]*V0[Jn[~isu], In[~isu]]
    rows += [n]; cols += [n]; vals += [diag]
    A = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(b.size, b.size))
    V = V0.copy(); V[unk] = spl.spsolve(A.tocsc(), b)
    Wsum = (eh[:, None]*np.diff(V, axis=1)**2).sum() + (ev[:, None]*np.diff(V, axis=0)**2).sum()
    return 0.5*e0*Wsum          # per strip, F/m

def Z(W, S):
    r = {}
    for m, s in (('even', 1), ('odd', -1)):
        C = cap(W, S, er, s); Ca = cap(W, S, 1.0, s)
        r[m] = (1/(c0*np.sqrt(C*Ca)), C/Ca)
    return r

if __name__ == '__main__':
    print('sanity (isolated 50-ohm, W=2.46mm, S=12mm):', Z(2.46e-3, 12e-3)['even'])
    def f(x):
        z = Z(x[0]*1e-3, x[1]*1e-3); return [z['even'][0]-81.38, z['odd'][0]-56.00]
    W, S = least_squares(f, [1.6, 0.8], bounds=([0.4, 0.1], [3.0, 3.0]), diff_step=1e-2, xtol=1e-4).x
    z = Z(W*1e-3, S*1e-3)
    print(f'RESULT W={W:.3f} mm  S={S:.3f} mm  Ze={z["even"][0]:.2f} ohm (eeff {z["even"][1]:.4f})  '
          f'Zo={z["odd"][0]:.2f} ohm (eeff {z["odd"][1]:.4f})')
