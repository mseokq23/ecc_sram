// Control block of the ECC 8T SRAM chip: Hamming(8,4) SEC-DED, fault injection, row decoding,
// and the read-out of the reliability monitor (canary latches on VDDA, ring oscillators).
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
// Read cycles with FI_MODE = 11: FI_POS[2:1] picks the view, FI_POS[0] the half where there are two.
//   00  raw view       DOUT = FI_POS[0] ? {R7, R6, R5, R3} (data bits) : {R4, R2, R1, R0} (check bits)
//   01  canary view    DOUT = FI_POS[0] ? CAN[7:4] : CAN[3:0]   (CAN = 1: that canary lost its set state)
//   10  canary set     CSET = 1 while CLK = 1 (all eight canaries forced into their set state);
//                      DOUT as in the canary view
//                      CRD_N = 0 in these two views only: the canary read-out gates are off otherwise
//                      (no static current in them while VDDA sits between 0.7 V and VDD)
//   11  ring osc.      DIN[1:0] = 00 INV, 01 NAND, 10 NOR ring runs (11: none); DOUT = {0, 0, 0, RO_DIV}
//                      (RO_DIV: the running ring divided by 256 in the ring-oscillator block)
// SEC_FLAG and DED_FLAG give the judgment of the addressed word in every read mode, the views included.
// Outside the ring-oscillator view every RO_EN is 0: the rings stand still and the block holds its divider reset.
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
    input  wire [7:0]  CAN,        // canary read-out, 1 = canary lost its set state (CAN[0]: lowest threshold)
    input  wire        RO_DIV,     // running ring oscillator / 256 (ring-oscillator block)
    output wire [14:0] WWL,        // write word lines, rows 0-14
    output wire [14:0] RWL,        // read word lines, rows 0-14
    output wire        PRE_N,      // read bit line precharge, active low (= CLK)
    output wire [7:0]  WD,         // write data to the column drivers
    output wire [3:0]  DOUT,
    output wire        SEC_FLAG,
    output wire        DED_FLAG,
    output wire        CSET,       // canary set, active high
    output wire        CRD_N,      // canary read-out enable, active low
    output wire [2:0]  RO_EN       // ring oscillator enables: 0 INV, 1 NAND, 2 NOR (one at a time)
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
    wire [7:0] rmask = (FI_MODE == 2'b01) ? h1 : (FI_MODE == 2'b10) ? h2 : 8'd0;
    wire       view  = (FI_MODE == 2'b11);       // on a read cycle: one of the four views

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

    // syndrome, overall parity, flags and correction
    wire [2:0] s = {r[4] ^ r[5] ^ r[6] ^ r[7], r[2] ^ r[3] ^ r[6] ^ r[7], r[1] ^ r[3] ^ r[5] ^ r[7]};
    wire q = ^r;
    assign SEC_FLAG = q;
    assign DED_FLAG = (|s) & ~q;
    wire [3:0] corr = {r[7] ^ (q & (s == 3'd7)), r[6] ^ (q & (s == 3'd6)),
                       r[5] ^ (q & (s == 3'd5)), r[3] ^ (q & (s == 3'd3))};

    // views (read cycles with FI_MODE = 11)
    wire v_mon = ~WE & view;
    wire v_can = v_mon & (FI_POS[2:1] == 2'b01);
    wire v_set = v_mon & (FI_POS[2:1] == 2'b10);
    wire v_ro  = v_mon & (FI_POS[2:1] == 2'b11);
    assign CSET = CLK & v_set;
    assign CRD_N = ~(v_can | v_set);

    // ring oscillators: DIN[1:0] picks one
    assign RO_EN = {v_ro & (DIN[1:0] == 2'b10), v_ro & (DIN[1:0] == 2'b01), v_ro & (DIN[1:0] == 2'b00)};

    wire [3:0] raw = FI_POS[0] ? {r[7], r[6], r[5], r[3]} : {r[4], r[2], r[1], r[0]};
    wire [3:0] canv = FI_POS[0] ? CAN[7:4] : CAN[3:0];
    assign DOUT = ~view ? corr
                : v_ro ? {3'b000, RO_DIV}
                : (v_can | v_set) ? canv
                : raw;
endmodule
