// Logic of the chip core for simulation: control block + decoder block, wired as on the chip.
module core_logic (
    input  wire        CLK,
    input  wire        WE,
    input  wire [3:0]  ADDR,
    input  wire [3:0]  DIN,
    input  wire [1:0]  FI_MODE,
    input  wire [2:0]  FI_POS,
    input  wire [7:0]  SENSE,
    output wire [14:0] WWL,
    output wire [14:0] RWL,
    output wire        PRE_N,
    output wire [7:0]  WD,
    output wire [3:0]  DOUT,
    output wire        SEC_FLAG,
    output wire        DED_FLAG
);
    wire [7:0] r; wire view, v_dir, half;
    ecc_fi_ctrl u_ctrl (.CLK(CLK), .WE(WE), .ADDR(ADDR), .DIN(DIN), .FI_MODE(FI_MODE), .FI_POS(FI_POS),
                        .SENSE(SENSE), .WWL(WWL), .RWL(RWL), .PRE_N(PRE_N), .WD(WD),
                        .R(r), .VIEW(view), .V_DIR(v_dir), .HALF(half));
    ecc_dec u_dec (.R(r), .VIEW(view), .V_DIR(v_dir), .HALF(half),
                   .DOUT(DOUT), .SEC_FLAG(SEC_FLAG), .DED_FLAG(DED_FLAG));
endmodule
