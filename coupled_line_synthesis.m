%% Coupled-microstrip synthesis for the divider's output branches
% Finds strip width W and gap S of the symmetric coupled microstrip
% (er = 2.2, h = 0.8 mm) giving Ze = 81.38 ohm and Zo = 56.00 ohm.
% Method: quasi-static 2-D finite-difference solution of Laplace's equation
% over the cross-section, for even (+1,+1) and odd (+1,-1) excitation, with
% and without the dielectric:
%     C (per strip) from stored field energy,
%     Z = 1/(c0*sqrt(C*C_air)),   eps_eff = C/C_air.
% A W x S grid is swept, then interpolated to the target impedances.
% (Same algorithm as em/coupled_synth.py + em/coupled_sweep.py.)
clear; clc;
er = 2.2; h = 0.8e-3; d = 0.04e-3;            % substrate, grid step 40 um
Ze_t = 81.38; Zo_t = 56.00;

fprintf('Sanity check, isolated 50-ohm line (W = 2.46 mm, S = 12 mm): Z = %.2f ohm\n', ...
        cl_Z(2.46e-3, 12e-3, er, h, d, +1));

Ws = 0.80:0.20:1.60;  Ss = 0.20:0.16:0.84;     % mm
ZE = zeros(numel(Ws), numel(Ss)); ZO = ZE; EE = ZE; EO = ZE;
for a = 1:numel(Ws)
    for c = 1:numel(Ss)
        [ZE(a,c), EE(a,c)] = cl_Z(Ws(a)*1e-3, Ss(c)*1e-3, er, h, d, +1);
        [ZO(a,c), EO(a,c)] = cl_Z(Ws(a)*1e-3, Ss(c)*1e-3, er, h, d, -1);
        fprintf('W=%.2f S=%.2f  Ze=%.2f  Zo=%.2f\n', Ws(a), Ss(c), ZE(a,c), ZO(a,c));
    end
end
[SS, WW] = meshgrid(Ss, Ws);
err = @(x) [interp2(SS, WW, ZE, x(2), x(1), 'spline') - Ze_t, ...
            interp2(SS, WW, ZO, x(2), x(1), 'spline') - Zo_t];
x = fminsearch(@(x) sum(err(x).^2), [1.2 0.5]);
W = x(1); S = x(2);
[Ze, ee_e] = cl_Z(W*1e-3, S*1e-3, er, h, d, +1);
[Zo, ee_o] = cl_Z(W*1e-3, S*1e-3, er, h, d, -1);
fprintf('\nRESULT: W = %.3f mm, S = %.3f mm\n', W, S);
fprintf('  direct check: Ze = %.2f ohm (eps_eff %.4f), Zo = %.2f ohm (eps_eff %.4f)\n', Ze, ee_e, Zo, ee_o);

function [Z, eeff] = cl_Z(W, S, er, h, d, sgn)
    C  = cl_cap(W, S, er,  h, d, sgn);
    Ca = cl_cap(W, S, 1.0, h, d, sgn);
    Z = 1/(299792458*sqrt(C*Ca)); eeff = C/Ca;
end

function C = cl_cap(W, S, er, h, d, sgn)
% Per-unit-length capacitance of one strip (F/m), shielded box 10h tall.
    half = S/2 + W + 8*h;
    nx = 2*round(half/d) + 1; ny = round(10*h/d) + 1; jh = round(h/d) + 1;
    xc = ((1:nx) - (nx+1)/2) * d;
    V0 = nan(ny, nx); V0([1 end], :) = 0; V0(:, [1 end]) = 0;
    V0(jh, xc >=  S/2 & xc <=  S/2 + W) = 1;
    V0(jh, xc <= -S/2 & xc >= -S/2 - W) = sgn;
    row = (1:ny).';
    eh = ones(ny,1); eh(row < jh) = er; eh(jh) = (er+1)/2;   % x-directed edges in row j
    ev = ones(ny-1,1); ev((1:ny-1).' < jh) = er;            % y-directed edge j -> j+1
    unk = isnan(V0); num = zeros(ny, nx); num(unk) = 1:nnz(unk);
    [J, I] = find(unk); n = num(unk); N = numel(n);
    rows = []; cols = []; vals = []; b = zeros(N,1); dg = zeros(N,1);
    nb = { [0 1], eh(J); [0 -1], eh(J); [1 0], ev(J); [-1 0], ev(J-1) };
    for q = 1:4
        dj = nb{q,1}(1); di = nb{q,1}(2); e = nb{q,2};
        Jn = J + dj; In = I + di; dg = dg + e;
        lin = sub2ind([ny nx], Jn, In); m = num(lin); isu = m > 0;
        rows = [rows; n(isu)]; cols = [cols; m(isu)]; vals = [vals; -e(isu)]; %#ok<AGROW>
        b(~isu) = b(~isu) + e(~isu) .* V0(lin(~isu));
    end
    A = sparse([rows; n], [cols; n], [vals; dg], N, N);
    V = V0; V(unk) = A \ b;
    Wsum = sum(eh .* diff(V, 1, 2).^2, 'all') + sum(ev .* diff(V, 1, 1).^2, 'all');
    C = 0.5 * 8.854187817e-12 * Wsum;
end
