// Decoder block of the ECC 8T SRAM chip (above the top channel, drives the output pads): the standard
// SEC-DED decoder, the raw view and a direction-aware decoder, all on the read word R of the control block.
//
//   VIEW = 0   standard decoding: DOUT = corrected data, SEC_FLAG = overall parity Q, DED_FLAG = S != 0 & ~Q
//   VIEW = 1, V_DIR = 0   raw view: DOUT = HALF ? {R7, R6, R5, R3} : {R4, R2, R1, R0}, flags as above
//   V_DIR = 1  direction view: R of the (8,4) extended Hamming code is decoded knowing that a bad bit can only
//              have gone one way: HALF = 1, a 1 that was written as 0 (the low-voltage failures of the 8T
//              array: a 0 read as 1 at low VDDA, a 0 not written over a 1 at low VDDW); HALF = 0, the reverse.
//              The bits that can be bad are U = HALF ? R : ~R.
//   Q = 0, S = 0    no error
//   Q = 1           one bad bit at S if U[S] (corrected), else detected: an odd number of one-way errors
//                   whose single-error position holds a bit that cannot be bad is three or more errors
//                   (every 3-bit one-way error lands here: the standard decoder would flip a good bit)
//   Q = 0, S != 0   two bad bits: of the four pairs {i, i^S}, the one whose two bits can both be bad is
//                   corrected; none or more than one: detected. Only a U of exactly two bits has one such pair.
// DOUT = corrected data bits {R7, R6, R5, R3} (as read when detected);
// {SEC_FLAG, DED_FLAG} = 00 no error, 10 one bit corrected, 11 two bits corrected, 01 detected.
// Combinational only: no state, nothing to set after power-up.
module ecc_dec (
    input  wire [7:0] R,
    input  wire       VIEW,
    input  wire       V_DIR,
    input  wire       HALF,
    output wire [3:0] DOUT,        // to the pads
    output wire       SEC_FLAG,
    output wire       DED_FLAG
);
    // standard decoding
    wire [2:0] S = {R[4] ^ R[5] ^ R[6] ^ R[7], R[2] ^ R[3] ^ R[6] ^ R[7], R[1] ^ R[3] ^ R[5] ^ R[7]};
    wire       Q = ^R;
    wire [3:0] corr = {R[7] ^ (Q & (S == 3'd7)), R[6] ^ (Q & (S == 3'd6)),
                       R[5] ^ (Q & (S == 3'd5)), R[3] ^ (Q & (S == 3'd3))};
    wire [3:0] raw  = HALF ? {R[7], R[6], R[5], R[3]} : {R[4], R[2], R[1], R[0]};

    // direction-aware decoding
    wire [7:0] u  = HALF ? R : ~R;                   // bits that can be bad
    wire [7:0] sd = 8'd1 << S;                       // one-hot syndrome
    wire       z1 = Q & |(sd & u);                   // the single bad bit is possible

    // two bad bits: with Q = 0 and S != 0 the candidates are the pairs {i, i^S} inside U. A U of two bits is
    // one such pair (its syndrome is S), a U of four has none (its other two bits would have to XOR to 0) and
    // a U of six has three, so a single candidate means exactly two bits can be bad: those two are corrected
    // (a 0 word with two bits gone to 1, or a 1 word with two gone to 0).
    function [3:0] popc(input [7:0] x);
        integer t;
        begin popc = 4'd0; for (t = 0; t < 8; t = t + 1) popc = popc + x[t]; end
    endfunction
    wire       z2   = (popc(u) == 4'd2);              // implies Q = 0 and S != 0
    wire [7:0] fix  = ({8{z1}} & sd) | ({8{z2}} & u);
    wire [7:0] c    = R ^ fix;
    wire       zbad = (Q | (S != 3'd0)) & ~z1 & ~z2;  // an error that is not corrected

    assign DOUT     = V_DIR ? {c[7], c[6], c[5], c[3]} : VIEW ? raw : corr;
    assign SEC_FLAG = V_DIR ? (z1 | z2) : Q;
    assign DED_FLAG = V_DIR ? (z2 | zbad) : ((|S) & ~Q);
endmodule
