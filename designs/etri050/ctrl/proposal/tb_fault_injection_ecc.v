`timescale 1ns/1ps
// Exhaustive check of the Hamming(8,4) SEC-DED + fault-injection datapath.
// Golden model is written independently from the DUT equations:
//   encode: parity bit at position p (1,2,4) = XOR of positions i in {3,5,6,7} with (i & p) != 0
//   decode: syndrome = XOR of indices i (1..7) where r[i] = 1, overall parity q = XOR r[0..7]
module tb;
    reg        CLK = 1'b0, WE = 1'b0;
    reg  [2:0] ADDR = 3'd0, FI_POS = 3'd0;
    reg  [3:0] DIN = 4'd0;
    reg  [1:0] FI_MODE = 2'b00;
    wire [3:0] DOUT_RAW, DOUT_CORR;
    wire       SEC_FLAG, DED_FLAG;

    fault_injection_ecc_sram_top dut (
        .CLK(CLK), .WE(WE), .ADDR(ADDR), .DIN(DIN), .FI_MODE(FI_MODE), .FI_POS(FI_POS),
        .DOUT_RAW(DOUT_RAW), .DOUT_CORR(DOUT_CORR), .SEC_FLAG(SEC_FLAG), .DED_FLAG(DED_FLAG));

    integer checks = 0, errors = 0;
    integer n_err0 = 0, n_err1 = 0, n_err2 = 0, n_err3 = 0;
    integer n1_ok = 0, n2_ok = 0, n3_sec = 0, n3_miscorr = 0, n_cancel = 0;

    function [7:0] g_encode(input [3:0] d);
        reg [7:0] c; integer i, p;
        begin
            c = 8'd0;
            c[3] = d[0]; c[5] = d[1]; c[6] = d[2]; c[7] = d[3];
            for (p = 1; p <= 4; p = p * 2) begin
                c[p] = 1'b0;
                for (i = 3; i <= 7; i = i + 1)
                    if ((i != 4) && ((i & p) != 0)) c[p] = c[p] ^ c[i];
            end
            c[0] = c[1] ^ c[2] ^ c[3] ^ c[4] ^ c[5] ^ c[6] ^ c[7];
            g_encode = c;
        end
    endfunction

    function [2:0] g_syn(input [7:0] r);
        reg [2:0] s; integer i;
        begin
            s = 3'd0;
            for (i = 1; i <= 7; i = i + 1) if (r[i]) s = s ^ i[2:0];
            g_syn = s;
        end
    endfunction

    function [7:0] g_mask(input [1:0] mode, input [2:0] pos, input for_write);
        begin
            if (for_write) g_mask = (mode == 2'b11) ? (8'd1 << pos) : 8'd0;
            else if (mode == 2'b01) g_mask = (8'd1 << pos);
            else if (mode == 2'b10) g_mask = (8'd1 << pos) | (8'd1 << (pos ^ 3'd1));
            else g_mask = 8'd0;
        end
    endfunction

    function integer popcount8(input [7:0] v);
        integer i;
        begin
            popcount8 = 0;
            for (i = 0; i < 8; i = i + 1) popcount8 = popcount8 + v[i];
        end
    endfunction

    task write_word(input [2:0] a, input [3:0] d, input [1:0] m, input [2:0] p);
        begin
            WE = 1'b1; ADDR = a; DIN = d; FI_MODE = m; FI_POS = p;
            #5 CLK = 1'b1; #5 CLK = 1'b0; #1 WE = 1'b0;
        end
    endtask

    task read_check(input [2:0] a, input [3:0] d_true, input [7:0] stored,
                    input [1:0] m, input [2:0] p);
        reg [7:0] r, cw, corr; reg [2:0] s; reg q, e_sec, e_ded; reg [3:0] e_raw, e_corr;
        integer nerr;
        begin
            WE = 1'b0; ADDR = a; FI_MODE = m; FI_POS = p; DIN = ~d_true; // DIN must not matter on read
            #5;
            cw   = g_encode(d_true);
            r    = stored ^ g_mask(m, p, 1'b0);
            s    = g_syn(r);
            q    = ^r;
            corr = q ? (r ^ (8'd1 << s)) : r;
            e_sec = q; e_ded = (~q) & (s != 3'd0);
            e_raw  = {r[7], r[6], r[5], r[3]};
            e_corr = {corr[7], corr[6], corr[5], corr[3]};
            checks = checks + 1;
            if ({DOUT_RAW, DOUT_CORR, SEC_FLAG, DED_FLAG} !== {e_raw, e_corr, e_sec, e_ded}) begin
                errors = errors + 1;
                if (errors <= 10)
                    $display("MISMATCH a=%0d d=%h stored=%b m=%b p=%0d : RAW %h/%h CORR %h/%h SEC %b/%b DED %b/%b",
                             a, d_true, stored, m, p, DOUT_RAW, e_raw, DOUT_CORR, e_corr,
                             SEC_FLAG, e_sec, DED_FLAG, e_ded);
            end
            nerr = popcount8(r ^ cw);
            case (nerr)
                0: begin n_err0 = n_err0 + 1;
                         if (SEC_FLAG || DED_FLAG || DOUT_CORR !== d_true || DOUT_RAW !== d_true) errors = errors + 1; end
                1: begin n_err1 = n_err1 + 1;
                         if (DOUT_CORR === d_true && SEC_FLAG && !DED_FLAG) n1_ok = n1_ok + 1; else errors = errors + 1; end
                2: begin n_err2 = n_err2 + 1;
                         if (DED_FLAG && !SEC_FLAG) n2_ok = n2_ok + 1; else errors = errors + 1; end
                3: begin n_err3 = n_err3 + 1;
                         if (SEC_FLAG) n3_sec = n3_sec + 1;
                         if (DOUT_CORR !== d_true) n3_miscorr = n3_miscorr + 1; end
                default: ;
            endcase
        end
    endtask

    integer a, d, wm, wp, rm, rp;
    reg [7:0] stored;
    initial begin
        for (a = 0; a < 8; a = a + 1)
          for (d = 0; d < 16; d = d + 1)
            for (wm = 0; wm < 4; wm = wm + 3)          // write: normal (00) or write-fault (11)
              for (wp = 0; wp < 8; wp = wp + 1) begin
                if (wm == 0 && wp != 0) ;              // normal write: one position is enough
                else begin
                  write_word(a[2:0], d[3:0], wm[1:0], wp[2:0]);
                  stored = g_encode(d[3:0]) ^ g_mask(wm[1:0], wp[2:0], 1'b1);
                  for (rm = 0; rm < 4; rm = rm + 1)
                    for (rp = 0; rp < 8; rp = rp + 1) begin
                      read_check(a[2:0], d[3:0], stored, rm[1:0], rp[2:0]);
                      if (wm == 3 && rm == 1 && rp == wp) n_cancel = n_cancel + 1;
                    end
                end
              end
        $display("checks=%0d errors=%0d", checks, errors);
        $display("received-word error counts: 0:%0d 1:%0d 2:%0d 3:%0d", n_err0, n_err1, n_err2, n_err3);
        $display("1-bit corrected ok=%0d/%0d, 2-bit detected ok=%0d/%0d", n1_ok, n_err1, n2_ok, n_err2);
        $display("3-bit: SEC_FLAG=1 in %0d/%0d, wrong DOUT_CORR in %0d/%0d (SEC-DED limit)", n3_sec, n_err3, n3_miscorr, n_err3);
        $display("write-fault + read-fault on same bit (cancel) cases=%0d", n_cancel);
        if (errors == 0) $display("TB RESULT: PASS"); else $display("TB RESULT: FAIL");
        $finish;
    end
endmodule
