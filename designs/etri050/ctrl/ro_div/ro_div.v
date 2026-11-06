// Divider of the ring-oscillator monitor: the running ring divided by 256 for the control block.
//
// TAP[2:0] are the buffered taps of the three rings (INV, NAND, NOR). A ring whose enable is 0 stands
// still with its tap at 1, so the AND of the three taps is the one running ring. The divider is a ripple
// of eight toggle stages, held reset while no enable is 1 (outside the ring-oscillator view, or with
// DIN[1:0] = 11 in it): DIV = 1 there, then DIV = not q7, a square wave at f(ring) / 256.
//
// The toggle stages are the kit's DFFSR (the only cell with an asynchronous reset). Its set input is not
// tied to VDD as synthesis would do: set_n = rst_n | ~rst_n from two kit cells, which is 1 apart from a
// pulse of one inverter delay while the reset goes active (reset has priority, so the stages still clear).
// No gate of the block then sits on VDD or VSS, whose chip-wide metal the antenna rules of the rule
// document v1.1 would divide by that gate area.
module ro_div (
    input  wire [2:0] TAP,     // ring oscillator taps (stopped ring: 1)
    input  wire [2:0] EN,      // ring enables from the control block (RO_EN)
    output wire       DIV      // running ring / 256
);
    wire rst_n = |EN;
    wire rst_b, set_n;
    INVX1 u_rb  (.A(rst_n), .Y(rst_b));
    OR2X1 u_set (.A(rst_n), .B(rst_b), .Y(set_n));
    wire [8:0] dclk;
    assign dclk[0] = &TAP;
    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : g_div
            reg dq;
            always @(posedge dclk[i] or negedge rst_n or negedge set_n)
                if (!rst_n)      dq <= 1'b0;
                else if (!set_n) dq <= 1'b1;
                else             dq <= ~dq;
            assign dclk[i + 1] = ~dq;
        end
    endgenerate
    assign DIV = dclk[8];
endmodule
