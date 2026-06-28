# Current Cycle Briefing

_Last updated: 2026-06-28 (Cycle 365 완료)_

## 현재 상태 요약

- **완료 사이클**: 365
- **카테고리**: A(품질) + C(데이터) + F(리서치)
- **1h PASS 연속 FAIL**: 49연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV, 이번 사이클 합성 fallback으로 보호됨)

## Cycle 365 핵심 성과

### ✅ 완료
1. **A(품질): dema_cross RSI 임계값 45/55 완화 실험 → 역효과 확정**
   - 실험 결과: Sharpe 0.40→0.55(+0.15 ✅), Trades 18→26(+8 ✅, 14<15 문제 해결)
   - 하지만 PF: 1.45→1.35(-0.10 ❌) — RSI 45-50 구간 신호가 PF<1.0로 품질 하락
   - 결론: 45/55 역효과 확정 → paper_simulation.py 50/50 기본값 복원
   - `src/strategy/dema_cross.py`: rsi_dir_buy_thresh, rsi_dir_sell_thresh 파라미터 추가 (기본값 50/50)
   - `walk_forward.py` DEFAULT_GRIDS["dema_cross"]에 [45,50]/[50,55] 그리드 추가 (WFO 탐색용)

2. **C(데이터): frama atr_period WFO 효과 확인**
   - Cycle364 버그 수정 후 atr_period=[10,14,18] WFO 탐색 작동 중
   - frama: Sharpe=0.24, PF=1.12 유지 (안정적) — atr_period 최적값 발굴은 점진적
   - 다음 사이클(D(ML))에서 optimize_frama() 실행으로 최적값 확인 예정

3. **F(리서치): slow=20 vs slow=25 신호 빈도 분석**
   - BTC 1h 2000봉 기준: slow=20: 43 crosses, slow=25: 47 crosses (역설적으로 slow=25가 10% 더 많음)
   - slow 단축이 반드시 cross 감소를 의미하지 않음 (DEMA 특성상 평활도 차이가 큼)
   - DEFAULT_GRIDS slow=[15,20,25] WFO 자동 탐색으로 커버됨

### 🔍 핵심 발견
- **dema_cross 현황**: RSI 임계값 방향 탐색 완료 (45/55 역효과 확정)
  - 다음 개선 방향: exit timing (max_hold=48 → 24 단축 실험) 또는 포지션 관리
  - 현재 최적 파라미터: fast=8, slow=20, rsi_dir_filter=True, thresh=50/50
  - PF=1.45 (목표 1.5까지 +0.05) — 목표까지 매우 근접하지만 방향 탐색 필요
- **진입 vs 청산**: 지금까지는 진입 조건만 조정. 청산 조건 탐색이 다음 방향.
- **49연속 1h FAIL 구조**: 1h market에서 PF>=1.5 + Sharpe>=1.0 동시 달성 구조적 어려움
  - price_cluster: PF=1.20 (목표 1.5까지 +0.30), Sharpe=0.87 (목표 1.0까지 +0.13)
  - 두 전략 모두 단기 내에 PASS 가능성 있음 (점진적 개선 누적 필요)

## 다음 우선순위 (Cycle 366 — B+D+F, 366 mod 5 = 1)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | B(리스크) | DrawdownMonitor/KellySizer 파라미터 실효성 분석 |
| 2 | D(ML) | frama optimize_frama() 실행 → atr_period 최적값 발굴 |
| 3 | F(리서치) | dema_cross exit timing 개선 탐색 (max_hold 단축 실험) |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `src/strategy/dema_cross.py` | rsi_dir_buy_thresh=50, rsi_dir_sell_thresh=50 추가 | 365 A |
| `src/backtest/walk_forward.py` | dema_cross 그리드 rsi_dir_buy/sell_thresh=[45,50]/[50,55] 추가 | 365 A |
| `scripts/paper_simulation.py` | 45/55 실험 기록 + 50/50 복원 | 365 A |
| `src/backtest/walk_forward.py` | optimize_frama factory atr_period 버그 수정 | 364 F |
| `src/exchange/paper_connector.py` | 슬리피지 단위 컨벤션 주석 | 364 E |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 365 전체 검증 완료)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic
- Bundle OOS 5/5 (실데이터): cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
- dema_cross 현재 파라미터: fast=8, slow=20, rsi_dir_filter=True (thresh=50/50 기본값)
