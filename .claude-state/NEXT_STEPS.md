# Next Steps

_Last updated: 2026-06-09 (Cycle 290 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 290

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 288 | C+B+F | resample_ohlcv partial bucket 제거, regime_transition 경고 로깅 강화 |
| 289 | D+E+F | detect_regime 벡터화, oos_sharpes 앙상블 파라미터, paper_sim fee 오표기 수정 |
| 290 | A+C+F | --timeframe 4h 지원 paper_sim, IS 극단 과최적화 마커, IS vs OOS 괴리 분석 |

### 🎯 Cycle 291 작업 방향 (291 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): Risk 모듈 점검
- **탐색 방향**:
  - DrawdownMonitor의 cmf/supertrend_multi 포지션 관리 개선
  - supertrend_multi fold3/4 구조적 제외(레짐 전환 20%)로 실전 투입 시 리스크 관리 전략
  - Kelly Sizer: 4h PASS 전략(cmf, supertrend_multi) 포지션 사이즈 계산 검증

#### D(ML): 4h Paper Sim 실행 및 결과 분석
- **핵심 작업**:
  - `python3 scripts/paper_simulation.py --timeframe 4h --csv-dir data/historical --symbols BTC/USDT`
  - 4h 모드에서 cmf PASS 확인 목표 (Bundle OOS 4h PASS 일관성 검증)
  - 결과: ACTIVE_TIMEFRAME=4h → train=1260, test=360, step=180 candles
  - 예상: 1h 0/22 PASS → 4h에서 cmf/supertrend_multi PASS 가능성 높음

#### F(리서치): IS vs OOS 괴리 심층 분석
- **주요 발견 (Cycle 290)**:
  - supertrend_multi IS/OOS ratio=0.683 > cmf ratio=0.366
  - "합성 IS Sharpe 낮을수록 더 잘 일반화" 가설 확인 필요
  - elder_impulse IS>5.0 → OOS<0 패턴: 합성 데이터 과최적화 마커 추가됨 (walk_forward.py)
  - 다음 사이클: elder_impulse 개선 가능성 탐색 (min_volatility 상향, EMA 기간 조정)

### ⚠️ 주의 사항 (Cycle 291)
- **4h Paper Sim 첫 실행 시도**: `--timeframe 4h --csv-dir data/historical`
  - 1h CSV → 4h 리샘플링 후 walk-forward (train=1260, test=360 candles)
  - 예상 소요: 22 전략 × ~4 windows ≈ 5-8분
- **supertrend_multi regime_transition_ratio=20%**: fold4 제외 상태 유지
- **IS 극단 과최적화 마커**: walk_forward.py에 추가됨 (IS>5.0 && OOS<0)

### 핵심 메트릭 (Cycle 290)
- 테스트: **8386 passed** (5개 추가) — 회귀 없음
- Paper Sim BTC 1h (8 windows): 0/22 PASS
  - rank1: supertrend_multi (score=73.9, +6.73%, Sharpe=0.60, PF=1.17, 2/8)
  - cmf rank13: Sharpe=-1.24, PF=0.90, trades=75 avg
- Bundle OOS BTC 4h (5-fold, CSV):
  - cmf: **PASS** avg=2.508, std=1.888 ← **18회 연속 PASS**
  - supertrend_multi: **PASS** avg=3.674, std=1.860 ← **4회 연속 PASS**
    - fold3 excluded (trades<3) / fold4 excluded (레짐 전환 IS=2.51>2.0, WFE<0)
  - elder_impulse: FAIL | narrow_range: FAIL | value_area: FAIL
  - **총 PASS: 2/5 유지**

### 주요 코드 변경 이력 (Cycle 290)
1. `scripts/paper_simulation.py` — --timeframe 4h 옵션 + ACTIVE_TIMEFRAME 글로벌 (C 데이터)
   - `_TF_CANDLE_RATIO` dict: 타임프레임별 1h 대비 캔들 비율 상수
   - `make_walk_forward_windows()`: ratio 기반 캔들 수 스케일링
   - `simulate_symbol()`: resample_ohlcv() 통합
   - argparser: `--timeframe` 인수 추가
2. `src/backtest/walk_forward.py` — IS 극단 과최적화 마커 (A 품질)
   - RollingOOSValidator: IS>5.0 && OOS<0 fold에 "IS 극단 과최적화" fail_reason 추가
3. `tests/test_paper_simulation.py` — TestTimeframeCandles 4개 테스트 (A 품질)
4. `tests/test_walk_forward.py` — 과최적화 마커 테스트 1개 추가 (A 품질)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조)
- Paper simulation 1h: 22 전략 × 8 windows → 약 8분 소요 (BTC only)
- Paper simulation 4h: 22 전략 × ~4 windows → 약 4-5분 예상
