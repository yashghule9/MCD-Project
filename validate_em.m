%% Validation: lossless MATLAB model vs. HFSS/CST simulation
% Export the simulated S-parameters from HFSS/CST as Touchstone (.s3p),
% matching the port numbering Port1/Port2/Port3 used in this project,
% and point EM_FILE at it. Until that file exists, this script just
% prints the design point to run the EM sweep over.
clear; clc;
EM_FILE = 'em_results.s3p';

Z0 = 50; f1 = 500e6; k = 4; Zo_n = 1.12;
f = linspace(0.2*f1, 1.3*k*f1, 2001);
[design, f, S] = wilkinson_model(f1, k, Zo_n, Z0, f);

if ~isfile(EM_FILE)
    fprintf(['No EM results found at "%s" yet.\n' ...
        'Run the HFSS/CST sweep over %.0f-%.0f MHz, export 3-port S-parameters\n' ...
        'as Touchstone (.s3p) with %d ohm reference impedance, save as "%s",\n' ...
        'and re-run this script to overlay it against the lossless model.\n'], ...
        EM_FILE, f(1)/1e6, f(end)/1e6, Z0, EM_FILE);
    return;
end

em = sparameters(EM_FILE);   % requires RF Toolbox
f_em = em.Frequencies;
S11_em = squeeze(em.Parameters(1,1,:));
S21_em = squeeze(em.Parameters(2,1,:));
S22_em = squeeze(em.Parameters(2,2,:));
S23_em = squeeze(em.Parameters(3,2,:));

figure('Name','Validation: S11');
plot(f/1e9, 20*log10(abs(S.S11)), 'b-', f_em/1e9, 20*log10(abs(S11_em)), 'r--', 'LineWidth', 1.5);
xlabel('Frequency (GHz)'); ylabel('Magnitude (dB)'); grid on;
legend('MATLAB (lossless)','EM simulation'); title('S_{11}: model vs. EM simulation');

figure('Name','Validation: S21');
plot(f/1e9, 20*log10(abs(S.S21)), 'b-', f_em/1e9, 20*log10(abs(S21_em)), 'r--', 'LineWidth', 1.5);
xlabel('Frequency (GHz)'); ylabel('Magnitude (dB)'); grid on;
legend('MATLAB (lossless)','EM simulation'); title('S_{21}: model vs. EM simulation');

figure('Name','Validation: S22');
plot(f/1e9, 20*log10(abs(S.S22)), 'b-', f_em/1e9, 20*log10(abs(S22_em)), 'r--', 'LineWidth', 1.5);
xlabel('Frequency (GHz)'); ylabel('Magnitude (dB)'); grid on;
legend('MATLAB (lossless)','EM simulation'); title('S_{22}: model vs. EM simulation');

figure('Name','Validation: S23 (isolation)');
plot(f/1e9, 20*log10(abs(S.S23)), 'b-', f_em/1e9, 20*log10(abs(S23_em)), 'r--', 'LineWidth', 1.5);
xlabel('Frequency (GHz)'); ylabel('Magnitude (dB)'); grid on;
legend('MATLAB (lossless)','EM simulation'); title('S_{32}: model vs. EM simulation');
