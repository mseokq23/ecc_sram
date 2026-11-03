`timescale 1ns/1ps
// Exhaustive check of ecc_fi_ctrl with a behavioral 8T array (15 rows) that precharges while CLK = 0.
//  phase 1: every address x data x stored-fault mode/position, each read back with every read-fault mode
//  phase 2: distinct data in all 16 words, then all read back (address decoding, no cross-writes)
//  monitors: word lines only while CLK = 1, at most one at a time, none for address 15
module tb;
    reg        CLK = 1'b0, WE = 1'b0;
    reg  [3:0] ADDR = 4'd0, DIN = 4'd0;
    reg  [1:0] FI_MODE = 2'b00;
    reg  [2:0] FI_POS = 3'd0;
    wire [14:0] WWL, RWL;
    wire PRE_N, SEC_FLAG, DED_FLAG;
    wire [7:0] WD;
    wire [3:0] DOUT_RAW, DOUT_CORR;
    reg  [7:0] SENSE;

    ecc_fi_ctrl dut (.CLK(CLK), .WE(WE), .ADDR(ADDR), .DIN(DIN), .FI_MODE(FI_MODE), .FI_POS(FI_POS),
                     .SENSE(SENSE), .WWL(WWL), .RWL(RWL), .PRE_N(PRE_N), .WD(WD),
                     .DOUT_RAW(DOUT_RAW), .DOUT_CORR(DOUT_CORR), .SEC_FLAG(SEC_FLAG), .DED_FLAG(DED_FLAG));

    // behavioral array: write while WWL[i] is high; the read bitline only discharges (stored 0) during
    // evaluation and returns to 1 only through precharge (PRE_N = 0)
    reg [7:0] mem [0:14];
    reg [7:0] rbl = 8'hFF;
    integer i, sel;
    always @(PRE_N or RWL) begin
        if (!PRE_N) rbl = 8'hFF;
        else begin
            sel = -1;
            for (i = 0; i < 15; i = i + 1) if (RWL[i]) begin
                if (sel != -1) $display("ERROR: two read wordlines at once");
                sel = i;
            end
            if (sel != -1) rbl = rbl & mem[sel];
        end
    end
    always @* SENSE = rbl;
    always @(posedge CLK) #0.1 begin
        for (i = 0; i < 15; i = i + 1) if (WWL[i]) mem[i] <= WD;
    end

    integer checks = 0, errors = 0, pre_checks = 0, wl_errors = 0;

    // word line monitors
    always @(WWL or RWL or CLK or ADDR) #0.01 begin
        if (!CLK && (|WWL || |RWL)) begin
            wl_errors = wl_errors + 1; $display("ERROR: word line high while CLK = 0");
        end
        if ((WWL & (WWL - 15'd1)) != 0 || (RWL & (RWL - 15'd1)) != 0 || (|WWL && |RWL)) begin
            wl_errors = wl_errors + 1; $display("ERROR: more than one word line high");
        end
        if (ADDR == 4'd15 && (|WWL || |RWL)) begin
            wl_errors = wl_errors + 1; $display("ERROR: address 15 drove an array word line");
        end
    end
    function [7:0] g_encode(input [3:0] d);
        reg [7:0] c; integer k, p;
        begin
            c = 8'd0; c[3] = d[0]; c[5] = d[1]; c[6] = d[2]; c[7] = d[3];
            for (p = 1; p <= 4; p = p * 2) begin
                c[p] = 1'b0;
                for (k = 3; k <= 7; k = k + 1) if ((k != 4) && ((k & p) != 0)) c[p] = c[p] ^ c[k];
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

    task wr(input [3:0] a, input [3:0] d, input [1:0] m, input [2:0] p);
        begin
            WE = 1; ADDR = a; DIN = d; FI_MODE = m; FI_POS = p;
            #5 CLK = 1; #5 CLK = 0; #2 WE = 0;
        end
    endtask

    task rd_check(input [3:0] a, input [7:0] stored, input [1:0] m, input [2:0] p);
        reg [7:0] r, corr; reg [2:0] s; reg q; integer k;
        reg [3:0] e_raw, e_corr; reg e_sec, e_ded;
        begin
            WE = 0; ADDR = a; FI_MODE = m; FI_POS = p; DIN = $random;
            #2;                                              // precharge phase: array side shows all ones
            if (a != 4'd15 && m == 2'b00) begin
                pre_checks = pre_checks + 1;
                if (DOUT_RAW !== 4'hF || SEC_FLAG || DED_FLAG) begin
                    errors = errors + 1; $display("precharge view unexpected a=%0d", a);
                end
            end
            #3 CLK = 1; #3;
            r = stored ^ g_mask(m, p, 1'b0);
            s = 3'd0; for (k = 1; k <= 7; k = k + 1) if (r[k]) s = s ^ k[2:0];
            q = ^r;
            corr = q ? (r ^ (8'd1 << s)) : r;
            e_raw = {r[7], r[6], r[5], r[3]};
            e_corr = (m == 2'b11) ? {r[4], r[2], r[1], r[0]} : {corr[7], corr[6], corr[5], corr[3]};
            e_sec = q; e_ded = ~q & (s != 3'd0);
            checks = checks + 1;
            if ({DOUT_RAW, DOUT_CORR, SEC_FLAG, DED_FLAG} !== {e_raw, e_corr, e_sec, e_ded}) begin
                errors = errors + 1;
                if (errors < 10) $display("MISMATCH a=%0d stored=%b m=%b p=%0d got %h %h %b%b exp %h %h %b%b",
                    a, stored, m, p, DOUT_RAW, DOUT_CORR, SEC_FLAG, DED_FLAG, e_raw, e_corr, e_sec, e_ded);
            end
            #2 CLK = 0;
        end
    endtask

    integer a, d, wm, wp, rm, rp;
    reg [7:0] st;
    initial begin
        for (a = 0; a < 16; a = a + 1)
          for (d = 0; d < 16; d = d + 1)
            for (wm = 0; wm < 4; wm = wm + 1)
              for (wp = 0; wp < 8; wp = wp + 1)
                if (!(wm == 0 && wp != 0)) begin
                    wr(a[3:0], d[3:0], wm[1:0], wp[2:0]);
                    st = g_encode(d[3:0]) ^ g_mask(wm[1:0], wp[2:0], 1'b1);
                    for (rm = 0; rm < 4; rm = rm + 1)
                        for (rp = 0; rp < 8; rp = rp + 1)
                            if (!((rm == 0 || rm == 3) && rp != 0)) rd_check(a[3:0], st, rm[1:0], rp[2:0]);
                end
        // phase 2: distinct data in every word, then read all of them back
        for (a = 0; a < 16; a = a + 1) wr(a[3:0], a[3:0] ^ 4'h5, 2'b00, 3'd0);
        for (a = 0; a < 16; a = a + 1) rd_check(a[3:0], g_encode(a[3:0] ^ 4'h5), 2'b00, 3'd0);
        errors = errors + wl_errors;
        $display("checks=%0d precharge-view checks=%0d word-line errors=%0d errors=%0d",
                 checks, pre_checks, wl_errors, errors);
        if (errors == 0) $display("TB RESULT: PASS"); else $display("TB RESULT: FAIL");
        $finish;
    end
endmodule
