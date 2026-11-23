%% Physical microstrip dimensions for HFSS/CST layout
% Substrate matches the paper: er=2.2, h=0.8mm (RT/duroid 5880-class)
% Hammerstad single-microstrip synthesis (exact closed-form, W/h from Z0).
%
% Z1's line is a real design value (exact). The Ze/Zo values are given as
% ISOLATED single-line widths only -- a starting guess for the coupled-line
% layout, not an exact coupled-line synthesis (that needs the EM tool's
% own optimizer, see note below). Gap S must be tuned in HFSS/CST.
clear; clc;
er = 2.2;
h  = 0.8e-3;   % m
c0 = 3e8;

f1 = 500e6;
k  = 4;
th_f1 = pi/(1+k);

Z1 = 30.72; Ze = 81.38; Zo = 56.00;  % from wilkinson_dualband_design.m

names = {'Z1 (single line)', 'Ze (coupled, even -- guess only)', 'Zo (coupled, odd -- guess only)'};
Zvals = [Z1 Ze Zo];

for n = 1:3
    [W, eeff] = hammerstad_width(Zvals(n), er, h);
    lambda_g = c0/(f1*sqrt(eeff));
    L = th_f1/(2*pi) * lambda_g;
    fprintf('%-34s Z0=%.2f ohm -> W=%.3f mm, eps_eff=%.3f, L=%.3f mm\n', ...
        names{n}, Zvals(n), W*1e3, eeff, L*1e3);
end

fprintf('\nCoupled-line starting guess: W ~= %.2f mm (average of Ze,Zo guesses), gap S ~= h = %.2f mm.\n', ...
    mean([hammerstad_width(Ze,er,h) hammerstad_width(Zo,er,h)])*1e3, h*1e3);
fprintf('Tune W and S in HFSS/CST Optimetrics/Optimizer to hit Ze=%.2f ohm, Zo=%.2f ohm exactly.\n', Ze, Zo);

function [W, eeff] = hammerstad_width(Z0, er, h)
    A = Z0/60*sqrt((er+1)/2) + (er-1)/(er+1)*(0.23+0.11/er);
    Wh_narrow = 8*exp(A)/(exp(2*A)-2);

    B = 377*pi/(2*Z0*sqrt(er));
    Wh_wide = (2/pi)*(B-1-log(2*B-1)) + (er-1)/(pi*er)*(log(B-1)+0.39-0.61/er);

    if Wh_narrow < 2
        Wh = Wh_narrow;
    else
        Wh = Wh_wide;
    end
    W = Wh*h;

    if Wh >= 1
        eeff = (er+1)/2 + (er-1)/2 * 1/sqrt(1+12/Wh);
    else
        eeff = (er+1)/2 + (er-1)/2 * (1/sqrt(1+12/Wh) + 0.04*(1-Wh)^2);
    end
end
