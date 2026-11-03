module fault_injection_ecc_sram_top (
    input  wire       CLK,        // 0: Precharge, 1: Evaluate/Write
    input  wire       WE,         // 1: Write, 0: Read
    input  wire [2:0] ADDR,       // 8-Word Address
    input  wire [3:0] DIN,        // 4-bit Input Data {D3, D2, D1, D0}
    input  wire [1:0] FI_MODE,    // 00: Normal, 01: 1-bit Err, 10: 2-bit Err, 11: Write-Fault
    input  wire [2:0] FI_POS,     // Target bit position (0~7)
    output wire [3:0] DOUT_RAW,   // Raw Output (Before ECC)
    output wire [3:0] DOUT_CORR,  // Corrected Output (After ECC)
    output wire       SEC_FLAG,   // Single Error Corrected
    output wire       DED_FLAG    // Double Error Detected
);

    // 1. Hamming(8,4) SEC-DED Encoder
    wire p0, p1, p2, p_all;
    assign p0    = DIN[0] ^ DIN[1] ^ DIN[3];
    assign p1    = DIN[0] ^ DIN[2] ^ DIN[3];
    assign p2    = DIN[1] ^ DIN[2] ^ DIN[3];
    assign p_all = DIN[0] ^ DIN[1] ^ DIN[2];

    wire [7:0] enc_code = {DIN[3], DIN[2], DIN[1], p2, DIN[0], p1, p0, p_all};

    // 2. Fault-Injection Mask Generator
    wire [7:0] pos_1hot = (8'b0000_0001 << FI_POS);
    wire [7:0] pos_2hot = (8'b0000_0001 << FI_POS) | (8'b0000_0001 << (FI_POS ^ 3'b001));

    wire [7:0] wr_fault_mask = (FI_MODE == 2'b11) ? pos_1hot : 8'b0000_0000;
    wire [7:0] rd_fault_mask = (FI_MODE == 2'b01) ? pos_1hot :
                               (FI_MODE == 2'b10) ? pos_2hot : 8'b0000_0000;

    // 3. SRAM behavioral model
    wire [7:0] wdata_to_sram = enc_code ^ wr_fault_mask;
    reg  [7:0] sram_array [0:7];
    wire [7:0] sram_sense_out;

    always @(posedge CLK) begin
        if (WE) sram_array[ADDR] <= wdata_to_sram;
    end
    assign sram_sense_out = sram_array[ADDR];

    // 4. Read-path fault injection and raw output
    wire [7:0] r = sram_sense_out ^ rd_fault_mask;
    assign DOUT_RAW = {r[7], r[6], r[5], r[3]};

    // 5. Syndrome and overall parity
    wire [2:0] s;
    assign s[0] = r[1] ^ r[3] ^ r[5] ^ r[7];
    assign s[1] = r[2] ^ r[3] ^ r[6] ^ r[7];
    assign s[2] = r[4] ^ r[5] ^ r[6] ^ r[7];

    wire p_chk = ^r;
    wire syn_nonzero = |s;

    // 6. Flags
    assign SEC_FLAG = p_chk;
    assign DED_FLAG = syn_nonzero & (~p_chk);

    // 7. Correction
    assign DOUT_CORR[0] = r[3] ^ (SEC_FLAG & (s == 3'd3));
    assign DOUT_CORR[1] = r[5] ^ (SEC_FLAG & (s == 3'd5));
    assign DOUT_CORR[2] = r[6] ^ (SEC_FLAG & (s == 3'd6));
    assign DOUT_CORR[3] = r[7] ^ (SEC_FLAG & (s == 3'd7));

endmodule
