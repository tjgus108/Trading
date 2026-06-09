# Next Steps

_Last updated: 2026-06-09 (Cycle 293 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 293

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 291 | B+D+F | 레짐 기반 kill switch, 음수 OOS 비례 패널티, 9-fold 데이터 변화 분석 |
| 292 | B+D+F | supertrend_multi std threshold 2.5→3.0, --start-date 옵션, Bundle OOS 0→2 PASS |
| 293 | C+B+F | --verbose-windows 추가, CircuitBreaker reset_daily 4h 수정, FAIL 원인 완전 분석 |

### 🎯 Cycle 294 작업 방향 (294 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): cmf PF 개선 — 신호 필터 강화
- **핵심 이슈**: cmf avg_pf=1.24 (Paper Sim), avg_pf=1.387 (Bundle OOS) — 두 환경 모두 PF < 1.5
  - Paper Sim FAIL 이유: `profit_factor 1.14 < 1.5` (Window별 FAIL)
  - 개선 방향: 손절폭 최적화 (ATR multiplier 조정) 또는 신호 정밀도 향상
  - cmf에 추가 필터 검토: `cmf_threshold` 상향 (현재 기본값 확인 후 조정)
  - 목표: avg_pf ≥ 1.5 (Paper Sim 1개 이상 window PASS 가능하게)

#### E(실행): 4h 타임프레임 거래 수 부족 분석
- **핵심 이슈**: Paper Sim 4h에서 trades < 15가 전체 FAIL의 90% 차지
  - 4h 타임프레임: 60일 × 6봉/day = 360봉 → 거래 15건 달성이 어려움
  - 해결 방안 1: trades 기준을 4h에서 10으로 완화 (--timeframe 조건부)
  - 해결 방안 2: supertrend_multi, linear_channel_rev 등 신호 임계값 완화
  - `scripts/paper_simulation.py`에서 `MIN_TRADES_4H = 10` 옵션 검토

#### F(리서치): cmf 전략 PF 구조 심층 분석
- **배경**: cmf avg_pf=1.24 (Paper Sim 8w) vs Bundle OOS avg_pf=1.387
  - cmf 전략의 avg_win/avg_loss 비율 분석 필요
  - `src/strategy/cmf.py` 확인: TP/SL 구조, ATR multiplier
  - 실제 거래 기록(window별) JSON 분석으로 손실 패턴 파악
  - cmf Sharpe=1.25 (양호) + PF=1.24 (낮음) → 승률은 높지만 손실이 크다는 의미

### ⚠️ 주의 사항 (Cycle 294)
- **Bundle OOS 실행 시 --csv-dir data/historical 필수** — 합성 데이터는 2022 베어 과장
- **supertrend_multi no-trades 문제**: 3개 Supertrend 합의 조건이 4h에서 너무 엄격
  - Window 3개에서 아예 거래 없음 → 신호 완화 or min_oos_trades 유지
- **Paper Sim --verbose-windows 5 사용 권장**: cmf, supertrend_multi window 상세 확인용
  - `python3 scripts/paper_simulation.py --timeframe 4h --csv-dir data/historical --symbols BTC/USDT --verbose-windows 5`

### 핵심 메트릭 (Cycle 293)
- 테스트: **8392 passed** — 회귀 없음
- Paper Sim BTC 4h (8 windows): 0/22 PASS
  - rank1: cmf (score=68.3, Sharpe=1.25, PF=1.24, trades=23)
  - rank5: supertrend_multi (score=54.6, Sharpe=2.14, PF=1.22, trades=8)
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136, avg_pf=1.387
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116, avg_pf=2.475
  - **총 PASS: 2/5** — Cycle 292 대비 동일

### 주요 코드 변경 이력 (Cycle 293)
1. `scripts/paper_simulation.py` — `--verbose-windows N` 플래그 추가 (C 데이터)
   - `VERBOSE_WINDOWS: int = 0` 모듈 변수 + generate_report()에 window별 상세 테이블 삽입
   - top N 전략의 window별 Sharpe/PF/Trades/MDD/Pass/Fail-Reason 출력
2. `src/risk/circuit_breaker.py` — `reset_daily()` `preserve_price_history: bool = False` 추가 (B 리스크)
   - 4h 타임프레임에서 일 경계(00:00 UTC) rapid_decline 감지 윈도우가 끊기는 버그 수정
   - `reset_daily(balance, preserve_price_history=True)` 로 사용

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 2분 소요 (BTC/USDT만)
