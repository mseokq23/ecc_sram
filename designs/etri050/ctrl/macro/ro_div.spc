.subckt ro_div vdd gnd DIV EN[0] EN[1] EN[2] TAP[0]
+ TAP[1] TAP[2] 

X_19_ _g_div[0].dq_ _0_ vdd gnd INVX1
XFILL19050x3750 gnd vdd FILL
X_16_ _8_ _9_ _10_ rst_n vdd gnd NAND3X1
X_13_ EN[1] _8_ vdd gnd INVX1
XFILL19650x150 gnd vdd FILL
XFILL19350x7350 gnd vdd FILL
Xu_rb rst_n rst_b vdd gnd INVX1
X_36_ rst_n _7_ _0_ dclk[0] _g_div[0].dq_ vdd 
+ gnd
+ DFFSR
X_33_ rst_n _7_ _3_ _2_ _g_div[3].dq_ vdd 
+ gnd
+ DFFSR
X_30_ rst_n _7_ _6_ _5_ _g_div[6].dq_ vdd 
+ gnd
+ DFFSR
X_27_ set_n _12_ vdd gnd INVX1
X_24_ _g_div[5].dq_ _5_ vdd gnd INVX1
X_21_ _g_div[2].dq_ _2_ vdd gnd INVX1
X_18_ _11_ dclk[0] vdd gnd INVX1
X_15_ EN[2] _10_ vdd gnd INVX1
XFILL19650x7350 gnd vdd FILL
X_35_ rst_n _7_ _1_ _0_ _g_div[1].dq_ vdd 
+ gnd
+ DFFSR
XFILL19050x7350 gnd vdd FILL
X_32_ rst_n _7_ _4_ _3_ _g_div[4].dq_ vdd 
+ gnd
+ DFFSR
X_29_ rst_n _7_ dclk[8] _6_ _g_div[7].dq_ vdd 
+ gnd
+ DFFSR
Xu_set rst_n rst_b set_n vdd gnd OR2X1
X_26_ _g_div[7].dq_ dclk[8] vdd gnd INVX1
XFILL19350x3750 gnd vdd FILL
X_23_ _g_div[4].dq_ _4_ vdd gnd INVX1
X_20_ _g_div[1].dq_ _1_ vdd gnd INVX1
X_17_ TAP[1] TAP[0] TAP[2] _11_ vdd gnd NAND3X1
X_14_ EN[0] _9_ vdd gnd INVX1
X_37_ dclk[8] DIV vdd gnd BUFX2
X_34_ rst_n _7_ _2_ _1_ _g_div[2].dq_ vdd 
+ gnd
+ DFFSR
X_31_ rst_n _7_ _5_ _4_ _g_div[5].dq_ vdd 
+ gnd
+ DFFSR
XFILL19650x3750 gnd vdd FILL
X_28_ _12_ rst_n _7_ vdd gnd NAND2X1
X_25_ _g_div[6].dq_ _6_ vdd gnd INVX1
X_22_ _g_div[3].dq_ _3_ vdd gnd INVX1

.ends
.end
