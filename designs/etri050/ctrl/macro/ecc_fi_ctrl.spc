.subckt ecc_fi_ctrl vdd gnd ADDR[0] ADDR[1] ADDR[2] ADDR[3] CAN[0]
+ CAN[1] CAN[2] CAN[3] CAN[4] CAN[5] CAN[6] CAN[7] CLK
+ CRD_N CSET DED_FLAG DIN[0] DIN[1] DIN[2] DIN[3] DOUT[0]
+ DOUT[1] DOUT[2] DOUT[3] FI_MODE[0] FI_MODE[1] FI_POS[0] FI_POS[1] FI_POS[2]
+ PRE_N RO_DIV RO_EN[0] RO_EN[1] RO_EN[2] RWL[0] RWL[1] RWL[2]
+ RWL[3] RWL[4] RWL[5] RWL[6] RWL[7] RWL[8] RWL[9] RWL[10]
+ RWL[11] RWL[12] RWL[13] RWL[14] SEC_FLAG SENSE[0] SENSE[1] SENSE[2]
+ SENSE[3] SENSE[4] SENSE[5] SENSE[6] SENSE[7] WD[0] WD[1] WD[2]
+ WD[3] WD[4] WD[5] WD[6] WD[7] WE WWL[0] WWL[1]
+ WWL[2] WWL[3] WWL[4] WWL[5] WWL[6] WWL[7] WWL[8] WWL[9]
+ WWL[10] WWL[11] WWL[12] WWL[13] WWL[14] 

X_588_ _193_ _192_ _196_ _197_ _198_ vdd 
+ gnd
+ AOI22X1
X_800_ _363_ _381_[5] _369_ vdd gnd NAND2X1
X_397_ _11_ _17_ _379_[4] vdd gnd NOR2X1
X_703_ _242_ _243_ _301_ _302_ vdd gnd OAI21X1
X_512_ _41_ _121_ _122_ vdd gnd NOR2X1
X_741_ _104_ _335_ _336_ vdd gnd NAND2X1
X_550_ _158_ _46__bF$buf3 _159_ _160_ vdd gnd OAI21X1
X_606_ _215_ _380_ vdd gnd INVX1
X_835_ _379_[5] RWL[5] vdd gnd BUFX2
X_415_ _11_ _29_ _379_[10] vdd gnd NOR2X1
X_644_ _113_ _114_ _179_ _178_ _247_ vdd 
+ gnd
+ OAI22X1
X_453_ FI_POS[1] _63_ vdd gnd INVX1
X_509_ FI_POS[2] _63_ _119_ vdd gnd NOR2X1
X_682_ _144_ _77_ _70_ _283_ vdd gnd MUX2X1
X_738_ _333_ _332_ _381_[3] vdd gnd NAND2X1
X_491_ refw[4] _46__bF$buf2 _100_ _101_ vdd gnd OAI21X1
X_547_ _90_ _55_ _41_ _157_ vdd gnd AOI21X1
X_776_ _360_ _17_ _382_[4] vdd gnd NOR2X1
X_585_ _102_ _108_ _195_ vdd gnd AND2X2
X_394_ ADDR[1] ADDR[0] _15_ vdd gnd NOR2X1
X_679_ _249_ _265_ _266_ _280_ vdd gnd NAND3X1
X_488_ FI_POS[2] _97_ _41_ _98_ vdd gnd AOI21X1
X_700_ _36_ _149_ _41_ _299_ vdd gnd OAI21X1
X_603_ _191_ _198_ _207_ _212_ _213_ vdd 
+ gnd
+ OAI22X1
X_832_ _379_[2] RWL[2] vdd gnd BUFX2
X_412_ _27_ _12_ _28_ vdd gnd OR2X2
X_641_ _218_ _221_ _62_ _244_ vdd gnd OAI21X1
X_450_ _58_ _46__bF$buf3 _59_ _60_ vdd gnd OAI21X1
X_506_ _102_ _108_ _87_ _95_ _116_ vdd 
+ gnd
+ AOI22X1
X_735_ _122_ _330_ _331_ vdd gnd NOR2X1
XFILL47250x3750 gnd vdd FILL
X_544_ refw[1] _46__bF$buf1 _153_ _154_ vdd gnd OAI21X1
X_773_ _360_ _362_ _382_[1] vdd gnd NOR2X1
X_829_ _379_[12] RWL[12] vdd gnd BUFX2
X_409_ ADDR[3] _373_ _15_ _26_ vdd gnd NAND3X1
X_582_ _77_ _185_ _192_ vdd gnd NAND2X1
X_638_ DIN[0] _239_ _243_ vdd gnd NOR2X1
X_391_ ADDR[1] ADDR[0] _13_ vdd gnd AND2X2
X_447_ _55_ _56_ _39_ _57_ vdd gnd OAI21X1
X_676_ _277_ _271_ _377_[1] vdd gnd NAND2X1
X_485_ _91_ _89_ _94_ _95_ vdd gnd OAI21X1
X_579_ _87_ _95_ _110_ _189_ vdd gnd NAND3X1
X_388_ CLK _10_ _11_ vdd gnd NAND2X1
X_600_ _162_ _205_ _210_ vdd gnd NAND2X1
X_503_ _69_ _76_ _62_ _113_ vdd gnd AOI21X1
X_732_ _55_ _90_ _328_ vdd gnd NAND2X1
X_541_ FI_POS[2] _82_ _39_ _151_ vdd gnd OAI21X1
X_770_ _12_ _373_ _15_ _361_ vdd gnd NAND3X1
X_826_ _379_[1] RWL[1] vdd gnd BUFX2
X_406_ _11_ _24_ _379_[6] vdd gnd NOR2X1
X_635_ _241_ _238_ _378_[0] vdd gnd NOR2X1
X_444_ _34_ _53_ _41_ _54_ vdd gnd OAI21X1
X_673_ CAN[5] CAN[1] FI_POS[0] _275_ vdd gnd MUX2X1
X_729_ _319_ _325_ _326_ vdd gnd OR2X2
X_482_ refw[5] _92_ vdd gnd INVX1
X_538_ FI_POS[1] FI_POS[2] _148_ vdd gnd NOR2X1
X_767_ _44_ _356_ DIN[3] _359_ vdd gnd OAI21X1
X_576_ _69_ _76_ _186_ vdd gnd AND2X2
X_385_ ADDR[1] _372_ _373_ _8_ vdd gnd NAND3X1
X_479_ _37_ _88_ _39_ _89_ vdd gnd AOI21X1
X_500_ _108_ _102_ _110_ vdd gnd NAND2X1
X_823_ _378_[1] RO_EN[1] vdd gnd BUFX2
X_403_ ADDR[1] ADDR[2] _372_ _22_ vdd gnd NAND3X1
X_632_ DIN[1] _239_ vdd gnd INVX1
X_861_ _382_[7] WWL[7] vdd gnd BUFX2
X_441_ refw[7] _46__bF$buf3 _50_ _51_ vdd gnd OAI21X1
X_670_ _233_ _237_ _272_ vdd gnd NOR2X1
X_726_ _320_ _321_ _323_ vdd gnd NOR2X1
X_535_ _126_ _133_ _144_ _145_ vdd gnd AOI21X1
X_764_ _355_ _232_ _350_ _356_ vdd gnd AOI21X1
X_573_ _177_ _182_ _183_ vdd gnd NAND2X1
X_629_ _236_ CLK _375_ vdd gnd AND2X2
X_858_ _382_[4] WWL[4] vdd gnd BUFX2
X_438_ ADDR[1] ADDR[0] _48_ vdd gnd NAND2X1
X_667_ _118_ _183_ _249_ _269_ vdd gnd NOR3X1
X_476_ refw[5] _46__bF$buf2 _85_ _86_ vdd gnd OAI21X1
X_799_ _105_ _363_ _368_ _4_ vdd gnd OAI21X1
X_820_ _377_[3] DOUT[3] vdd gnd BUFX2
X_400_ _19_ _20_ vdd gnd INVX1
X_723_ DIN[0] DIN[2] _320_ vdd gnd NOR2X1
X_532_ _140_ _46__bF$buf0 _141_ _142_ vdd gnd OAI21X1
X_761_ _353_ _352_ _381_[6] vdd gnd NAND2X1
X_817_ _377_[0] DOUT[0] vdd gnd BUFX2
X_570_ _155_ _161_ _174_ _180_ vdd gnd AOI21X1
X_626_ WE _233_ _234_ vdd gnd NOR2X1
X_855_ _382_[14] WWL[14] vdd gnd BUFX2
X_435_ ADDR[3] ADDR[2] _45_ vdd gnd AND2X2
X_664_ _207_ _212_ _266_ vdd gnd NOR2X1
X_473_ _55_ _82_ _39_ _83_ vdd gnd OAI21X1
X_529_ FI_POS[2] _71_ _39_ _139_ vdd gnd OAI21X1
X_758_ _350_ _349_ _72_ _351_ vdd gnd OAI21X1
X_567_ _145_ _147_ _176_ _175_ _177_ vdd 
+ gnd
+ OAI22X1
X_796_ _363_ _381_[3] _367_ vdd gnd NAND2X1
X_699_ _297_ _233_ _298_ vdd gnd NOR2X1
X_720_ _36_ _127_ _41_ _317_ vdd gnd OAI21X1
XFILL46950x10950 gnd vdd FILL
X_814_ _374_ CRD_N vdd gnd BUFX2
X_623_ _231_ _376_ vdd gnd INVX1
X_852_ _382_[11] WWL[11] vdd gnd BUFX2
X_432_ FI_POS[0] FI_POS[1] FI_POS[2] _42_ vdd gnd NAND3X1
X_661_ RO_DIV _238_ _232_ _264_ vdd gnd OAI21X1
X_717_ _313_ _309_ _315_ vdd gnd OR2X2
X_470_ FI_POS[2] _63_ _80_ vdd gnd NAND2X1
X_526_ _48_ _49_ _135_ _136_ vdd gnd OAI21X1
X_755_ _348_ _347_ _381_[5] vdd gnd NAND2X1
X_564_ _168_ _173_ _174_ vdd gnd NAND2X1
XFILL47250x10950 gnd vdd FILL
X_793_ _158_ _363_ _365_ _1_ vdd gnd OAI21X1
X_849_ _382_[0] WWL[0] vdd gnd BUFX2
X_429_ FI_MODE[1] _38_ _39_ vdd gnd NOR2X1
X_658_ _260_ _255_ _261_ vdd gnd NAND2X1
X_467_ _76_ _69_ _77_ vdd gnd NAND2X1
X_696_ _272_ _295_ _292_ _296_ vdd gnd NAND3X1
X_599_ _199_ _201_ _209_ vdd gnd NAND2X1
X_811_ _5_ CLK refw[5] vdd gnd DFFPOSX1
X_620_ _228_ _227_ _229_ vdd gnd NAND2X1
X_714_ DIN[3] _303_ _312_ vdd gnd NAND2X1
X_523_ _128_ _129_ _132_ _133_ vdd gnd NAND3X1
X_752_ _39_ _345_ _83_ _346_ vdd gnd OAI21X1
X_808_ _2_ CLK refw[2] vdd gnd DFFPOSX1
X_561_ _48_ _49_ SENSE[0] _171_ vdd gnd OAI21X1
X_617_ _225_ _222_ _226_ vdd gnd NAND2X1
X_790_ _363_ _381_[0] _364_ vdd gnd NAND2X1
X_846_ _381_[5] WD[5] vdd gnd BUFX2
X_426_ FI_MODE[1] _36_ vdd gnd INVX2
X_655_ CAN[0] _258_ vdd gnd INVX1
X_464_ _48_ _49_ SENSE[6] _74_ vdd gnd OAI21X1
X_693_ FI_POS[0] CAN[3] _293_ vdd gnd NOR2X1
X_749_ _342_ _336_ _344_ vdd gnd OR2X2
X_558_ _164_ _150_ _167_ _168_ vdd gnd NAND3X1
X_787_ _11_ _361_ _379_[0] vdd gnd NOR2X1
X_596_ _205_ _204_ _206_ vdd gnd NAND2X1
XBUFX2_insert0 _46_ _46__bF$buf3 vdd gnd BUFX2
XBUFX2_insert1 _46_ _46__bF$buf2 vdd gnd BUFX2
XBUFX2_insert2 _46_ _46__bF$buf1 vdd gnd BUFX2
XBUFX2_insert3 _46_ _46__bF$buf0 vdd gnd BUFX2
X_499_ _102_ _108_ _96_ _109_ vdd gnd AOI21X1
X_711_ _299_ _308_ _151_ _309_ vdd gnd OAI21X1
X_520_ refw[3] _130_ vdd gnd INVX1
X_805_ _58_ _363_ _371_ _7_ vdd gnd OAI21X1
X_614_ _194_ _219_ _220_ _223_ vdd gnd NAND3X1
X_843_ _381_[2] WD[2] vdd gnd BUFX2
X_423_ _11_ _33_ _379_[14] vdd gnd NOR2X1
X_652_ _374_ _255_ vdd gnd INVX2
XFILL46950x39750 gnd vdd FILL
X_708_ _300_ _305_ _307_ vdd gnd OR2X2
X_461_ FI_POS[1] _70_ _71_ vdd gnd NAND2X1
X_517_ FI_POS[1] _55_ _127_ vdd gnd NAND2X1
X_690_ _185_ _289_ _280_ _290_ vdd gnd MUX2X1
X_746_ DIN[3] _340_ _341_ vdd gnd NAND2X1
X_555_ SENSE[0] _165_ vdd gnd INVX1
X_784_ _360_ _31_ _382_[12] vdd gnd NOR2X1
X_593_ _174_ _162_ _203_ vdd gnd NAND2X1
X_649_ _229_ _213_ _252_ vdd gnd NOR2X1
X_458_ refw[6] _46__bF$buf3 _67_ _68_ vdd gnd OAI21X1
XFILL47250x39750 gnd vdd FILL
X_687_ _255_ _283_ _287_ _288_ vdd gnd OAI21X1
X_496_ _48_ _49_ SENSE[4] _106_ vdd gnd OAI21X1
X_802_ _363_ _381_[6] _370_ vdd gnd NAND2X1
X_399_ ADDR[0] ADDR[2] _18_ _19_ vdd gnd NAND3X1
X_611_ _204_ _201_ _220_ vdd gnd NAND2X1
X_840_ _380_ SEC_FLAG vdd gnd BUFX2
X_420_ ADDR[3] _20_ _32_ vdd gnd NAND2X1
X_705_ DIN[2] _303_ _304_ vdd gnd NAND2X1
X_514_ _48_ _49_ _123_ _124_ vdd gnd OAI21X1
X_743_ _239_ _301_ _338_ vdd gnd NOR2X1
X_552_ _155_ _161_ _162_ vdd gnd NAND2X1
X_608_ _162_ _201_ _217_ vdd gnd NAND2X1
X_781_ _360_ _28_ _382_[9] vdd gnd NOR2X1
X_837_ _379_[7] RWL[7] vdd gnd BUFX2
X_417_ _11_ _30_ _379_[11] vdd gnd NOR2X1
X_590_ _146_ _199_ _200_ vdd gnd NAND2X1
X_646_ _248_ _247_ _249_ vdd gnd NAND2X1
X_455_ _64_ FI_POS[2] _41_ _65_ vdd gnd AOI21X1
X_684_ CAN[6] _70_ _285_ vdd gnd NOR2X1
X_493_ FI_POS[2] _97_ _103_ vdd gnd NAND2X1
X_549_ _48_ _49_ SENSE[1] _159_ vdd gnd OAI21X1
X_778_ _360_ _24_ _382_[6] vdd gnd NOR2X1
X_587_ _116_ _197_ vdd gnd INVX1
X_396_ _16_ ADDR[3] _17_ vdd gnd OR2X2
X_702_ DIN[2] _301_ vdd gnd INVX1
X_511_ FI_POS[2] _56_ _121_ vdd gnd NOR2X1
X_740_ _233_ _334_ _89_ _335_ vdd gnd OAI21X1
X_605_ _214_ _184_ _215_ vdd gnd NOR2X1
X_834_ _379_[4] RWL[4] vdd gnd BUFX2
X_414_ _8_ _12_ _29_ vdd gnd OR2X2
X_643_ _245_ _244_ _246_ vdd gnd NAND2X1
XFILL46950x46950 gnd vdd FILL
X_452_ _61_ _52_ _62_ vdd gnd NAND2X1
X_508_ _112_ _117_ _118_ vdd gnd NAND2X1
X_681_ _281_ _279_ _233_ _282_ vdd gnd OAI21X1
X_737_ _122_ _330_ DIN[0] _333_ vdd gnd OAI21X1
X_490_ _48_ _49_ _99_ _100_ vdd gnd OAI21X1
X_546_ _37_ _148_ _39_ _156_ vdd gnd AOI21X1
X_775_ _360_ _14_ _382_[3] vdd gnd NOR2X1
X_584_ _95_ _87_ _194_ vdd gnd AND2X2
X_393_ _11_ _14_ _379_[3] vdd gnd NOR2X1
XFILL47250x46950 gnd vdd FILL
X_449_ _48_ _49_ SENSE[7] _59_ vdd gnd OAI21X1
X_678_ _278_ _246_ _77_ _279_ vdd gnd AOI21X1
X_487_ FI_POS[0] FI_POS[1] _97_ vdd gnd NOR2X1
X_602_ _211_ _210_ _208_ _209_ _212_ vdd 
+ gnd
+ AOI22X1
X_831_ _379_[14] RWL[14] vdd gnd BUFX2
X_411_ ADDR[0] _18_ _373_ _27_ vdd gnd NAND3X1
X_640_ _88_ _119_ _234_ _374_ vdd gnd OAI21X1
X_505_ _110_ _96_ _115_ vdd gnd NOR2X1
X_734_ _329_ _232_ _317_ _330_ vdd gnd AOI21X1
X_543_ _48_ _49_ _152_ _153_ vdd gnd OAI21X1
X_772_ _27_ ADDR[3] _362_ vdd gnd OR2X2
X_828_ _379_[11] RWL[11] vdd gnd BUFX2
X_408_ _11_ _25_ _379_[7] vdd gnd NOR2X1
X_581_ _189_ _190_ _187_ _188_ _191_ vdd 
+ gnd
+ AOI22X1
X_637_ _237_ _242_ _378_[1] vdd gnd AND2X2
X_390_ ADDR[3] _12_ vdd gnd INVX2
X_446_ FI_POS[0] FI_POS[1] _56_ vdd gnd NAND2X1
X_675_ _272_ _276_ _277_ vdd gnd NAND2X1
X_484_ _92_ _46__bF$buf2 _93_ _94_ vdd gnd OAI21X1
X_769_ CLK WE _360_ vdd gnd NAND2X1
X_578_ _79_ _188_ vdd gnd INVX1
XFILL47250x32550 gnd vdd FILL
X_387_ WE _10_ vdd gnd INVX1
X_502_ _111_ _109_ _79_ _78_ _112_ vdd 
+ gnd
+ OAI22X1
X_731_ _327_ _326_ _381_[2] vdd gnd NAND2X1
X_540_ _53_ _149_ _41_ _150_ vdd gnd OAI21X1
X_825_ _379_[0] RWL[0] vdd gnd BUFX2
X_405_ _12_ _23_ _24_ vdd gnd NAND2X1
X_634_ _239_ _240_ _241_ vdd gnd NAND2X1
X_863_ _382_[9] WWL[9] vdd gnd BUFX2
X_443_ FI_MODE[1] _38_ _53_ vdd gnd NAND2X1
X_672_ FI_POS[0] _162_ _273_ _274_ vdd gnd OAI21X1
X_728_ _322_ _324_ _325_ vdd gnd NAND2X1
X_481_ _90_ FI_POS[2] _41_ _91_ vdd gnd AOI21X1
X_537_ _138_ _143_ _146_ _147_ vdd gnd AOI21X1
XFILL47250x150 gnd vdd FILL
X_766_ _310_ _357_ _358_ vdd gnd NAND2X1
X_575_ _52_ _61_ _185_ vdd gnd AND2X2
X_384_ ADDR[2] _373_ vdd gnd INVX2
X_669_ _268_ _270_ _233_ _271_ vdd gnd OAI21X1
X_478_ FI_POS[1] _55_ _88_ vdd gnd NOR2X1
X_822_ _378_[0] RO_EN[0] vdd gnd BUFX2
X_402_ _11_ _21_ _379_[5] vdd gnd NOR2X1
X_631_ _237_ _238_ vdd gnd INVX1
X_860_ _382_[6] WWL[6] vdd gnd BUFX2
X_440_ _48_ _49_ _47_ _50_ vdd gnd OAI21X1
X_725_ _320_ _321_ _310_ _322_ vdd gnd OAI21X1
X_534_ _143_ _138_ _144_ vdd gnd NAND2X1
X_763_ _354_ _355_ vdd gnd INVX1
X_819_ _377_[2] DOUT[2] vdd gnd BUFX2
X_572_ _180_ _181_ _179_ _178_ _182_ vdd 
+ gnd
+ OAI22X1
X_628_ _80_ _235_ _236_ vdd gnd NOR2X1
X_857_ _382_[3] WWL[3] vdd gnd BUFX2
X_437_ SENSE[7] _47_ vdd gnd INVX1
X_666_ _96_ _246_ _267_ _268_ vdd gnd NOR3X1
X_475_ _48_ _49_ _84_ _85_ vdd gnd OAI21X1
X_569_ _144_ _146_ _179_ vdd gnd NOR2X1
X_798_ _363_ _381_[4] _368_ vdd gnd NAND2X1
X_722_ _318_ _319_ vdd gnd INVX1
X_531_ _48_ _49_ SENSE[2] _141_ vdd gnd OAI21X1
X_760_ DIN[2] _351_ _353_ vdd gnd NAND2X1
X_816_ _376_ DED_FLAG vdd gnd BUFX2
X_625_ _232_ _233_ vdd gnd INVX2
XFILL46650x39750 gnd vdd FILL
X_854_ _382_[13] WWL[13] vdd gnd BUFX2
X_434_ _41_ _43_ _44_ vdd gnd NOR2X1
X_663_ _191_ _198_ _265_ vdd gnd NOR2X1
X_719_ _163_ _233_ _316_ vdd gnd NOR2X1
X_472_ FI_POS[0] _63_ _82_ vdd gnd NAND2X1
X_528_ _134_ _120_ _137_ _138_ vdd gnd OAI21X1
X_757_ _36_ _34_ _41_ _350_ vdd gnd OAI21X1
X_566_ _174_ _162_ _176_ vdd gnd NOR2X1
X_795_ _140_ _363_ _366_ _2_ vdd gnd OAI21X1
X_469_ _52_ _61_ _69_ _76_ _79_ vdd 
+ gnd
+ AOI22X1
X_698_ _55_ _64_ _297_ vdd gnd NAND2X1
X_813_ _7_ CLK refw[7] vdd gnd DFFPOSX1
X_622_ _226_ _230_ _215_ _231_ vdd gnd OAI21X1
X_851_ _382_[10] WWL[10] vdd gnd BUFX2
X_431_ FI_MODE[0] _36_ _41_ vdd gnd NAND2X1
X_660_ _237_ _262_ _263_ vdd gnd NOR2X1
X_716_ _309_ _313_ _314_ vdd gnd NAND2X1
X_525_ SENSE[2] _135_ vdd gnd INVX1
X_754_ DIN[1] _346_ _348_ vdd gnd NAND2X1
X_563_ _169_ _156_ _172_ _173_ vdd gnd OAI21X1
X_619_ _113_ _114_ _145_ _147_ _228_ vdd 
+ gnd
+ OAI22X1
X_792_ _363_ _381_[1] _365_ vdd gnd NAND2X1
X_848_ _381_[7] WD[7] vdd gnd BUFX2
X_428_ FI_MODE[0] _38_ vdd gnd INVX1
X_657_ FI_POS[0] _258_ _259_ _260_ vdd gnd OAI21X1
X_466_ _54_ _72_ _75_ _76_ vdd gnd NAND3X1
X_695_ _293_ _294_ _255_ _295_ vdd gnd OAI21X1
X_789_ _10_ _46__bF$buf2 _363_ vdd gnd NOR2X1
X_598_ _144_ _146_ _208_ vdd gnd NAND2X1
X_810_ _4_ CLK refw[4] vdd gnd DFFPOSX1
X_713_ _242_ _243_ _310_ _311_ vdd gnd OAI21X1
X_522_ _130_ _46__bF$buf1 _131_ _132_ vdd gnd OAI21X1
X_751_ _36_ _80_ _42_ _233_ _345_ vdd 
+ gnd
+ OAI22X1
X_807_ _1_ CLK refw[1] vdd gnd DFFPOSX1
X_560_ refw[0] _170_ vdd gnd INVX1
X_616_ _62_ _223_ _224_ _225_ vdd gnd NAND3X1
XFILL46650x46950 gnd vdd FILL
X_845_ _381_[4] WD[4] vdd gnd BUFX2
X_425_ _34_ _35_ vdd gnd INVX1
X_654_ FI_POS[0] _174_ _256_ _257_ vdd gnd OAI21X1
X_463_ refw[6] _73_ vdd gnd INVX1
X_519_ FI_POS[2] _56_ _39_ _129_ vdd gnd OAI21X1
X_692_ _70_ _62_ _291_ _292_ vdd gnd OAI21X1
X_748_ _336_ _342_ _343_ vdd gnd NAND2X1
X_557_ refw[0] _46__bF$buf0 _166_ _167_ vdd gnd OAI21X1
X_786_ _360_ _33_ _382_[14] vdd gnd NOR2X1
X_595_ _173_ _168_ _205_ vdd gnd AND2X2
X_689_ _218_ _221_ _289_ vdd gnd NOR2X1
X_498_ _81_ _104_ _107_ _108_ vdd gnd NAND3X1
X_710_ _121_ _232_ _308_ vdd gnd AND2X2
X_804_ _363_ _381_[7] _371_ vdd gnd NAND2X1
X_613_ _218_ _221_ _185_ _222_ vdd gnd OAI21X1
X_842_ _381_[1] WD[1] vdd gnd BUFX2
X_422_ ADDR[3] _23_ _33_ vdd gnd NAND2X1
X_651_ _253_ _251_ _233_ _254_ vdd gnd OAI21X1
X_707_ _305_ _300_ _306_ vdd gnd NAND2X1
X_460_ FI_POS[0] _70_ vdd gnd INVX2
X_516_ _120_ _122_ _125_ _126_ vdd gnd OAI21X1
X_745_ _337_ _338_ _340_ vdd gnd NOR2X1
X_554_ _39_ _163_ _164_ vdd gnd NAND2X1
X_783_ _360_ _30_ _382_[11] vdd gnd NOR2X1
X_839_ _379_[9] RWL[9] vdd gnd BUFX2
X_419_ _11_ _31_ _379_[12] vdd gnd NOR2X1
X_592_ _144_ _201_ _202_ vdd gnd NAND2X1
X_648_ _201_ _250_ _246_ _251_ vdd gnd NOR3X1
X_457_ _48_ _49_ _66_ _67_ vdd gnd OAI21X1
X_686_ _272_ _286_ _287_ vdd gnd AND2X2
X_495_ refw[4] _105_ vdd gnd INVX1
X_589_ _138_ _143_ _199_ vdd gnd AND2X2
X_801_ _92_ _363_ _369_ _5_ vdd gnd OAI21X1
X_398_ ADDR[1] _18_ vdd gnd INVX1
X_610_ _162_ _146_ _219_ vdd gnd NAND2X1
X_704_ _242_ _243_ _303_ vdd gnd NOR2X1
X_513_ SENSE[3] _123_ vdd gnd INVX1
X_742_ DIN[1] DIN[2] _337_ vdd gnd NOR2X1
X_551_ _156_ _157_ _160_ _161_ vdd gnd OAI21X1
X_607_ _146_ _204_ _216_ vdd gnd NAND2X1
X_780_ _360_ _26_ _382_[8] vdd gnd NOR2X1
X_836_ _379_[6] RWL[6] vdd gnd BUFX2
X_416_ ADDR[3] _373_ _13_ _30_ vdd gnd NAND3X1
X_645_ _145_ _147_ _78_ _79_ _248_ vdd 
+ gnd
+ OAI22X1
X_454_ FI_POS[0] _63_ _64_ vdd gnd NOR2X1
X_683_ FI_POS[0] CAN[2] _284_ vdd gnd NOR2X1
X_739_ _70_ _63_ FI_POS[2] _334_ vdd gnd OAI21X1
X_492_ _98_ _89_ _101_ _102_ vdd gnd OAI21X1
X_548_ refw[1] _158_ vdd gnd INVX1
X_777_ _360_ _21_ _382_[5] vdd gnd NOR2X1
X_586_ _195_ _194_ _196_ vdd gnd NAND2X1
X_395_ ADDR[2] _15_ _16_ vdd gnd NAND2X1
X_489_ SENSE[4] _99_ vdd gnd INVX1
X_701_ _299_ _298_ _164_ _300_ vdd gnd OAI21X1
X_510_ _37_ _119_ _39_ _120_ vdd gnd AOI21X1
XFILL47250x28950 gnd vdd FILL
X_604_ _213_ _214_ vdd gnd INVX1
X_833_ _379_[3] RWL[3] vdd gnd BUFX2
X_413_ _11_ _28_ _379_[9] vdd gnd NOR2X1
X_642_ _185_ _223_ _224_ _245_ vdd gnd NAND3X1
X_451_ _54_ _57_ _60_ _61_ vdd gnd NAND3X1
X_507_ _113_ _114_ _116_ _115_ _117_ vdd 
+ gnd
+ OAI22X1
X_680_ _186_ _226_ _280_ _281_ vdd gnd NOR3X1
X_736_ _240_ _331_ _332_ vdd gnd NAND2X1
X_545_ _151_ _150_ _154_ _155_ vdd gnd NAND3X1
X_774_ _360_ _9_ _382_[2] vdd gnd NOR2X1
X_583_ _62_ _186_ _193_ vdd gnd NAND2X1
X_639_ _237_ _243_ _378_[2] vdd gnd AND2X2
X_392_ _12_ _373_ _13_ _14_ vdd gnd NAND3X1
X_448_ refw[7] _58_ vdd gnd INVX1
X_677_ _118_ _183_ _229_ _278_ vdd gnd NOR3X1
X_486_ _87_ _95_ _96_ vdd gnd NAND2X1
X_389_ _11_ _9_ _379_[2] vdd gnd NOR2X1
X_601_ _174_ _204_ _211_ vdd gnd NAND2X1
X_830_ _379_[13] RWL[13] vdd gnd BUFX2
X_410_ _11_ _26_ _379_[8] vdd gnd NOR2X1
X_504_ _52_ _61_ _77_ _114_ vdd gnd AOI21X1
X_733_ _328_ _329_ vdd gnd INVX1
X_542_ SENSE[1] _152_ vdd gnd INVX1
X_771_ _360_ _361_ _382_[0] vdd gnd NOR2X1
X_827_ _379_[10] RWL[10] vdd gnd BUFX2
X_407_ _12_ ADDR[2] _13_ _25_ vdd gnd NAND3X1
X_580_ _102_ _108_ _96_ _190_ vdd gnd NAND3X1
X_636_ DIN[1] _240_ _242_ vdd gnd NOR2X1
X_445_ FI_POS[2] _55_ vdd gnd INVX2
X_674_ _274_ _275_ _374_ _276_ vdd gnd MUX2X1
X_483_ _48_ _49_ SENSE[5] _93_ vdd gnd OAI21X1
X_539_ _148_ _149_ vdd gnd INVX1
X_768_ _359_ _358_ _381_[7] vdd gnd NAND2X1
X_577_ _185_ _186_ _187_ vdd gnd NAND2X1
X_386_ _8_ ADDR[3] _9_ vdd gnd OR2X2
X_501_ _87_ _95_ _110_ _111_ vdd gnd AOI21X1
X_730_ _325_ _319_ _327_ vdd gnd NAND2X1
X_824_ _378_[2] RO_EN[2] vdd gnd BUFX2
X_404_ _22_ _23_ vdd gnd INVX1
X_633_ DIN[0] _240_ vdd gnd INVX1
X_862_ _382_[8] WWL[8] vdd gnd BUFX2
X_442_ _44_ _40_ _51_ _52_ vdd gnd OAI21X1
X_671_ FI_POS[0] _194_ _273_ vdd gnd NAND2X1
X_727_ DIN[3] _323_ _324_ vdd gnd NAND2X1
X_480_ FI_POS[1] _70_ _90_ vdd gnd NOR2X1
X_536_ _133_ _126_ _146_ vdd gnd NAND2X1
X_765_ _44_ _356_ _357_ vdd gnd NOR2X1
X_574_ _118_ _183_ _184_ vdd gnd NOR2X1
X_383_ ADDR[0] _372_ vdd gnd INVX1
X_859_ _382_[5] WWL[5] vdd gnd BUFX2
X_439_ ADDR[3] ADDR[2] _49_ vdd gnd NAND2X1
X_668_ _269_ _226_ _194_ _270_ vdd gnd AOI21X1
X_477_ _81_ _83_ _86_ _87_ vdd gnd NAND3X1
X_821_ CLK PRE_N vdd gnd BUFX2
X_401_ _12_ _20_ _21_ vdd gnd NAND2X1
X_630_ _34_ _235_ _237_ vdd gnd NOR2X1
X_724_ _240_ _301_ _321_ vdd gnd NOR2X1
X_533_ _128_ _139_ _142_ _143_ vdd gnd NAND3X1
XFILL46350x46950 gnd vdd FILL
X_762_ FI_POS[2] _90_ _354_ vdd gnd NAND2X1
X_818_ _377_[1] DOUT[1] vdd gnd BUFX2
X_571_ _168_ _173_ _162_ _181_ vdd gnd AOI21X1
X_627_ _234_ _235_ vdd gnd INVX1
X_856_ _382_[2] WWL[2] vdd gnd BUFX2
X_436_ _13_ _45_ _46_ vdd gnd NAND2X1
X_665_ _229_ _265_ _266_ _267_ vdd gnd NAND3X1
X_474_ SENSE[5] _84_ vdd gnd INVX1
X_759_ _351_ DIN[2] _352_ vdd gnd OR2X2
X_568_ _146_ _144_ _178_ vdd gnd AND2X2
X_797_ _130_ _363_ _367_ _3_ vdd gnd OAI21X1
X_721_ _317_ _316_ _139_ _318_ vdd gnd OAI21X1
X_530_ refw[2] _140_ vdd gnd INVX1
X_815_ _375_ CSET vdd gnd BUFX2
X_624_ _38_ _36_ _232_ vdd gnd NOR2X1
X_853_ _382_[12] WWL[12] vdd gnd BUFX2
X_433_ _42_ _43_ vdd gnd INVX1
X_662_ _263_ _264_ _254_ _377_[0] vdd gnd OAI21X1
X_718_ _314_ _315_ _381_[1] vdd gnd NAND2X1
X_471_ _53_ _80_ _41_ _81_ vdd gnd OAI21X1
X_527_ refw[2] _46__bF$buf0 _136_ _137_ vdd gnd OAI21X1
X_756_ _103_ _233_ _349_ vdd gnd NOR2X1
X_565_ _162_ _174_ _175_ vdd gnd AND2X2
X_794_ _363_ _381_[2] _366_ vdd gnd NAND2X1
X_659_ _255_ _257_ _261_ _262_ vdd gnd OAI21X1
X_468_ _62_ _77_ _78_ vdd gnd NOR2X1
X_697_ _232_ _290_ _296_ _377_[3] vdd gnd OAI21X1
X_812_ _6_ CLK refw[6] vdd gnd DFFPOSX1
X_621_ _191_ _198_ _229_ _230_ vdd gnd OAI21X1
X_850_ _382_[1] WWL[1] vdd gnd BUFX2
X_430_ _37_ _35_ _39_ _40_ vdd gnd AOI21X1
X_715_ _311_ _312_ _313_ vdd gnd NAND2X1
X_524_ _64_ _55_ _41_ _134_ vdd gnd AOI21X1
X_753_ _346_ DIN[1] _347_ vdd gnd OR2X2
X_809_ _3_ CLK refw[3] vdd gnd DFFPOSX1
X_562_ _170_ _46__bF$buf1 _171_ _172_ vdd gnd OAI21X1
X_618_ _79_ _78_ _179_ _178_ _227_ vdd 
+ gnd
+ OAI22X1
X_791_ _170_ _363_ _364_ _0_ vdd gnd OAI21X1
X_847_ _381_[6] WD[6] vdd gnd BUFX2
X_427_ FI_MODE[0] _36_ _37_ vdd gnd NOR2X1
X_656_ FI_POS[0] CAN[4] _259_ vdd gnd NAND2X1
X_465_ _73_ _46__bF$buf3 _74_ _75_ vdd gnd OAI21X1
X_694_ CAN[7] _70_ _294_ vdd gnd NOR2X1
X_559_ _55_ _97_ _41_ _169_ vdd gnd AOI21X1
X_788_ _11_ _362_ _379_[1] vdd gnd NOR2X1
X_597_ _206_ _203_ _200_ _202_ _207_ vdd 
+ gnd
+ AOI22X1
X_712_ DIN[3] _310_ vdd gnd INVX1
X_521_ _48_ _49_ SENSE[3] _131_ vdd gnd OAI21X1
X_750_ _343_ _344_ _381_[4] vdd gnd NAND2X1
X_806_ _0_ CLK refw[0] vdd gnd DFFPOSX1
X_615_ _96_ _216_ _217_ _224_ vdd gnd NAND3X1
X_844_ _381_[3] WD[3] vdd gnd BUFX2
X_424_ FI_POS[1] FI_POS[2] _34_ vdd gnd NAND2X1
X_653_ FI_POS[0] _146_ _256_ vdd gnd NAND2X1
X_709_ _306_ _307_ _381_[0] vdd gnd NAND2X1
X_462_ _55_ _71_ _39_ _72_ vdd gnd OAI21X1
X_518_ _53_ _127_ _41_ _128_ vdd gnd OAI21X1
XFILL47250x36150 gnd vdd FILL
X_691_ _195_ _70_ _255_ _291_ vdd gnd AOI21X1
X_747_ _341_ _339_ _342_ vdd gnd AND2X2
X_556_ _48_ _49_ _165_ _166_ vdd gnd OAI21X1
X_785_ _360_ _32_ _382_[13] vdd gnd NOR2X1
X_594_ _161_ _155_ _204_ vdd gnd AND2X2
X_459_ _40_ _65_ _68_ _69_ vdd gnd OAI21X1
X_688_ _288_ _282_ _377_[2] vdd gnd NAND2X1
X_497_ _105_ _46__bF$buf0 _106_ _107_ vdd gnd OAI21X1
X_803_ _73_ _363_ _370_ _6_ vdd gnd OAI21X1
X_612_ _220_ _219_ _194_ _221_ vdd gnd AOI21X1
X_841_ _381_[0] WD[0] vdd gnd BUFX2
X_421_ _11_ _32_ _379_[13] vdd gnd NOR2X1
X_650_ _252_ _226_ _146_ _253_ vdd gnd AOI21X1
X_706_ _302_ _304_ _305_ vdd gnd NAND2X1
X_515_ refw[3] _46__bF$buf1 _124_ _125_ vdd gnd OAI21X1
X_744_ _337_ _338_ _310_ _339_ vdd gnd OAI21X1
X_553_ _55_ _97_ _163_ vdd gnd NAND2X1
X_609_ _217_ _216_ _96_ _218_ vdd gnd AOI21X1
X_782_ _360_ _29_ _382_[10] vdd gnd NOR2X1
X_838_ _379_[8] RWL[8] vdd gnd BUFX2
X_418_ _16_ _12_ _31_ vdd gnd OR2X2
X_591_ _126_ _133_ _201_ vdd gnd AND2X2
X_647_ _118_ _183_ _249_ _250_ vdd gnd NAND3X1
X_456_ SENSE[6] _66_ vdd gnd INVX1
X_685_ _284_ _285_ _255_ _286_ vdd gnd OAI21X1
X_494_ _39_ _103_ _104_ vdd gnd NAND2X1
X_779_ _360_ _25_ _382_[7] vdd gnd NOR2X1

.ends
.end
