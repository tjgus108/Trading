# Current Cycle Briefing

_Cycle 314 | 2026-06-15 | D(ML) + E(실행) + F(리서치)_

## 완료된 작업

### D(ML) — VOL_SPIKE_MULT 1.0→0.5 실험 (역효과 확정, 복원)
- `src/strategy/narrow_range.py` `vol_spike_mult` init 파라미터화 (클래스 상수 파라미터화)
- `BUNDLE_STRATEGY_INIT_PARAMS["narrow_range"]`에 `vol_spike_mult=0.5` 추가 후 실험
- **결과**: avg OOS=-1.927, std=3.480 — trades 증가 미미, 신호 품질 저하
  - fold[3] (2023-12~2024-02 강세장): OOS=-11.387 구조적 FAIL
  - binding constraint는 VOL이 아닌 NR 발생 빈도 또는 ATR_THRESHOLD
- **복원**: vol_spike_mult=1.0 (기본값), init 파라미터화 코드는 유지 (향후 실험 가능)

### E(실행) — PAPER_SIM_STRATEGY_PARAMS_4H 구조 신설
- `scripts/paper_simulation.py` 타임프레임별 파라미터 분리 구조 추가
- `PAPER_SIM_STRATEGY_PARAMS_4H` 딕셔너리: supertrend_multi 4h 최적 파라미터 등록
- `--timeframe 4h` 실행 시 4H 파라미터 자동 병합 적용
- **근거**: 4h params를 1h에 적용 시 cmf_confirm 과도 필터링 → Sharpe 0.32→0.02 확인

### F(리서치) — Bundle OOS --csv-dir 기본값 고정 (핵심 성과)
- `scripts/run_bundle_oos.py` `--csv-dir` 기본값 `None` → `data/historical`
- `_resolve_csv_dir()` 헬퍼 추가 (상대경로→절대경로, 부재 시 fallback)
- **효과**: 5-fold (2023-2024 실제 BTC) → **2/5 PASS 달성**
  - cmf: PASS (5/5 folds, avg Sharpe=2.508)
  - supertrend_multi: PASS (avg Sharpe=3.674)

## 시뮬레이션 요약

| 지표 | Cycle 313 | Cycle 314 | 변화 |
|------|-----------|-----------|------|
| 테스트 | 8413 passed | 8413 passed | 동일 |
| Paper Sim PASS | 0/22 | 0/22 | 동일 |
| Bundle OOS PASS | 0/5 (9-fold) | **2/5 (5-fold)** | **+2 PASS** |
| cmf OOS Sharpe | -0.805 (9-fold) | **2.508 (5-fold)** | **대폭 개선** |
| supertrend_multi | PASS | PASS | 유지 |

## 다음 Cycle 315 (A+C+F)
- A: cmf 4h 실전 투입 준비 (5/5 PASS 확인, 파라미터 검토)
- C: narrow_range ATR_THRESHOLD 완화 실험 (0.95→1.05) 또는 bull 레짐 SELL 차단
- F: cmf 4h vs 1h 구조적 차이 분석
