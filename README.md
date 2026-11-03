# ecc_sram

ETRI 0.5 µm CMOS(NSPL 2P3M 5 V) 마이칩(MyChip) 공정으로 만드는 **결함 주입 ECC 8T SRAM** 칩.

- 맞춤 8T SRAM 어레이 15행 × 8열 + 표준셀 기준 워드(주소 15) = 16워드, 워드마다 데이터 4비트 + 검사 4비트
- Hamming(8,4) SEC-DED. 외부 핀으로 결함을 넣는다: 쓰기 때 1/2/3비트 저장 오류, 읽기 때 1/2비트 오류, 패리티 원시 보기
- 어레이 전원 VDDA를 따로 뺐다. VDDA를 낮춰 보존 실패·읽기 실패 같은 **실제 물리 결함**을 만들고, ECC가 그것을 고치고 검출하는지 측정한다
- 제출 목표: 2027년 1차. 일정이 앞당겨지면 2026년 4차(DB 마감 12/7)

사양은 [docs/spec.md](docs/spec.md), 단계별 검증 기록과 판단은 [docs/verification.md](docs/verification.md).

## 진행 상황 (2026-11-03)

| 블록 | 결과 |
|---|---|
| 8T 셀 회로 모의 (PDK 260820 모델) | 45조건 쓰기·읽기 통과, 보존 전압 TT 0.37 V, 읽기 Vmin(VDDA) TT 1.42 V |
| 8T 셀·15×8 어레이 레이아웃 | Magic DRC 0, KLayout DRC 0, LVS 일치, Calibre 전용 73규칙·금속 규칙·안테나 0 |
| 어레이 후모의 (추출 C × 1.5) | 5 코너 + VDDA 2 V, 240비트씩 오류 0 |
| 제어 블록 ecc_fi_ctrl | RTL·게이트·배치 후 넷리스트 시험 통과, 평면 LVS 일치, DRC 0, 매크로 고정 |
| 컬럼 회로(프리차지·keeper·센스·쓰기 드라이버) 레이아웃 | 다음 단계 |
| VDDA 디커플링, 패드 링, 칩 조립·칩 검사 | 그다음 |

## 구성

```
.devcontainer/            Codespaces/Dev Container (IIC-OSIC-TOOLS 이미지 + noVNC 데스크톱)
scripts/
  setup-all.sh            처음 한 번: 킷 받기 + PDK 모델 꺼내기 + qflow 설치
  setup-etri050.sh        ETRI050 디자인 킷을 .pdk/ 로 받고 Magic·KLayout 설정
  get-models.sh           킷 안의 PDK(260820) 압축에서 모델 두 개를 sim/models 로 꺼냄
  install-qflow-etri050.sh  qflow, graywolf, qrouter
  etri050-env.sh          magic-etri, klayout-etri, etri-check 같은 셸 함수
  smoke-test.sh           도구·킷·모델 점검
  extra_checks.sh         킷 KLayout 덱이 안 보는 규칙: calibre_rules.py, metal_rules.py, antenna_rules.py
  fill_notches.py, snap_grid.py   qflow 결과의 금속 틈 메우기, 0.01 µm 격자 맞추기
  mychip_gds_check.py     제출 GDS 자체 검사(층, 격자, 스크라이브 레인, 패드 개구 …)
designs/etri050/
  gen/sram8t.py           8T 셀과 어레이 레이아웃 생성기(Magic), 비교용 넷리스트
  sim/cell/               셀·컬럼 트랜지스터 수준 모의(코너, 보존 전압, 읽기 Vmin, 보존 시간)
  sim/post/array_post.py  그린 어레이를 추출해 컬럼 회로와 함께 쓰기·읽기 모의
  ctrl/                   제어 블록: RTL, 테스트벤치, 합성, qflow 배치·배선, 매크로 고정
  ctrl/macro/             고정한 제어 블록(GDS, 넷리스트, 핀 좌표)
docs/                     사양, 검증 기록
```

PDK 파일(모델, 덱 원본, GPIO, 패드 프레임)은 저장소에 넣지 않는다. 모델은 `scripts/get-models.sh`가 킷에 들어 있는 PDK 압축에서 꺼내고, `.gitignore`가 그 폴더를 뺀다. 표준셀은 공개 킷(GPL-3.0)의 것이고 `ctrl/macro`에는 그 셀로 만든 배치 결과만 있다.

## 개발환경

### Codespaces (권장)

저장소에서 Code → Codespaces로 만들면 `.devcontainer`가 이미지(`hpretl/iic-osic-tools-devcontainer:2026.10`)를 받고 `scripts/setup-all.sh`를 실행한다. 4코어 이상을 권장한다. GUI(Magic, KLayout, Xschem)는 포트 6080의 noVNC 데스크톱에서 연다.

```bash
bash scripts/smoke-test.sh          # 도구, 킷, 모델, DRC/LVS 한 바퀴
```

### 로컬 Linux

같은 이미지를 Docker로 쓰는 것이 가장 간단하다. 배포판 패키지로 맞출 때 필요한 것:

- magic 8.3, netgen, klayout 0.28 이상(파이썬 모듈 포함), ngspice 42, iverilog 12, yosys, python3 + numpy
- qflow 빌드: `libxt-dev libx11-dev`, graywolf 실행: `libgsl27 libgslcblas0`
- Ubuntu의 netgen은 `netgen-lvs`라는 이름이다. `ln -s /usr/bin/netgen-lvs /usr/local/bin/netgen`

그다음 `bash scripts/setup-all.sh`, `source scripts/etri050-env.sh`.

## 실행

```bash
source scripts/etri050-env.sh

# 셀·어레이 생성 + Magic DRC, KLayout DRC(킷 덱), LVS
python3 designs/etri050/gen/sram8t.py all --check
bash scripts/extra_checks.sh designs/etri050/sram/build/sram_array.gds

# 셀 모의 (결과는 designs/etri050/sim/cell/build)
python3 designs/etri050/sim/cell/sweep_basic.py            # 45조건 쓰기·읽기·트립·keeper
python3 designs/etri050/sim/cell/sweep_vdda.py             # 읽기 Vmin(VDDA), 셀을 뒤집는 주입 전류
python3 designs/etri050/sim/cell/drv_butterfly.py nominal  # 유지 SNM, 보존 전압(코너)
python3 designs/etri050/sim/cell/drv_mc_small.py TT 27 200 12 15   # 보존 전압 퍼짐(Vt 불일치 가정)
python3 designs/etri050/sim/cell/retention_time.py         # VDDA를 낮춘 채 버티는 시간

# 어레이 후모의
python3 designs/etri050/sim/post/array_post.py

# 제어 블록
make -C designs/etri050/ctrl sim synth gatesim   # RTL, 합성, 게이트 수준
make -C designs/etri050/ctrl flow qflowsim       # qflow 배치·배선, 검사, 배치 후 넷리스트 시험
bash designs/etri050/ctrl/freeze_macro.sh        # ctrl/macro 갱신
bash scripts/extra_checks.sh designs/etri050/ctrl/build/qflow/layout/ecc_fi_ctrl_F_grid.gds
```

## 작업 규칙

- 블록마다 DRC(Magic, 킷 KLayout 덱, `extra_checks.sh`) 0과 LVS 일치를 확인한 뒤 올린다
- 모의 결과 수치는 `docs/verification.md`에 남긴다
