.subckt ecc_fi_ctrl vdd gnd ADDR[0] ADDR[1] ADDR[2] ADDR[3] CLK
+ DED_FLAG DIN[0] DIN[1] DIN[2] DIN[3] DOUT[0] DOUT[1] DOUT[2]
+ DOUT[3] FI_MODE[0] FI_MODE[1] FI_POS[0] FI_POS[1] FI_POS[2] PRE_N RWL[0]
+ RWL[1] RWL[2] RWL[3] RWL[4] RWL[5] RWL[6] RWL[7] RWL[8]
+ RWL[9] RWL[10] RWL[11] RWL[12] RWL[13] RWL[14] SEC_FLAG SENSE[0]
+ SENSE[1] SENSE[2] SENSE[3] SENSE[4] SENSE[5] SENSE[6] SENSE[7] WD[0]
+ WD[1] WD[2] WD[3] WD[4] WD[5] WD[6] WD[7] WE
+ WWL[0] WWL[1] WWL[2] WWL[3] WWL[4] WWL[5] WWL[6] WWL[7]
+ WWL[8] WWL[9] WWL[10] WWL[11] WWL[12] WWL[13] WWL[14] 

X_588_ _306_ _280_ _343_[0] vdd gnd NOR2X1
X_397_ _51_ _62_ _144_ vdd gnd NAND2X1
X_703_ _22_ _28_ _18_ _65_ vdd gnd AOI21X1
X_512_ _219_ _249_ _251_ vdd gnd NAND2X1
X_741_ _342_[0] DOUT[0] vdd gnd BUFX2
X_550_ _282_ ADDR[3] _283_ vdd gnd OR2X2
X_606_ WE _340__bF$buf3 _309_ vdd gnd NAND2X1
X_415_ _160_ _159_ _51_ _161_ vdd gnd AOI21X1
X_644_ ADDR[3] ADDR[2] _339_ vdd gnd NAND2X1
X_453_ _91_ _94_ _85_ _197_ vdd gnd AOI21X1
X_509_ _11_ _72_ _247_ _248_ vdd gnd OAI21X1
X_682_ FI_POS[1] _326_ _44_ vdd gnd NOR2X1
X_738_ _6_ CLK refw[6] vdd gnd DFFPOSX1
X_491_ _221_ _220_ DIN[3] _232_ vdd gnd OAI21X1
X_547_ _276_ _280_ _346_[0] vdd gnd NOR2X1
X_776_ _346_[14] WWL[14] vdd gnd BUFX2
X_356_ _44_ _325_ _332_ _103_ vdd gnd AOI21X1
X_585_ _276_ _304_ _346_[14] vdd gnd NOR2X1
X_394_ _139_ _140_ _138_ _135_ _141_ vdd 
+ gnd
+ AOI22X1
X_679_ refw[5] _340__bF$buf2 _41_ vdd gnd NAND2X1
X_488_ _109_ _228_ _110_ _229_ vdd gnd OAI21X1
X_700_ _60_ _56_ _62_ vdd gnd NAND2X1
X_603_ _149_ _158_ _307_ vdd gnd NOR2X1
X_412_ _154_ _157_ _158_ vdd gnd AND2X2
X_641_ _335_ _336_ vdd gnd INVX1
X_450_ _113_ _123_ _194_ vdd gnd AND2X2
X_506_ _245_ _244_ _345_[2] vdd gnd NAND2X1
X_735_ _3_ CLK refw[3] vdd gnd DFFPOSX1
X_544_ ADDR[2] _278_ vdd gnd INVX2
X_773_ _346_[11] WWL[11] vdd gnd BUFX2
X_353_ _32_ _326_ _325_ _100_ vdd gnd NAND3X1
X_409_ _29_ _96_ _99_ _155_ vdd gnd NAND3X1
X_582_ ADDR[3] _292_ _303_ vdd gnd NAND2X1
X_638_ _332_ _333_ vdd gnd INVX2
X_391_ _136_ _137_ _138_ vdd gnd NAND2X1
X_447_ _191_ _188_ _342_[1] vdd gnd NAND2X1
X_676_ _37_ _38_ vdd gnd INVX1
X_485_ _225_ _216_ _227_ vdd gnd NAND2X1
X_579_ _276_ _301_ _346_[11] vdd gnd NOR2X1
X_388_ _18_ _29_ _135_ vdd gnd NAND2X1
X_600_ _306_ _302_ _343_[12] vdd gnd NOR2X1
X_503_ _240_ _242_ _243_ vdd gnd NAND2X1
X_732_ _0_ CLK refw[0] vdd gnd DFFPOSX1
X_541_ _275_ _274_ _345_[7] vdd gnd NAND2X1
X_770_ _346_[0] WWL[0] vdd gnd BUFX2
X_350_ _84_ _77_ _97_ vdd gnd AND2X2
X_406_ _137_ _96_ _99_ _152_ vdd gnd NAND3X1
X_635_ FI_MODE[1] _330_ vdd gnd INVX1
X_444_ FI_POS[0] _125_ _189_ vdd gnd NOR2X1
X_673_ _325_ _33_ _34_ _35_ vdd gnd OAI21X1
XFILL45750x14550 gnd vdd FILL
X_729_ _87_ _73_ _90_ _91_ vdd gnd OAI21X1
X_482_ DIN[2] _223_ _224_ vdd gnd NAND2X1
X_538_ _272_ _13_ _273_ vdd gnd AND2X2
X_767_ _345_[5] WD[5] vdd gnd BUFX2
X_347_ _92_ _93_ _79_ _94_ vdd gnd NAND3X1
X_576_ _285_ _277_ _300_ vdd gnd OR2X2
X_385_ _123_ _125_ _132_ vdd gnd NAND2X1
X_479_ DIN[1] DIN[0] _221_ vdd gnd NOR2X1
X_500_ _239_ _238_ _230_ _240_ vdd gnd OAI21X1
X_403_ _133_ _128_ _150_ vdd gnd NOR2X1
X_632_ FI_POS[1] FI_POS[2] _326_ _327_ vdd gnd NAND3X1
X_441_ _158_ _151_ _186_ vdd gnd NOR2X1
X_670_ FI_POS[1] _32_ vdd gnd INVX1
X_726_ SENSE[2] _88_ vdd gnd INVX1
X_535_ _270_ _269_ _345_[6] vdd gnd NAND2X1
X_764_ _345_[2] WD[2] vdd gnd BUFX2
X_573_ _276_ _298_ _346_[8] vdd gnd NOR2X1
X_629_ _309_ _323_ _324_ _7_ vdd gnd OAI21X1
X_382_ _77_ _84_ _95_ _129_ vdd gnd NAND3X1
X_438_ _149_ _150_ _172_ _183_ vdd gnd NAND3X1
X_667_ _22_ _28_ _29_ vdd gnd NAND2X1
X_476_ DIN[1] _218_ vdd gnd INVX1
X_379_ _122_ _119_ _126_ vdd gnd AND2X2
X_400_ _145_ _146_ _147_ vdd gnd NAND2X1
XFILL46650x36150 gnd vdd FILL
X_723_ _77_ _84_ _85_ vdd gnd NAND2X1
X_532_ _334_ _267_ _20_ _268_ vdd gnd AOI21X1
X_761_ _344_ SEC_FLAG vdd gnd BUFX2
X_570_ _277_ ADDR[2] _287_ _297_ vdd gnd NAND3X1
X_626_ _309_ _321_ _322_ _6_ vdd gnd OAI21X1
X_435_ _326_ _85_ _180_ _181_ vdd gnd OAI21X1
X_664_ refw[6] _340__bF$buf1 _26_ vdd gnd NAND2X1
XFILL46350x150 gnd vdd FILL
X_473_ _86_ _101_ _177_ _215_ vdd gnd OAI21X1
X_529_ _265_ _264_ _345_[5] vdd gnd NAND2X1
X_758_ _343_[7] RWL[7] vdd gnd BUFX2
X_567_ _294_ _295_ vdd gnd INVX1
X_376_ _119_ _122_ _123_ vdd gnd NAND2X1
XFILL46350x14550 gnd vdd FILL
X_699_ _56_ _60_ _51_ _61_ vdd gnd AOI21X1
X_720_ refw[3] _340__bF$buf4 _82_ vdd gnd NAND2X1
XFILL46650x3750 gnd vdd FILL
X_623_ _309_ _319_ _320_ _5_ vdd gnd OAI21X1
X_432_ _177_ _178_ vdd gnd INVX2
X_661_ FI_POS[1] _326_ _23_ vdd gnd NAND2X1
X_717_ _11_ _78_ _332_ _79_ vdd gnd OAI21X1
X_470_ FI_POS[0] _62_ _212_ _213_ vdd gnd OAI21X1
X_526_ _36_ _262_ _39_ _263_ vdd gnd AOI21X1
X_755_ _343_[4] RWL[4] vdd gnd BUFX2
X_564_ _277_ _292_ _293_ vdd gnd NAND2X1
X_373_ FI_POS[2] _52_ _333_ _120_ vdd gnd OAI21X1
X_429_ _174_ _171_ _85_ _175_ vdd gnd AOI21X1
X_658_ _332_ _19_ _20_ vdd gnd NOR2X1
X_467_ _174_ _203_ _18_ _210_ vdd gnd AOI21X1
X_696_ refw[4] _340__bF$buf3 _58_ vdd gnd NAND2X1
X_599_ _306_ _301_ _343_[11] vdd gnd NOR2X1
X_620_ _309_ _317_ _318_ _4_ vdd gnd OAI21X1
XFILL46650x43350 gnd vdd FILL
X_714_ refw[3] SENSE[3] _340__bF$buf4 _76_ vdd gnd MUX2X1
X_523_ _259_ _253_ _261_ vdd gnd NAND2X1
X_752_ _343_[14] RWL[14] vdd gnd BUFX2
X_561_ _276_ _290_ _346_[4] vdd gnd NOR2X1
X_617_ _309_ _315_ _316_ _3_ vdd gnd OAI21X1
X_370_ refw[0] _340__bF$buf4 _117_ vdd gnd NAND2X1
X_426_ _154_ _157_ _172_ vdd gnd NAND2X1
X_655_ _13_ _16_ _12_ _17_ vdd gnd NAND3X1
X_464_ _137_ _95_ FI_POS[0] _208_ vdd gnd MUX2X1
X_693_ refw[4] SENSE[4] _340__bF$buf2 _55_ vdd gnd MUX2X1
X_749_ _343_[11] RWL[11] vdd gnd BUFX2
X_558_ _276_ _288_ _346_[3] vdd gnd NOR2X1
X_367_ _100_ _114_ vdd gnd INVX1
X_596_ _306_ _298_ _343_[8] vdd gnd NOR2X1
XBUFX2_insert0 _340_ _340__bF$buf4 vdd gnd BUFX2
XBUFX2_insert1 _340_ _340__bF$buf3 vdd gnd BUFX2
XBUFX2_insert2 _340_ _340__bF$buf2 vdd gnd BUFX2
XBUFX2_insert3 _340_ _340__bF$buf1 vdd gnd BUFX2
XBUFX2_insert4 _340_ _340__bF$buf0 vdd gnd BUFX2
X_499_ DIN[0] DIN[2] _239_ vdd gnd NOR2X1
X_711_ _72_ _331_ _333_ _73_ vdd gnd AOI21X1
X_520_ DIN[3] _257_ _258_ vdd gnd NAND2X1
XFILL46650x150 gnd vdd FILL
X_614_ _309_ _313_ _314_ _2_ vdd gnd OAI21X1
X_423_ _165_ _168_ _158_ _169_ vdd gnd NAND3X1
X_652_ SENSE[7] _14_ vdd gnd INVX1
X_708_ _64_ _69_ _70_ vdd gnd NAND2X1
X_461_ _137_ _204_ _205_ vdd gnd NOR2X1
X_517_ DIN[1] DIN[2] _255_ vdd gnd NOR2X1
X_690_ _32_ _326_ _52_ vdd gnd NAND2X1
X_746_ _343_[0] RWL[0] vdd gnd BUFX2
X_555_ _276_ _286_ _346_[2] vdd gnd NOR2X1
X_784_ _346_[9] WWL[9] vdd gnd BUFX2
X_364_ refw[1] SENSE[1] _340__bF$buf3 _111_ vdd gnd MUX2X1
X_593_ _306_ _293_ _343_[5] vdd gnd NOR2X1
X_649_ _331_ _11_ vdd gnd INVX2
X_458_ _201_ _196_ _202_ vdd gnd NAND2X1
X_687_ refw[5] SENSE[5] _340__bF$buf2 _49_ vdd gnd MUX2X1
X_496_ _114_ _72_ _177_ _236_ vdd gnd OAI21X1
X_399_ _56_ _60_ _146_ vdd gnd AND2X2
X_611_ _309_ _311_ _312_ _1_ vdd gnd OAI21X1
X_420_ _145_ _162_ _163_ _166_ vdd gnd NAND3X1
X_705_ _62_ _51_ _67_ vdd gnd AND2X2
X_514_ _19_ _35_ _177_ _252_ vdd gnd OAI21X1
X_743_ _342_[2] DOUT[2] vdd gnd BUFX2
X_552_ ADDR[0] _284_ vdd gnd INVX1
X_608_ _309_ _308_ _310_ _0_ vdd gnd OAI21X1
X_781_ _346_[6] WWL[6] vdd gnd BUFX2
X_361_ _45_ _44_ _325_ _108_ vdd gnd OAI21X1
X_417_ _97_ _125_ _163_ vdd gnd NAND2X1
X_590_ _306_ _286_ _343_[2] vdd gnd NOR2X1
X_646_ refw[7] SENSE[7] _340__bF$buf0 _8_ vdd gnd MUX2X1
X_455_ _107_ _112_ _123_ _199_ vdd gnd AOI21X1
X_684_ _45_ _44_ FI_POS[2] _46_ vdd gnd OAI21X1
X_493_ _233_ _229_ _234_ vdd gnd NAND2X1
X_549_ ADDR[0] _281_ _278_ _282_ vdd gnd NAND3X1
X_778_ _346_[3] WWL[3] vdd gnd BUFX2
X_358_ refw[1] _340__bF$buf3 _105_ vdd gnd NAND2X1
X_587_ CLK _305_ _306_ vdd gnd NAND2X1
X_396_ _18_ _137_ _143_ vdd gnd NAND2X1
X_702_ _30_ _31_ _61_ _63_ _64_ vdd 
+ gnd
+ OAI22X1
X_511_ _249_ _219_ _250_ vdd gnd OR2X2
X_740_ _341_ DED_FLAG vdd gnd BUFX2
X_605_ _345_[0] _308_ vdd gnd INVX1
X_414_ _113_ _97_ _160_ vdd gnd NAND2X1
X_643_ ADDR[1] ADDR[0] _338_ vdd gnd NAND2X1
X_452_ _192_ _193_ _195_ _194_ _196_ vdd 
+ gnd
+ OAI22X1
X_508_ _246_ _178_ _11_ _247_ vdd gnd OAI21X1
X_681_ _39_ _36_ _42_ _43_ vdd gnd OAI21X1
X_737_ _5_ CLK refw[5] vdd gnd DFFPOSX1
X_490_ _230_ _223_ _231_ vdd gnd NAND2X1
X_546_ _277_ _278_ _279_ _280_ vdd gnd NAND3X1
X_775_ _346_[13] WWL[13] vdd gnd BUFX2
X_355_ _101_ _331_ _333_ _102_ vdd gnd AOI21X1
X_584_ ADDR[3] _295_ _304_ vdd gnd NAND2X1
X_393_ _56_ _60_ _51_ _140_ vdd gnd NAND3X1
X_449_ _85_ _95_ _193_ vdd gnd NOR2X1
X_678_ SENSE[5] _40_ vdd gnd INVX1
X_487_ _108_ _74_ _178_ _228_ vdd gnd AOI21X1
X_602_ _306_ _304_ _343_[14] vdd gnd NOR2X1
X_411_ _136_ _156_ _155_ _157_ vdd gnd NAND3X1
XFILL46350x36150 gnd vdd FILL
X_640_ FI_POS[1] FI_POS[0] FI_POS[2] _335_ vdd gnd NAND3X1
X_505_ _243_ _237_ _245_ vdd gnd NAND2X1
X_734_ _2_ CLK refw[2] vdd gnd DFFPOSX1
X_543_ ADDR[3] _277_ vdd gnd INVX2
X_772_ _346_[10] WWL[10] vdd gnd BUFX2
X_352_ _97_ _98_ _99_ vdd gnd NAND2X1
X_408_ _18_ _153_ _152_ _154_ vdd gnd NAND3X1
X_581_ _276_ _302_ _346_[12] vdd gnd NOR2X1
X_637_ FI_MODE[0] _330_ _332_ vdd gnd NAND2X1
X_390_ _28_ _22_ _137_ vdd gnd AND2X2
X_446_ _189_ _190_ _177_ _191_ vdd gnd OAI21X1
X_675_ FI_POS[0] FI_POS[2] _32_ _37_ vdd gnd NAND3X1
X_484_ _216_ _225_ _226_ vdd gnd OR2X2
X_769_ _345_[7] WD[7] vdd gnd BUFX2
X_349_ _85_ _95_ _96_ vdd gnd NAND2X1
X_578_ ADDR[3] _278_ _287_ _301_ vdd gnd NAND3X1
XFILL46050x14550 gnd vdd FILL
X_387_ _128_ _133_ _70_ _134_ vdd gnd OAI21X1
X_502_ DIN[3] _241_ _242_ vdd gnd NAND2X1
X_731_ refw[2] SENSE[2] _340__bF$buf1 _93_ vdd gnd MUX2X1
XFILL46650x10950 gnd vdd FILL
X_540_ _230_ _273_ _275_ vdd gnd NAND2X1
X_405_ _134_ _151_ _344_ vdd gnd NAND2X1
X_634_ _325_ _328_ _327_ _329_ vdd gnd OAI21X1
X_443_ _184_ _187_ _178_ _188_ vdd gnd OAI21X1
X_672_ FI_POS[2] _32_ _326_ _34_ vdd gnd NAND3X1
X_728_ _88_ _340__bF$buf1 _89_ _90_ vdd gnd OAI21X1
X_481_ _221_ _220_ _223_ vdd gnd NOR2X1
X_537_ _330_ _271_ _332_ _272_ vdd gnd OAI21X1
X_766_ _345_[4] WD[4] vdd gnd BUFX2
X_575_ _276_ _299_ _346_[9] vdd gnd NOR2X1
X_384_ _113_ _126_ _131_ vdd gnd NAND2X1
X_669_ _18_ _29_ _31_ vdd gnd NOR2X1
X_478_ _218_ _219_ _220_ vdd gnd NOR2X1
X_402_ _141_ _148_ _149_ vdd gnd NOR2X1
X_631_ FI_POS[0] _326_ vdd gnd INVX2
X_440_ _173_ _185_ vdd gnd INVX1
X_725_ _332_ _86_ _87_ vdd gnd NOR2X1
X_534_ _217_ _268_ _270_ vdd gnd NAND2X1
X_763_ _345_[1] WD[1] vdd gnd BUFX2
X_572_ ADDR[3] _278_ _279_ _298_ vdd gnd NAND3X1
X_628_ refw[7] _309_ _324_ vdd gnd NAND2X1
XFILL46650x18150 gnd vdd FILL
X_381_ _99_ _96_ _124_ _127_ _128_ vdd 
+ gnd
+ AOI22X1
X_437_ _182_ _179_ _342_[0] vdd gnd NAND2X1
X_666_ _24_ _27_ _12_ _28_ vdd gnd NAND3X1
X_475_ DIN[2] _217_ vdd gnd INVX1
X_569_ _276_ _296_ _346_[6] vdd gnd NOR2X1
X_378_ _112_ _107_ _125_ vdd gnd AND2X2
X_722_ _80_ _83_ _79_ _84_ vdd gnd NAND3X1
X_531_ _266_ _329_ _177_ _267_ vdd gnd OAI21X1
X_760_ _343_[9] RWL[9] vdd gnd BUFX2
X_625_ refw[6] _309_ _322_ vdd gnd NAND2X1
XFILL46650x39750 gnd vdd FILL
X_434_ _326_ _123_ _180_ vdd gnd NAND2X1
X_663_ SENSE[6] _25_ vdd gnd INVX1
X_719_ SENSE[3] _81_ vdd gnd INVX1
X_472_ _214_ _211_ _342_[3] vdd gnd NAND2X1
X_528_ _218_ _263_ _265_ vdd gnd NAND2X1
X_757_ _343_[6] RWL[6] vdd gnd BUFX2
X_566_ ADDR[1] ADDR[2] _284_ _294_ vdd gnd NAND3X1
X_375_ _120_ _121_ _109_ _122_ vdd gnd NAND3X1
X_469_ FI_POS[0] _136_ _212_ vdd gnd NAND2X1
X_698_ _53_ _59_ _47_ _60_ vdd gnd NAND3X1
X_622_ refw[5] _309_ _320_ vdd gnd NAND2X1
X_431_ _176_ _330_ _177_ vdd gnd NOR2X1
X_660_ _20_ _334_ _21_ _22_ vdd gnd OAI21X1
X_716_ _71_ _74_ _78_ vdd gnd AND2X2
X_525_ _336_ _35_ _177_ _262_ vdd gnd OAI21X1
X_754_ _343_[3] RWL[3] vdd gnd BUFX2
X_563_ _291_ _292_ vdd gnd INVX1
X_619_ refw[4] _309_ _318_ vdd gnd NAND2X1
X_372_ _115_ _102_ _118_ _119_ vdd gnd OAI21X1
X_428_ _172_ _173_ _174_ vdd gnd NOR2X1
X_657_ _327_ _19_ vdd gnd INVX1
X_466_ _136_ _151_ _169_ _209_ vdd gnd NOR3X1
X_695_ SENSE[4] _57_ vdd gnd INVX1
X_369_ SENSE[0] _116_ vdd gnd INVX1
X_598_ _306_ _300_ _343_[10] vdd gnd NOR2X1
X_713_ _333_ _74_ _75_ vdd gnd AND2X2
X_522_ _253_ _259_ _260_ vdd gnd OR2X2
X_751_ _343_[13] RWL[13] vdd gnd BUFX2
X_560_ _289_ ADDR[3] _290_ vdd gnd OR2X2
X_616_ refw[3] _309_ _316_ vdd gnd NAND2X1
X_425_ _134_ _171_ vdd gnd INVX1
X_654_ _14_ _340__bF$buf0 _15_ _16_ vdd gnd OAI21X1
X_463_ _205_ _206_ _178_ _207_ vdd gnd OAI21X1
X_519_ _255_ _254_ _257_ vdd gnd NOR2X1
X_692_ _53_ _54_ vdd gnd INVX1
X_748_ _343_[10] RWL[10] vdd gnd BUFX2
X_557_ _277_ _278_ _287_ _288_ vdd gnd NAND3X1
X_366_ _107_ _112_ _113_ vdd gnd NAND2X1
X_595_ _306_ _297_ _343_[7] vdd gnd NOR2X1
X_689_ _43_ _50_ _51_ vdd gnd NAND2X1
X_498_ _219_ _217_ _238_ vdd gnd NOR2X1
X_710_ FI_POS[2] _328_ _71_ _72_ vdd gnd OAI21X1
XFILL46050x36150 gnd vdd FILL
X_613_ refw[2] _309_ _314_ vdd gnd NAND2X1
XFILL45750x18150 gnd vdd FILL
X_422_ _136_ _167_ _166_ _168_ vdd gnd NAND3X1
X_651_ _337_ _13_ vdd gnd INVX1
X_707_ _65_ _66_ _68_ _67_ _69_ vdd 
+ gnd
+ OAI22X1
X_460_ _158_ _173_ _203_ _204_ vdd gnd NAND3X1
X_516_ _218_ _217_ _254_ vdd gnd NOR2X1
X_745_ CLK PRE_N vdd gnd BUFX2
XFILL46650x32550 gnd vdd FILL
X_554_ _285_ ADDR[3] _286_ vdd gnd OR2X2
X_783_ _346_[8] WWL[8] vdd gnd BUFX2
X_363_ _103_ _110_ vdd gnd INVX1
X_419_ _161_ _164_ _18_ _165_ vdd gnd OAI21X1
X_592_ _306_ _290_ _343_[4] vdd gnd NOR2X1
X_648_ _327_ _335_ _10_ vdd gnd AND2X2
X_457_ _197_ _198_ _199_ _200_ _201_ vdd 
+ gnd
+ OAI22X1
X_686_ _325_ _33_ _333_ _48_ vdd gnd OAI21X1
X_495_ _234_ _235_ _345_[1] vdd gnd NAND2X1
X_589_ _306_ _283_ _343_[1] vdd gnd NOR2X1
X_398_ _50_ _43_ _145_ vdd gnd AND2X2
X_610_ refw[1] _309_ _312_ vdd gnd NAND2X1
X_704_ _9_ _17_ _29_ _66_ vdd gnd AOI21X1
XFILL46350x10950 gnd vdd FILL
X_513_ _251_ _250_ _345_[3] vdd gnd NAND2X1
X_742_ _342_[1] DOUT[1] vdd gnd BUFX2
X_551_ _276_ _283_ _346_[1] vdd gnd NOR2X1
X_607_ refw[0] _309_ _310_ vdd gnd NAND2X1
X_780_ _346_[5] WWL[5] vdd gnd BUFX2
X_360_ _103_ _102_ _106_ _107_ vdd gnd OAI21X1
X_416_ _85_ _113_ _162_ vdd gnd NAND2X1
X_645_ _338_ _339_ _340_ vdd gnd NOR2X1
X_454_ _77_ _84_ _95_ _198_ vdd gnd AOI21X1
X_683_ FI_POS[1] FI_POS[0] _45_ vdd gnd NOR2X1
X_739_ _7_ CLK refw[7] vdd gnd DFFPOSX1
X_492_ _232_ _231_ _233_ vdd gnd NAND2X1
X_548_ ADDR[1] _281_ vdd gnd INVX1
X_777_ _346_[2] WWL[2] vdd gnd BUFX2
X_357_ SENSE[1] _104_ vdd gnd INVX1
X_586_ WE _305_ vdd gnd INVX1
X_395_ _29_ _136_ _142_ vdd gnd NAND2X1
X_489_ DIN[3] _230_ vdd gnd INVX1
X_701_ _43_ _50_ _62_ _63_ vdd gnd AOI21X1
X_510_ _248_ _332_ _75_ _249_ vdd gnd AOI21X1
X_604_ _307_ _173_ _344_ _341_ vdd gnd AOI21X1
X_413_ _107_ _112_ _85_ _159_ vdd gnd NAND3X1
X_642_ _332_ _336_ _337_ vdd gnd NOR2X1
X_451_ _113_ _123_ _195_ vdd gnd NOR2X1
X_507_ FI_POS[1] FI_POS[0] _325_ _246_ vdd gnd OAI21X1
X_680_ _40_ _340__bF$buf2 _41_ _42_ vdd gnd OAI21X1
X_736_ _4_ CLK refw[4] vdd gnd DFFPOSX1
X_545_ ADDR[1] ADDR[0] _279_ vdd gnd NOR2X1
XFILL46350x18150 gnd vdd FILL
X_774_ _346_[12] WWL[12] vdd gnd BUFX2
X_354_ FI_POS[2] _33_ _100_ _101_ vdd gnd OAI21X1
X_583_ _276_ _303_ _346_[13] vdd gnd NOR2X1
X_639_ _329_ _331_ _333_ _334_ vdd gnd AOI21X1
X_392_ _43_ _50_ _62_ _139_ vdd gnd NAND3X1
X_448_ _85_ _95_ _192_ vdd gnd AND2X2
X_677_ _332_ _38_ _39_ vdd gnd NOR2X1
X_486_ _227_ _226_ _345_[0] vdd gnd NAND2X1
XFILL46650x7350 gnd vdd FILL
X_389_ _17_ _9_ _136_ vdd gnd AND2X2
X_601_ _306_ _303_ _343_[13] vdd gnd NOR2X1
X_410_ _137_ _129_ _130_ _156_ vdd gnd NAND3X1
X_504_ _237_ _243_ _244_ vdd gnd OR2X2
X_733_ _1_ CLK refw[1] vdd gnd DFFPOSX1
X_542_ CLK WE _276_ vdd gnd NAND2X1
X_771_ _346_[1] WWL[1] vdd gnd BUFX2
X_351_ _94_ _91_ _98_ vdd gnd AND2X2
XFILL46350x39750 gnd vdd FILL
X_407_ _29_ _129_ _130_ _153_ vdd gnd NAND3X1
X_580_ _289_ _277_ _302_ vdd gnd OR2X2
X_636_ FI_MODE[0] _330_ _331_ vdd gnd NOR2X1
X_445_ _326_ _145_ _190_ vdd gnd NOR2X1
X_674_ _35_ _331_ _333_ _36_ vdd gnd AOI21X1
X_483_ _222_ _224_ _225_ vdd gnd NAND2X1
X_539_ _273_ _230_ _274_ vdd gnd OR2X2
X_768_ _345_[6] WD[6] vdd gnd BUFX2
X_348_ _91_ _94_ _95_ vdd gnd NAND2X1
X_577_ _276_ _300_ _346_[10] vdd gnd NOR2X1
X_386_ _129_ _130_ _131_ _132_ _133_ vdd 
+ gnd
+ AOI22X1
X_501_ _239_ _238_ _241_ vdd gnd NOR2X1
X_730_ FI_POS[2] _23_ _333_ _92_ vdd gnd OAI21X1
X_404_ _149_ _150_ _151_ vdd gnd NAND2X1
X_633_ FI_POS[1] FI_POS[0] _328_ vdd gnd NAND2X1
X_442_ _186_ _185_ _145_ _187_ vdd gnd AOI21X1
X_671_ FI_POS[0] _32_ _33_ vdd gnd NAND2X1
X_727_ refw[2] _340__bF$buf1 _89_ vdd gnd NAND2X1
X_480_ _221_ _220_ _217_ _222_ vdd gnd OAI21X1
X_536_ _11_ _38_ _329_ _271_ vdd gnd AOI21X1
X_765_ _345_[3] WD[3] vdd gnd BUFX2
X_574_ _282_ _277_ _299_ vdd gnd OR2X2
X_383_ _91_ _94_ _85_ _130_ vdd gnd NAND3X1
X_439_ _51_ _173_ _183_ _184_ vdd gnd NOR3X1
X_668_ _18_ _29_ _30_ vdd gnd AND2X2
X_477_ DIN[0] _219_ vdd gnd INVX1
X_401_ _142_ _143_ _147_ _144_ _148_ vdd 
+ gnd
+ AOI22X1
X_630_ FI_POS[2] _325_ vdd gnd INVX4
X_724_ _71_ _86_ vdd gnd INVX1
X_533_ _268_ _217_ _269_ vdd gnd OR2X2
X_762_ _345_[0] WD[0] vdd gnd BUFX2
X_571_ _276_ _297_ _346_[7] vdd gnd NOR2X1
X_627_ _345_[7] _323_ vdd gnd INVX1
X_380_ _125_ _126_ _127_ vdd gnd NAND2X1
X_436_ _177_ _181_ _182_ vdd gnd NAND2X1
X_665_ _25_ _340__bF$buf0 _26_ _27_ vdd gnd OAI21X1
X_474_ _102_ _215_ _115_ _216_ vdd gnd AOI21X1
X_759_ _343_[8] RWL[8] vdd gnd BUFX2
X_568_ _277_ _295_ _296_ vdd gnd NAND2X1
X_377_ _113_ _123_ _124_ vdd gnd NAND2X1
X_721_ _81_ _340__bF$buf1 _82_ _83_ vdd gnd OAI21X1
X_530_ _34_ _266_ vdd gnd INVX1
X_624_ _345_[6] _321_ vdd gnd INVX1
X_433_ _175_ _170_ _178_ _179_ vdd gnd OAI21X1
X_662_ _325_ _23_ _333_ _24_ vdd gnd OAI21X1
X_718_ FI_POS[2] _328_ _333_ _80_ vdd gnd OAI21X1
X_471_ _177_ _213_ _214_ vdd gnd NAND2X1
X_527_ _263_ _218_ _264_ vdd gnd OR2X2
X_756_ _343_[5] RWL[5] vdd gnd BUFX2
X_565_ _276_ _293_ _346_[5] vdd gnd NOR2X1
X_374_ refw[0] SENSE[0] _340__bF$buf4 _121_ vdd gnd MUX2X1
X_659_ refw[6] SENSE[6] _340__bF$buf0 _21_ vdd gnd MUX2X1
X_468_ _210_ _209_ _178_ _211_ vdd gnd OAI21X1
X_697_ _57_ _340__bF$buf2 _58_ _59_ vdd gnd OAI21X1
X_621_ _345_[5] _319_ vdd gnd INVX1
X_430_ FI_MODE[0] _176_ vdd gnd INVX1
XFILL46050x10950 gnd vdd FILL
X_715_ _75_ _73_ _76_ _77_ vdd gnd OAI21X1
X_524_ _261_ _260_ _345_[4] vdd gnd NAND2X1
XFILL46350x3750 gnd vdd FILL
X_753_ _343_[2] RWL[2] vdd gnd BUFX2
X_562_ ADDR[0] ADDR[2] _281_ _291_ vdd gnd NAND3X1
X_618_ _345_[4] _317_ vdd gnd INVX1
X_371_ _116_ _340__bF$buf4 _117_ _118_ vdd gnd OAI21X1
X_427_ _168_ _165_ _173_ vdd gnd NAND2X1
X_656_ _9_ _17_ _18_ vdd gnd NAND2X1
X_465_ _178_ _208_ _207_ _342_[2] vdd gnd OAI21X1
X_694_ _36_ _54_ _55_ _56_ vdd gnd OAI21X1
XFILL46650x28950 gnd vdd FILL
X_559_ ADDR[2] _279_ _289_ vdd gnd NAND2X1
X_368_ _332_ _114_ _115_ vdd gnd NOR2X1
X_597_ _306_ _299_ _343_[9] vdd gnd NOR2X1
X_712_ FI_POS[1] FI_POS[0] _325_ _74_ vdd gnd NAND3X1
X_521_ _256_ _258_ _259_ vdd gnd NAND2X1
X_750_ _343_[12] RWL[12] vdd gnd BUFX2
X_615_ _345_[3] _315_ vdd gnd INVX1
X_424_ _97_ _134_ _169_ _170_ vdd gnd NOR3X1
X_653_ refw[7] _340__bF$buf0 _15_ vdd gnd NAND2X1
X_709_ FI_POS[1] _326_ _325_ _71_ vdd gnd NAND3X1
X_462_ _204_ _137_ _206_ vdd gnd AND2X2
X_518_ _255_ _254_ _230_ _256_ vdd gnd OAI21X1
X_691_ _325_ _52_ _333_ _53_ vdd gnd OAI21X1
XFILL46050x18150 gnd vdd FILL
X_747_ _343_[1] RWL[1] vdd gnd BUFX2
X_556_ _338_ _287_ vdd gnd INVX1
X_365_ _110_ _111_ _109_ _112_ vdd gnd NAND3X1
X_594_ _306_ _296_ _343_[6] vdd gnd NOR2X1
X_459_ _70_ _202_ _203_ vdd gnd NOR2X1
X_688_ _48_ _49_ _47_ _50_ vdd gnd NAND3X1
XFILL46650x14550 gnd vdd FILL
X_497_ _73_ _236_ _87_ _237_ vdd gnd AOI21X1
X_612_ _345_[2] _313_ vdd gnd INVX1
X_421_ _51_ _159_ _160_ _167_ vdd gnd NAND3X1
X_650_ _11_ _10_ _332_ _12_ vdd gnd OAI21X1
X_706_ _51_ _62_ _68_ vdd gnd NOR2X1
X_515_ _36_ _252_ _54_ _253_ vdd gnd AOI21X1
X_744_ _342_[3] DOUT[3] vdd gnd BUFX2
XFILL46050x39750 gnd vdd FILL
X_553_ ADDR[1] _284_ _278_ _285_ vdd gnd NAND3X1
X_609_ _345_[1] _311_ vdd gnd INVX1
X_782_ _346_[7] WWL[7] vdd gnd BUFX2
X_362_ _11_ _108_ _332_ _109_ vdd gnd OAI21X1
X_418_ _163_ _162_ _145_ _164_ vdd gnd AOI21X1
X_591_ _306_ _288_ _343_[3] vdd gnd NOR2X1
X_647_ _337_ _334_ _8_ _9_ vdd gnd OAI21X1
X_456_ _119_ _122_ _113_ _200_ vdd gnd AOI21X1
X_685_ _11_ _46_ _332_ _47_ vdd gnd OAI21X1
X_494_ _229_ _233_ _235_ vdd gnd OR2X2
X_779_ _346_[4] WWL[4] vdd gnd BUFX2
X_359_ _104_ _340__bF$buf3 _105_ _106_ vdd gnd OAI21X1

.ends
.end
