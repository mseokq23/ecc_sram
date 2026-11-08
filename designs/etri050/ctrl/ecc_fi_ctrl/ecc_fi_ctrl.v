// Control block of the ECC 8T SRAM chip: Hamming(8,4) encoder, fault injection, row decoding, reference word.
// The read word R (after the read-fault mask) goes to the decoder block ecc_dec (above the top channel),
// which decodes it and drives the output pads.
//
// Array: 15 rows x 8 columns of 8T cells (rows 0-14) + one reference word in standard cells (address 15).
// Codeword C[7:0] = {D3, D2, D1, P2, D0, P1, P0, PALL}: the syndrome value is the index of a single bad bit.
//
// FI_MODE on a write cycle (WE = 1), k = FI_POS:          FI_MODE on a read cycle (WE = 0):
//   00  codeword as encoded                               00  normal read, corrected
//   01  bit k flipped            (1-bit stored error)     01  bit k flipped after sensing (transient)
//   10  bits k, k^1 flipped      (2-bit stored error)     10  bits k, k^1 flipped after sensing
//   11  bits k, k^1, k^2 flipped (3-bit stored error)     11  views, picked by FI_POS[2:1] (below)
//
// Read cycles with FI_MODE = 11 (VIEW = 1):
//   FI_POS[2:1] = 01  direction view (V_DIR = 1): ecc_dec decodes R knowing which way its bad bits can have
//                     gone (HALF = FI_POS[0] = 1: 0 -> 1, 0: 1 -> 0). DIN[3] = 1 flips bit DIN[2:0] of R
//                     (one transient flip: with a stored fault, every 2-bit pattern and the 3-bit patterns
//                     that hold a pair {2m, 2m+1} can be tested in logic). Reads in this view keep DIN = 0
//                     unless a flip is wanted.
//   otherwise         raw view: ecc_dec shows R, half picked by HALF.
//
// Timing: CLK = 0 precharges the read bit lines; ADDR, WE, DIN, FI_MODE and FI_POS change only while CLK = 0.
// CLK = 1 reads (outputs valid while CLK stays 1) or writes the addressed row.
// The write drivers are always on: only the selected row's WWL writes, so no write enable is needed.
module ecc_fi_ctrl (
    input  wire        CLK,
    input  wire        WE,
    input  wire [3:0]  ADDR,
    input  wire [3:0]  DIN,
    input  wire [1:0]  FI_MODE,
    input  wire [2:0]  FI_POS,
    input  wire [7:0]  SENSE,      // column outputs, same polarity as the stored Q
    output wire [14:0] WWL,        // write word lines, rows 0-14
    output wire [14:0] RWL,        // read word lines, rows 0-14
    output wire        PRE_N,      // read bit line precharge, active low (= CLK)
    output wire [7:0]  WD,         // write data to the column drivers
    output wire [7:0]  R,          // read word after the read-fault mask (to ecc_dec)
    output wire        VIEW,       // FI_MODE = 11
    output wire        V_DIR,      // direction view
    output wire        HALF        // FI_POS[0]: raw-view half, decoding direction
);
    // encoder
    wire p0 = DIN[0] ^ DIN[1] ^ DIN[3];
    wire p1 = DIN[0] ^ DIN[2] ^ DIN[3];
    wire p2 = DIN[1] ^ DIN[2] ^ DIN[3];
    wire pa = DIN[0] ^ DIN[1] ^ DIN[2];          // = XOR of C[7:1]
    wire [7:0] enc = {DIN[3], DIN[2], DIN[1], p2, DIN[0], p1, p0, pa};

    // fault masks
    wire [7:0] h1 = 8'd1 << FI_POS;
    wire [7:0] h2 = h1 | (8'd1 << (FI_POS ^ 3'd1));
    wire [7:0] h3 = h2 | (8'd1 << (FI_POS ^ 3'd2));
    wire [7:0] wmask = (FI_MODE == 2'b01) ? h1 : (FI_MODE == 2'b10) ? h2 : (FI_MODE == 2'b11) ? h3 : 8'd0;
    wire       view  = (FI_MODE == 2'b11);
    assign VIEW  = view;
    assign V_DIR = ~WE & view & (FI_POS[2:1] == 2'b01);
    assign HALF  = FI_POS[0];
    wire [7:0] rmask = (FI_MODE == 2'b01) ? h1 : (FI_MODE == 2'b10) ? h2
                     : (V_DIR & DIN[3]) ? (8'd1 << DIN[2:0]) : 8'd0;

    assign WD = enc ^ wmask;

    // row decoding and word line gating (CLK = 1 only)
    wire        is_ref = (ADDR == 4'd15);
    wire [15:0] dec = 16'd1 << ADDR;
    wire        wr = CLK & WE;
    wire        rd = CLK & ~WE;
    assign WWL   = dec[14:0] & {15{wr}};
    assign RWL   = dec[14:0] & {15{rd}};
    assign PRE_N = CLK;

    // reference word (standard cells), written on the rising edge of CLK
    reg [7:0] refw;
    always @(posedge CLK) if (WE & is_ref) refw <= WD;

    wire [7:0] stored = is_ref ? refw : SENSE;
    wire [7:0] r = stored ^ rmask;

    assign R = r;
endmodule
