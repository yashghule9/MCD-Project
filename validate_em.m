%% Validation: lossless MATLAB model vs. HFSS full-wave simulation
% Reads the 3-port Touchstone file exported by HFSS (em/wilkinson_dualband.s3p,
% produced by em/build_hfss.py) with a built-in parser -- no RF Toolbox needed --
% overlays it on the closed-form lossless model (wilkinson_model.m), saves the
% figures to report_assets/, and prints the comparison table used in the report.
clear; clc; close all;
EM_FILE = fullfile('em', 'wilkinson_dualband.s3p');
OUT     = 'report_assets';

Z0 = 50; f1 = 500e6; k = 4; Zo_n = 1.12;
f = linspace(0.1e9, 2.6e9, 2001);
[design, f, S] = wilkinson_model(f1, k, Zo_n, Z0, f);

if ~isfile(EM_FILE)
    error('EM results "%s" not found. Run em/build_hfss.py in HFSS first.', EM_FILE);
end
[f_em, Sem] = read_s3p(EM_FILE);
dB = @(x) 20*log10(abs(x));

plots = { 'S11', S.S11, squeeze(Sem(1,1,:)), 'Input return loss S_{11}',  [-50 0];
          'S21', S.S21, squeeze(Sem(2,1,:)), 'Transmission S_{21}',       [-6 -2.5];
          'S22', S.S22, squeeze(Sem(2,2,:)), 'Output return loss S_{22}', [-50 0];
          'S23', S.S23, squeeze(Sem(3,2,:)), 'Isolation S_{32}',          [-50 0] };
for n = 1:size(plots,1)
    fig = figure('Name', ['Validation: ' plots{n,1}]);
    plot(f/1e9, dB(plots{n,2}), 'b-', f_em/1e9, dB(plots{n,3}), 'r--', 'LineWidth', 1.5);
    if strcmp(plots{n,1}, 'S21')
        hold on; plot(f_em/1e9, dB(squeeze(Sem(3,1,:))), 'r:', 'LineWidth', 1.2);
        legend('MATLAB (lossless)', 'HFSS S_{21}', 'HFSS S_{31}', 'Location', 'southwest');
    else
        legend('MATLAB (lossless)', 'HFSS', 'Location', 'southeast');
    end
    xline([0.5 2.0], ':', 'Color', [0.6 0.6 0.6], 'HandleVisibility', 'off');
    ylim(plots{n,5}); grid on;
    xlabel('Frequency (GHz)'); ylabel('Magnitude (dB)'); title(plots{n,4});
    exportgraphics(fig, fullfile(OUT, ['val_' lower(plots{n,1}) '_matlab.png']), 'Resolution', 160);
end

% ---- comparison table at the two design frequencies
names = {'S11','S21','S31','S22','S33','S23'};
idx   = [1 1; 2 1; 3 1; 2 2; 3 3; 3 2];
mdl   = {S.S11, S.S21, S.S31, S.S22, S.S33, S.S23};
fprintf('%-8s %5s |', 'source', 'f/GHz'); fprintf(' %7s', names{:}); fprintf('\n');
for fx = [design.f1 design.f2]
    [~, i] = min(abs(f - fx)); [~, j] = min(abs(f_em - fx));
    fprintf('%-8s %5.2f |', 'MATLAB', fx/1e9);
    for m = 1:6, fprintf(' %7.2f', dB(mdl{m}(i))); end; fprintf('\n');
    fprintf('%-8s %5.2f |', 'HFSS', fx/1e9);
    for m = 1:6, fprintf(' %7.2f', dB(Sem(idx(m,1), idx(m,2), j))); end; fprintf('\n');
end

function [f, S] = read_s3p(file)
% Minimal Touchstone v1 reader for 3-port files (MA / DB / RI, any freq unit).
    txt = fileread(file); lines = regexp(txt, '\r?\n', 'split');
    mul = 1e9; fmt = 'MA'; nums = [];
    units = struct('hz', 1, 'khz', 1e3, 'mhz', 1e6, 'ghz', 1e9);
    for n = 1:numel(lines)
        L = strtrim(regexprep(lines{n}, '!.*$', ''));
        if isempty(L), continue; end
        if L(1) == '#'
            tok = strsplit(lower(strtrim(L(2:end))));
            mul = units.(tok{1}); fmt = upper(tok{3}); continue;
        end
        nums = [nums, sscanf(L, '%f').']; %#ok<AGROW>
    end
    a = reshape(nums, 19, []).';
    f = a(:,1) * mul;
    v1 = a(:, 2:2:end); v2 = a(:, 3:2:end);
    switch fmt
        case 'MA', z = v1 .* exp(1i*deg2rad(v2));
        case 'DB', z = 10.^(v1/20) .* exp(1i*deg2rad(v2));
        otherwise, z = v1 + 1i*v2;
    end
    % Touchstone 3-port rows are S11 S12 S13 / S21 S22 S23 / S31 S32 S33
    S = zeros(3, 3, numel(f));
    for r = 1:3
        for c = 1:3
            S(r, c, :) = z(:, (r-1)*3 + c);
        end
    end
end
