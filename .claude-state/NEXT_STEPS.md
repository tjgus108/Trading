# Next Steps

_Last updated: 2026-06-05 (Cycle 275 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 275

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 273 | C+B+F | ADX 필터 제거(4h OOS 1.289로 개선), cmf threshold 0.05/-0.05 실험(소폭 개선) |
| 274 | D+E+F | vol_mult 그리드 상향, supertrend_multi 파라미터화, cmf threshold 복원→4h OOS PASS 달성 |
| 275 | A+C+F | CMF rsi_max_buy 파라미터화, wick_reversal min_wick_ratio 그리드 상향 [0.55-0.65] |

### 🎯 Cycle 276 작업 방향 (276 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): cmf rsi_max_buy 그리드 효과 검증
- rsi_max_buy [75,78,80] 추가 완료 (Cycle 275)
- run_bundle_oos 재실행하여 fold2 (2023-10~12) OOS Sharpe 개선 여부 확인
  - 기존: fold2 OOS=0.642, WFE=0.434 (barely PASS with 0.4 threshold)
  - 목표: WFE > 0.5 으로 개선 + avg OOS > 2.5 유지
- rsi_max_buy=80이 fold0,1 고Sharpe 구간(RSI 안정적)에서 역효과 없는지 확인

#### D(ML): wick_reversal min_wick_ratio 그리드 효과 검증
- min_wick_ratio [0.50,0.55,0.60]→[0.55,0.60,0.65] 변경 완료 (Cycle 275)
- run_bundle_oos 실행 후 fold1(-4.606), fold2(-2.046) 개선 여부 확인
  - 예상: 더 긴 wick 요구 → fold1,2 false reversal 차단 가능성
  - 위험: 거래 수 감소 (이미 7-8 trades per fold)
  - 거래 수가 5 이하로 떨어지면 min_wick_ratio 롤백 고려
- vol_mult 1.0-1.2 + min_wick_ratio 0.55-0.65 복합 효과 분석

#### F(리서치): wick_reversal 개선 방향 리서치
- 현재 문제: 추세장(2023-08~12)에서 Shooting Star SELL 오신호
- 리서치 방향:
  - Hammer/Shooting Star 패턴은 본질적으로 반전 전략 → 추세장에서 약함
  - 해결책 1: 레짐 필터 추가 (레인지/추세 구분) — ADX 제거 경험 있음
  - 해결책 2: Shooting Star 조건 강화 (close < sma20 * 1.01, 현재 1.03)
  - 해결책 3: wick_reversal을 bundle에서 제외하고 cmf+supertrend_multi로 대체 검토

### ⚠️ 긴급 사항
- **wick_reversal OOS std=4.842**: min_wick_ratio 그리드 상향 효과 확인 필수
  - fold1(2023-08) OOS=-4.606이 핵심 문제 — 볼륨+wick 필터로 차단 가능한지 확인
  - 만약 개선 없으면: Shooting Star `close < sma20 * 1.01` 조건 강화 검토
- **CMF fold2 WFE=0.434**: rsi_max_buy 완화로 개선 여부 다음 사이클 검증
  - 목표: fold2 WFE > 0.5 달성하여 안정적 PASS 확보

### 핵심 메트릭 (Cycle 275)
- 테스트: **8369 passed, 23 skipped** — 회귀 없음
- Paper Sim BTC 1h: 0/22 PASS
  - top: supertrend_multi +5.87%, cmf rank=13 AvgSharpe=-1.24
  - wick_reversal: rank=22, AvgSharpe=-2.79 (1h 기본 파라미터)
- Bundle OOS BTC 4h (5-fold): **1/5 PASS** (유지)
  - cmf: PASS ✅ avg OOS=2.508, std=1.888
  - wick_reversal: FAIL avg=1.200, std=4.842

### 주요 코드 변경 이력 (Cycle 275)
1. `src/strategy/cmf.py` — rsi_max_buy 파라미터 추가 (기본값 75.0, rsi < 75 하드코딩 제거)
2. `src/backtest/walk_forward.py` — DEFAULT_GRIDS["cmf"]에 rsi_max_buy: [75, 78, 80] 추가
3. `src/backtest/walk_forward.py` — DEFAULT_GRIDS["wick_reversal"] min_wick_ratio [0.50-0.60]→[0.55-0.65]

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv, 5-fold 4h 구조)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수
