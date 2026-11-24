"""To-scale top view of the HFSS layout (same numbers as hfss_params.py)."""
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
P = {}; exec(open('hfss_params.py').read(), P); v = lambda k: float(P[k].replace('mm', ''))
W1, L1, Wc, Sc, Lc, W50, Lf, Ly, Lx = map(v, 'W1 L1 Wc Sc Lc W50 Lf Ly Lx'.split())
fig, ax = plt.subplots(figsize=(10, 3.4)); cu = '#c8862a'
for x, y, w, h in [(-(L1+Lf), -W50/2, Lf, W50), (-L1, -W1/2, L1, W1), (0, Sc/2, Lc, Wc), (0, -Sc/2-Wc, Lc, Wc),
                   (Lc, Sc/2, W50, Ly), (Lc, Sc/2+Ly-W50, Lx, W50), (Lc, -Sc/2-Ly, W50, Ly), (Lc, -Sc/2-Ly, Lx, W50)]:
    ax.add_patch(Rectangle((x, y), w, h, color=cu))
ax.add_patch(Rectangle((Lc+W50-0.6, -Sc/2), 0.6, Sc, color='k'))
ax.annotate('R, L, 2C (lumped)', (Lc+W50/2, 0), (Lc-22, -9), arrowprops=dict(arrowstyle='->'), fontsize=9)
for lbl, x, y in [('Port 1', -(L1+Lf), 0), ('Port 2', Lc+Lx, Sc/2+Ly-W50/2), ('Port 3', Lc+Lx, -Sc/2-Ly+W50/2)]:
    ax.plot(x, y, 'rs'); ax.text(x + (-1 if lbl == 'Port 1' else 1), y, lbl, ha='right' if lbl == 'Port 1' else 'left', va='center', color='r')
ax.text(-L1/2, W1/2+1, f'$Z_1$ line: {W1} x {L1:.1f} mm', ha='center', fontsize=9)
ax.text(Lc/2, Sc/2+Wc+1, f'coupled pair: W={Wc}, S={Sc}, L={Lc:.1f} mm', ha='center', fontsize=9)
ax.set_aspect('equal'); ax.set_xlim(-(L1+Lf)-10, Lc+Lx+12); ax.set_ylim(-Sc/2-Ly-4, Sc/2+Ly+4)
ax.set_xlabel('x (mm)'); ax.set_ylabel('y (mm)'); ax.set_title('HFSS layout (top view, to scale) -- substrate $\epsilon_r$=2.2, h=0.8 mm')
ax.grid(alpha=0.3); fig.tight_layout(); fig.savefig('../report_assets/layout.png', dpi=170)
