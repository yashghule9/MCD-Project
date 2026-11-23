%% Dual-band Wilkinson power divider with wide frequency ratio
% Reproduces the design equations of:
% N. Gao, G. Wu, Q. Tang, "Design of a Novel Compact Dual-Band Wilkinson
% Power Divider With Wide Frequency Ratio," IEEE MWCL, vol.24, no.2, 2014.
% Math is in wilkinson_model.m; this script sets the design point, runs
% the sweep, self-checks the result, and plots it (paper's Fig.5-8 layout).
clear; clc;

Z0   = 50; f1 = 500e6; k = 4; Zo_n = 1.12;
f = linspace(0.2*f1, 1.3*k*f1, 2001);

[design, f, S] = wilkinson_model(f1, k, Zo_n, Z0, f);

fprintf('Z1 = %.2f ohm, Ze = %.2f ohm, Zo = %.2f ohm\n', design.Z1, design.Ze, design.Zo);
fprintf('L = %.3f nH, C = %.3f pF, R = %.1f ohm\n', design.L*1e9, design.C*1e12, design.R);
fprintf('Coupling coefficient C(dB) = %.2f dB\n', design.CdB);

for ftest = [design.f1 design.f2]
    [~,idx] = min(abs(f-ftest));
    assert(20*log10(abs(S.S11(idx))) < -20, 'S11 not matched near %.0f MHz', ftest/1e6);
    assert(20*log10(abs(S.S22(idx))) < -20, 'S22 not matched near %.0f MHz', ftest/1e6);
    assert(20*log10(abs(S.S23(idx))) < -20, 'Isolation not met near %.0f MHz', ftest/1e6);
end
disp('Self-check passed: S11, S22, S23 all below -20 dB at f1 and f2.');

figure('Name','Input return loss');
plot(f/1e9, 20*log10(abs(S.S11)), 'LineWidth', 1.5);
xlabel('Frequency (GHz)'); ylabel('Magnitude (dB)'); title('S_{11}'); grid on;

figure('Name','Output return loss');
plot(f/1e9, 20*log10(abs(S.S22)), f/1e9, 20*log10(abs(S.S33)), '--', 'LineWidth', 1.5);
xlabel('Frequency (GHz)'); ylabel('Magnitude (dB)'); legend('S_{22}','S_{33}'); title('Output return loss'); grid on;

figure('Name','Isolation');
plot(f/1e9, 20*log10(abs(S.S23)), 'LineWidth', 1.5);
xlabel('Frequency (GHz)'); ylabel('Magnitude (dB)'); title('S_{32}'); grid on;

figure('Name','Insertion loss');
plot(f/1e9, 20*log10(abs(S.S21)), f/1e9, 20*log10(abs(S.S31)), '--', 'LineWidth', 1.5);
xlabel('Frequency (GHz)'); ylabel('Magnitude (dB)'); legend('S_{21}','S_{31}'); title('Insertion loss'); grid on;
