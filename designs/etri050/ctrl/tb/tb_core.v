`timescale 1ns/1ps
// Self-checking test of the control block + direction-aware decoder (core_logic, or the two synthesized
// netlists) with a behavioral 8T array (15 rows, read bit lines precharged while CLK = 0).
//  phase 1: every address x data x stored-fault mode/position, read back in every read-fault mode and in
//           the raw views: the outputs of the chip before this change (main), checked by a model
//  phase 2: distinct data in all 16 words, all read back (address decoding, no cross-writes)
//  phase 3: direction view, every stored 8-bit word (cells of the behavioral array set directly, as a
//           physical fault would) x both directions x no flip / a flip at each of the 8 bits, three array
//           rows; checked against a model that searches all 16 codewords (no shared code with the RTL)
//  phase 4: the same through stored faults written by the chip (reference word and an array row):
//           every data x write mode/position x direction x flip
//  phase 5: random operations, every read checked
//  monitors: word lines only while CLK = 1, at most one at a time, none for address 15
module tb;
    parameter integer NRAND = 100000;
    reg        CLK = 1'b0, WE = 1'b0;
    reg  [3:0] ADDR = 4'd0, DIN = 4'd0;
    reg  [1:0] FI_MODE = 2'b00;
    reg  [2:0] FI_POS = 3'd0;
    wire [14:0] WWL, RWL;
    wire PRE_N, SEC_FLAG, DED_FLAG;
    wire [7:0] WD;
    wire [3:0] DOUT;
    reg  [7:0] SENSE;

    core_logic dut (.CLK(CLK), .WE(WE), .ADDR(ADDR), .DIN(DIN), .FI_MODE(FI_MODE), .FI_POS(FI_POS),
                    .SENSE(SENSE), .WWL(WWL), .RWL(RWL), .PRE_N(PRE_N), .WD(WD),
                    .DOUT(DOUT), .SEC_FLAG(SEC_FLAG), .DED_FLAG(DED_FLAG));

    // behavioral array
    reg [7:0] mem [0:14];
    reg [7:0] rbl = 8'hFF;
    integer i, sel;
    always @(negedge PRE_N) #1 if (!PRE_N) rbl = 8'hFF;
    always @(PRE_N or RWL) if (PRE_N) begin
        sel = -1;
        for (i = 0; i < 15; i = i + 1) if (RWL[i]) begin
            if (sel != -1) $display("ERROR: two read wordlines at once");
            sel = i;
        end
        if (sel != -1) rbl = rbl & mem[sel];
    end
    always @* SENSE = rbl;
    always @(posedge CLK) #0.1 begin
        for (i = 0; i < 15; i = i + 1) if (WWL[i]) mem[i] <= WD;
    end

    reg [7:0] m_refw;
    integer checks = 0, errors = 0, wl_errors = 0, dir_checks = 0;
    integer n_c1 = 0, n_c2 = 0, n_det = 0, n_ok = 0;
    reg [3:0] o_dout; reg o_sec, o_ded;

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
    function [7:0] g_mask(input [1:0] m, input [2:0] p, input wr);
        reg [7:0] h1, h2, h3;
        begin
            h1 = 8'd1 << p; h2 = h1 | (8'd1 << (p ^ 3'd1)); h3 = h2 | (8'd1 << (p ^ 3'd2));
            case (m)
                2'b01: g_mask = h1;
                2'b10: g_mask = h2;
                2'b11: g_mask = wr ? h3 : 8'd0;
                default: g_mask = 8'd0;
            endcase
        end
    endfunction
    function integer popc(input [7:0] x);
        integer kk; begin popc = 0; for (kk = 0; kk < 8; kk = kk + 1) popc = popc + x[kk]; end
    endfunction
    // direction-aware decoding by search: the codewords within distance 2 whose differences from r all
    // sit on bits that can be bad; result {dout, sec, ded}
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

    task wr(input [3:0] a, input [3:0] d, input [1:0] m, input [2:0] p);
        begin
            WE = 1; ADDR = a; DIN = d; FI_MODE = m; FI_POS = p;
            #5 CLK = 1; #8 CLK = 0;
            if (a == 4'd15) m_refw = g_encode(d) ^ g_mask(m, p, 1'b1);
            #3 WE = 0;
        end
    endtask

    task rd(input [3:0] a, input [1:0] m, input [2:0] p, input [3:0] din);
        reg [7:0] st, r, cw; reg [2:0] s; reg q; reg [3:0] e_dout; reg e_sec, e_ded; integer kk;
        reg [5:0] zd;
        begin
            WE = 0; ADDR = a; FI_MODE = m; FI_POS = p; DIN = din;
            #5 CLK = 1; #8;
            st = (a == 4'd15) ? m_refw : mem[a];
            if (m == 2'b11 && p[2:1] == 2'b01) begin
                r = st ^ (din[3] ? (8'd1 << din[2:0]) : 8'd0);
                zd = m_dir(r, p[0]);
                {e_dout, e_sec, e_ded} = zd;
                dir_checks = dir_checks + 1;
                case ({e_sec, e_ded}) 2'b00: n_ok = n_ok + 1; 2'b10: n_c1 = n_c1 + 1;
                                      2'b11: n_c2 = n_c2 + 1; default: n_det = n_det + 1; endcase
            end else begin
                r = st ^ g_mask(m, p, 1'b0);
                s = 3'd0; for (kk = 1; kk <= 7; kk = kk + 1) if (r[kk]) s = s ^ kk[2:0];
                q = ^r;
                cw = q ? (r ^ (8'd1 << s)) : r;
                e_dout = (m != 2'b11) ? {cw[7], cw[6], cw[5], cw[3]}
                       : (p[0] ? {r[7], r[6], r[5], r[3]} : {r[4], r[2], r[1], r[0]});
                e_sec = q; e_ded = ~q & (s != 3'd0);
            end
            o_dout = DOUT; o_sec = SEC_FLAG; o_ded = DED_FLAG;
            checks = checks + 1;
            if ({DOUT, SEC_FLAG, DED_FLAG} !== {e_dout, e_sec, e_ded}) begin
                errors = errors + 1;
                if (errors < 12) $display("%0t MISMATCH a=%0d st=%b m=%b p=%0d din=%h got %h %b%b exp %h %b%b",
                    $time, a, st, m, p, din, DOUT, SEC_FLAG, DED_FLAG, e_dout, e_sec, e_ded);
`ifdef FASTFAIL
                if (errors >= 5) begin $display("TB RESULT: FAIL (stopped after 5 errors)"); $finish; end
`endif
            end
            CLK = 0; #3;
        end
    endtask

    always @(WWL or RWL or CLK or ADDR) #0.01 begin
        if (!CLK && (|WWL || |RWL)) begin wl_errors = wl_errors + 1; $display("ERROR: word line high while CLK = 0"); end
        if ((WWL & (WWL - 15'd1)) != 0 || (RWL & (RWL - 15'd1)) != 0 || (|WWL && |RWL)) begin
            wl_errors = wl_errors + 1; $display("ERROR: more than one word line high");
        end
        if (ADDR == 4'd15 && (|WWL || |RWL)) begin wl_errors = wl_errors + 1; $display("ERROR: address 15 drove an array word line"); end
    end

    integer a, d, wm, wp, rm, rp, v, dir, f, t, op, n2;
    reg [3:0] dd [0:15];
    integer arow [0:2];
    initial begin
        // ---------------- phase 1
        for (a = 0; a < 16; a = a + 1)
          for (d = 0; d < 16; d = d + 1)
            for (wm = 0; wm < 4; wm = wm + 1)
              for (wp = 0; wp < 8; wp = wp + 1)
                if (!(wm == 0 && wp != 0)) begin
                    wr(a[3:0], d[3:0], wm[1:0], wp[2:0]);
                    for (rm = 0; rm < 3; rm = rm + 1)
                        for (rp = 0; rp < 8; rp = rp + 1)
                            if (!(rm == 0 && rp != 0)) rd(a[3:0], rm[1:0], rp[2:0], $random);
                    rd(a[3:0], 2'b11, 3'b000, $random); rd(a[3:0], 2'b11, 3'b001, $random);
                    rd(a[3:0], 2'b11, 3'b100, $random); rd(a[3:0], 2'b11, 3'b111, $random);
                end
        $display("phase 1 done: checks %0d errors %0d", checks, errors);
        // ---------------- phase 2
        for (a = 0; a < 16; a = a + 1) begin dd[a] = $random; wr(a[3:0], dd[a], 2'b00, 3'd0); end
        for (a = 0; a < 16; a = a + 1) begin
            rd(a[3:0], 2'b00, 3'd0, 4'd0);
            if (o_dout !== dd[a]) begin errors = errors + 1; $display("phase 2: word %0d", a); end
        end
        $display("phase 2 done: checks %0d errors %0d", checks, errors);
        // ---------------- phase 3: every stored word in the direction view
        arow[0] = 0; arow[1] = 7; arow[2] = 14;
        for (a = 0; a < 3; a = a + 1)
          for (v = 0; v < 256; v = v + 1) begin
              mem[arow[a]] = v[7:0];
              for (dir = 0; dir < 2; dir = dir + 1)
                  for (f = 0; f < 9; f = f + 1)
                      rd(arow[a], 2'b11, {2'b01, dir[0]}, (f == 8) ? 4'd0 : {1'b1, f[2:0]});
              rd(arow[a], 2'b00, 3'd0, 4'd0);                     // standard read of the same word
          end
        $display("phase 3 done: checks %0d errors %0d (direction view %0d: no error %0d, 1 corrected %0d, 2 corrected %0d, detected %0d)",
                 checks, errors, dir_checks, n_ok, n_c1, n_c2, n_det);
        // ---------------- phase 4: stored faults written by the chip
        for (a = 0; a < 2; a = a + 1)
          for (d = 0; d < 16; d = d + 1)
            for (wm = 0; wm < 4; wm = wm + 1)
              for (wp = 0; wp < 8; wp = wp + 1)
                if (!(wm == 0 && wp != 0)) begin
                    wr((a == 0) ? 4'd15 : 4'd9, d[3:0], wm[1:0], wp[2:0]);
                    for (dir = 0; dir < 2; dir = dir + 1)
                        for (f = 0; f < 9; f = f + 1)
                            rd((a == 0) ? 4'd15 : 4'd9, 2'b11, {2'b01, dir[0]}, (f == 8) ? 4'd0 : {1'b1, f[2:0]});
                end
        $display("phase 4 done: checks %0d errors %0d", checks, errors);
        // ---------------- phase 5: random
        for (t = 0; t < NRAND; t = t + 1) begin
            op = $random & 255;
            if (op < 60) wr($random, $random, (($random & 7) == 0) ? ($random & 3) : 2'b00, $random);
            else if (op < 70) begin a = ($random & 15) % 15; mem[a] = mem[a] | (8'd1 << ($random & 7)); end
            else if (op < 150) rd($random, $random & 3, $random, $random);
            else rd($random, 2'b11, {2'b01, $random & 1'b1}, $random);
        end
        $display("phase 5 done: checks %0d errors %0d", checks, errors);
        $display("word line errors %0d", wl_errors);
        if (errors == 0 && wl_errors == 0) $display("TB RESULT: PASS (%0d checks, %0d in the direction view)", checks, dir_checks);
        else $display("TB RESULT: FAIL (%0d errors, %0d word line errors)", errors, wl_errors);
        $finish;
    end
endmodule
