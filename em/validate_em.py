"""Validation: lossless circuit model (line-for-line port of wilkinson_model.m)
vs. HFSS full-wave S-parameters (tuned design) (Touchstone .s3p).
Usage: python validate_em.py <file.s3p> [<file2.s3p> label2]
Writes overlay figures to ../report_assets and prints a band-by-band table."""
import sys, os, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'report_assets')


def wilkinson_model(f1, k, Zo_n, Z0, f):
    f2 = k*f1; th1 = np.pi/(1+k); t2 = np.tan(th1)**2
    Z1n = np.sqrt((-1 + np.sqrt(1+8*t2**2))/(4*t2)); Zen = 1/Z1n
    Z1, Ze, Zo, R = Z0*Z1n, Z0*Zen, Z0*Zo_n, 2*Z0
    w1, w2 = 2*np.pi*f1, 2*np.pi*f2
    L = 2*Zo*np.tan(th1)/(w2-w1); C = (w2-w1)/(Zo*w1*w2*np.tan(th1))
    t = np.tan(th1*f/f1); w = 2*np.pi*f; th = th1*f/f1
    Zin_e = 2*Z1*(2*Z0 + 1j*2*Z1*t)/(2*Z1 + 1j*2*Z0*t)
    Zp = Ze*(Zin_e + 1j*Ze*t)/(Ze + 1j*Zin_e*t); Ge = (Zp-Z0)/(Zp+Z0)
    Za = 1j*Zo*t; Zs = 1/(1j*w*C) + 1j*w*L/2; Zb = (R/2)*Zs/(R/2 + Zs)
    Zpp = Za*Zb/(Za+Zb); Go = (Zpp-Z0)/(Zpp+Z0)
    Zbr = Ze*(Z0 + 1j*Ze*t)/(Ze + 1j*Z0*t); Zin1 = Z1*(Zbr/2 + 1j*Z1*t)/(Z1 + 1j*Zbr/2*t)
    c2, s2, sc = np.cos(th)**2, np.sin(th)**2, np.sin(th)*np.cos(th)
    Rk = 150*c2 - (100*Z1/Ze + 50*Ze/Z1)*s2
    Ik = (Ze + 2*Z1 + 2500/Z1 + 5000/Ze)*sc
    return dict(S11=(Zin1-Z0)/(Zin1+Z0), S21=100/(Rk+1j*Ik), S22=(Ge+Go)/2, S23=(Ge-Go)/2)


def read_s3p(path):
    unit = {'hz': 1, 'khz': 1e3, 'mhz': 1e6, 'ghz': 1e9}; fmt = 'MA'; mul = 1e9; nums = []
    for line in open(path):
        line = line.split('!')[0].strip()
        if not line: continue
        if line.startswith('#'):
            tok = line[1:].lower().split(); mul = unit[tok[0]]; fmt = tok[2].upper(); continue
        nums += [float(x) for x in line.split()]
    a = np.array(nums).reshape(-1, 19); f = a[:, 0]*mul; v = a[:, 1:].reshape(-1, 9, 2)
    if fmt == 'MA': z = v[..., 0]*np.exp(1j*np.deg2rad(v[..., 1]))
    elif fmt == 'DB': z = 10**(v[..., 0]/20)*np.exp(1j*np.deg2rad(v[..., 1]))
    else: z = v[..., 0] + 1j*v[..., 1]
    S = z.reshape(-1, 3, 3)
    return f, dict(S11=S[:, 0, 0], S21=S[:, 1, 0], S31=S[:, 2, 0], S22=S[:, 1, 1], S33=S[:, 2, 2], S23=S[:, 2, 1])


dB = lambda x: 20*np.log10(np.abs(x))

if __name__ == '__main__':
    em_files = [(sys.argv[1], 'HFSS (EM)')]
    if len(sys.argv) > 3: em_files.append((sys.argv[2], sys.argv[3]))
    f = np.linspace(0.1e9, 2.6e9, 2001)
    M = wilkinson_model(500e6, 4, 1.12, 50, f)
    ems = [(lbl,) + read_s3p(p) for p, lbl in em_files]
    titles = dict(S11='Input return loss $S_{11}$', S21='Transmission $S_{21}$',
                  S22='Output return loss $S_{22}$', S23='Isolation $S_{32}$')
    styles = ['r--', 'g-.']
    for key, ttl in titles.items():
        plt.figure(figsize=(5.2, 3.6))
        plt.plot(f/1e9, dB(M[key]), 'b-', lw=1.6, label='Circuit model (lossless)')
        for (lbl, fe, S), st in zip(ems, styles):
            plt.plot(fe/1e9, dB(S[key]), st, lw=1.6, label=lbl)
            if key == 'S21': plt.plot(fe/1e9, dB(S['S31']), st[0]+':', lw=1.2, label=lbl + ' $S_{31}$')
        if key == 'S21': plt.ylim(-6, -2.5)
        else: plt.ylim(-50, 0)
        for fx in (0.5, 2.0): plt.axvline(fx, color='0.6', lw=0.8, ls=':')
        plt.xlabel('Frequency (GHz)'); plt.ylabel('Magnitude (dB)'); plt.title(ttl)
        plt.grid(alpha=0.4); plt.legend(fontsize=8, loc='lower right' if key != 'S21' else 'lower left')
        plt.tight_layout(); plt.savefig(os.path.join(OUT, f'val_{key.lower()}.png'), dpi=160); plt.close()
    # EM-only 4-in-1 figure
    lbl, fe, S = ems[-1]
    plt.figure(figsize=(7, 4.2))
    for key, st in (('S11', '-'), ('S22', '--'), ('S33', ':'), ('S23', '-.'), ('S21', '-'), ('S31', '--')):
        plt.plot(fe/1e9, dB(S[key]), st, lw=1.4, label=f'$S_{{{key[1:]}}}$')
    plt.ylim(-50, 0); plt.xlabel('Frequency (GHz)'); plt.ylabel('Magnitude (dB)')
    plt.title('HFSS full-wave S-parameters (tuned design)'); plt.grid(alpha=0.4); plt.legend(ncol=3, fontsize=8)
    plt.tight_layout(); plt.savefig(os.path.join(OUT, 'em_all.png'), dpi=160); plt.close()
    # table at the design bands + the actual nulls
    print(f'{"":10s}{"f":>6s} | {"S11":>7s} {"S21":>7s} {"S31":>7s} {"S22":>7s} {"S33":>7s} {"S23":>7s}')
    for fx in (0.5e9, 2.0e9):
        i = np.argmin(abs(f-fx))
        print(f'{"model":10s}{fx/1e9:6.2f} | {dB(M["S11"][i]):7.2f} {dB(M["S21"][i]):7.2f} {dB(M["S21"][i]):7.2f} '
              f'{dB(M["S22"][i]):7.2f} {dB(M["S22"][i]):7.2f} {dB(M["S23"][i]):7.2f}')
        for lbl, fe, S in ems:
            j = np.argmin(abs(fe-fx))
            print(f'{lbl[:10]:10s}{fx/1e9:6.2f} | ' + ' '.join(f'{dB(S[k][j]):7.2f}' for k in ('S11', 'S21', 'S31', 'S22', 'S33', 'S23')))
    for lbl, fe, S in ems:
        for key in ('S11', 'S22', 'S23'):
            for lo, hi in ((0.2e9, 1.0e9), (1.4e9, 2.6e9)):
                m = (fe >= lo) & (fe <= hi); j = np.argmin(dB(S[key][m]))
                print(f'{lbl}: {key} null in {lo/1e9:.1f}-{hi/1e9:.1f} GHz at {fe[m][j]/1e9:.3f} GHz = {dB(S[key][m][j]):.1f} dB')
        for key in ('S11', 'S22', 'S23'):
            for fx in (0.5e9, 2.0e9):
                m = dB(S[key]) < -15
                # -15 dB bandwidth around fx
                j = np.argmin(abs(fe-fx))
                if not m[j]: print(f'{lbl}: {key} not below -15 dB at {fx/1e9} GHz'); continue
                a = j; b = j
                while a > 0 and m[a-1]: a -= 1
                while b < len(fe)-1 and m[b+1]: b += 1
                print(f'{lbl}: {key} -15 dB band around {fx/1e9:.1f} GHz: {fe[a]/1e9:.3f}-{fe[b]/1e9:.3f} GHz')
