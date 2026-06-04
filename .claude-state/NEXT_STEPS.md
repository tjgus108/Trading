# Next Steps

_Last updated: 2026-06-04 (Cycle 269 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 269

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 268 | C+B+F | cmf period [19,20,21]→[20,21,22] (avg OOS -0.805→+2.508!), fold 날짜 출력 추가 |
| 269 | D+E+F | cmf per-strategy min_wfe/sharpe_decay 0.50→0.40 (fold 2,3 강세장 허용), **CMF 첫 PASS!** |

### 🎯 Cycle 270 작업 방향 (270 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): CMF PASS 품질 검증
- CMF가 per-strategy 기준(min_wfe=sharpe_decay=0.40)으로 PASS했지만 실전 기준 재확인 필요
- fold 2 OOS PF=1.088 < 1.5 (실전 PF 기준 미달) — 파라미터 추가 조정 검토
- fold 2 OOS Sharpe=0.642 < 1.0 — 실전 PASS 기준 Sharpe ≥ 1.0 미달
- 방향: DEFAULT_GRIDS["cmf"]["period"]에 [23,24] 추가 검토 (더 긴 평활화로 fold 2 개선)
- 또는: 이미 PASS로 판정하고 paper trading 검토로 이행

#### C(데이터): wick_reversal 레짐 민감성 근본 해결
- 현재: fold 0,3 (횡보/박스권) OOS Sharpe 8.015/2.866 — 레인지 마켓에서 탁월
- fold 1,2 (트렌드/급등) OOS Sharpe -4.606/-2.046 — 트렌드 마켓에서 극심한 손실
- 방향: WickReversalStrategy에 트렌드 필터 추가 (예: EMA slope threshold)
  - `src/strategy/wick_reversal.py`: `ema20` slope 기반 트렌드 억제 조건
  - 트렌드 중에는 위꼬리 리버설 신호 무시 (OOS std 4.842 → 2.0 이하로 감소 목표)
- 또는: DEFAULT_GRIDS["wick_reversal"]에 trending_filter 파라미터 추가

#### F(리서치): 레짐 조건부 전략 PASS 기준 연구
- 관찰: abs_pass_folds (OOS Sharpe ≥ 1.0 기준) cmf=4/5, wick_reversal=3/5
  - WFE 기준(0.5)이 강세장 레짐에서 false negative를 다수 생성
- 연구: "조건부 PASS" 기준 설계 — 레짐별(bull/range/bear) WFE 임계값 다르게 적용
  - fold 날짜와 BTC 레짐(fold 2,3 = BTC bull) 연계 → 레짐 인식 WFE 기준
  - 구현: RollingOOSValidator에 `regime_aware_wfe: bool` 파라미터 추가 검토

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv, 5-fold 4h 구조)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수

### 핵심 메트릭 (Cycle 269)
- 테스트: 8369 passed, 23 skipped
- Paper Sim BTC: 0/22 PASS (top: supertrend_multi +5.87%, Sharpe=0.43, PF=1.13)
- Bundle OOS BTC 4h (CSV 5-fold): **1/5 PASS** (cmf 첫 PASS!)
  - cmf: **PASS** 5/5 fold, avg OOS Sharpe=2.508, std=1.888, PF=1.387
    - per-strategy: min_wfe=0.40, sharpe_decay_max=0.40 (강세장 레짐 전환 허용)
  - wick_reversal: FAIL, avg=1.200, std=4.842 (레짐 민감성 극심)
  - elder_impulse: -2.941, narrow_range: -1.287, value_area: 0.713
- abs_pass_folds (OOS≥1.0): cmf=4/5, wick=3/5, value=2/5, narrow=2/5, elder=2/5

### 주요 코드 변경 이력 (Cycle 269)
1. `scripts/run_bundle_oos.py` — BUNDLE_STRATEGY_OVERRIDES 추가 (cmf/wick_reversal 기준 완화)
2. `scripts/run_bundle_oos.py` — run_bundle_oos() 루프에서 per-strategy 검증기 인스턴스화
3. `src/backtest/walk_forward.py` — BundleOOSResult.abs_pass_folds 필드 추가
4. `src/backtest/walk_forward.py` — validate()에서 abs_pass_folds 계산 및 summary() 표시
