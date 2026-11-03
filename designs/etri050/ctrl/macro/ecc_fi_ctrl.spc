.subckt ecc_fi_ctrl vdd gnd ADDR[0] ADDR[1] ADDR[2] ADDR[3] CLK
+ DED_FLAG DIN[0] DIN[1] DIN[2] DIN[3] DOUT_CORR[0] DOUT_CORR[1] DOUT_CORR[2]
+ DOUT_CORR[3] DOUT_RAW[0] DOUT_RAW[1] DOUT_RAW[2] DOUT_RAW[3] FI_MODE[0] FI_MODE[1] FI_POS[0]
+ FI_POS[1] FI_POS[2] PRE_N RWL[0] RWL[1] RWL[2] RWL[3] RWL[4]
+ RWL[5] RWL[6] RWL[7] RWL[8] RWL[9] RWL[10] RWL[11] RWL[12]
+ RWL[13] RWL[14] SEC_FLAG SENSE[0] SENSE[1] SENSE[2] SENSE[3] SENSE[4]
+ SENSE[5] SENSE[6] SENSE[7] WD[0] WD[1] WD[2] WD[3] WD[4]
+ WD[5] WD[6] WD[7] WE WWL[0] WWL[1] WWL[2] WWL[3]
+ WWL[4] WWL[5] WWL[6] WWL[7] WWL[8] WWL[9] WWL[10] WWL[11]
+ WWL[12] WWL[13] WWL[14] 

X_588_ FI_POS[2] _302_ _307_ _19_ vdd gnd OAI21X1
X_397_ _179_ _147_ _132_ _180_ vdd gnd NAND3X1
X_703_ _314_[3] RWL[3] vdd gnd BUFX2
X_512_ _250_ _274_ _317_[10] vdd gnd NOR2X1
X_321_ FI_POS[2] _24_ _307_ _107_ vdd gnd OAI21X1
X_550_ _316_[3] _289_ vdd gnd INVX1
X_606_ _300_ _24_ _307_ _36_ vdd gnd OAI21X1
X_415_ _195_ _194_ _191_ _196_ vdd gnd OAI21X1
X_644_ _300_ _70_ _307_ _71_ vdd gnd OAI21X1
X_453_ DIN[1] DIN[2] _230_ vdd gnd NOR2X1
X_509_ _256_ _251_ _273_ vdd gnd OR2X2
X_682_ _5_ CLK refw[5] vdd gnd DFFPOSX1
X_318_ _102_ _100_ _103_ _104_ vdd gnd OAI21X1
X_491_ _10_ _261_ vdd gnd INVX1
X_547_ _316_[2] _287_ vdd gnd INVX1
X_356_ _33_ _38_ _140_ _138_ _141_ vdd 
+ gnd
+ AOI22X1
X_585_ _301_ _309_ _16_ vdd gnd AND2X2
X_394_ _169_ _139_ _178_ vdd gnd NAND2X1
X_679_ _2_ CLK refw[2] vdd gnd DFFPOSX1
XFILL47550x18150 gnd vdd FILL
X_488_ ADDR[1] _258_ _252_ _259_ vdd gnd NAND3X1
X_700_ _314_[13] RWL[13] vdd gnd BUFX2
X_603_ _29_ _26_ _32_ _33_ vdd gnd OAI21X1
X_412_ DIN[0] _193_ vdd gnd INVX1
X_641_ refw[4] SENSE[4] _12__bF$buf0 _68_ vdd gnd MUX2X1
X_450_ _42_ _25_ _169_ _227_ vdd gnd OAI21X1
X_506_ _250_ _271_ _317_[7] vdd gnd NOR2X1
X_544_ _316_[1] _285_ vdd gnd INVX1
X_353_ _313_[0] _121_ _138_ vdd gnd NAND2X1
X_409_ _189_ _100_ _113_ _190_ vdd gnd AOI21X1
X_582_ refw[3] _12__bF$buf1 _13_ vdd gnd NAND2X1
X_638_ _313_[2] _63_ _65_ vdd gnd NOR2X1
X_391_ _313_[1] _174_ _175_ vdd gnd NOR2X1
X_447_ _224_ _193_ _225_ vdd gnd OR2X2
X_676_ refw[1] SENSE[1] _12__bF$buf4 _103_ vdd gnd MUX2X1
X_485_ _256_ ADDR[3] _257_ vdd gnd OR2X2
XFILL47550x39750 gnd vdd FILL
X_579_ ADDR[1] ADDR[0] _10_ vdd gnd NAND2X1
X_388_ _172_ _171_ _312_[0] vdd gnd NAND2X1
X_600_ SENSE[5] _30_ vdd gnd INVX1
X_503_ _251_ _269_ _270_ vdd gnd NAND2X1
X_732_ _317_[8] WWL[8] vdd gnd BUFX2
X_541_ WE _12__bF$buf2 _283_ vdd gnd NAND2X1
X_350_ _121_ _134_ _135_ vdd gnd NAND2X1
X_406_ _170_ _186_ _187_ _188_ vdd gnd NAND3X1
X_635_ _57_ _62_ _63_ vdd gnd NAND2X1
X_444_ _101_ _305_ _222_ vdd gnd NOR2X1
X_673_ _99_ _305_ _307_ _100_ vdd gnd AOI21X1
X_729_ _317_[5] WWL[5] vdd gnd BUFX2
X_482_ _250_ _254_ _317_[0] vdd gnd NOR2X1
X_538_ _179_ _165_ _281_ vdd gnd NOR2X1
X_347_ _132_ _133_ vdd gnd INVX1
X_576_ _309_ _310_ vdd gnd INVX1
X_385_ _169_ _170_ vdd gnd INVX1
X_479_ ADDR[2] _252_ vdd gnd INVX2
X_500_ _250_ _267_ _317_[5] vdd gnd NOR2X1
X_403_ _185_ _184_ _312_[2] vdd gnd NAND2X1
X_632_ refw[7] _12__bF$buf3 _60_ vdd gnd NAND2X1
X_441_ _213_ _219_ _220_ vdd gnd OR2X2
X_670_ _15_ _21_ _96_ _97_ vdd gnd AOI21X1
X_726_ _317_[2] WWL[2] vdd gnd BUFX2
X_535_ _280_ _276_ _314_[12] vdd gnd NOR2X1
X_344_ _129_ _124_ _130_ vdd gnd NAND2X1
X_573_ _306_ _307_ vdd gnd INVX4
X_629_ _55_ _41_ _56_ _57_ vdd gnd OAI21X1
X_382_ _166_ _165_ _134_ _167_ vdd gnd AOI21X1
X_438_ _215_ _214_ _217_ vdd gnd NOR2X1
X_667_ _90_ _93_ _18_ _94_ vdd gnd NAND3X1
X_476_ _249_ _248_ _316_[7] vdd gnd NAND2X1
X_379_ _63_ _145_ _144_ _164_ vdd gnd NAND3X1
X_400_ _47_ _54_ _182_ _147_ _183_ vdd 
+ gnd
+ AOI22X1
X_723_ _317_[12] WWL[12] vdd gnd BUFX2
X_532_ _280_ _273_ _314_[9] vdd gnd NOR2X1
X_341_ _117_ _119_ _121_ _127_ vdd gnd AOI21X1
X_570_ FI_MODE[1] _304_ vdd gnd INVX1
X_626_ _47_ _54_ _313_[2] vdd gnd NAND2X1
X_435_ _193_ _191_ _214_ vdd gnd NOR2X1
X_664_ SENSE[2] _91_ vdd gnd INVX1
X_473_ _41_ _246_ _55_ _247_ vdd gnd AOI21X1
X_529_ _280_ _270_ _314_[6] vdd gnd NOR2X1
X_338_ _95_ _97_ _120_ _123_ _124_ vdd 
+ gnd
+ OAI22X1
X_567_ FI_POS[1] _299_ _300_ _301_ vdd gnd NAND3X1
X_376_ _157_ _160_ _148_ _161_ vdd gnd NAND3X1
XFILL47550x32550 gnd vdd FILL
X_699_ _314_[12] RWL[12] vdd gnd BUFX2
X_720_ _317_[1] WWL[1] vdd gnd BUFX2
X_623_ _300_ _51_ _307_ _52_ vdd gnd OAI21X1
X_432_ _98_ _211_ vdd gnd INVX1
X_661_ refw[2] SENSE[2] _12__bF$buf4 _88_ vdd gnd MUX2X1
X_717_ _316_[6] WD[6] vdd gnd BUFX2
X_470_ _191_ _243_ _245_ vdd gnd NAND2X1
X_526_ _280_ _262_ _314_[3] vdd gnd NOR2X1
X_335_ _104_ _111_ _121_ vdd gnd NAND2X1
X_564_ _283_ _297_ _298_ _7_ vdd gnd OAI21X1
X_373_ _149_ _153_ _155_ _158_ vdd gnd NAND3X1
X_429_ _204_ _208_ _209_ vdd gnd OR2X2
X_658_ _84_ _79_ _85_ vdd gnd NAND2X1
X_467_ _66_ _40_ _169_ _242_ vdd gnd OAI21X1
X_696_ _314_[1] RWL[1] vdd gnd BUFX2
X_599_ _306_ _28_ _29_ vdd gnd NOR2X1
X_620_ _39_ _48_ _49_ vdd gnd AND2X2
X_714_ _316_[3] WD[3] vdd gnd BUFX2
X_523_ _280_ _254_ _314_[0] vdd gnd NOR2X1
X_332_ refw[0] SENSE[0] _12__bF$buf0 _118_ vdd gnd MUX2X1
X_561_ _283_ _295_ _296_ _6_ vdd gnd OAI21X1
X_617_ _44_ _12__bF$buf1 _45_ _46_ vdd gnd OAI21X1
X_370_ _134_ _154_ _155_ vdd gnd NAND2X1
X_426_ _195_ _194_ _205_ _206_ vdd gnd OAI21X1
X_655_ _69_ _75_ _313_[1] _82_ vdd gnd AOI21X1
X_464_ _239_ _192_ _240_ vdd gnd OR2X2
X_693_ _313_[3] DOUT_RAW[3] vdd gnd BUFX2
X_329_ refw[0] _12__bF$buf3 _115_ vdd gnd NAND2X1
X_558_ _283_ _293_ _294_ _5_ vdd gnd OAI21X1
X_367_ _149_ _150_ _151_ _152_ vdd gnd NAND3X1
X_596_ _25_ _305_ _307_ _26_ vdd gnd AOI21X1
XFILL47250x18150 gnd vdd FILL
XBUFX2_insert0 _12_ _12__bF$buf4 vdd gnd BUFX2
XBUFX2_insert1 _12_ _12__bF$buf3 vdd gnd BUFX2
XBUFX2_insert2 _12_ _12__bF$buf2 vdd gnd BUFX2
XBUFX2_insert3 _12_ _12__bF$buf1 vdd gnd BUFX2
XBUFX2_insert4 _12_ _12__bF$buf0 vdd gnd BUFX2
X_499_ _251_ _266_ _267_ vdd gnd NAND2X1
X_711_ _316_[0] WD[0] vdd gnd BUFX2
X_520_ _250_ _278_ _317_[14] vdd gnd NOR2X1
XFILL47850x14550 gnd vdd FILL
X_614_ _306_ _42_ _43_ vdd gnd NOR2X1
X_423_ _304_ _202_ _306_ _203_ vdd gnd OAI21X1
X_652_ _64_ _65_ _76_ _78_ _79_ vdd 
+ gnd
+ OAI22X1
X_708_ _314_[8] RWL[8] vdd gnd BUFX2
X_461_ _48_ _305_ _237_ vdd gnd NOR2X1
X_517_ ADDR[3] _266_ _277_ vdd gnd NAND2X1
X_690_ _313_[0] DOUT_RAW[0] vdd gnd BUFX2
X_326_ FI_POS[2] _70_ _307_ _112_ vdd gnd OAI21X1
X_555_ _283_ _291_ _292_ _4_ vdd gnd OAI21X1
X_364_ _313_[2] _149_ vdd gnd INVX1
X_593_ FI_POS[2] _22_ _299_ _23_ vdd gnd NAND3X1
X_649_ _38_ _33_ _69_ _75_ _76_ vdd 
+ gnd
+ AOI22X1
X_458_ _228_ _234_ _235_ vdd gnd OR2X2
XFILL47250x39750 gnd vdd FILL
X_687_ _312_[1] DOUT_CORR[1] vdd gnd BUFX2
X_496_ _250_ _264_ _317_[4] vdd gnd NOR2X1
X_399_ _85_ _130_ _173_ _182_ vdd gnd NOR3X1
X_611_ _300_ _302_ _39_ _40_ vdd gnd OAI21X1
X_420_ _199_ _190_ _201_ vdd gnd NAND2X1
X_705_ _314_[5] RWL[5] vdd gnd BUFX2
X_514_ _250_ _275_ _317_[11] vdd gnd NOR2X1
X_323_ refw[1] _12__bF$buf4 _109_ vdd gnd NAND2X1
X_552_ _283_ _289_ _290_ _3_ vdd gnd OAI21X1
X_608_ _36_ _37_ _35_ _38_ vdd gnd NAND3X1
X_361_ _313_[3] _145_ _144_ _146_ vdd gnd NAND3X1
X_417_ DIN[2] _197_ _198_ vdd gnd NAND2X1
X_590_ _19_ _20_ _18_ _21_ vdd gnd NAND3X1
X_646_ refw[4] _12__bF$buf2 _73_ vdd gnd NAND2X1
X_455_ _230_ _229_ _232_ vdd gnd NOR2X1
X_684_ _7_ CLK refw[7] vdd gnd DFFPOSX1
X_493_ _250_ _262_ _317_[3] vdd gnd NOR2X1
X_549_ _283_ _287_ _288_ _2_ vdd gnd OAI21X1
X_358_ _313_[1] _143_ vdd gnd INVX1
X_587_ _17_ _16_ _306_ _18_ vdd gnd OAI21X1
X_396_ _157_ _160_ _179_ vdd gnd AND2X2
X_702_ _314_[2] RWL[2] vdd gnd BUFX2
X_511_ _259_ _251_ _274_ vdd gnd OR2X2
X_320_ _17_ _105_ _306_ _106_ vdd gnd OAI21X1
XFILL47550x3750 gnd vdd FILL
X_605_ _17_ _34_ _306_ _35_ vdd gnd OAI21X1
X_414_ DIN[1] DIN[0] _195_ vdd gnd NOR2X1
X_643_ _22_ _299_ _70_ vdd gnd NAND2X1
X_452_ _192_ _191_ _229_ vdd gnd NOR2X1
X_508_ _250_ _272_ _317_[8] vdd gnd NOR2X1
X_681_ _4_ CLK refw[4] vdd gnd DFFPOSX1
X_490_ _250_ _260_ _317_[2] vdd gnd NOR2X1
X_546_ _283_ _285_ _286_ _1_ vdd gnd OAI21X1
X_355_ _134_ _139_ _140_ vdd gnd NAND2X1
X_584_ _8_ _308_ _14_ _15_ vdd gnd OAI21X1
X_393_ _175_ _176_ _170_ _177_ vdd gnd OAI21X1
X_449_ _226_ _225_ _316_[3] vdd gnd NAND2X1
X_678_ _1_ CLK refw[1] vdd gnd DFFPOSX1
X_487_ ADDR[0] _258_ vdd gnd INVX1
X_602_ _30_ _12__bF$buf0 _31_ _32_ vdd gnd OAI21X1
X_411_ DIN[1] _192_ vdd gnd INVX1
X_640_ _306_ _66_ _67_ vdd gnd NOR2X1
X_505_ _251_ ADDR[2] _261_ _271_ vdd gnd NAND3X1
X_543_ _283_ _282_ _284_ _0_ vdd gnd OAI21X1
X_352_ _135_ _136_ _313_[1] _137_ vdd gnd AOI21X1
X_408_ _86_ _99_ _169_ _189_ vdd gnd OAI21X1
X_581_ _10_ _11_ _12_ vdd gnd NOR2X1
X_637_ _313_[2] _63_ _64_ vdd gnd AND2X2
X_390_ _173_ _165_ _132_ _174_ vdd gnd NAND3X1
X_446_ _223_ _306_ _8_ _224_ vdd gnd AOI21X1
X_675_ _307_ _101_ _102_ vdd gnd AND2X2
X_484_ ADDR[0] _255_ _252_ _256_ vdd gnd NAND3X1
X_349_ _21_ _15_ _134_ vdd gnd AND2X2
X_578_ SENSE[3] _9_ vdd gnd INVX1
XFILL47250x32550 gnd vdd FILL
X_387_ _169_ _122_ _172_ vdd gnd NAND2X1
X_502_ _268_ _269_ vdd gnd INVX1
X_731_ _317_[7] WWL[7] vdd gnd BUFX2
X_540_ _316_[0] _282_ vdd gnd INVX1
X_405_ _173_ _133_ _63_ _187_ vdd gnd OAI21X1
X_634_ _58_ _61_ _50_ _62_ vdd gnd NAND3X1
X_443_ _221_ _220_ _316_[2] vdd gnd NAND2X1
X_672_ FI_POS[2] _24_ _98_ _99_ vdd gnd OAI21X1
X_728_ _317_[4] WWL[4] vdd gnd BUFX2
X_481_ _251_ _252_ _253_ _254_ vdd gnd NAND3X1
X_537_ _280_ _278_ _314_[14] vdd gnd NOR2X1
X_346_ _85_ _130_ _132_ vdd gnd NOR2X1
X_575_ FI_POS[1] FI_POS[0] _300_ _309_ vdd gnd NAND3X1
X_384_ _168_ _304_ _169_ vdd gnd NOR2X1
X_669_ _89_ _94_ _96_ vdd gnd NAND2X1
X_478_ ADDR[3] _251_ vdd gnd INVX2
X_402_ _169_ _154_ _185_ vdd gnd NAND2X1
X_631_ SENSE[7] _59_ vdd gnd INVX1
X_440_ _216_ _218_ _219_ vdd gnd NAND2X1
X_725_ _317_[14] WWL[14] vdd gnd BUFX2
X_534_ _280_ _275_ _314_[11] vdd gnd NOR2X1
X_343_ _127_ _128_ _126_ _125_ _129_ vdd 
+ gnd
+ OAI22X1
X_572_ FI_MODE[0] _304_ _306_ vdd gnd NAND2X1
XFILL47850x36150 gnd vdd FILL
X_628_ refw[7] SENSE[7] _12__bF$buf3 _56_ vdd gnd MUX2X1
X_381_ _161_ _166_ vdd gnd INVX1
X_437_ _215_ _214_ _205_ _216_ vdd gnd OAI21X1
X_666_ _91_ _12__bF$buf0 _92_ _93_ vdd gnd OAI21X1
XFILL47850x7350 gnd vdd FILL
X_475_ _205_ _247_ _249_ vdd gnd NAND2X1
X_569_ FI_POS[2] _302_ _301_ _303_ vdd gnd OAI21X1
X_378_ _137_ _141_ _313_[3] _163_ vdd gnd OAI21X1
X_722_ _317_[11] WWL[11] vdd gnd BUFX2
X_531_ _280_ _272_ _314_[8] vdd gnd NOR2X1
XFILL47550x14550 gnd vdd FILL
X_340_ _313_[0] _96_ _126_ vdd gnd NOR2X1
X_625_ _52_ _53_ _50_ _54_ vdd gnd NAND3X1
X_434_ _308_ _212_ _87_ _213_ vdd gnd AOI21X1
X_663_ FI_POS[2] _51_ _307_ _90_ vdd gnd OAI21X1
X_719_ _317_[0] WWL[0] vdd gnd BUFX2
X_472_ _28_ _40_ _169_ _246_ vdd gnd OAI21X1
X_528_ _280_ _267_ _314_[5] vdd gnd NOR2X1
X_337_ _121_ _122_ _123_ vdd gnd NOR2X1
X_566_ FI_POS[2] _300_ vdd gnd INVX2
X_375_ _313_[3] _159_ _158_ _160_ vdd gnd NAND3X1
X_469_ _243_ _191_ _244_ vdd gnd OR2X2
X_698_ _314_[11] RWL[11] vdd gnd BUFX2
XFILL47550x150 gnd vdd FILL
X_622_ FI_POS[1] _299_ _51_ vdd gnd NAND2X1
X_431_ _210_ _209_ _316_[1] vdd gnd NAND2X1
X_660_ _306_ _86_ _87_ vdd gnd NOR2X1
X_716_ _316_[5] WD[5] vdd gnd BUFX2
X_525_ _280_ _260_ _314_[2] vdd gnd NOR2X1
X_334_ _111_ _104_ _117_ _119_ _120_ vdd 
+ gnd
+ AOI22X1
X_563_ refw[7] _283_ _298_ vdd gnd NAND2X1
X_619_ FI_POS[1] FI_POS[0] FI_POS[2] _48_ vdd gnd NAND3X1
X_372_ _63_ _152_ _156_ _157_ vdd gnd NAND3X1
X_428_ _206_ _207_ _208_ vdd gnd NAND2X1
X_657_ _80_ _81_ _82_ _83_ _84_ vdd 
+ gnd
+ OAI22X1
X_466_ _241_ _240_ _316_[5] vdd gnd NAND2X1
X_695_ _314_[0] RWL[0] vdd gnd BUFX2
X_369_ _94_ _89_ _154_ vdd gnd AND2X2
X_598_ _27_ _28_ vdd gnd INVX1
XFILL47250x7350 gnd vdd FILL
X_713_ _316_[2] WD[2] vdd gnd BUFX2
X_522_ CLK _279_ _280_ vdd gnd NAND2X1
X_331_ _100_ _113_ _116_ _117_ vdd gnd OAI21X1
X_560_ refw[6] _283_ _296_ vdd gnd NAND2X1
X_616_ refw[6] _12__bF$buf1 _45_ vdd gnd NAND2X1
X_425_ DIN[3] _205_ vdd gnd INVX1
X_654_ _47_ _54_ _63_ _81_ vdd gnd AOI21X1
X_463_ _238_ _306_ _29_ _239_ vdd gnd AOI21X1
X_519_ ADDR[3] _269_ _278_ vdd gnd NAND2X1
X_692_ _313_[2] DOUT_RAW[2] vdd gnd BUFX2
X_328_ SENSE[0] _114_ vdd gnd INVX1
X_557_ refw[5] _283_ _294_ vdd gnd NAND2X1
X_366_ _89_ _94_ _313_[0] _151_ vdd gnd NAND3X1
X_595_ _300_ _24_ _23_ _25_ vdd gnd OAI21X1
X_689_ _312_[3] DOUT_CORR[3] vdd gnd BUFX2
X_498_ _265_ _266_ vdd gnd INVX1
X_710_ _315_ SEC_FLAG vdd gnd BUFX2
X_613_ _39_ _42_ vdd gnd INVX1
X_422_ _310_ _17_ _99_ _202_ vdd gnd AOI21X1
X_651_ _313_[1] _77_ _78_ vdd gnd NOR2X1
X_707_ _314_[7] RWL[7] vdd gnd BUFX2
X_460_ _236_ _235_ _316_[4] vdd gnd NAND2X1
X_516_ _250_ _276_ _317_[12] vdd gnd NOR2X1
X_325_ _107_ _110_ _106_ _111_ vdd gnd NAND3X1
X_554_ refw[4] _283_ _292_ vdd gnd NAND2X1
X_363_ _79_ _84_ _124_ _129_ _148_ vdd 
+ gnd
+ AOI22X1
X_419_ _190_ _199_ _200_ vdd gnd OR2X2
X_592_ FI_POS[1] _22_ vdd gnd INVX2
X_648_ _71_ _74_ _35_ _75_ vdd gnd NAND3X1
X_457_ _231_ _233_ _234_ vdd gnd NAND2X1
X_686_ _312_[0] DOUT_CORR[0] vdd gnd BUFX2
XFILL47850x150 gnd vdd FILL
X_495_ _263_ ADDR[3] _264_ vdd gnd OR2X2
X_589_ refw[3] SENSE[3] _12__bF$buf1 _20_ vdd gnd MUX2X1
X_398_ _313_[2] _180_ _181_ vdd gnd NOR2X1
X_610_ FI_POS[1] FI_POS[2] _299_ _39_ vdd gnd NAND3X1
X_704_ _314_[4] RWL[4] vdd gnd BUFX2
X_513_ ADDR[3] _252_ _261_ _275_ vdd gnd NAND3X1
X_322_ SENSE[1] _108_ vdd gnd INVX1
X_551_ refw[3] _283_ _290_ vdd gnd NAND2X1
X_607_ refw[5] SENSE[5] _12__bF$buf2 _37_ vdd gnd MUX2X1
X_360_ _313_[1] _136_ _135_ _145_ vdd gnd NAND3X1
X_416_ _195_ _194_ _197_ vdd gnd NOR2X1
X_645_ SENSE[4] _72_ vdd gnd INVX1
X_454_ _230_ _229_ _205_ _231_ vdd gnd OAI21X1
X_683_ _6_ CLK refw[6] vdd gnd DFFPOSX1
X_319_ _98_ _101_ _105_ vdd gnd AND2X2
X_492_ _251_ _252_ _261_ _262_ vdd gnd NAND3X1
X_548_ refw[2] _283_ _288_ vdd gnd NAND2X1
X_357_ _137_ _141_ _63_ _142_ vdd gnd OAI21X1
X_586_ _305_ _17_ vdd gnd INVX2
X_395_ _178_ _177_ _312_[1] vdd gnd NAND2X1
X_489_ _259_ ADDR[3] _260_ vdd gnd OR2X2
X_701_ _314_[14] RWL[14] vdd gnd BUFX2
X_510_ _250_ _273_ _317_[9] vdd gnd NOR2X1
X_604_ _23_ _27_ _34_ vdd gnd AND2X2
X_413_ _192_ _193_ _194_ vdd gnd NOR2X1
X_642_ _67_ _26_ _68_ _69_ vdd gnd OAI21X1
X_451_ _26_ _227_ _67_ _228_ vdd gnd AOI21X1
X_507_ ADDR[3] _252_ _253_ _272_ vdd gnd NAND3X1
X_680_ _3_ CLK refw[3] vdd gnd DFFPOSX1
X_545_ refw[1] _283_ _286_ vdd gnd NAND2X1
XFILL47550x36150 gnd vdd FILL
X_354_ _111_ _104_ _139_ vdd gnd AND2X2
X_583_ _9_ _12__bF$buf1 _13_ _14_ vdd gnd OAI21X1
X_639_ _23_ _66_ vdd gnd INVX1
X_392_ _174_ _313_[1] _176_ vdd gnd AND2X2
X_448_ _193_ _224_ _226_ vdd gnd NAND2X1
X_677_ _0_ CLK refw[0] vdd gnd DFFPOSX1
X_486_ _250_ _257_ _317_[1] vdd gnd NOR2X1
X_389_ _157_ _160_ _173_ vdd gnd NAND2X1
X_601_ refw[5] _12__bF$buf2 _31_ vdd gnd NAND2X1
X_410_ DIN[2] _191_ vdd gnd INVX1
X_504_ _250_ _270_ _317_[6] vdd gnd NOR2X1
X_733_ _317_[9] WWL[9] vdd gnd BUFX2
X_542_ refw[0] _283_ _284_ vdd gnd NAND2X1
X_351_ _104_ _111_ _313_[0] _136_ vdd gnd NAND3X1
X_407_ _77_ _170_ _188_ _312_[3] vdd gnd OAI21X1
X_580_ ADDR[3] ADDR[2] _11_ vdd gnd NAND2X1
X_636_ _63_ _313_[3] vdd gnd INVX1
X_445_ _303_ _222_ FI_MODE[1] _223_ vdd gnd OAI21X1
XFILL47850x10950 gnd vdd FILL
X_674_ FI_POS[0] _22_ _300_ _101_ vdd gnd NAND3X1
X_483_ ADDR[1] _255_ vdd gnd INVX1
X_539_ _85_ _281_ _315_ _311_ vdd gnd AOI21X1
X_348_ _131_ _133_ _315_ vdd gnd NAND2X1
X_577_ _306_ _310_ _8_ vdd gnd NOR2X1
X_386_ _162_ _167_ _170_ _171_ vdd gnd OAI21X1
X_501_ ADDR[1] ADDR[2] _258_ _268_ vdd gnd NAND3X1
X_730_ _317_[6] WWL[6] vdd gnd BUFX2
X_404_ _137_ _141_ _182_ _186_ vdd gnd OAI21X1
X_633_ _59_ _12__bF$buf3 _60_ _61_ vdd gnd OAI21X1
X_442_ _219_ _213_ _221_ vdd gnd NAND2X1
X_671_ _22_ _299_ _300_ _98_ vdd gnd NAND3X1
X_727_ _317_[3] WWL[3] vdd gnd BUFX2
X_480_ ADDR[1] ADDR[0] _253_ vdd gnd NOR2X1
X_536_ _280_ _277_ _314_[13] vdd gnd NOR2X1
X_345_ _85_ _130_ _131_ vdd gnd NAND2X1
X_574_ _303_ _305_ _307_ _308_ vdd gnd AOI21X1
X_383_ FI_MODE[0] _168_ vdd gnd INVX1
X_439_ DIN[3] _217_ _218_ vdd gnd NAND2X1
X_668_ _89_ _94_ _313_[0] _95_ vdd gnd AOI21X1
X_477_ CLK WE _250_ vdd gnd NAND2X1
XFILL47850x18150 gnd vdd FILL
X_401_ _181_ _183_ _170_ _184_ vdd gnd OAI21X1
X_630_ _300_ _302_ _307_ _58_ vdd gnd OAI21X1
X_724_ _317_[13] WWL[13] vdd gnd BUFX2
X_533_ _280_ _274_ _314_[10] vdd gnd NOR2X1
X_342_ _104_ _111_ _122_ _128_ vdd gnd AOI21X1
X_571_ FI_MODE[0] _304_ _305_ vdd gnd NOR2X1
X_627_ _307_ _48_ _55_ vdd gnd AND2X2
X_380_ _164_ _163_ _165_ vdd gnd NAND2X1
X_436_ DIN[0] DIN[2] _215_ vdd gnd NOR2X1
X_665_ refw[2] _12__bF$buf0 _92_ vdd gnd NAND2X1
X_474_ _247_ _205_ _248_ vdd gnd OR2X2
X_339_ _313_[0] _96_ _125_ vdd gnd AND2X2
XFILL47850x39750 gnd vdd FILL
X_568_ FI_POS[1] FI_POS[0] _302_ vdd gnd NAND2X1
X_377_ _313_[0] _147_ _161_ _162_ vdd gnd NOR3X1
X_721_ _317_[10] WWL[10] vdd gnd BUFX2
X_530_ _280_ _271_ _314_[7] vdd gnd NOR2X1
X_624_ refw[6] SENSE[6] _12__bF$buf4 _53_ vdd gnd MUX2X1
X_433_ _211_ _303_ _169_ _212_ vdd gnd OAI21X1
X_662_ _87_ _308_ _88_ _89_ vdd gnd OAI21X1
X_718_ _316_[7] WD[7] vdd gnd BUFX2
X_471_ _245_ _244_ _316_[6] vdd gnd NAND2X1
X_527_ _280_ _264_ _314_[4] vdd gnd NOR2X1
X_336_ _119_ _117_ _122_ vdd gnd NAND2X1
X_565_ FI_POS[0] _299_ vdd gnd INVX2
X_374_ _313_[2] _150_ _151_ _159_ vdd gnd NAND3X1
X_659_ _301_ _86_ vdd gnd INVX1
X_468_ _41_ _242_ _43_ _243_ vdd gnd AOI21X1
X_697_ _314_[10] RWL[10] vdd gnd BUFX2
XFILL47850x25350 gnd vdd FILL
XFILL47550x7350 gnd vdd FILL
X_621_ _17_ _49_ _306_ _50_ vdd gnd OAI21X1
X_430_ _208_ _204_ _210_ vdd gnd NAND2X1
X_715_ _316_[4] WD[4] vdd gnd BUFX2
X_524_ _280_ _257_ _314_[1] vdd gnd NOR2X1
X_333_ _112_ _118_ _106_ _119_ vdd gnd NAND3X1
X_562_ _316_[7] _297_ vdd gnd INVX1
X_618_ _43_ _41_ _46_ _47_ vdd gnd OAI21X1
X_371_ _313_[2] _153_ _155_ _156_ vdd gnd NAND3X1
X_427_ DIN[3] _197_ _207_ vdd gnd NAND2X1
X_656_ _33_ _38_ _77_ _83_ vdd gnd AOI21X1
X_465_ _192_ _239_ _241_ vdd gnd NAND2X1
X_694_ CLK PRE_N vdd gnd BUFX2
X_559_ _316_[6] _295_ vdd gnd INVX1
X_368_ _313_[0] _96_ _153_ vdd gnd NAND2X1
X_597_ FI_POS[0] FI_POS[2] _22_ _27_ vdd gnd NAND3X1
X_712_ _316_[1] WD[1] vdd gnd BUFX2
X_521_ WE _279_ vdd gnd INVX1
X_330_ _114_ _12__bF$buf3 _115_ _116_ vdd gnd OAI21X1
X_615_ SENSE[6] _44_ vdd gnd INVX1
X_424_ _203_ _107_ _204_ vdd gnd AND2X2
X_653_ _57_ _62_ _313_[2] _80_ vdd gnd AOI21X1
X_709_ _314_[9] RWL[9] vdd gnd BUFX2
X_462_ _25_ _237_ FI_MODE[1] _238_ vdd gnd OAI21X1
X_518_ _250_ _277_ _317_[13] vdd gnd NOR2X1
X_691_ _313_[1] DOUT_RAW[1] vdd gnd BUFX2
X_327_ _112_ _113_ vdd gnd INVX1
X_556_ _316_[5] _293_ vdd gnd INVX1
X_365_ _15_ _21_ _96_ _150_ vdd gnd NAND3X1
X_594_ FI_POS[0] _22_ _24_ vdd gnd NAND2X1
X_459_ _234_ _228_ _236_ vdd gnd NAND2X1
XFILL47850x32550 gnd vdd FILL
X_688_ _312_[2] DOUT_CORR[2] vdd gnd BUFX2
X_497_ ADDR[0] ADDR[2] _255_ _265_ vdd gnd NAND3X1
XFILL47850x3750 gnd vdd FILL
X_612_ _40_ _305_ _307_ _41_ vdd gnd AOI21X1
X_421_ _201_ _200_ _316_[0] vdd gnd NAND2X1
X_650_ _69_ _75_ _77_ vdd gnd NAND2X1
X_706_ _314_[6] RWL[6] vdd gnd BUFX2
X_515_ _263_ _251_ _276_ vdd gnd OR2X2
X_324_ _108_ _12__bF$buf4 _109_ _110_ vdd gnd OAI21X1
X_553_ _316_[4] _291_ vdd gnd INVX1
X_609_ _33_ _38_ _313_[1] vdd gnd NAND2X1
X_362_ _146_ _142_ _147_ vdd gnd NAND2X1
X_418_ _196_ _198_ _199_ vdd gnd NAND2X1
X_591_ _15_ _21_ _313_[0] vdd gnd NAND2X1
X_647_ _72_ _12__bF$buf2 _73_ _74_ vdd gnd OAI21X1
X_456_ DIN[3] _232_ _233_ vdd gnd NAND2X1
X_685_ _311_ DED_FLAG vdd gnd BUFX2
X_494_ ADDR[2] _253_ _263_ vdd gnd NAND2X1
X_359_ _143_ _138_ _140_ _144_ vdd gnd NAND3X1

.ends
.end
