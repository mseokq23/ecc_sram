/* Verilog module written by vlog2Verilog (qflow) */

module ro_div(
    output DIV,
    input [2:0] EN,
    input [2:0] TAP
);

wire vdd = 1'b1;
wire gnd = 1'b0;

wire rst_b ;
wire rst_n ;
wire _7_ ;
wire _10_ ;
wire _4_ ;
wire _1_ ;
wire [8:0] dclk ;
wire \g_div[4].dq  ;
wire \g_div[6].dq  ;
wire DIV ;
wire [2:0] EN ;
wire [2:0] TAP ;
wire _9_ ;
wire set_n ;
wire _12_ ;
wire _6_ ;
wire _3_ ;
wire _0_ ;
wire \g_div[0].dq  ;
wire \g_div[2].dq  ;
wire [7:0] \g_div  ;
wire _8_ ;
wire _11_ ;
wire _5_ ;
wire _2_ ;
wire \g_div[1].dq  ;
wire \g_div[3].dq  ;
wire \g_div[5].dq  ;
wire \g_div[7].dq  ;

INVX1 _19_ (
    .A(\g_div[0].dq ),
    .Y(_0_)
);

FILL FILL19050x3750 (
);

NAND3X1 _16_ (
    .A(_8_),
    .B(_9_),
    .C(_10_),
    .Y(rst_n)
);

INVX1 _13_ (
    .A(EN[1]),
    .Y(_8_)
);

FILL FILL19650x150 (
);

FILL FILL19350x7350 (
);

INVX1 u_rb (
    .A(rst_n),
    .Y(rst_b)
);

DFFSR _36_ (
    .R(rst_n),
    .S(_7_),
    .D(_0_),
    .CLK(dclk[0]),
    .Q(\g_div[0].dq )
);

DFFSR _33_ (
    .R(rst_n),
    .S(_7_),
    .D(_3_),
    .CLK(_2_),
    .Q(\g_div[3].dq )
);

DFFSR _30_ (
    .R(rst_n),
    .S(_7_),
    .D(_6_),
    .CLK(_5_),
    .Q(\g_div[6].dq )
);

INVX1 _27_ (
    .A(set_n),
    .Y(_12_)
);

INVX1 _24_ (
    .A(\g_div[5].dq ),
    .Y(_5_)
);

INVX1 _21_ (
    .A(\g_div[2].dq ),
    .Y(_2_)
);

INVX1 _18_ (
    .A(_11_),
    .Y(dclk[0])
);

INVX1 _15_ (
    .A(EN[2]),
    .Y(_10_)
);

FILL FILL19650x7350 (
);

DFFSR _35_ (
    .R(rst_n),
    .S(_7_),
    .D(_1_),
    .CLK(_0_),
    .Q(\g_div[1].dq )
);

FILL FILL19050x7350 (
);

DFFSR _32_ (
    .R(rst_n),
    .S(_7_),
    .D(_4_),
    .CLK(_3_),
    .Q(\g_div[4].dq )
);

DFFSR _29_ (
    .R(rst_n),
    .S(_7_),
    .D(dclk[8]),
    .CLK(_6_),
    .Q(\g_div[7].dq )
);

OR2X1 u_set (
    .A(rst_n),
    .B(rst_b),
    .Y(set_n)
);

INVX1 _26_ (
    .A(\g_div[7].dq ),
    .Y(dclk[8])
);

FILL FILL19350x3750 (
);

INVX1 _23_ (
    .A(\g_div[4].dq ),
    .Y(_4_)
);

INVX1 _20_ (
    .A(\g_div[1].dq ),
    .Y(_1_)
);

NAND3X1 _17_ (
    .A(TAP[1]),
    .B(TAP[0]),
    .C(TAP[2]),
    .Y(_11_)
);

INVX1 _14_ (
    .A(EN[0]),
    .Y(_9_)
);

BUFX2 _37_ (
    .A(dclk[8]),
    .Y(DIV)
);

DFFSR _34_ (
    .R(rst_n),
    .S(_7_),
    .D(_2_),
    .CLK(_1_),
    .Q(\g_div[2].dq )
);

DFFSR _31_ (
    .R(rst_n),
    .S(_7_),
    .D(_5_),
    .CLK(_4_),
    .Q(\g_div[5].dq )
);

FILL FILL19650x3750 (
);

NAND2X1 _28_ (
    .A(_12_),
    .B(rst_n),
    .Y(_7_)
);

INVX1 _25_ (
    .A(\g_div[6].dq ),
    .Y(_6_)
);

INVX1 _22_ (
    .A(\g_div[3].dq ),
    .Y(_3_)
);

endmodule
