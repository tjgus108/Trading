# Current Cycle Briefing

_Last updated: 2026-07-03 (Cycle 385 완료)_

## 현재 상태

- **완료된 사이클**: 385
- **다음 사이클**: 386 (386 mod 5 = 1 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Consist=4/8)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 385 주요 결과

### A(품질): test_price_cluster.py 테스트 보강
- `tests/test_price_cluster.py`: 3개 테스트 추가 (총 19개)
  - `test_n_bins_4_returns_valid_signal`: n_bins=4 Signal 유효성 확인
  - `test_n_bins_4_wider_bins_than_5`: n_bins=4 bin_width 수학적 검증
  - `test_rsi_oversold_filter_accepts_neutral_rsi_data`: dead param 행동 문서화

### C(데이터): roc_ma_cross FAIL 윈도우 실데이터 분석
- BTC 1h 실데이터에서 W2/W3/W4 구간 ROC_MA 신호 품질 직접 분석:
  - **FAIL 윈도우 vol_ratio at signals mean: 0.89-0.97** (PASS 윈도우: 1.14-1.19)
  - W3/W4에서 vol>=1.2 통과 신호: 각 14건 → **Trades<15 기준이 FAIL 핵심 원인**
  - W4 24h fwd return(vol-filtered): +2.10% — 신호 품질 자체는 양호
  - walk_forward.py DEFAULT_GRIDS 주석에 반영

### F(리서치): roc_ma_cross ATR expand filter — dead param 확정
- `src/strategy/roc_ma_cross.py`: `atr_expand_filter`, `atr_expand_min` 파라미터 추가 (코드 유지)
  - paper_sim 실험 (atr_expand_filter=True): **Sh=1.43(↓-0.38), PF=1.84(↓-0.18), Consist=2/8(FAIL!)**
  - 원인: 추가 필터 → Trades=14 경계선에서 PASS 윈도우 FAIL 전락
  - **핵심 교훈: roc_ma_cross는 추가 signal filter 절대 금지**
  - 즉시 paper_sim 복원 (기본값 False)

## 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| paper_sim (atr_expand_filter=True 실험) | Sh=1.43, PF=1.84, Trades=14, Consist=2/8 FAIL (역효과) |
| paper_sim (복원 후 baseline) | **1/19 PASS** (roc_ma_cross Sh=1.81, PF=2.02, Trades=14, 4/8) |
| bundle_oos (4h BTC, CSV) | **5/5 PASS 유지** |

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `tests/test_price_cluster.py` | n_bins=4 테스트 3개 추가 (A) |
| `src/backtest/walk_forward.py` | FAIL 윈도우 분석 주석 추가 + ATR filter dead param 기록 (C/F) |
| `src/strategy/roc_ma_cross.py` | `atr_expand_filter`, `atr_expand_min` 파라미터 추가 (코드 유지, F) |
| `scripts/paper_simulation.py` | atr_expand_filter=True 실험 → dead param → 기본값 복원 + 결과 주석 (F) |

## Cycle 386 예고 (386 mod 5 = 1 → B+D+F)

- **B(리스크)**: DrawdownMonitor/kelly_sizer 코드 품질 점검 + 단위 테스트 추가
- **D(ML)**: price_cluster n_bins=4 WFO 탐색 결과 분석 (직접 WFO 실행)
- **F(리서치)**: roc_ma_cross SL/TP 실험 (atr_multiplier_sl=1.2 또는 tp=2.5) — Trades 무영향, Sharpe/PF 개선 경로
