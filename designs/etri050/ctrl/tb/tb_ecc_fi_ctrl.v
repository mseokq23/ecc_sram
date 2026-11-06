`timescale 1ns/1ps
// Exhaustive check of ecc_fi_ctrl with a behavioral 8T array (15 rows) that precharges while CLK = 0,
// a behavioral canary block and a behavioral ring-oscillator block (three rings, enable-gated, /256).
//  phase 1: every address x data x stored-fault mode/position, each read back with every read-fault mode
//           and every view of read mode 11 (raw view halves, canary view and set halves, ring oscillators)
//  phase 2: distinct data in all 16 words, then all read back (address decoding, no cross-writes)
//  phase 3: canary set / view sequence (set clears all eight, injected losses show in the right half and bit)
//  phase 4: ring oscillators: DOUT[0] period = 256 periods of the selected ring, RO_EN one-hot only in
//           the view, divider restart value
//  RO_DIV carries a random level in phases 1-3, so a view that passed it through would show as a mismatch
//  monitors: word lines only while CLK = 1, at most one at a time, none for address 15; CSET only while
//            CLK = 1 in the canary-set view; CRD_N = 0 only in the canary views; RO_EN only in the
//            ring-oscillator view, one at a time
module tb;
    reg        CLK = 1'b0, WE = 1'b0;
    reg  [3:0] ADDR = 4'd0, DIN = 4'd0;
    reg  [1:0] FI_MODE = 2'b00;
    reg  [2:0] FI_POS = 3'd0;
    wire [14:0] WWL, RWL;
    wire PRE_N, SEC_FLAG, DED_FLAG, CSET, CRD_N;
    wire [7:0] WD;
    wire [3:0] DOUT;
    wire [2:0] RO_EN;
    reg  [7:0] SENSE;
    reg  [7:0] CAN;
    reg        RO_DIV;

    ecc_fi_ctrl dut (.CLK(CLK), .WE(WE), .ADDR(ADDR), .DIN(DIN), .FI_MODE(FI_MODE), .FI_POS(FI_POS),
                     .SENSE(SENSE), .CAN(CAN), .RO_DIV(RO_DIV), .WWL(WWL), .RWL(RWL), .PRE_N(PRE_N), .WD(WD),
                     .DOUT(DOUT), .SEC_FLAG(SEC_FLAG), .DED_FLAG(DED_FLAG), .CSET(CSET), .CRD_N(CRD_N),
                     .RO_EN(RO_EN));

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

    // behavioral canary block: CSET puts every canary into its set state (read-out 0); the read-out gates
    // give 0 while CRD_N = 1
    reg [7:0] can_state = 8'hFF;                  // power-up: all canaries in their preferred state
    always @* CAN = (CRD_N | CSET) ? 8'h00 : can_state;
    always @(posedge CSET) can_state = 8'h00;

    // behavioral ring-oscillator block: a ring toggles only while its RO_EN is 1 (a stopped ring holds 1),
    // the AND of the three taps is divided by 256 (ripple), the divider is reset while no RO_EN is 1
    reg  [2:0] tap = 3'b111;
    real ro_half [0:2];
    initial begin ro_half[0] = 3.10; ro_half[1] = 3.70; ro_half[2] = 4.30; end
    always begin #(ro_half[0]) tap[0] = RO_EN[0] ? ~tap[0] : 1'b1; end
    always begin #(ro_half[1]) tap[1] = RO_EN[1] ? ~tap[1] : 1'b1; end
    always begin #(ro_half[2]) tap[2] = RO_EN[2] ? ~tap[2] : 1'b1; end
    reg [7:0] dv = 8'd0;
    wire ro_rst_n = |RO_EN;
    wire [8:0] dck = {~dv, &tap};
    genvar gi;
    generate
        for (gi = 0; gi < 8; gi = gi + 1) begin : g_bdiv
            always @(posedge dck[gi] or negedge ro_rst_n) dv[gi] <= ro_rst_n ? ~dv[gi] : 1'b0;
        end
    endgenerate
    reg rodiv_tb = 1'b0, ro_phase = 1'b0;
    always @* RO_DIV = ro_phase ? dck[8] : rodiv_tb;

    integer checks = 0, errors = 0, pre_checks = 0, wl_errors = 0, mon_errors = 0, view_checks = 0;

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
    // monitor-output monitors (CSET, RO_EN) against the inputs, at every input change
    wire in_view = ~WE & (FI_MODE == 2'b11);
    always @(CLK or WE or FI_MODE or FI_POS or DIN or CSET or CRD_N or RO_EN) #0.01 begin
        if (CSET !== (CLK & in_view & (FI_POS[2:1] == 2'b10))) begin
            mon_errors = mon_errors + 1;
            if (mon_errors < 10) $display("ERROR: CSET=%b CLK=%b WE=%b FI_MODE=%b FI_POS=%b", CSET, CLK, WE, FI_MODE, FI_POS);
        end
        if (CRD_N !== ~(in_view & (FI_POS[2:1] == 2'b01 || FI_POS[2:1] == 2'b10))) begin
            mon_errors = mon_errors + 1;
            if (mon_errors < 10) $display("ERROR: CRD_N=%b WE=%b FI_MODE=%b FI_POS=%b", CRD_N, WE, FI_MODE, FI_POS);
        end
        if (RO_EN !== ((in_view && FI_POS[2:1] == 2'b11 && DIN[1:0] != 2'b11) ? (3'b001 << DIN[1:0]) : 3'b000)) begin
            mon_errors = mon_errors + 1;
            if (mon_errors < 10) $display("ERROR: RO_EN=%b WE=%b FI_MODE=%b FI_POS=%b DIN=%b", RO_EN, WE, FI_MODE, FI_POS, DIN);
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

    // one read cycle in mode m, FI_POS p; in the views the canary block holds can (before the cycle)
    task rd_check(input [3:0] a, input [7:0] stored, input [1:0] m, input [2:0] p, input [7:0] can);
        reg [7:0] r, corr; reg [2:0] s; reg q; integer k;
        reg [3:0] e_dout, mask_dout; reg e_sec, e_ded;
        begin
            WE = 0; ADDR = a; FI_MODE = m; FI_POS = p; DIN = $random; can_state = can; rodiv_tb = $random;
            #2;                                              // precharge phase: array side shows all ones
            if (a != 4'd15 && m == 2'b00) begin
                pre_checks = pre_checks + 1;
                if (DOUT !== 4'hF || SEC_FLAG || DED_FLAG) begin
                    errors = errors + 1; $display("precharge view unexpected a=%0d", a);
                end
            end
            #3 CLK = 1; #3;
            r = stored ^ g_mask(m, p, 1'b0);
            s = 3'd0; for (k = 1; k <= 7; k = k + 1) if (r[k]) s = s ^ k[2:0];
            q = ^r;
            corr = q ? (r ^ (8'd1 << s)) : r;
            mask_dout = 4'hF;
            if (m != 2'b11)            e_dout = {corr[7], corr[6], corr[5], corr[3]};
            else if (p[2:1] == 2'b00)  e_dout = p[0] ? {r[7], r[6], r[5], r[3]} : {r[4], r[2], r[1], r[0]};
            else if (p[2:1] == 2'b01)  e_dout = p[0] ? can[7:4] : can[3:0];
            else if (p[2:1] == 2'b10)  e_dout = 4'h0;              // the set has cleared every canary
            else begin                 e_dout = 4'h0; mask_dout = 4'hE; end   // RO: DOUT[0] = divider
            e_sec = q; e_ded = ~q & (s != 3'd0);
            checks = checks + 1;
            if (m == 2'b11 && p[2:1] != 2'b00) view_checks = view_checks + 1;
            if ({DOUT & mask_dout, SEC_FLAG, DED_FLAG} !== {e_dout, e_sec, e_ded}) begin
                errors = errors + 1;
                if (errors < 10) $display("MISMATCH a=%0d stored=%b m=%b p=%0d can=%h got %h %b%b exp %h %b%b",
                    a, stored, m, p, can, DOUT, SEC_FLAG, DED_FLAG, e_dout, e_sec, e_ded);
            end
            #2 CLK = 0;
        end
    endtask

    // phase 4 helper: rising edges of DOUT[0] in a window, and the time between the first and the last
    integer n_edges; real t_first, t_last;
    reg counting = 1'b0;
    always @(posedge DOUT[0]) if (counting) begin
        if (n_edges == 0) t_first = $realtime;
        t_last = $realtime; n_edges = n_edges + 1;
    end

    integer a, d, wm, wp, rm, rp, k;
    reg [7:0] st, cv;
    real period, expect;
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
                            if (!(rm == 0 && rp != 0)) rd_check(a[3:0], st, rm[1:0], rp[2:0], $random);
                end
        // phase 2: distinct data in every word, then read all of them back
        for (a = 0; a < 16; a = a + 1) wr(a[3:0], a[3:0] ^ 4'h5, 2'b00, 3'd0);
        for (a = 0; a < 16; a = a + 1) rd_check(a[3:0], g_encode(a[3:0] ^ 4'h5), 2'b00, 3'd0, 8'h00);
        // phase 3: canary sequence. Power-up pattern, set, then losses injected one canary at a time
        cv = 8'hFF;
        rd_check(4'd3, g_encode(4'd3 ^ 4'h5), 2'b11, 3'b010, cv);      // canary view, low half
        rd_check(4'd3, g_encode(4'd3 ^ 4'h5), 2'b11, 3'b011, cv);      // high half
        rd_check(4'd3, g_encode(4'd3 ^ 4'h5), 2'b11, 3'b100, cv);      // set
        for (k = 0; k < 8; k = k + 1) begin
            cv = 8'd1 << k;
            rd_check(4'd3, g_encode(4'd3 ^ 4'h5), 2'b11, 3'b010, cv);
            rd_check(4'd3, g_encode(4'd3 ^ 4'h5), 2'b11, 3'b011, cv);
        end
        // phase 4: ring oscillators, each selection for 3 x 256 periods of its ring
        ro_phase = 1'b1;
        for (k = 0; k < 4; k = k + 1) begin
            WE = 0; ADDR = 4'd2; FI_MODE = 2'b11; FI_POS = 3'b110; DIN = k[3:0];
            #1;
            if (DOUT !== 4'b0001) begin errors = errors + 1; $display("RO view: divider not reset (DOUT=%b)", DOUT); end
            n_edges = 0; counting = 1'b1;
            period = (k < 3) ? 2.0 * ro_half[k] : 10.0;
            #(3.2 * 256 * period);
            counting = 1'b0;
            checks = checks + 1;
            if (k < 3) begin
                expect = 256.0 * period;
                if (n_edges < 3 || ((t_last - t_first) / (n_edges - 1) - expect) > 0.05 || (expect - (t_last - t_first) / (n_edges - 1)) > 0.05) begin
                    errors = errors + 1;
                    $display("RO %0d: %0d edges, period %f ns, expected %f ns", k, n_edges, (t_last - t_first) / (n_edges - 1), expect);
                end else
                    $display("RO %0d: DOUT[0] period %.2f ns = 256 x %.2f ns", k, (t_last - t_first) / (n_edges - 1), period);
            end else if (n_edges != 0) begin
                errors = errors + 1; $display("RO select 11: DOUT[0] toggled %0d times", n_edges);
            end
            if (DOUT[3:1] !== 3'b000) begin errors = errors + 1; $display("RO view: DOUT[3:1]=%b", DOUT[3:1]); end
            FI_POS = 3'b000; #2;                                // leave the view: rings stop, divider resets
        end
        ro_phase = 1'b0;
        #10;
        errors = errors + wl_errors + mon_errors;
        $display("checks=%0d (views %0d) precharge-view checks=%0d word-line errors=%0d monitor errors=%0d errors=%0d",
                 checks, view_checks, pre_checks, wl_errors, mon_errors, errors);
        if (errors == 0) $display("TB RESULT: PASS"); else $display("TB RESULT: FAIL");
        $finish;
    end
endmodule
