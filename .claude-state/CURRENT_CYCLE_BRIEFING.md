# Current Cycle Briefing

_Last updated: 2026-06-28 (Cycle 364 완료)_

## 현재 상태 요약

- **완료 사이클**: 364
- **카테고리**: D(ML) + E(실행) + F(리서치)
- **1h PASS 연속 FAIL**: 48연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV)

## Cycle 364 핵심 성과

### ✅ 완료
1. **D(ML): dema_cross fast=7 실험 결과 검증**
   - fast=7 실측: Trades=24(+6, ✅ 기대됨), PF=1.00(↓ from 1.45), Sharpe=-0.69(↓ from 0.40)
   - 결론: fast=7은 역효과. DEMA 단기화 → 노이즈 증가, RSI필터가 binding constraint
   - `paper_simulation.py` dema_cross: fast=7→8 복원
   - `walk_forward.py` DEFAULT_GRIDS["dema_cross"] fast=[7,8,10,12]→[8,10,12] (7 제거)

2. **E(실행): fee/slippage 모델 검토**
   - fee_rate=0.00055 (Bybit taker 0.055%) ✅ 적정
   - slippage_pct=0.0005 (0.05%) ✅ 적정 (BTC 대형 거래소 현실적)
   - PaperConnector(0.05%) vs BacktestEngine(0.0005) 단위 컨벤션 불일치 발견 → 명문화
   - `src/exchange/paper_connector.py` 슬리피지 단위 주석 추가

3. **F(리서치): frama atr_period 그리드 버그 수정**
   - Cycle363에서 atr_period=[10,14,18] 그리드 추가했으나 factory에서 파라미터 전달 누락 발견
   - `walk_forward.py` optimize_frama factory: `atr_period=params.get("atr_period", 14)` 추가
   - 이제 atr_period 그리드가 실제 WFO에서 탐색됨

### 🔍 핵심 발견
- **dema_cross**: RSI direction filter가 trade quality의 binding constraint
  - fast 기간 단축(7) → 더 많은 진입 신호 → 하지만 RSI필터 통과 후 저품질 신호 잔류
  - fast=8/slow=20이 현재 최적. trades<15 x2 윈도우는 구조적 제약
- **frama**: WFO에서 atr_period 실제 탐색 시작 (Cycle365에서 효과 확인 예정)
- **slippage 컨벤션**: PaperTrader는 % 포인트(0.05), BacktestEngine은 소수(0.0005) — 동일 크기

## 다음 우선순위 (Cycle 365 — A+C+F, 365 mod 5 = 0)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | A(전략) | dema_cross 다음 개선 탐색 (slow 조정? 아니면 다른 전략?) |
| 2 | C(데이터) | frama atr_period WFO 효과 분석 (OOS Sharpe 변화 확인) |
| 3 | F(리서치) | 49연속 FAIL 구조 분석 — 1h PASS 전략 존재 가능성 탐색 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `scripts/paper_simulation.py` | dema_cross fast=7→8 복원 | 364 D |
| `src/backtest/walk_forward.py` | dema_cross DEFAULT_GRIDS fast=[7,8,10,12]→[8,10,12] | 364 D |
| `src/backtest/walk_forward.py` | optimize_frama factory atr_period 전달 버그 수정 | 364 F |
| `src/exchange/paper_connector.py` | 슬리피지 단위 컨벤션 주석 추가 | 364 E |
| `src/backtest/walk_forward.py` | frama DEFAULT_GRIDS atr_period=[10,14,18] 추가 | 363 F |
| `src/risk/circuit_breaker.py` | 독스트링/파라미터 주석 BTC 실증 데이터 반영 | 363 B |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 363 기준, Cycle 364 개별 검증 완료)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
- dema_cross 현재 파라미터: fast=8, slow=20, rsi_dir_filter=True
