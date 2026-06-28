# Current Cycle Briefing

_Last updated: 2026-06-28 (Cycle 365 완료)_

## 현재 상태 요약

- **완료 사이클**: 365
- **카테고리**: A(품질) + C(데이터) + F(리서치)
- **1h PASS 연속 FAIL**: 49연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV)

## Cycle 365 핵심 성과

### ✅ 완료
1. **A(품질): dema_cross fast=8 복원 확인**
   - paper_sim 결과: Sharpe=0.40, PF=1.45, Trades=18 — Cycle363 기준값과 동일 ✅
   - fast=7→8 복원이 완전히 정상화됨 확인
   - FAIL 원인: trades=14<15 (x2윈도우), PF=0.85<1.5 (x1), Sharpe=-0.88 (x1)
   - RSI 방향 필터가 binding constraint 재확인

2. **A(품질)/F(리서치): rsi_dir_threshold 파라미터 추가**
   - `src/strategy/dema_cross.py`: `rsi_dir_threshold=50` 가변 파라미터 추가
   - BUY: RSI > threshold, SELL: RSI < (100-threshold)
   - threshold=45 실험 설정 (paper_simulation.py): 신호 10.1/60d → 13.4/60d (+32%)
   - Cycle366에서 PF/Sharpe 영향 검증 예정

3. **C(데이터): optimize_dema_cross() WFO 함수 추가**
   - DEFAULT_GRIDS["dema_cross"]는 Cycle356에 추가됐으나 함수가 없어 그리드 사문화
   - `src/backtest/walk_forward.py`에 `optimize_dema_cross()` 함수 추가
   - rsi_dir_threshold=[45,50] 그리드 포함 → WFO 탐색 가능

4. **F(리서치): slow=25 + threshold=45 신호 분석**
   - BTC 1h 실데이터: fast=8/slow=25/threshold=45 → 16.5/60d ← 항상 min_trades=15 초과
   - 구조적 trades 부족 해결 가능 조합 발견

### 🔍 핵심 발견
- **optimize_dema_cross() 누락 버그**: DEFAULT_GRIDS 추가만 하고 factory 함수를 추가하지 않으면 WFO가 실행되지 않음 (optimize_frama와 동일 패턴)
- **threshold=45 기대**: 신호 +32% 증가, PF 영향 미지수 — fast=7처럼 PF 악화 가능
- **slow=25 재탐색 가치**: threshold=45+slow=25 조합은 16.5/60d으로 trades 기준 통과 가능

## 다음 우선순위 (Cycle 366 — B+D+F, 366 mod 5 = 1)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | D(ML) | paper_sim 실행 → dema_cross threshold=45 결과 분석 |
| 2 | B(리스크) | DrawdownMonitor 실데이터 시나리오 점검 |
| 3 | F(리서치) | threshold=45 결과에 따라 slow=25 조합 탐색 결정 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `src/strategy/dema_cross.py` | rsi_dir_threshold=50 파라미터 추가 | 365 A |
| `src/backtest/walk_forward.py` | optimize_dema_cross() 함수 추가 | 365 C |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"] rsi_dir_threshold=[45,50] 추가 | 365 A/C |
| `scripts/paper_simulation.py` | dema_cross rsi_dir_threshold=45 실험 설정 | 365 A/F |

## 환경 상태

- 테스트: 8434 passed, 23 skipped ✅
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
- dema_cross 현재 파라미터: fast=8, slow=20, rsi_dir_filter=True, **rsi_dir_threshold=45 (실험 중)**
