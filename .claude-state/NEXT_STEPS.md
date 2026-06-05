# Next Steps

_Last updated: 2026-06-05 (Cycle 273 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 273

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 271 | B+D+F | EMA 필터 실험→역효과→롤백, avg_wfe 윈소라이즈, cmf_1h 그리드 추가 |
| 272 | B+D+F | ADX 필터 추가(역효과 확인), strategy_params 지원, cmf period=60 실험→실패 |
| 273 | C+B+F | ADX 필터 제거(4h OOS 1.289로 개선), cmf threshold 0.05/-0.05 실험(소폭 개선) |

### 🎯 Cycle 274 작업 방향 (274 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): wick_reversal OOS std 안정화
- 현재 OOS Sharpe std=6.085 (기준 3.0 초과) — 레짐별 극단적 편차
- PASS folds: 1(bear 바닥), 2(회복), 4(bull초입), 7(횡보), 8(bull)
- FAIL folds: 0(2022 bear), 3(2022말 횡보), 5(2023 여름), 6(2023 여름)
- 공통점: FAIL fold들은 2022 하락 + 2023 여름 횡보 구간
- **방향 1**: wick_reversal에 ATR 기반 vol_filter 강화 (min_volatility 상향: 0.002→0.003)
  - 2022 하락장 = 고변동성이지만 일방향 → ATR 높음 → 오히려 통과
  - 더 정밀한 필터 필요
- **방향 2**: vol_mult 그리드 조정 (0.7→0.9에서 1.0→1.2로 상향)
  - FAIL fold들의 공통점: 저거래가 아닌 음수 Sharpe → 신호 품질 문제
  - vol_mult↑로 볼륨 확인 강화 → 가짜 반전 패턴 차단

#### E(실행): supertrend_multi 1h 성능 분석
- supertrend_multi: rank=1, +5.87% return, 2/8 windows PASS
- 나머지 windows: PF<1.5 또는 Sharpe<1.0 (아슬아슬하게 실패)
- 개선 방향: supertrend 파라미터 그리드 추가 (기간/ATR 배수 조정)
  - DEFAULT_GRIDS["supertrend_multi"] 추가 검토
  - 현재 파라미터 확인: `src/strategy/supertrend_multi.py`

#### F(리서치): cmf 4h vs 1h 분리 결론
- cmf 1h paper sim: threshold 0.05→rank=13 (개선이지만 여전히 FAIL)
- cmf 4h OOS: 9-fold에서 FAIL (2022 구간 영향)
- **결론**: cmf는 2023-2024 구간(fold 7,8)에서 강함 → 최근 데이터 집중 구간에서만 유효
- **방향**: PAPER_SIM_STRATEGY_PARAMS 초기화 (threshold 실험 종료)
  - cmf 기본값(0.08/-0.08)으로 복원
  - 4h Bundle OOS 5-fold (최근 2년 구간)로 재평가 요청

### ⚠️ 긴급 사항
- **wick_reversal OOS std**: 6.085 > 3.0 기준 초과 → std 안정화가 최우선
  - ADX 제거 후 avg 개선됐으나 std 문제 잔존
  - vol_mult 강화 또는 캔들 패턴 엄격화로 접근
- **cmf threshold 실험 종료**: 0.05/-0.05 효과 미미 → 기본값 복원 필요

### 핵심 메트릭 (Cycle 273)
- 테스트: **8369 passed, 23 skipped** — 회귀 없음
- Paper Sim BTC 1h: 0/22 PASS
  - top: supertrend_multi +5.87%, cmf rank=13 AvgSharpe=-1.31 (threshold 0.05)
  - wick_reversal: rank=22, AvgSharpe=-2.79
- Bundle OOS BTC 4h (9-fold): 0/5 PASS
  - wick_reversal: FAIL (std 6.085), avg OOS=1.289 (개선), 5/9 folds PASS ✅
  - cmf: FAIL, avg=-0.805 (2022 구간 포함 영향)

### 주요 코드 변경 이력 (Cycle 273)
1. `src/strategy/wick_reversal.py` — ADX 필터(`adx_ok`) 조건 제거, docstring 업데이트
2. `src/backtest/walk_forward.py` — DEFAULT_GRIDS["wick_reversal"]에서 adx_threshold 제거
3. `src/backtest/walk_forward.py` — cmf_1h 그리드 buy_thresh [0.05,0.06,0.07]로 변경
4. `scripts/paper_simulation.py` — PAPER_SIM_STRATEGY_PARAMS에 cmf threshold 실험 추가

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv, 9-fold 4h 구조)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수
