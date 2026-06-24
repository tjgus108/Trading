# Current Cycle Briefing

_Last updated: 2026-06-24 (Cycle 350 완료)_

## 현재 상태 요약

- **완료 사이클**: 350
- **카테고리**: A(품질) + C(데이터) + F(리서치)
- **1h PASS 연속 FAIL**: 30연속 0/20 (BTC 실데이터 기준)
- **4h PASS**: 0/22 (trades<15 구조적 문제)
- **Bundle OOS**: 5/5 PASS 유지 (2026-06-23 결과, SSL 차단으로 재실행 불가)

## Cycle 350 핵심 성과

### ✅ 완료
1. **SOL 합성 데이터 보정**: vol_spike_prob 0.35→0.15, HIGH% 54%→39%
2. **4h 슬리피지 버그 수정**: `paper_simulation.py` BacktestEngine `timeframe=ACTIVE_TIMEFRAME` 누락 수정
   - 영향: SOL 4h 슬리피지 100% HIGH (잘못) → NORMAL (정상)
3. **price_cluster Bundle OOS 불가 확정**: avg_trades=10/60일 → ~2/fold, min_oos_trades=3 미달

### 🔍 핵심 발견
- **4h 슬리피지 버그**: BacktestEngine `timeframe` 미전달 시 1h 임계값 적용 → 4h 모든 슬리피지 과도 계산됨
  - 1h HIGH 임계값: ATR/close ≥ 3% → BTC 4h 3.0%, SOL 4h 5.4% 모두 HIGH 오분류
  - 수정 후 4h HIGH 임계값: ≥ 6% → 정상 분류
- **4h trades<15 구조적 한계**: 60일/4일(max_hold) = 15 이론상 최대, 실제는 8-10
  - Cycle 351 B(리스크)에서 4h min_trades 기준 8로 완화 검토 예정

## 다음 우선순위

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | B(리스크) | 4h paper_sim min_trades 15→8 완화 후 재실행 |
| 2 | D(ML) | 슬리피지 버그 수정 후 4h sim 재실행, Sharpe 변화 측정 |
| 3 | F(리서치) | 4h min_trades 완화 통계적 근거 리서치 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `scripts/generate_garch_csv.py` | SOL vol_spike_prob 0.35→0.15 | 350 C |
| `data/historical/synthetic/SOLUSDT/1h.csv` | 재생성 (HIGH% 39%) | 350 C |
| `scripts/paper_simulation.py` | BacktestEngine `timeframe=ACTIVE_TIMEFRAME` 추가 | 350 A |
| `scripts/paper_simulation.py` | `--max-hold-override` CLI 추가, 4h=24봉 자동 | 349 E |

## 환경 상태

- 테스트: 8434 passed, 23 skipped
- SSL 차단: bybit/binance/okx 모두 불가 → Bundle OOS 신규 실행 불가
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
