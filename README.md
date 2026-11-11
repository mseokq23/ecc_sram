# ecc_sram

ETRI 0.5 µm CMOS(NSPL 2P3M 5 V) 마이칩(MyChip) 공정으로 만드는 **결함 주입 ECC 8T SRAM** 칩.

- 맞춤 8T SRAM 어레이 15행 × 8열 + 표준셀 기준 워드(주소 15) = 16워드, 워드마다 데이터 4비트 + 검사 4비트
- Hamming(8,4) SEC-DED. 외부 핀으로 결함을 넣는다: 쓰기 때 1/2/3비트 저장 오류, 읽기 때 1/2비트 오류, 저장된 코드워드 원시 보기
- 셀 전원 VDDA와 비트라인 드라이버 전원 VDDW를 따로 뺐다. 이 둘을 낮춰 보존 실패·읽기 실패·쓰기 실패 같은 **실제 물리 결함**을 만들고, ECC가 그것을 고치고 검출하는지 측정한다
- **방향을 아는 복호**: 저전압 읽기·쓰기 실패는 0 → 1 한 방향이다. 읽기 모드 11의 방향 보기(FI_POS 011)는 이 방향을 알고 같은 부호·같은 저장 비트를 다시 판정해, 표준 SEC-DED가 틀린 값으로 고치는(SEC만 나오는) 한 방향 3비트 오류 112가지를 모두 검출하고 데이터 0 워드의 2비트 오류는 고친다. 복호는 코어 위쪽의 조합 논리 블록 `ecc_dec`가 한다(새 핀 없음)
- 제출: 2026년 4차(신청서·DB 마감 12/7)

**최종 보고서**: [docs/report.md](docs/report.md) — 칩의 목표, 구성, 동작, 검증 결과, 제출 준비, 측정 계획을 한 문서로 정리했다. 사양은 [docs/spec.md](docs/spec.md), 단계별 검증 기록과 판단은 [docs/verification.md](docs/verification.md).

**최종 GDS**: [`designs/etri050/chip/final/ecc_sram_Top.gds.gz`](designs/etri050/chip/final) (최상위 셀 `ecc_sram_Top`, 재검사 기록 `check_report.txt`), 제출 파일 `ecc_sram_Top.zip`과 신청서용 DRC·LVS 화면도 같은 폴더에 있다. 칩 주제, 각 부분의 기능, Codespaces에서 결과물 보는 법은 [docs/guide.md](docs/guide.md).

## 검증 결과

| 블록 | 결과 |
|---|---|
| 8T 셀 회로 모의 (PDK 260820 모델) | 45조건 쓰기·읽기 통과, 보존 전압 TT 0.37 V, 읽기 Vmin(VDDA) TT 1.42 V, 쓰기 Vmin(VDDW) TT 1.86 V |
| 8T 셀·15×8 어레이 레이아웃 | Magic DRC 0, KLayout DRC 0, LVS 일치, Calibre 전용 73규칙·금속 규칙·안테나 0 |
| SRAM 매크로(어레이 + 컬럼 회로), 디커플링 | 같은 검사 모두 0·일치. 후모의 5 코너 + VDDA 2 V, 240비트씩 오류 0 |
| 제어 블록 ecc_fi_ctrl, 복호 블록 ecc_dec | 칩 코어 논리 시험 235,865회 비교(방향 보기 30,206회)와 ecc_dec 입력 2,048가지 전수 시험이 RTL·게이트·배치 후·고정 넷리스트에서 통과, 틀린 RTL 14개 모두 잡힘. 두 블록 평면 LVS 일치, DRC 0, 매크로 고정 |
| 패드 링·칩 조립 | 칩 전체 공식 DRC 0, Calibre 전용 0, 안테나 0, 코어 LVS 일치(3,982 소자), 기판·우물 접점 모두 전원 금속, 제출 GDS 검사 통과 |
| 칩 코어 트랜지스터 모의 (코어 전체 추출) | TT 27 °C 5 V, SS 125 °C 4.5 V, FF 0 °C 5.5 V, VDDA·VDDW 2.0 V: 쓰기·읽기·결함 주입·방향 보기 25번 읽기 모두 ECC 모델과 같음 |
| 최종 GDS | GitHub Codespaces(IIC-OSIC-TOOLS 2026.10)에서 `chip/check_all.sh --save`: 소스에서 블록과 칩을 다시 만들어 위 검사를 모두 다시 통과한 GDS를 `chip/final`에 저장(4,742,062 B, sha256 14540645…72a1eb). 제출 zip은 그 GDS로 제출 GDS 검사를 다시 통과시켜 만듦. 로컬 도구로 만든 이전 GDS와 19개 층 모두 XOR 0 |

선례로 정한 것(ETRI 문의 없이): VDDA·VDDW는 PANA PADR, 전원 패드 PVDD 2·PVSS 3, 출력 POB8 — 근거는 docs/verification.md 7절.

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
  render_gds.py, doc_figures.py   GDS를 PNG로 그리기, docs/img 그림 다시 그리기
  gds_xor.py              두 GDS의 도형 비교(층마다 XOR 면적)
  tap_check.py            기판·우물 접점이 모두 금속으로 전원 패드에 이어지는지(LVS가 못 보는 것)
  float_metal.py          어디에도 이어지지 않은 금속 조각 찾기
designs/etri050/
  gen/sram8t.py           8T 셀과 어레이 레이아웃 생성기(Magic), 비교용 넷리스트
  gen/colper.py           어레이 아래 컬럼 회로, 어레이와 합친 SRAM 매크로(sram_macro)
  gen/decap.py            VDDW·VDDA 디커플링(MOS 커패시터)
  sim/cell/               셀·컬럼 트랜지스터 수준 모의(코너, 보존 전압, 읽기 Vmin, 보존 시간, 쓰기 실패 방향)
  sim/post/array_post.py  그린 어레이(또는 --macro: 매크로 전체)를 추출해 쓰기·읽기 모의
  ctrl/                   제어 블록 ecc_fi_ctrl과 복호 블록 ecc_dec: RTL, 테스트벤치, 합성, qflow 배치·배선, 매크로 고정
  ctrl/macro/             고정한 두 블록(GDS, 넷리스트, 핀 좌표)
  chip/                   패드 링(pins.csv, run_pad_ring.sh), 칩 조립(assemble.py), 코어 LVS(core_lvs.py)
  chip/check_all.sh       소스에서 전체를 다시 만들고 모든 검사, --save면 통과한 GDS를 chip/final에 저장
  chip/final/             최종 GDS(gzip), sha256, 재검사 기록, 제출 zip과 그 검사 기록, 신청서용 DRC·LVS 화면
  sim/chip/chip_sim.py    칩 코어 전체 트랜지스터 모의(쓰기·읽기·결함 주입·방향 보기를 ECC 모델과 비교)
docs/                     최종 보고서(report.md), 안내(guide.md), 사양, 검증 기록, 그림(img/)
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
- 배포판 KLayout의 파이썬 모듈이 쓰는 파이썬과 `python3`이 다르면 `pip install klayout`으로 모듈만 따로 넣는다(Ubuntu 24.04 + Python 3.13: klayout 0.30.13)
- qflow 빌드: `libxt-dev libx11-dev`, graywolf 실행: `libgsl27 libgslcblas0`
- Ubuntu의 netgen은 `netgen-lvs`라는 이름이다. `ln -s /usr/bin/netgen-lvs /usr/local/bin/netgen`

그다음 `bash scripts/setup-all.sh`, `source scripts/etri050-env.sh`.

## 실행

```bash
source scripts/etri050-env.sh

# 셀·어레이 생성 + Magic DRC, KLayout DRC(킷 덱), LVS
python3 designs/etri050/gen/sram8t.py all --check
python3 designs/etri050/gen/colper.py --check            # 어레이 + 컬럼 회로 = sram_macro
bash scripts/extra_checks.sh designs/etri050/sram/build/sram_array.gds designs/etri050/sram/build/sram_macro.gds

# 셀 모의 (결과는 designs/etri050/sim/cell/build)
python3 designs/etri050/sim/cell/sweep_basic.py            # 45조건 쓰기·읽기·트립·keeper
python3 designs/etri050/sim/cell/sweep_vdda.py             # 읽기 Vmin(VDDA), 셀을 뒤집는 주입 전류
python3 designs/etri050/sim/cell/drv_butterfly.py nominal  # 유지 SNM, 보존 전압(코너)
python3 designs/etri050/sim/cell/drv_mc_small.py TT 27 200 12 15   # 보존 전압 퍼짐(Vt 불일치 가정)
python3 designs/etri050/sim/cell/retention_time.py         # VDDA를 낮춘 채 버티는 시간
python3 designs/etri050/sim/cell/write_dir.py              # VDDW를 낮췄을 때 쓰기 실패 방향(0 → 1만)

# 어레이 후모의(컬럼 회로는 회로도), 매크로 후모의(그린 컬럼 회로)
python3 designs/etri050/sim/post/array_post.py
python3 designs/etri050/sim/post/array_post.py --macro

# 디커플링
python3 designs/etri050/gen/decap.py --check

# 제어 블록과 복호 블록
make -C designs/etri050/ctrl sim dec_sim synth gatesim mutants   # RTL, 전수 시험, 합성, 게이트 수준, 틀린 RTL
make -C designs/etri050/ctrl flow dec_flow qflowsim             # qflow 배치·배선, 검사, 배치 후 넷리스트 시험
bash designs/etri050/ctrl/freeze_macro.sh                       # ctrl/macro 갱신
TOP=ecc_dec bash designs/etri050/ctrl/freeze_macro.sh
bash scripts/extra_checks.sh designs/etri050/ctrl/build/qflow/layout/ecc_fi_ctrl_F_grid.gds \
    designs/etri050/ctrl/build/qflow_ecc_dec/layout/ecc_dec_F_grid.gds

# 패드 링, 칩 조립과 검사
bash designs/etri050/chip/run_pad_ring.sh
python3 designs/etri050/chip/assemble.py                 # build/ecc_sram_Top.gds
etri-drc-klayout designs/etri050/chip/build/ecc_sram_Top.gds
BASELINE=designs/etri050/chip/build/ecc_sram_Pad.gds bash scripts/extra_checks.sh designs/etri050/chip/build/ecc_sram_Top.gds
python3 designs/etri050/chip/core_lvs.py
python3 scripts/mychip_gds_check.py --top ecc_sram_Top designs/etri050/chip/build/ecc_sram_Top.gds
python3 designs/etri050/sim/chip/chip_sim.py

# 위 전체를 한 번에: 블록·칩 다시 만들기와 모든 검사 (--save: 통과하면 chip/final에 저장)
bash designs/etri050/chip/check_all.sh
```

## 작업 규칙

- 블록마다 DRC(Magic, 킷 KLayout 덱, `extra_checks.sh`) 0과 LVS 일치를 확인한 뒤 올린다
- 모의 결과 수치는 `docs/verification.md`에 남긴다
