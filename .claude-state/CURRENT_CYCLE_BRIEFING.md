# Current Cycle Briefing

_Cycle 325 | 2026-06-18 | A(품질) + C(데이터) + F(리서치)_

## 완료된 작업

### A(품질): 1h 제외 전략 확정

- `scripts/paper_simulation.py`에 `STRATEGIES_TIMEFRAME_EXCLUDE` 추가
  - `"1h": {"value_area", "supertrend_multi"}` — 4h 전용 전략 1h paper_sim 제외
- supertrend_multi 1h WFO 실행 (reduced grid 9조합, 4 windows):
  - avg OOS Sharpe=-2.858, WFE=-2.71 → 4h 전용 완전 확정
- Paper Sim: 22→20전략, 0/20 PASS, rank1=price_cluster(+2.19%, 1/8)

### C(데이터): live_paper_trader 4h CSV fallback

- `fetch_latest_candles()` exchange 실패 시 `data/historical/` CSV 자동 fallback
- 4h 요청: 1h CSV → `resample_ohlcv('4h')` (volume=sum 검증 완료)
- synthetic보다 실거래소 우선 정렬 추가

### F(리서치): 레짐 스위칭 실효성 분석

- BTC 5-fold ATR% 분석: 전 구간 2.5-3.3% → 전부 HIGH_VOL 판정
- **발견**: MarketRegimeDetector HIGH_VOL 임계값(2.5%)이 BTC 정상 변동성 수준보다 낮음
- OFI+supertrend의 TREND_UP 우세 패턴 확인 → 레짐 매핑 방향은 옳으나 감지기 재보정 필요

## 현재 시스템 상태

- 테스트: 8413 passed, 23 skipped
- Paper Sim: 0/20 PASS (1h, 8 windows) — rank1 price_cluster
- Bundle OOS: **5/5 PASS** (5 사이클 연속 유지)
- 코드 변경: paper_simulation.py + live_paper_trader.py (회귀 없음)

## 다음 사이클 (326) 핵심 작업

- **B(리스크)**: MarketRegimeDetector HIGH_VOL 임계값 crypto 재보정
- **D(ML)**: roc_ma_cross 1h 파라미터 탐색 (2/8 consistency 개선 가능성)
- **F**: Bundle fold4 ATH 구간 OFI>supertrend 패턴 → 레짐 스위칭 근거 강화
