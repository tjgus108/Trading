# Next Steps

_Last updated: 2026-06-05 (Cycle 274 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 274

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 272 | B+D+F | ADX 필터 추가(역효과 확인), strategy_params 지원, cmf period=60 실험→실패 |
| 273 | C+B+F | ADX 필터 제거(4h OOS 1.289로 개선), cmf threshold 0.05/-0.05 실험(소폭 개선) |
| 274 | D+E+F | vol_mult 그리드 상향, supertrend_multi 파라미터화, cmf threshold 복원→4h OOS PASS 달성 |

### 🎯 Cycle 275 작업 방향 (275 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): supertrend_multi 4h Bundle OOS 평가
- supertrend_multi BTC 1h: rank=1, +5.87%, 2/8 PASS windows (PF 1.44 아슬아슬)
- BUNDlE_STRATEGIES에 supertrend_multi 추가 검토
  - 현재 5전략: cmf, elder_impulse, wick_reversal, narrow_range, value_area
  - supertrend_multi atr_threshold 그리드 [0.7,0.8,0.9]로 4h OOS 검증 필요
- cmf 4h PASS 확인 → cmf 파라미터 안정화 (best_params 기록)
  - cmf fold 결과: fold0=5.111, fold1=3.858, fold2=0.642, fold3=1.480, fold4=1.451
  - fold2,3에서 약함 (2023-10~2024-02 구간) → 파라미터가 이 구간에서 왜 약한지 분석

#### C(데이터): wick_reversal vol_mult 그리드 효과 검증
- vol_mult 그리드 [1.0,1.1,1.2]로 변경 완료 (Cycle 274)
- 다음 단계: run_bundle_oos에 wick_reversal 재최적화 후 결과 비교
  - 기존 avg OOS=1.200, std=4.842 → vol_mult 강화 후 std 개선 여부 확인
  - 예상: 볼륨 확인 강화로 fold1(2023-08 여름) 음수 OOS 방지 가능성

#### F(리서치): cmf PASS 분석 + 다음 전략 후보 탐색
- cmf 4h Bundle OOS PASS (avg=2.508) — 2022 구간 제외 시 실질적 알파 존재
- 다음 검토: supertrend_multi을 bundle에 추가할 경우 전체 포트폴리오 상관관계 분석
  - cmf(추세 추종 모멘텀) + supertrend_multi(ATR 추세) → 상관성 높을 수 있음
  - 독립적인 전략 믹스 필요: cmf + wick_reversal(반전) + narrow_range(변동성) 조합 유지

### ⚠️ 긴급 사항
- **wick_reversal OOS std=4.842**: vol_mult [1.0-1.2] 그리드로 재최적화 필요
  - run_bundle_oos.py 실행 후 새 그리드 효과 확인
  - fold1(2023-08) OOS=-4.606이 핵심 문제 → 볼륨 필터 강화로 방어 가능한지 확인
- **supertrend_multi ETH/SOL 성능 급락**: BTC +5.87% vs ETH -19.68%, SOL -8.54%
  - ETH에서 극도로 나쁜 성능 → 전략이 BTC 1h에 과적합 가능성
  - atr_threshold=0.9 (현재)이 ETH 변동성 구조에 맞지 않을 수 있음

### 핵심 메트릭 (Cycle 274)
- 테스트: **8369 passed, 23 skipped** — 회귀 없음
- Paper Sim BTC 1h: 0/22 PASS
  - top: supertrend_multi +5.87%, cmf rank=13 AvgSharpe=-1.24
  - wick_reversal: rank=22, AvgSharpe=-2.79
- Bundle OOS BTC 4h (5-fold): **1/5 PASS** ← cmf 첫 PASS 달성! ✅
  - cmf: PASS avg OOS=2.508, std=1.888
  - wick_reversal: FAIL avg=1.200, std=4.842

### 주요 코드 변경 이력 (Cycle 274)
1. `src/strategy/supertrend_multi.py` — atr_threshold 생성자 파라미터화 (기본값 0.9)
2. `src/backtest/walk_forward.py` — DEFAULT_GRIDS["supertrend_multi"] 추가 (atr_threshold [0.7,0.8,0.9])
3. `src/backtest/walk_forward.py` — optimize_supertrend_multi() 함수 추가
4. `src/backtest/walk_forward.py` — wick_reversal vol_mult [0.7,0.8,0.9]→[1.0,1.1,1.2]
5. `scripts/paper_simulation.py` — PAPER_SIM_STRATEGY_PARAMS 초기화 (cmf 실험 종료)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv, 5-fold 4h 구조)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수
