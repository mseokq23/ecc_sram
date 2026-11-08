.subckt ecc_fi_ctrl vdd gnd ADDR[0] ADDR[1] ADDR[2] ADDR[3] CLK
+ DIN[0] DIN[1] DIN[2] DIN[3] FI_MODE[0] FI_MODE[1] FI_POS[0] FI_POS[1]
+ FI_POS[2] HALF PRE_N R[0] R[1] R[2] R[3] R[4]
+ R[5] R[6] R[7] RWL[0] RWL[1] RWL[2] RWL[3] RWL[4]
+ RWL[5] RWL[6] RWL[7] RWL[8] RWL[9] RWL[10] RWL[11] RWL[12]
+ RWL[13] RWL[14] SENSE[0] SENSE[1] SENSE[2] SENSE[3] SENSE[4] SENSE[5]
+ SENSE[6] SENSE[7] VIEW V_DIR WD[0] WD[1] WD[2] WD[3]
+ WD[4] WD[5] WD[6] WD[7] WE WWL[0] WWL[1] WWL[2]
+ WWL[3] WWL[4] WWL[5] WWL[6] WWL[7] WWL[8] WWL[9] WWL[10]
+ WWL[11] WWL[12] WWL[13] WWL[14] 

XFILL_0__585_ gnd vdd FILL
X_588_ _131_ _159_ _293_[14] vdd gnd NOR2X1
XFILL_1__372_ gnd vdd FILL
XFILL_0__394_ gnd vdd FILL
X_397_ _101_ _221_ _270_ _4_ vdd gnd MUX2X1
XFILL_0__297_ gnd vdd FILL
X_512_ _101_ _292_[4] vdd gnd INVX1
X_321_ _208_ _169__bF$buf0 _209_ _210_ vdd gnd OAI21X1
X_550_ _131_ _135_ _293_[0] vdd gnd NOR2X1
XFILL_0__603_ gnd vdd FILL
X_606_ WE _278_ _162_ vdd gnd NOR2X1
XFILL_0__412_ gnd vdd FILL
X_415_ FI_POS[1] _279_ _286_ _9_ vdd gnd NAND3X1
XFILL_0__641_ gnd vdd FILL
X_644_ _289_[11] RWL[11] vdd gnd BUFX2
XFILL_0__450_ gnd vdd FILL
X_453_ _278_ _45_ _31_ _46_ vdd gnd OAI21X1
XFILL_0__506_ gnd vdd FILL
X_509_ _97_ _98_ _87_ _99_ vdd gnd OAI21X1
X_682_ _293_[4] WWL[4] vdd gnd BUFX2
XFILL46050x25350 gnd vdd FILL
X_318_ _206_ _67_ _284__bF$buf1 _207_ vdd gnd AOI21X1
X_491_ _13_ _76_ _81_ _82_ vdd gnd NAND3X1
XFILL_0__544_ gnd vdd FILL
X_547_ ADDR[2] _133_ vdd gnd INVX2
XFILL_1__331_ gnd vdd FILL
XFILL_0__353_ gnd vdd FILL
X_356_ _104_ _242_ _241_ _243_ vdd gnd NAND3X1
XFILL_1__560_ gnd vdd FILL
XFILL_0__409_ gnd vdd FILL
XFILL_0__582_ gnd vdd FILL
XFILL_1__616_ gnd vdd FILL
X_585_ ADDR[3] _147_ _158_ vdd gnd NAND2X1
X_394_ _270_ _78_ _82_ _275_ vdd gnd NAND3X1
XFILL_1__654_ gnd vdd FILL
X_679_ _293_[14] WWL[14] vdd gnd BUFX2
XFILL_1__463_ gnd vdd FILL
XFILL_0__485_ gnd vdd FILL
XFILL_1__519_ gnd vdd FILL
X_488_ _285_ _286_ FI_POS_2_bF$buf1 _79_ vdd gnd AOI21X1
X_297_ _32_ _187_ _30_ _188_ vdd gnd OAI21X1
XFILL_1__366_ gnd vdd FILL
XFILL_1__595_ gnd vdd FILL
XFILL_0__600_ gnd vdd FILL
X_603_ _160_ _158_ _289_[13] vdd gnd NOR2X1
X_412_ FI_POS[0] _286_ vdd gnd INVX2
X_641_ _289_[0] RWL[0] vdd gnd BUFX2
X_450_ FI_MODE[0] _29_ _43_ vdd gnd NOR2X1
X_506_ FI_POS_2_bF$buf0 _285_ _96_ vdd gnd NAND2X1
XFILL_0__312_ gnd vdd FILL
X_315_ DIN[2] _203_ _204_ vdd gnd NOR2X1
XFILL45750x28950 gnd vdd FILL
XFILL_0__541_ gnd vdd FILL
X_544_ _130_ _292_[7] vdd gnd INVX1
X_353_ _173_ _239_ _43_ _240_ vdd gnd AOI21X1
X_409_ FI_MODE[0] _283_ vdd gnd INVX1
X_582_ _131_ _156_ _293_[11] vdd gnd NOR2X1
X_638_ FI_POS[0] HALF vdd gnd BUFX2
XFILL_1__422_ gnd vdd FILL
X_391_ _64_ _270_ _71_ _273_ vdd gnd NAND3X1
X_447_ _39_ _19_ _20_ _40_ vdd gnd NAND3X1
XFILL_0__673_ gnd vdd FILL
X_676_ _293_[11] WWL[11] vdd gnd BUFX2
X_485_ FI_POS_2_bF$buf2 _75_ _284__bF$buf0 _76_ vdd gnd OAI21X1
X_294_ _48_ _181_ _184_ _185_ vdd gnd OAI21X1
X_579_ _140_ _132_ _155_ vdd gnd OR2X2
XFILL_0__385_ gnd vdd FILL
X_388_ _42_ _270_ _50_ _271_ vdd gnd NAND3X1
X_600_ _160_ _155_ _289_[10] vdd gnd NOR2X1
X_503_ _92_ _91_ _39_ _93_ vdd gnd OAI21X1
X_312_ _56_ _201_ _200_ _202_ vdd gnd NAND3X1
X_541_ _124_ _128_ vdd gnd INVX1
X_350_ _235_ _169__bF$buf1 _236_ _237_ vdd gnd OAI21X1
XFILL_1_BUFX2_insert3 gnd vdd FILL
XFILL_1_BUFX2_insert8 gnd vdd FILL
X_406_ WE _281_ vdd gnd INVX2
X_635_ _5_ CLK refw[5] vdd gnd DFFPOSX1
XFILL_0__441_ gnd vdd FILL
X_444_ FI_POS_2_bF$buf3 _36_ _284__bF$buf1 _37_ vdd gnd OAI21X1
X_673_ _293_[0] WWL[0] vdd gnd BUFX2
XFILL45750x14550 gnd vdd FILL
X_309_ _173_ _198_ _43_ _199_ vdd gnd AOI21X1
X_482_ _278_ _72_ _31_ _73_ vdd gnd OAI21X1
X_538_ _39_ _124_ _123_ _125_ vdd gnd NAND3X1
XFILL_0__344_ gnd vdd FILL
X_347_ _233_ _217_ _284__bF$buf3 _234_ vdd gnd AOI21X1
XFILL_0__573_ gnd vdd FILL
X_576_ _131_ _153_ _293_[8] vdd gnd NOR2X1
XFILL_0__629_ gnd vdd FILL
XFILL_0__382_ gnd vdd FILL
X_385_ _264_ _269_ _288_[7] vdd gnd NAND2X1
XFILL_0__438_ gnd vdd FILL
XFILL_0__667_ gnd vdd FILL
XFILL_0__476_ gnd vdd FILL
X_479_ _69_ _68_ _70_ _71_ vdd gnd OAI21X1
X_500_ _88_ _89_ DIN[3] _90_ vdd gnd OAI21X1
XFILL_0__379_ gnd vdd FILL
XFILL_0__400_ gnd vdd FILL
X_403_ _278_ _290_ vdd gnd INVX1
X_632_ _2_ CLK refw[2] vdd gnd DFFPOSX1
X_441_ _283_ _33_ FI_MODE[1] _34_ vdd gnd OAI21X1
XFILL_1__489_ gnd vdd FILL
X_670_ _292_[5] WD[5] vdd gnd BUFX2
XFILL_0__303_ gnd vdd FILL
X_306_ _194_ _169__bF$buf3 _195_ _196_ vdd gnd OAI21X1
XFILL_0__532_ gnd vdd FILL
X_535_ FI_POS_2_bF$buf2 FI_POS[0] _285_ _122_ vdd gnd NAND3X1
XFILL_0__341_ gnd vdd FILL
X_344_ _104_ _231_ vdd gnd INVX1
XFILL_0__570_ gnd vdd FILL
X_573_ _132_ ADDR[2] _142_ _152_ vdd gnd NAND3X1
XFILL_0__626_ gnd vdd FILL
X_629_ _182_ _169__bF$buf3 _183_ _184_ vdd gnd OAI21X1
X_382_ _252_ _266_ _30_ _267_ vdd gnd OAI21X1
XFILL_0__435_ gnd vdd FILL
X_438_ FI_MODE[1] _283_ _31_ vdd gnd NAND2X1
XFILL_0__664_ gnd vdd FILL
X_667_ _292_[2] WD[2] vdd gnd BUFX2
XFILL_0__473_ gnd vdd FILL
X_476_ _29_ FI_MODE[0] _66_ _67_ _68_ vdd 
+ gnd
+ AOI22X1
XFILL_1__680_ gnd vdd FILL
XFILL_0__529_ gnd vdd FILL
XFILL_1__316_ gnd vdd FILL
XFILL_0__338_ gnd vdd FILL
XFILL_0__567_ gnd vdd FILL
X_379_ _128_ _260_ _263_ _264_ vdd gnd OAI21X1
XFILL_1__639_ gnd vdd FILL
XFILL_1__392_ gnd vdd FILL
X_400_ _121_ _248_ _270_ _6_ vdd gnd MUX2X1
XFILL_1__448_ gnd vdd FILL
XFILL_1__295_ gnd vdd FILL
XFILL_0__300_ gnd vdd FILL
X_303_ _192_ _67_ _284__bF$buf1 _193_ vdd gnd AOI21X1
X_532_ _119_ _118_ DIN[2] _120_ vdd gnd OAI21X1
X_341_ _223_ _229_ vdd gnd INVX1
X_570_ _149_ _150_ vdd gnd INVX1
XFILL_0__623_ gnd vdd FILL
X_626_ _180_ _44_ _284__bF$buf1 _181_ vdd gnd AOI21X1
X_435_ _28_ _292_[0] vdd gnd INVX1
XFILL45750x21750 gnd vdd FILL
XFILL_0__661_ gnd vdd FILL
X_664_ _291_ V_DIR vdd gnd BUFX2
XFILL_0__470_ gnd vdd FILL
XFILL_1__504_ gnd vdd FILL
X_473_ FI_POS[1] _286_ _279_ _65_ vdd gnd OAI21X1
XFILL_0__526_ gnd vdd FILL
X_529_ _29_ _110_ _30_ _117_ vdd gnd OAI21X1
X_338_ _218_ _226_ vdd gnd INVX1
X_567_ _132_ _147_ _148_ vdd gnd NAND2X1
XFILL_1__351_ gnd vdd FILL
XFILL_1__407_ gnd vdd FILL
X_376_ refw[7] _261_ vdd gnd INVX1
XFILL_1__580_ gnd vdd FILL
XFILL_0__429_ gnd vdd FILL
XFILL_1__483_ gnd vdd FILL
XFILL_1__539_ gnd vdd FILL
X_300_ _185_ _190_ _288_[1] vdd gnd NAND2X1
X_623_ _172_ _178_ _288_[0] vdd gnd NAND2X1
X_432_ _284__bF$buf2 _25_ _8_ _26_ vdd gnd OAI21X1
X_661_ _288_[6] R[6] vdd gnd BUFX2
X_470_ _61_ _60_ _39_ _62_ vdd gnd OAI21X1
X_526_ _85_ _284__bF$buf0 _114_ vdd gnd NAND2X1
XFILL_1__310_ gnd vdd FILL
X_335_ _221_ _169__bF$buf0 _222_ _223_ vdd gnd OAI21X1
X_564_ _131_ _145_ _293_[4] vdd gnd NOR2X1
XFILL_0__370_ gnd vdd FILL
X_373_ _203_ _18_ _258_ vdd gnd OR2X2
X_429_ _8_ _22_ _12_ _23_ vdd gnd NAND3X1
X_658_ _288_[3] R[3] vdd gnd BUFX2
X_467_ _57_ _58_ DIN[3] _59_ vdd gnd OAI21X1
XFILL_0__329_ gnd vdd FILL
XFILL_0__558_ gnd vdd FILL
X_599_ _160_ _154_ _289_[9] vdd gnd NOR2X1
X_620_ _32_ _175_ _30_ _176_ vdd gnd OAI21X1
XFILL_0__499_ gnd vdd FILL
X_523_ _110_ _111_ vdd gnd INVX1
X_332_ _219_ _217_ _284__bF$buf3 _220_ vdd gnd AOI21X1
X_561_ _131_ _143_ _293_[3] vdd gnd NOR2X1
XFILL_0__614_ gnd vdd FILL
X_617_ _39_ _280_ _282_ _173_ vdd gnd NOR3X1
X_370_ _250_ _256_ vdd gnd INVX1
X_426_ DIN[1] _13_ _20_ vdd gnd NAND2X1
XFILL_0__652_ gnd vdd FILL
X_655_ _289_[9] RWL[9] vdd gnd BUFX2
XFILL_0__461_ gnd vdd FILL
X_464_ _9_ _284__bF$buf2 _56_ vdd gnd NAND2X1
XFILL_0__517_ gnd vdd FILL
XFILL_0__326_ gnd vdd FILL
X_329_ _279_ FI_POS[1] _43_ _217_ vdd gnd OAI21X1
XFILL_0__555_ gnd vdd FILL
X_558_ _131_ _141_ _293_[2] vdd gnd NOR2X1
XFILL_0__364_ gnd vdd FILL
X_367_ _245_ _253_ vdd gnd INVX1
XFILL_0__593_ gnd vdd FILL
X_596_ _160_ _151_ _289_[6] vdd gnd NOR2X1
XFILL_0__649_ gnd vdd FILL
XFILL_0__458_ gnd vdd FILL
XBUFX2_insert0 _284_ _284__bF$buf3 vdd gnd BUFX2
XBUFX2_insert1 _284_ _284__bF$buf2 vdd gnd BUFX2
XBUFX2_insert2 _284_ _284__bF$buf1 vdd gnd BUFX2
XBUFX2_insert3 _284_ _284__bF$buf0 vdd gnd BUFX2
XBUFX2_insert4 _169_ _169__bF$buf3 vdd gnd BUFX2
XBUFX2_insert5 _169_ _169__bF$buf2 vdd gnd BUFX2
XBUFX2_insert6 _169_ _169__bF$buf1 vdd gnd BUFX2
XBUFX2_insert7 _169_ _169__bF$buf0 vdd gnd BUFX2
XBUFX2_insert8 FI_POS[2] FI_POS_2_bF$buf3 vdd gnd BUFX2
XBUFX2_insert9 FI_POS[2] FI_POS_2_bF$buf2 vdd gnd BUFX2
XFILL_0__687_ gnd vdd FILL
XFILL_0__496_ gnd vdd FILL
X_499_ DIN[1] _18_ _89_ vdd gnd NOR2X1
X_520_ _106_ _108_ _292_[5] vdd gnd NAND2X1
XFILL_1__377_ gnd vdd FILL
XFILL_0__399_ gnd vdd FILL
XFILL_0__611_ gnd vdd FILL
X_614_ SENSE[0] _169__bF$buf1 _170_ vdd gnd NAND2X1
XFILL_0__420_ gnd vdd FILL
X_423_ _14_ _16_ DIN[2] _17_ vdd gnd OAI21X1
X_652_ _289_[6] RWL[6] vdd gnd BUFX2
X_461_ FI_POS_2_bF$buf1 _285_ _53_ vdd gnd NOR2X1
XFILL_0__514_ gnd vdd FILL
X_517_ DIN[1] _105_ _106_ vdd gnd NAND2X1
XFILL_0__323_ gnd vdd FILL
X_326_ _76_ _214_ _213_ _215_ vdd gnd NAND3X1
XFILL_0__552_ gnd vdd FILL
X_555_ ADDR[0] _139_ vdd gnd INVX1
XFILL_0__608_ gnd vdd FILL
XFILL46050x3750 gnd vdd FILL
XFILL_0__361_ gnd vdd FILL
X_364_ _248_ _169__bF$buf1 _249_ _250_ vdd gnd OAI21X1
XFILL_0__417_ gnd vdd FILL
XFILL_0__590_ gnd vdd FILL
X_593_ _160_ _143_ _289_[3] vdd gnd NOR2X1
XFILL_0__646_ gnd vdd FILL
X_649_ _289_[3] RWL[3] vdd gnd BUFX2
XFILL_1__433_ gnd vdd FILL
XFILL_0__455_ gnd vdd FILL
X_458_ _42_ _50_ _292_[1] vdd gnd NAND2X1
X_687_ _293_[9] WWL[9] vdd gnd BUFX2
XFILL45750x36150 gnd vdd FILL
X_496_ _278_ _85_ _84_ _86_ vdd gnd OAI21X1
XFILL_1__336_ gnd vdd FILL
XFILL_0__358_ gnd vdd FILL
XFILL_1__565_ gnd vdd FILL
XFILL_0__587_ gnd vdd FILL
X_399_ _235_ _270_ _277_ _5_ vdd gnd OAI21X1
XFILL45750x150 gnd vdd FILL
X_611_ _166_ _44_ _284__bF$buf1 _167_ vdd gnd AOI21X1
XFILL_1__659_ gnd vdd FILL
X_420_ DIN[1] _13_ _14_ vdd gnd NOR2X1
XFILL_1__468_ gnd vdd FILL
XFILL_0__511_ gnd vdd FILL
X_514_ _278_ _102_ _103_ vdd gnd NOR2X1
X_323_ _173_ _204_ _43_ _212_ vdd gnd AOI21X1
X_552_ ADDR[0] _136_ _133_ _137_ vdd gnd NAND3X1
X_608_ DIN[0] DIN[1] _164_ vdd gnd NOR2X1
X_361_ _246_ _244_ _284__bF$buf3 _247_ vdd gnd AOI21X1
XFILL_0__414_ gnd vdd FILL
X_417_ FI_MODE[1] _10_ _284__bF$buf2 _11_ vdd gnd AOI21X1
XFILL_1__621_ gnd vdd FILL
X_590_ _160_ _135_ _289_[0] vdd gnd NOR2X1
X_646_ _289_[13] RWL[13] vdd gnd BUFX2
XFILL45450x14550 gnd vdd FILL
X_455_ _37_ _48_ vdd gnd INVX1
X_684_ _293_[6] WWL[6] vdd gnd BUFX2
XFILL_1__524_ gnd vdd FILL
X_493_ FI_POS[1] _279_ _83_ vdd gnd NOR2X1
XFILL_0__546_ gnd vdd FILL
X_549_ _132_ _133_ _134_ _135_ vdd gnd NAND3X1
X_358_ _279_ _285_ _43_ _244_ vdd gnd OAI21X1
X_587_ ADDR[3] _150_ _159_ vdd gnd NAND2X1
XFILL_1__427_ gnd vdd FILL
X_396_ _275_ _276_ _3_ vdd gnd AND2X2
XFILL_0__678_ gnd vdd FILL
XFILL_0_BUFX2_insert10 gnd vdd FILL
XFILL_0_BUFX2_insert11 gnd vdd FILL
XFILL_0__487_ gnd vdd FILL
X_299_ _37_ _189_ _188_ _190_ vdd gnd NAND3X1
X_511_ _95_ _100_ _101_ vdd gnd AND2X2
X_320_ SENSE[3] _169__bF$buf1 _209_ vdd gnd NAND2X1
XFILL_0__602_ gnd vdd FILL
X_605_ _8_ _161_ vdd gnd INVX1
X_414_ FI_POS_2_bF$buf1 _287_ _284__bF$buf2 _8_ vdd gnd OAI21X1
X_643_ _289_[10] RWL[10] vdd gnd BUFX2
X_452_ FI_POS[0] _285_ _279_ _45_ vdd gnd OAI21X1
X_508_ _278_ _85_ _98_ vdd gnd NOR2X1
X_681_ _293_[3] WWL[3] vdd gnd BUFX2
XFILL_0__314_ gnd vdd FILL
X_317_ _205_ _163_ _31_ _206_ vdd gnd OAI21X1
X_490_ _54_ _80_ _30_ _81_ vdd gnd OAI21X1
X_546_ ADDR[3] _132_ vdd gnd INVX2
X_355_ _237_ _242_ vdd gnd INVX1
X_584_ _131_ _157_ _293_[12] vdd gnd NOR2X1
XFILL_0__390_ gnd vdd FILL
X_393_ _273_ _274_ _2_ vdd gnd AND2X2
XFILL_0__446_ gnd vdd FILL
X_449_ _37_ _41_ _35_ _42_ vdd gnd NAND3X1
XFILL46050x28950 gnd vdd FILL
XFILL_0__675_ gnd vdd FILL
X_678_ _293_[13] WWL[13] vdd gnd BUFX2
XFILL45750x43350 gnd vdd FILL
X_487_ _77_ _74_ DIN[0] _78_ vdd gnd OAI21X1
X_296_ _173_ _186_ _43_ _187_ vdd gnd AOI21X1
XFILL46050x150 gnd vdd FILL
XFILL_0__349_ gnd vdd FILL
XFILL_0__578_ gnd vdd FILL
XFILL_0__387_ gnd vdd FILL
X_602_ _160_ _157_ _289_[12] vdd gnd NOR2X1
X_411_ FI_POS[1] _285_ vdd gnd INVX2
X_640_ _288_[0] R[0] vdd gnd BUFX2
XFILL_0__502_ gnd vdd FILL
X_505_ _87_ _86_ _94_ _95_ vdd gnd NAND3X1
X_314_ DIN[0] DIN[1] _203_ vdd gnd NAND2X1
X_543_ _125_ _129_ _130_ vdd gnd AND2X2
X_352_ _232_ _239_ vdd gnd INVX1
XFILL_0__405_ gnd vdd FILL
X_408_ _280_ _282_ _291_ vdd gnd NOR2X1
X_581_ ADDR[3] _133_ _142_ _156_ vdd gnd NAND3X1
X_637_ _7_ CLK refw[7] vdd gnd DFFPOSX1
X_390_ _271_ _272_ _1_ vdd gnd AND2X2
XFILL_0__443_ gnd vdd FILL
X_446_ DIN[3] _39_ vdd gnd INVX1
XFILL_0__672_ gnd vdd FILL
X_675_ _293_[10] WWL[10] vdd gnd BUFX2
XFILL_0__308_ gnd vdd FILL
XFILL_0__481_ gnd vdd FILL
X_484_ FI_POS[1] FI_POS[0] _75_ vdd gnd NAND2X1
XFILL_0__537_ gnd vdd FILL
XFILL_0__346_ gnd vdd FILL
X_349_ SENSE[5] _169__bF$buf2 _236_ vdd gnd NAND2X1
XFILL_0__575_ gnd vdd FILL
X_578_ _131_ _154_ _293_[9] vdd gnd NOR2X1
XFILL_0__384_ gnd vdd FILL
XFILL46050x14550 gnd vdd FILL
X_387_ _28_ _168_ _270_ _0_ vdd gnd MUX2X1
XFILL_0__669_ gnd vdd FILL
XFILL_0__478_ gnd vdd FILL
XFILL_1__685_ gnd vdd FILL
XFILL_1__494_ gnd vdd FILL
X_502_ DIN[1] DIN[2] _92_ vdd gnd NOR2X1
X_311_ _196_ _201_ vdd gnd INVX1
X_540_ _290_ _126_ _117_ _127_ vdd gnd AOI21X1
XFILL_1__397_ gnd vdd FILL
XFILL_0__402_ gnd vdd FILL
X_405_ FI_POS[1] _279_ _280_ vdd gnd NAND2X1
X_634_ _4_ CLK refw[4] vdd gnd DFFPOSX1
XFILL_0__440_ gnd vdd FILL
X_443_ FI_POS[0] _285_ _36_ vdd gnd NAND2X1
X_672_ _292_[7] WD[7] vdd gnd BUFX2
XFILL_0__305_ gnd vdd FILL
X_308_ DIN[2] _20_ _198_ vdd gnd NOR2X1
X_481_ FI_POS[1] FI_POS[0] _279_ _72_ vdd gnd OAI21X1
XFILL_0__534_ gnd vdd FILL
X_537_ _279_ _75_ _284__bF$buf0 _124_ vdd gnd OAI21X1
XFILL_1__321_ gnd vdd FILL
XFILL_0__343_ gnd vdd FILL
X_346_ _232_ _163_ _31_ _233_ vdd gnd OAI21X1
XFILL_1__550_ gnd vdd FILL
XFILL_0__572_ gnd vdd FILL
XFILL_1__606_ gnd vdd FILL
X_575_ ADDR[3] _133_ _134_ _153_ vdd gnd NAND3X1
XFILL_0__628_ gnd vdd FILL
X_384_ _124_ _268_ _267_ _269_ vdd gnd NAND3X1
XFILL_1__644_ gnd vdd FILL
XFILL_0__666_ gnd vdd FILL
X_669_ _292_[4] WD[4] vdd gnd BUFX2
XFILL_1__453_ gnd vdd FILL
XFILL_0__475_ gnd vdd FILL
XFILL_1__509_ gnd vdd FILL
X_478_ _62_ _59_ _70_ vdd gnd AND2X2
XFILL_1__356_ gnd vdd FILL
XFILL_1__585_ gnd vdd FILL
X_402_ FI_MODE[1] FI_MODE[0] _278_ vdd gnd NAND2X1
X_631_ _1_ CLK refw[1] vdd gnd DFFPOSX1
X_440_ _286_ FI_POS[1] FI_POS_2_bF$buf1 _33_ vdd gnd AOI21X1
XFILL_0__302_ gnd vdd FILL
X_305_ SENSE[2] _169__bF$buf3 _195_ vdd gnd NAND2X1
XFILL_0__531_ gnd vdd FILL
X_534_ _121_ _292_[6] vdd gnd INVX1
X_343_ _224_ _230_ _288_[4] vdd gnd NAND2X1
X_572_ _131_ _151_ _293_[6] vdd gnd NOR2X1
X_628_ SENSE[1] _169__bF$buf2 _183_ vdd gnd NAND2X1
XFILL_1__412_ gnd vdd FILL
X_381_ _173_ _265_ _43_ _266_ vdd gnd AOI21X1
X_437_ FI_MODE[0] _29_ _30_ vdd gnd NAND2X1
X_666_ _292_[1] WD[1] vdd gnd BUFX2
X_475_ FI_POS_2_bF$buf3 _285_ _43_ _67_ vdd gnd OAI21X1
XFILL_1__544_ gnd vdd FILL
X_569_ ADDR[1] ADDR[2] _139_ _149_ vdd gnd NAND3X1
XFILL46050x21750 gnd vdd FILL
XFILL_0__375_ gnd vdd FILL
X_378_ _261_ _169__bF$buf0 _262_ _263_ vdd gnd OAI21X1
X_302_ _191_ _163_ _31_ _192_ vdd gnd OAI21X1
X_531_ _114_ _119_ vdd gnd INVX1
X_340_ _225_ _227_ _30_ _228_ vdd gnd OAI21X1
XFILL_1__600_ gnd vdd FILL
X_625_ _179_ _163_ _31_ _180_ vdd gnd OAI21X1
XFILL_0__431_ gnd vdd FILL
X_434_ _27_ _23_ _28_ vdd gnd AND2X2
X_663_ _290_ VIEW vdd gnd BUFX2
X_472_ _56_ _63_ _55_ _64_ vdd gnd NAND3X1
X_528_ _109_ _116_ vdd gnd INVX1
XFILL_0__334_ gnd vdd FILL
X_337_ _217_ _225_ vdd gnd INVX1
XFILL_0__563_ gnd vdd FILL
X_566_ _146_ _147_ vdd gnd INVX1
XFILL_0__619_ gnd vdd FILL
XFILL_0__372_ gnd vdd FILL
X_375_ _259_ _244_ _284__bF$buf3 _260_ vdd gnd AOI21X1
XFILL_0__657_ gnd vdd FILL
XFILL_0__466_ gnd vdd FILL
X_469_ DIN[0] DIN[2] _61_ vdd gnd NOR2X1
XFILL_0__369_ gnd vdd FILL
XFILL_0__598_ gnd vdd FILL
X_622_ _8_ _177_ _176_ _178_ vdd gnd NAND3X1
X_431_ _278_ _9_ _24_ _25_ vdd gnd OAI21X1
X_660_ _288_[5] R[5] vdd gnd BUFX2
XFILL_0__522_ gnd vdd FILL
X_525_ _278_ _109_ _112_ _113_ vdd gnd OAI21X1
XFILL_0__331_ gnd vdd FILL
X_334_ SENSE[4] _169__bF$buf2 _222_ vdd gnd NAND2X1
XFILL_0__560_ gnd vdd FILL
X_563_ _144_ ADDR[3] _145_ vdd gnd OR2X2
XFILL_0__616_ gnd vdd FILL
X_619_ _173_ _174_ _43_ _175_ vdd gnd AOI21X1
X_372_ _251_ _257_ _288_[6] vdd gnd NAND2X1
XFILL_0__425_ gnd vdd FILL
X_428_ _21_ _17_ _22_ vdd gnd NAND2X1
XFILL_0__654_ gnd vdd FILL
X_657_ _288_[2] R[2] vdd gnd BUFX2
XFILL_0__463_ gnd vdd FILL
X_466_ DIN[0] _18_ _58_ vdd gnd NOR2X1
XFILL_0__519_ gnd vdd FILL
XFILL45750x7350 gnd vdd FILL
XFILL_0__328_ gnd vdd FILL
XFILL_0__557_ gnd vdd FILL
XFILL_0__366_ gnd vdd FILL
X_369_ _252_ _254_ _30_ _255_ vdd gnd OAI21X1
XFILL_0__595_ gnd vdd FILL
X_598_ _160_ _153_ _289_[8] vdd gnd NOR2X1
XFILL_1__382_ gnd vdd FILL
XFILL_1__438_ gnd vdd FILL
X_522_ FI_POS_2_bF$buf2 FI_POS[1] _110_ vdd gnd NAND2X1
X_331_ _218_ _163_ _31_ _219_ vdd gnd OAI21X1
X_560_ _132_ _133_ _142_ _143_ vdd gnd NAND3X1
XFILL_0__613_ gnd vdd FILL
X_616_ _161_ _167_ _171_ _172_ vdd gnd OAI21X1
XFILL_0__422_ gnd vdd FILL
X_425_ DIN[0] _15_ _19_ vdd gnd NAND2X1
XFILL_0__651_ gnd vdd FILL
X_654_ _289_[8] RWL[8] vdd gnd BUFX2
XFILL_0__460_ gnd vdd FILL
X_463_ _54_ _52_ _30_ _55_ vdd gnd OAI21X1
XFILL_0__516_ gnd vdd FILL
X_519_ _15_ _104_ _107_ _108_ vdd gnd NAND3X1
X_328_ _87_ _216_ vdd gnd INVX1
X_557_ _140_ ADDR[3] _141_ vdd gnd OR2X2
XFILL_1__341_ gnd vdd FILL
XFILL_0__363_ gnd vdd FILL
X_366_ _244_ _252_ vdd gnd INVX1
XFILL_1__570_ gnd vdd FILL
XFILL_0__419_ gnd vdd FILL
XFILL_0__592_ gnd vdd FILL
XFILL_1__626_ gnd vdd FILL
X_595_ _160_ _148_ _289_[5] vdd gnd NOR2X1
XFILL_1__664_ gnd vdd FILL
XFILL_1__473_ gnd vdd FILL
XFILL_1__529_ gnd vdd FILL
X_498_ DIN[2] _15_ _88_ vdd gnd NOR2X1
XFILL46050x36150 gnd vdd FILL
X_613_ ADDR[3] ADDR[2] _142_ _169_ vdd gnd NAND3X1
XFILL45750x18150 gnd vdd FILL
X_422_ DIN[0] _15_ _16_ vdd gnd NOR2X1
X_651_ _289_[5] RWL[5] vdd gnd BUFX2
X_460_ _283_ _51_ FI_MODE[1] _52_ vdd gnd OAI21X1
X_516_ _103_ _97_ _104_ _105_ vdd gnd OAI21X1
XFILL_1__300_ gnd vdd FILL
X_325_ _210_ _214_ vdd gnd INVX1
X_554_ _131_ _138_ _293_[1] vdd gnd NOR2X1
X_363_ SENSE[6] _169__bF$buf2 _249_ vdd gnd NAND2X1
X_419_ DIN[0] _13_ vdd gnd INVX2
X_592_ _160_ _141_ _289_[2] vdd gnd NOR2X1
X_648_ _289_[2] RWL[2] vdd gnd BUFX2
X_457_ _48_ _47_ _49_ _50_ vdd gnd OAI21X1
XFILL_0__683_ gnd vdd FILL
X_686_ _293_[8] WWL[8] vdd gnd BUFX2
XFILL_0__319_ gnd vdd FILL
XFILL_0__492_ gnd vdd FILL
X_495_ FI_POS_2_bF$buf0 FI_POS[1] _286_ _85_ vdd gnd NAND3X1
XFILL_0__548_ gnd vdd FILL
X_589_ CLK _281_ _160_ vdd gnd NAND2X1
XFILL_0__395_ gnd vdd FILL
X_398_ _270_ _292_[5] _277_ vdd gnd NAND2X1
X_610_ _165_ _163_ _31_ _166_ vdd gnd OAI21X1
XFILL45750x39750 gnd vdd FILL
XFILL_0__489_ gnd vdd FILL
XFILL_0__298_ gnd vdd FILL
X_513_ FI_POS_2_bF$buf0 FI_POS[1] FI_POS[0] _102_ vdd gnd NAND3X1
X_322_ _77_ _207_ _210_ _211_ vdd gnd OAI21X1
X_551_ ADDR[1] _136_ vdd gnd INVX1
XFILL_0__604_ gnd vdd FILL
X_607_ DIN[3] _53_ _162_ _163_ vdd gnd NAND3X1
X_360_ _245_ _163_ _31_ _246_ vdd gnd OAI21X1
X_416_ FI_POS_2_bF$buf3 FI_POS[1] _10_ vdd gnd NOR2X1
XFILL_0__642_ gnd vdd FILL
X_645_ _289_[12] RWL[12] vdd gnd BUFX2
XFILL_0__451_ gnd vdd FILL
X_454_ _29_ FI_MODE[0] _46_ _44_ _47_ vdd 
+ gnd
+ AOI22X1
XFILL_0__507_ gnd vdd FILL
XFILL_0__680_ gnd vdd FILL
X_683_ _293_[5] WWL[5] vdd gnd BUFX2
XFILL_0__316_ gnd vdd FILL
X_319_ refw[3] _208_ vdd gnd INVX1
X_492_ _78_ _82_ _292_[3] vdd gnd NAND2X1
X_548_ ADDR[1] ADDR[0] _134_ vdd gnd NOR2X1
XFILL_0__354_ gnd vdd FILL
X_357_ _238_ _243_ _288_[5] vdd gnd NAND2X1
XFILL_0__583_ gnd vdd FILL
X_586_ _131_ _158_ _293_[13] vdd gnd NOR2X1
XFILL_0__639_ gnd vdd FILL
XFILL_0__392_ gnd vdd FILL
X_395_ _281_ _169__bF$buf0 _208_ _276_ vdd gnd OAI21X1
XFILL_0__448_ gnd vdd FILL
XFILL_0__677_ gnd vdd FILL
XFILL_0__486_ gnd vdd FILL
X_489_ _283_ _79_ FI_MODE[1] _80_ vdd gnd OAI21X1
XFILL_0__295_ gnd vdd FILL
X_298_ _184_ _189_ vdd gnd INVX1
X_510_ _90_ _93_ _99_ _100_ vdd gnd NAND3X1
XBUFX2_insert10 FI_POS[2] FI_POS_2_bF$buf1 vdd gnd BUFX2
XBUFX2_insert11 FI_POS[2] FI_POS_2_bF$buf0 vdd gnd BUFX2
XFILL46050x43350 gnd vdd FILL
XFILL_0__389_ gnd vdd FILL
X_604_ _160_ _159_ _289_[14] vdd gnd NOR2X1
XFILL_0__410_ gnd vdd FILL
X_413_ _285_ _286_ _287_ vdd gnd NAND2X1
X_642_ _289_[1] RWL[1] vdd gnd BUFX2
X_451_ FI_POS_2_bF$buf3 FI_POS[1] _43_ _44_ vdd gnd OAI21X1
XFILL_1__499_ gnd vdd FILL
XFILL_0__504_ gnd vdd FILL
X_507_ _29_ _96_ _30_ _97_ vdd gnd OAI21X1
X_680_ _293_[2] WWL[2] vdd gnd BUFX2
XFILL_0__313_ gnd vdd FILL
X_316_ _204_ _205_ vdd gnd INVX1
XFILL_0__542_ gnd vdd FILL
X_545_ WE CLK _131_ vdd gnd NAND2X1
XFILL_0__351_ gnd vdd FILL
X_354_ _225_ _240_ _30_ _241_ vdd gnd OAI21X1
XFILL_0__407_ gnd vdd FILL
XFILL_0__580_ gnd vdd FILL
X_583_ _144_ _132_ _157_ vdd gnd OR2X2
X_639_ CLK PRE_N vdd gnd BUFX2
X_392_ _281_ _169__bF$buf3 _194_ _274_ vdd gnd OAI21X1
XFILL_0__445_ gnd vdd FILL
X_448_ _40_ _38_ _41_ vdd gnd NAND2X1
X_677_ _293_[12] WWL[12] vdd gnd BUFX2
XFILL_0__483_ gnd vdd FILL
X_486_ _76_ _77_ vdd gnd INVX1
XFILL_0__539_ gnd vdd FILL
XFILL_1__326_ gnd vdd FILL
X_295_ DIN[2] _19_ _186_ vdd gnd NOR2X1
XFILL_0__348_ gnd vdd FILL
XFILL_1__555_ gnd vdd FILL
XFILL_0__577_ gnd vdd FILL
X_389_ _281_ _169__bF$buf3 _182_ _272_ vdd gnd OAI21X1
X_601_ _160_ _156_ _289_[11] vdd gnd NOR2X1
XFILL_1__649_ gnd vdd FILL
X_410_ FI_MODE[1] _283_ _284_ vdd gnd NOR2X1
XFILL_1__458_ gnd vdd FILL
XFILL_0__501_ gnd vdd FILL
X_504_ _90_ _93_ _94_ vdd gnd NAND2X1
XFILL_0__310_ gnd vdd FILL
X_313_ _197_ _202_ _288_[2] vdd gnd NAND2X1
X_542_ _128_ _127_ DIN[3] _129_ vdd gnd OAI21X1
X_351_ _231_ _234_ _237_ _238_ vdd gnd OAI21X1
XFILL_0__404_ gnd vdd FILL
X_407_ FI_MODE[1] FI_MODE[0] _281_ _282_ vdd gnd NAND3X1
XFILL_1__611_ gnd vdd FILL
X_580_ _131_ _155_ _293_[10] vdd gnd NOR2X1
X_636_ _6_ CLK refw[6] vdd gnd DFFPOSX1
X_445_ _14_ _16_ DIN[3] _38_ vdd gnd OAI21X1
XFILL_0__671_ gnd vdd FILL
X_674_ _293_[1] WWL[1] vdd gnd BUFX2
XFILL_0__307_ gnd vdd FILL
XFILL_0__480_ gnd vdd FILL
XFILL_1__514_ gnd vdd FILL
X_483_ _67_ _73_ _284__bF$buf3 _74_ vdd gnd AOI21X1
XFILL_0__536_ gnd vdd FILL
X_539_ _122_ _126_ vdd gnd INVX1
X_348_ refw[5] _235_ vdd gnd INVX1
X_577_ _137_ _132_ _154_ vdd gnd OR2X2
XFILL_1__361_ gnd vdd FILL
XFILL_1__417_ gnd vdd FILL
X_386_ _281_ _169__bF$buf2 _270_ vdd gnd NOR2X1
XFILL_1__590_ gnd vdd FILL
X_501_ _15_ _18_ _91_ vdd gnd NOR2X1
X_310_ _54_ _199_ _30_ _200_ vdd gnd OAI21X1
X_404_ FI_POS_2_bF$buf0 _279_ vdd gnd INVX2
X_633_ _3_ CLK refw[3] vdd gnd DFFPOSX1
X_442_ _32_ _34_ _30_ _35_ vdd gnd OAI21X1
X_671_ _292_[6] WD[6] vdd gnd BUFX2
X_307_ _69_ _193_ _196_ _197_ vdd gnd OAI21X1
X_480_ _64_ _71_ _292_[2] vdd gnd NAND2X1
X_536_ _278_ _122_ _112_ _123_ vdd gnd OAI21X1
X_345_ DIN[0] DIN[2] _15_ _232_ vdd gnd NAND3X1
X_574_ _131_ _152_ _293_[7] vdd gnd NOR2X1
XFILL_0__380_ gnd vdd FILL
X_383_ _263_ _268_ vdd gnd INVX1
XFILL_0__436_ gnd vdd FILL
X_439_ _10_ _31_ _32_ vdd gnd NOR2X1
X_668_ _292_[3] WD[3] vdd gnd BUFX2
X_477_ _56_ _69_ vdd gnd INVX1
XFILL_0__339_ gnd vdd FILL
XFILL_0__568_ gnd vdd FILL
XFILL_0__377_ gnd vdd FILL
X_401_ _130_ _261_ _270_ _7_ vdd gnd MUX2X1
X_630_ _0_ CLK refw[0] vdd gnd DFFPOSX1
XFILL46050x7350 gnd vdd FILL
X_304_ refw[2] _194_ vdd gnd INVX1
X_533_ _115_ _120_ _121_ vdd gnd AND2X2
X_342_ _87_ _229_ _228_ _230_ vdd gnd NAND3X1
X_571_ _132_ _150_ _151_ vdd gnd NAND2X1
XFILL_0__624_ gnd vdd FILL
X_627_ refw[1] _182_ vdd gnd INVX1
X_380_ _258_ _265_ vdd gnd INVX1
XFILL_0__433_ gnd vdd FILL
X_436_ FI_MODE[1] _29_ vdd gnd INVX2
XFILL_0__662_ gnd vdd FILL
X_665_ _292_[0] WD[0] vdd gnd BUFX2
XFILL_0__471_ gnd vdd FILL
X_474_ _278_ _65_ _31_ _66_ vdd gnd OAI21X1
XFILL_0__527_ gnd vdd FILL
XFILL_0__336_ gnd vdd FILL
X_339_ _173_ _226_ _43_ _227_ vdd gnd AOI21X1
XFILL_0__565_ gnd vdd FILL
X_568_ _131_ _148_ _293_[5] vdd gnd NOR2X1
XFILL_0__374_ gnd vdd FILL
X_377_ SENSE[7] _169__bF$buf0 _262_ vdd gnd NAND2X1
XFILL_0__659_ gnd vdd FILL
XFILL_0__468_ gnd vdd FILL
XFILL_1__675_ gnd vdd FILL
X_301_ _18_ _16_ _191_ vdd gnd NAND2X1
X_530_ _116_ _290_ _117_ _118_ vdd gnd AOI21X1
XFILL45450x18150 gnd vdd FILL
XFILL_1__387_ gnd vdd FILL
XFILL_0__621_ gnd vdd FILL
X_624_ _18_ _14_ _179_ vdd gnd NAND2X1
XFILL_0__430_ gnd vdd FILL
X_433_ _17_ _21_ _26_ _27_ vdd gnd NAND3X1
X_662_ _288_[7] R[7] vdd gnd BUFX2
X_471_ _59_ _62_ _63_ vdd gnd NAND2X1
XFILL_0__524_ gnd vdd FILL
X_527_ _18_ _114_ _113_ _115_ vdd gnd NAND3X1
XFILL_0__333_ gnd vdd FILL
X_336_ _216_ _220_ _223_ _224_ vdd gnd OAI21X1
XFILL_0__562_ gnd vdd FILL
X_565_ ADDR[0] ADDR[2] _136_ _146_ vdd gnd NAND3X1
XFILL_0__618_ gnd vdd FILL
X_374_ _258_ _163_ _31_ _259_ vdd gnd OAI21X1
XFILL_0__427_ gnd vdd FILL
XFILL_0__656_ gnd vdd FILL
X_659_ _288_[4] R[4] vdd gnd BUFX2
XFILL_1__443_ gnd vdd FILL
XFILL_0__465_ gnd vdd FILL
X_468_ _13_ _18_ _60_ vdd gnd NOR2X1
XFILL_1__346_ gnd vdd FILL
XFILL_0__368_ gnd vdd FILL
XFILL_1__575_ gnd vdd FILL
XFILL_0__597_ gnd vdd FILL
XFILL45450x39750 gnd vdd FILL
X_621_ _171_ _177_ vdd gnd INVX1
XFILL_1__669_ gnd vdd FILL
X_430_ FI_MODE[1] _10_ _24_ vdd gnd NAND2X1
XFILL_1__478_ gnd vdd FILL
XFILL46050x10950 gnd vdd FILL
XFILL_0__521_ gnd vdd FILL
X_524_ _111_ FI_MODE[1] _284__bF$buf0 _112_ vdd gnd AOI21X1
X_333_ refw[4] _221_ vdd gnd INVX1
X_562_ ADDR[2] _134_ _144_ vdd gnd NAND2X1
X_618_ _165_ _174_ vdd gnd INVX1
XFILL_1__402_ gnd vdd FILL
X_371_ _114_ _256_ _255_ _257_ vdd gnd NAND3X1
XFILL_0__424_ gnd vdd FILL
X_427_ _18_ _19_ _20_ _21_ vdd gnd NAND3X1
X_656_ _288_[1] R[1] vdd gnd BUFX2
X_465_ DIN[2] _13_ _57_ vdd gnd NOR2X1
XFILL_1__305_ gnd vdd FILL
XFILL_1__534_ gnd vdd FILL
X_559_ _136_ _139_ _142_ vdd gnd NOR2X1
X_368_ _173_ _253_ _43_ _254_ vdd gnd AOI21X1
X_597_ _160_ _152_ _289_[7] vdd gnd NOR2X1
XFILL_0__497_ gnd vdd FILL
X_521_ FI_POS_2_bF$buf2 _285_ _286_ _109_ vdd gnd NAND3X1
X_330_ DIN[2] _164_ _218_ vdd gnd NAND2X1
XFILL_0_BUFX2_insert0 gnd vdd FILL
XFILL_0_BUFX2_insert1 gnd vdd FILL
XFILL_0_BUFX2_insert3 gnd vdd FILL
XFILL_0_BUFX2_insert5 gnd vdd FILL
XFILL_0_BUFX2_insert6 gnd vdd FILL
XFILL_0_BUFX2_insert8 gnd vdd FILL
X_615_ _168_ _169__bF$buf1 _170_ _171_ vdd gnd OAI21X1
X_424_ DIN[2] _18_ vdd gnd INVX2
X_653_ _289_[7] RWL[7] vdd gnd BUFX2
X_462_ _31_ _53_ _54_ vdd gnd NOR2X1
X_518_ _278_ _102_ _84_ _107_ vdd gnd OAI21X1
XFILL_0__324_ gnd vdd FILL
XFILL46050x18150 gnd vdd FILL
X_327_ _211_ _215_ _288_[3] vdd gnd NAND2X1
XFILL_0__553_ gnd vdd FILL
X_556_ ADDR[1] _139_ _133_ _140_ vdd gnd NAND3X1
XFILL_0__609_ gnd vdd FILL
X_365_ _119_ _247_ _250_ _251_ vdd gnd OAI21X1
X_594_ _160_ _145_ _289_[4] vdd gnd NOR2X1
XFILL_0__647_ gnd vdd FILL
XFILL_0__456_ gnd vdd FILL
X_459_ _285_ FI_POS[0] FI_POS_2_bF$buf3 _51_ vdd gnd AOI21X1
XFILL_0__685_ gnd vdd FILL
XFILL_0__494_ gnd vdd FILL
X_497_ _279_ _287_ _284__bF$buf2 _87_ vdd gnd OAI21X1
XFILL_0__359_ gnd vdd FILL
XFILL_0__588_ gnd vdd FILL
XFILL_0__397_ gnd vdd FILL
X_612_ refw[0] _168_ vdd gnd INVX1
X_421_ DIN[1] _15_ vdd gnd INVX2
X_650_ _289_[4] RWL[4] vdd gnd BUFX2
XFILL_0__512_ gnd vdd FILL
X_515_ _279_ _36_ _284__bF$buf3 _104_ vdd gnd OAI21X1
XFILL_0__321_ gnd vdd FILL
X_324_ _54_ _212_ _30_ _213_ vdd gnd OAI21X1
XFILL46050x39750 gnd vdd FILL
XFILL_0__550_ gnd vdd FILL
X_553_ _137_ ADDR[3] _138_ vdd gnd OR2X2
XFILL_0__606_ gnd vdd FILL
X_609_ _18_ _164_ _165_ vdd gnd NAND2X1
X_362_ refw[6] _248_ vdd gnd INVX1
XFILL_0__415_ gnd vdd FILL
X_418_ _278_ _9_ _11_ _12_ vdd gnd OAI21X1
X_591_ _160_ _138_ _289_[1] vdd gnd NOR2X1
XFILL_0__644_ gnd vdd FILL
X_647_ _289_[14] RWL[14] vdd gnd BUFX2
XFILL_0__453_ gnd vdd FILL
X_456_ _38_ _40_ _49_ vdd gnd AND2X2
XFILL_0__509_ gnd vdd FILL
XFILL_0__682_ gnd vdd FILL
X_685_ _293_[7] WWL[7] vdd gnd BUFX2
XFILL_0__318_ gnd vdd FILL
XFILL_0__491_ gnd vdd FILL
X_494_ _83_ FI_MODE[1] _284__bF$buf0 _84_ vdd gnd AOI21X1
XFILL_0__547_ gnd vdd FILL
XFILL_0__356_ gnd vdd FILL
X_359_ DIN[1] DIN[2] _13_ _245_ vdd gnd NAND3X1

.ends
.end
