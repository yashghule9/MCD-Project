function [design, f, S] = wilkinson_model(f1, k, Zo_n, Z0, f)
% WILKINSON_MODEL  Lossless S-parameters of Gao/Wu/Tang's dual-band
% Wilkinson divider (IEEE MWCL 24(2), 2014) vs. frequency.
%   f1   : lower design frequency (Hz)
%   k    : frequency ratio, f2 = k*f1
%   Zo_n : odd-mode impedance of the coupled lines, normalized to Z0
%          (free design variable, must satisfy Zo_n <= Ze_n)
%   Z0   : port impedance (ohm)
%   f    : frequency vector to evaluate S-parameters over (Hz)

f2 = k*f1;
th_f1 = pi/(1+k);

t2 = tan(th_f1)^2;
Z1_n2 = (-1 + sqrt(1+8*t2^2)) / (4*t2);   % eq.5, Ze=1/Z1 substituted
Z1_n  = sqrt(Z1_n2);
Ze_n  = 1/Z1_n;
assert(Zo_n <= Ze_n, 'Zo must stay below Ze for a realizable coupling value');

Z1 = Z0*Z1_n; Ze = Z0*Ze_n; Zo = Z0*Zo_n;
R  = 2*Z0;                                 % eq.9

w1 = 2*pi*f1; w2 = 2*pi*f2;
tanth = tan(th_f1);
L = 2*Zo*tanth/(w2-w1);                    % eq.12
C = (w2-w1)/(Zo*w1*w2*tanth);
CdB = -20*log10((Ze+Zo)/(Ze-Zo));          % eq.13

design = struct('Z1',Z1,'Ze',Ze,'Zo',Zo,'L',L,'C',C,'R',R,'CdB',CdB,'f1',f1,'f2',f2,'k',k);

th = th_f1 * f/f1;
w  = 2*pi*f;
S11 = zeros(size(f)); S21 = S11; S22 = S11; S23 = S11;

for n = 1:numel(f)
    t  = tan(th(n));
    c2 = cos(th(n))^2; s2 = sin(th(n))^2; sc = sin(th(n))*cos(th(n));

    Zin_e = 2*Z1*(2*Z0 + 1i*2*Z1*t) / (2*Z1 + 1i*2*Z0*t);
    Zp    = Ze*(Zin_e + 1i*Ze*t) / (Ze + 1i*Zin_e*t);
    Geven = (Zp - Z0)/(Zp + Z0);

    Za = 1i*Zo*t;
    Zb = ((R/2)*(1/(1i*w(n)*C) + 1i*w(n)*L/2)) / ((R/2) + (1/(1i*w(n)*C) + 1i*w(n)*L/2));
    Zpp = Za*Zb/(Za+Zb);
    Godd = (Zpp - Z0)/(Zpp + Z0);

    S22(n) = (Geven + Godd)/2;
    S23(n) = (Geven - Godd)/2;

    Zbr  = Ze*(Z0 + 1i*Ze*t) / (Ze + 1i*Z0*t);
    Zpar = Zbr/2;
    Zin1 = Z1*(Zpar + 1i*Z1*t) / (Z1 + 1i*Zpar*t);
    S11(n) = (Zin1 - Z0)/(Zin1 + Z0);

    Rk = 150*c2 - (100*Z1/Ze + 50*Ze/Z1)*s2;
    Ik = (Ze + 2*Z1 + 2500/Z1 + 5000/Ze)*sc;
    S21(n) = 100/(Rk + 1i*Ik);
end

S = struct('S11',S11,'S21',S21,'S31',S21,'S22',S22,'S33',S22,'S23',S23,'S32',S23);
end
