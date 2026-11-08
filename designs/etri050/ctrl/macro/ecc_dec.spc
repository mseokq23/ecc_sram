.subckt ecc_dec vdd gnd DED_FLAG DOUT[0] DOUT[1] DOUT[2] DOUT[3]
+ HALF R[0] R[1] R[2] R[3] R[4] R[5] R[6]
+ R[7] SEC_FLAG VIEW V_DIR 

X_321_ _30_ _46_ _177_ _142_ _47_ vdd 
+ gnd
+ OAI22X1
X_224_ R[7] _138_ _139_ vdd gnd NAND2X1
X_262_ _175_ _174_ _177_ vdd gnd NOR2X1
X_318_ _169_ _43_ _41_ _44_ vdd gnd NAND3X1
X_356_ _107_ _57_ _159_ _80_ vdd gnd NAND3X1
X_259_ R[3] HALF _174_ vdd gnd AND2X2
X_297_ _22_ _23_ vdd gnd INVX1
X_221_ _107_ _135_ _136_ vdd gnd NAND2X1
X_315_ _40_ _38_ _41_ vdd gnd NAND2X1
X_353_ _71_ _77_ _190_[1] vdd gnd NAND2X1
X_218_ R[2] _133_ vdd gnd INVX1
X_391_ _190_[3] DOUT[3] vdd gnd BUFX2
X_256_ _98_ _163_ _171_ vdd gnd NOR2X1
X_294_ R[2] _163_ _20_ vdd gnd NAND2X1
X_388_ _190_[0] DOUT[0] vdd gnd BUFX2
X_197_ _110_ _111_ _112_ vdd gnd NAND2X1
X_312_ _18_ _37_ _24_ _38_ vdd gnd NAND3X1
X_350_ _74_ _75_ vdd gnd INVX1
X_215_ R[7] _129_ _130_ vdd gnd NAND2X1
X_253_ R[3] HALF _168_ vdd gnd OR2X2
X_309_ _27_ _33_ _35_ vdd gnd OR2X2
X_291_ _16_ _13_ _173_ _17_ vdd gnd AOI21X1
X_347_ _4_ _43_ _41_ _72_ vdd gnd NAND3X1
X_385_ V_DIR _159_ _109_ vdd gnd NAND2X1
X_194_ R[6] _107_ vdd gnd INVX1
X_288_ _5_ _14_ vdd gnd INVX1
X_212_ _110_ _125_ _127_ vdd gnd NAND2X1
X_250_ R[3] HALF _165_ vdd gnd NAND2X1
X_306_ _164_ _31_ _32_ vdd gnd NAND2X1
X_344_ _68_ _67_ VIEW _69_ vdd gnd AOI21X1
X_209_ R[1] R[3] _124_ vdd gnd NAND2X1
X_382_ _159_ _59_ _41_ _43_ _106_ vdd 
+ gnd
+ AOI22X1
X_247_ VIEW _162_ vdd gnd INVX1
X_285_ _9_ _10_ _11_ vdd gnd NAND2X1
XFILL43350x14550 gnd vdd FILL
X_379_ _101_ _103_ V_DIR _104_ vdd gnd OAI21X1
X_303_ HALF _121_ _29_ vdd gnd NAND2X1
X_341_ _65_ _159_ _66_ vdd gnd NAND2X1
X_206_ R[1] _121_ vdd gnd INVX1
X_244_ _156_ _159_ vdd gnd INVX2
X_282_ _7_ _6_ _3_ _8_ vdd gnd OAI21X1
X_338_ _63_ _62_ V_DIR _64_ vdd gnd OAI21X1
X_376_ _100_ _99_ R[7] _101_ vdd gnd AOI21X1
X_279_ _182_ _4_ _188_ _5_ vdd gnd NAND3X1
X_300_ _172_ _25_ _13_ _26_ vdd gnd OAI21X1
X_203_ _117_ _98_ _118_ vdd gnd OR2X2
X_241_ _155_ _154_ _156_ vdd gnd NAND2X1
X_335_ R[3] _60_ _44_ _61_ vdd gnd NAND3X1
X_373_ _96_ _94_ _88_ _97_ vdd gnd OAI21X1
X_238_ _152_ _148_ _153_ vdd gnd NAND2X1
X_276_ _1_ _2_ vdd gnd INVX1
X_200_ _114_ _107_ _115_ vdd gnd OR2X2
X_332_ _173_ _56_ _57_ _181_ _58_ vdd 
+ gnd
+ AOI22X1
X_370_ _93_ _92_ VIEW _94_ vdd gnd AOI21X1
X_235_ R[1] R[0] _150_ vdd gnd NAND2X1
X_273_ _185_ _186_ _187_ _188_ vdd gnd OAI21X1
X_329_ _53_ _54_ _55_ vdd gnd NAND2X1
X_367_ _56_ _159_ _91_ vdd gnd NAND2X1
X_232_ R[1] _146_ _147_ vdd gnd NOR2X1
X_270_ _168_ _165_ _183_ _184_ _185_ vdd 
+ gnd
+ AOI22X1
X_326_ _47_ _51_ _120_ _52_ vdd gnd OAI21X1
X_364_ _84_ _85_ R[6] _89_ vdd gnd AOI21X1
X_229_ _120_ _143_ _144_ vdd gnd NAND2X1
X_267_ _176_ _181_ _178_ _182_ vdd gnd NAND3X1
X_323_ _141_ _48_ _49_ vdd gnd NAND2X1
X_361_ _159_ _57_ _59_ _85_ vdd gnd NAND3X1
X_226_ _139_ _140_ _141_ vdd gnd AND2X2
X_264_ _107_ _163_ _179_ vdd gnd NAND2X1
X_358_ _20_ _180_ _162_ _82_ vdd gnd AOI21X1
X_299_ _8_ _5_ _12_ _25_ vdd gnd AOI21X1
X_320_ _131_ _45_ _46_ vdd gnd NAND2X1
X_223_ _137_ _136_ _138_ vdd gnd NAND2X1
X_261_ _174_ _175_ _145_ _147_ _176_ vdd 
+ gnd
+ OAI22X1
X_317_ _26_ _36_ _42_ _43_ vdd gnd AOI21X1
X_355_ _156_ _78_ R[6] _79_ vdd gnd OAI21X1
X_258_ _172_ _173_ vdd gnd INVX1
XFILL43050x14550 gnd vdd FILL
X_296_ _20_ _21_ _22_ vdd gnd NAND2X1
X_199_ _113_ _112_ _114_ vdd gnd NAND2X1
X_220_ _132_ _134_ _135_ vdd gnd NOR2X1
X_314_ _26_ _36_ _17_ _39_ _40_ vdd 
+ gnd
+ OAI22X1
X_352_ _76_ _75_ V_DIR _77_ vdd gnd OAI21X1
X_217_ R[3] R[2] _132_ vdd gnd NOR2X1
X_390_ _190_[2] DOUT[2] vdd gnd BUFX2
X_255_ R[7] HALF _170_ vdd gnd NOR2X1
X_293_ _173_ _13_ _16_ _19_ vdd gnd NAND3X1
X_349_ R[5] _73_ _72_ _74_ vdd gnd NAND3X1
X_387_ _189_ DED_FLAG vdd gnd BUFX2
X_196_ R[4] _111_ vdd gnd INVX1
X_311_ _36_ _26_ _37_ vdd gnd NOR2X1
X_214_ _127_ _126_ _129_ vdd gnd NAND2X1
X_252_ _166_ _161_ _88_ _167_ vdd gnd OAI21X1
X_308_ _33_ _27_ _34_ vdd gnd NAND2X1
X_290_ _15_ _14_ _11_ _16_ vdd gnd OAI21X1
X_346_ _70_ _69_ _88_ _71_ vdd gnd OAI21X1
X_384_ _53_ _50_ _156_ _108_ vdd gnd OAI21X1
X_193_ R[7] _98_ vdd gnd INVX1
X_249_ R[0] _163_ _164_ vdd gnd NAND2X1
X_287_ _5_ _12_ _8_ _13_ vdd gnd NAND3X1
X_211_ _125_ _110_ _126_ vdd gnd OR2X2
X_305_ HALF _146_ _31_ vdd gnd NAND2X1
X_343_ _66_ R[5] _68_ vdd gnd OR2X2
X_208_ _121_ _122_ _123_ vdd gnd NAND2X1
X_381_ _88_ _159_ _105_ vdd gnd NAND2X1
X_246_ _160_ _157_ VIEW _161_ vdd gnd AOI21X1
X_284_ HALF _111_ _10_ vdd gnd NAND2X1
X_378_ _102_ _103_ vdd gnd INVX1
X_302_ R[1] _163_ _28_ vdd gnd NAND2X1
X_340_ _120_ _46_ _65_ vdd gnd NOR2X1
X_205_ _119_ _118_ _120_ vdd gnd NAND2X1
X_243_ _144_ _158_ vdd gnd INVX1
X_281_ _178_ _176_ _181_ _7_ vdd gnd AOI21X1
X_337_ _44_ _60_ R[3] _63_ vdd gnd AOI21X1
X_375_ _173_ _43_ _41_ _100_ vdd gnd NAND3X1
X_278_ _3_ _4_ vdd gnd INVX1
X_202_ _116_ _115_ _117_ vdd gnd NAND2X1
X_240_ _153_ _120_ _155_ vdd gnd NAND2X1
X_334_ _158_ _159_ _59_ _60_ vdd gnd NAND3X1
X_372_ _95_ _9_ _162_ _96_ vdd gnd AOI21X1
X_237_ _132_ _134_ _151_ _152_ vdd gnd OAI21X1
X_275_ R[5] HALF _1_ vdd gnd NAND2X1
X_369_ _91_ R[7] _93_ vdd gnd OR2X2
X_331_ _120_ _49_ _57_ vdd gnd NOR2X1
X_234_ _121_ _146_ _149_ vdd gnd NAND2X1
X_272_ _181_ _187_ vdd gnd INVX1
X_328_ _3_ _46_ _11_ _50_ _54_ vdd 
+ gnd
+ OAI22X1
X_366_ _83_ _90_ _190_[2] vdd gnd NAND2X1
X_269_ R[0] _121_ _184_ vdd gnd NAND2X1
XFILL43350x10950 gnd vdd FILL
X_231_ R[0] _146_ vdd gnd INVX1
X_325_ _32_ _50_ _22_ _49_ _51_ vdd 
+ gnd
+ OAI22X1
X_363_ _86_ _87_ vdd gnd INVX1
X_228_ _142_ _143_ vdd gnd INVX1
X_266_ _180_ _179_ _181_ vdd gnd NAND2X1
X_322_ _131_ _48_ vdd gnd INVX1
X_360_ _181_ _43_ _41_ _84_ vdd gnd NAND3X1
X_225_ _98_ _137_ _136_ _140_ vdd gnd NAND3X1
XFILL43350x18150 gnd vdd FILL
X_263_ _151_ _177_ _178_ vdd gnd NAND2X1
X_319_ _140_ _139_ _45_ vdd gnd NAND2X1
X_357_ _79_ _80_ VIEW _81_ vdd gnd AOI21X1
X_298_ _19_ _23_ _24_ vdd gnd AND2X2
X_222_ _132_ _134_ R[6] _137_ vdd gnd OAI21X1
X_260_ R[3] HALF _175_ vdd gnd NOR2X1
X_316_ _34_ _156_ _42_ vdd gnd NAND2X1
X_354_ _57_ _78_ vdd gnd INVX1
X_219_ _122_ _133_ _134_ vdd gnd NOR2X1
X_392_ _191_ SEC_FLAG vdd gnd BUFX2
X_257_ _170_ _171_ _172_ vdd gnd NOR2X1
X_295_ HALF _133_ _21_ vdd gnd NAND2X1
X_389_ _190_[1] DOUT[1] vdd gnd BUFX2
X_198_ R[5] R[4] _113_ vdd gnd NAND2X1
X_313_ _23_ _19_ _39_ vdd gnd NAND2X1
X_351_ _72_ _73_ R[5] _76_ vdd gnd AOI21X1
X_216_ _128_ _130_ _131_ vdd gnd NAND2X1
X_254_ _165_ _168_ _169_ vdd gnd NAND2X1
X_292_ _17_ _18_ vdd gnd INVX1
X_348_ _159_ _65_ _59_ _73_ vdd gnd NAND3X1
X_386_ _109_ _59_ _108_ _189_ vdd gnd OAI21X1
X_195_ R[5] _110_ vdd gnd INVX1
X_289_ _188_ _182_ _4_ _15_ vdd gnd AOI21X1
X_310_ _35_ _34_ _36_ vdd gnd AND2X2
X_213_ _98_ _127_ _126_ _128_ vdd gnd NAND3X1
X_251_ _164_ _165_ _162_ _166_ vdd gnd AOI21X1
X_307_ _30_ _32_ _176_ _33_ vdd gnd OAI21X1
X_345_ _28_ _1_ _162_ _70_ vdd gnd AOI21X1
X_383_ _88_ _106_ _105_ _191_ vdd gnd OAI21X1
X_192_ V_DIR _88_ vdd gnd INVX1
X_248_ HALF _163_ vdd gnd INVX1
X_286_ _11_ _12_ vdd gnd INVX1
X_210_ _124_ _123_ _125_ vdd gnd NAND2X1
X_304_ _28_ _29_ _30_ vdd gnd NAND2X1
X_342_ R[5] _66_ _67_ vdd gnd NAND2X1
X_207_ R[3] _122_ vdd gnd INVX1
X_380_ _97_ _104_ _190_[3] vdd gnd NAND2X1
X_245_ _122_ _158_ _159_ _160_ vdd gnd NAND3X1
X_283_ R[4] _163_ _9_ vdd gnd NAND2X1
X_339_ _167_ _64_ _190_[0] vdd gnd NAND2X1
X_377_ R[7] _99_ _100_ _102_ vdd gnd NAND3X1
X_301_ _3_ _7_ _182_ _27_ vdd gnd OAI21X1
X_204_ _98_ _117_ _119_ vdd gnd NAND2X1
X_242_ _144_ _156_ R[3] _157_ vdd gnd OAI21X1
X_280_ _182_ _6_ vdd gnd INVX1
X_336_ _61_ _62_ vdd gnd INVX1
X_374_ _159_ _56_ _59_ _99_ vdd gnd NAND3X1
X_239_ _120_ _153_ _154_ vdd gnd OR2X2
XFILL43350x150 gnd vdd FILL
X_277_ _0_ _2_ _3_ vdd gnd NOR2X1
X_201_ _107_ _114_ _116_ vdd gnd NAND2X1
X_333_ _55_ _58_ _52_ _59_ vdd gnd NAND3X1
X_371_ _171_ _95_ vdd gnd INVX1
XFILL43050x18150 gnd vdd FILL
X_236_ _150_ _149_ _151_ vdd gnd NAND2X1
X_274_ R[5] HALF _0_ vdd gnd NOR2X1
X_368_ R[7] _91_ _92_ vdd gnd NAND2X1
X_330_ _120_ _142_ _56_ vdd gnd NOR2X1
X_233_ _145_ _147_ _135_ _148_ vdd gnd OAI21X1
X_271_ _149_ _150_ _169_ _186_ vdd gnd AOI21X1
X_327_ _120_ _53_ vdd gnd INVX1
X_365_ _89_ _87_ V_DIR _90_ vdd gnd OAI21X1
X_268_ R[1] _146_ _183_ vdd gnd NAND2X1
X_230_ R[0] _121_ _145_ vdd gnd NOR2X1
X_324_ _45_ _48_ _50_ vdd gnd NAND2X1
X_362_ R[6] _85_ _84_ _86_ vdd gnd NAND3X1
X_227_ _131_ _141_ _142_ vdd gnd NAND2X1
X_265_ R[6] HALF _180_ vdd gnd NAND2X1
X_359_ _82_ _81_ _88_ _83_ vdd gnd OAI21X1

.ends
.end
