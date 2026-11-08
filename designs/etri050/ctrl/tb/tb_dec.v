`timescale 1ns/1ps
// Exhaustive check of the decoder block ecc_dec: all 2^11 inputs (R, VIEW, V_DIR, HALF) against models
// written without the RTL's structure (standard: syndrome by loop; direction view: search of all 16 codewords).
module tb_dec;
    reg  [7:0] R; reg VIEW, V_DIR, HALF;
    wire [3:0] DOUT; wire SEC_FLAG, DED_FLAG;
    ecc_dec dut (.R(R), .VIEW(VIEW), .V_DIR(V_DIR), .HALF(HALF), .DOUT(DOUT), .SEC_FLAG(SEC_FLAG), .DED_FLAG(DED_FLAG));

    function [7:0] g_encode(input [3:0] d);
        reg [7:0] c; integer kk, p;
        begin
            c = 8'd0; c[3] = d[0]; c[5] = d[1]; c[6] = d[2]; c[7] = d[3];
            for (p = 1; p <= 4; p = p * 2) begin
                c[p] = 1'b0;
                for (kk = 3; kk <= 7; kk = kk + 1) if ((kk != 4) && ((kk & p) != 0)) c[p] = c[p] ^ c[kk];
            end
            c[0] = ^c[7:1];
            g_encode = c;
        end
    endfunction
    function integer popc(input [7:0] x);
        integer kk; begin popc = 0; for (kk = 0; kk < 8; kk = kk + 1) popc = popc + x[kk]; end
    endfunction
    function [5:0] m_dir(input [7:0] r, input dirn);
        reg [7:0] u, c, e, best; integer d, w, nbest, wbest, n0;
        begin
            u = dirn ? r : ~r; nbest = 0; wbest = 9; n0 = 0; best = r;
            for (d = 0; d < 16; d = d + 1) begin
                c = g_encode(d[3:0]); e = r ^ c; w = popc(e);
                if (w <= 2 && (e & ~u) == 8'd0) begin
                    if (w == 0) n0 = 1;
                    else if (w < wbest) begin wbest = w; nbest = 1; best = c; end
                    else if (w == wbest) nbest = nbest + 1;
                end
            end
            if (n0)              m_dir = {r[7], r[6], r[5], r[3], 2'b00};
            else if (nbest == 1) m_dir = {best[7], best[6], best[5], best[3], 1'b1, wbest == 2};
            else                 m_dir = {r[7], r[6], r[5], r[3], 2'b01};
        end
    endfunction
    function [5:0] m_std(input [7:0] r, input view, input half);
        reg [7:0] cw; reg [2:0] s; reg q; integer kk;
        begin
            s = 3'd0; for (kk = 1; kk <= 7; kk = kk + 1) if (r[kk]) s = s ^ kk[2:0];
            q = ^r; cw = q ? (r ^ (8'd1 << s)) : r;
            m_std[5:2] = view ? (half ? {r[7], r[6], r[5], r[3]} : {r[4], r[2], r[1], r[0]}) : {cw[7], cw[6], cw[5], cw[3]};
            m_std[1:0] = {q, ~q & (s != 3'd0)};
        end
    endfunction

    integer v, errors = 0, n = 0;
    integer cnt [0:3];
    reg [5:0] e;
    initial begin
        cnt[0] = 0; cnt[1] = 0; cnt[2] = 0; cnt[3] = 0;
        for (v = 0; v < 2048; v = v + 1) begin
            {V_DIR, VIEW, HALF, R} = v[10:0];
            #5;
            e = V_DIR ? m_dir(R, HALF) : m_std(R, VIEW, HALF);
            n = n + 1;
            if (V_DIR) cnt[{SEC_FLAG, DED_FLAG}] = cnt[{SEC_FLAG, DED_FLAG}] + 1;
            if ({DOUT, SEC_FLAG, DED_FLAG} !== e) begin
                errors = errors + 1;
                if (errors < 10) $display("MISMATCH R=%b VIEW=%b V_DIR=%b HALF=%b got %h %b%b exp %h %b%b",
                                          R, VIEW, V_DIR, HALF, DOUT, SEC_FLAG, DED_FLAG, e[5:2], e[1], e[0]);
            end
        end
        $display("direction view (1024 inputs): no error %0d, 1 corrected %0d, 2 corrected %0d, detected %0d",
                 cnt[0], cnt[2], cnt[3], cnt[1]);
        if (errors == 0) $display("TB RESULT: PASS (%0d of 2048 inputs)", n);
        else $display("TB RESULT: FAIL (%0d errors)", errors);
        $finish;
    end
endmodule
