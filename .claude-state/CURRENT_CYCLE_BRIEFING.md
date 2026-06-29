# Current Cycle Briefing

_Last updated: 2026-06-29 (Cycle 368 완료)_

## 현재 상태 요약

- **완료 사이클**: 368
- **카테고리**: E(실행) + A(품질) + F(리서치)
- **1h PASS 연속 FAIL**: 53연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 기준, Cycle367)

## Cycle 368 핵심 성과

### ✅ 완료

1. **E(실행): PaperConnector use_tiered_slippage 분석 및 테스트**
   - False(기본): slippage_pct=0.05% 플랫 → BTC/SOL 동일 슬리피지
   - True: BTC(large)=0.05%, SOL(mid)=0.20% 차등 적용
   - 핵심 발견: slippage는 P&L에만 영향, 신호 생성과 무관 → paper_sim trades 수 영향 없음
   - `tests/test_exchange.py`에 `TestPaperConnectorTieredSlippage` 클래스 추가 (+6 테스트)

2. **A(품질): optimize_dema_cross() 엣지케이스 테스트 추가**
   - `test_optimize_dema_cross_single_window`: n_windows=1 단일 윈도우 (엣지케이스)
   - `test_optimize_dema_cross_returns_result_fields`: result 구조 확인 (avg_oos_sharpe 필드명 확인)
   - 총 2개 테스트 추가

3. **F(리서치): roc_ma_cross ma_period=5 실험 → 역효과 확정**
   - 결과: Sharpe=-0.91, PF=1.00, Trades=34, rank15
   - 비교: ma=3 → Sharpe=0.34, rank2
   - 결론: ma 스무딩 강화 = 신호 지연 → roc_ma_cross PF 개선 실패
   - paper_simulation.py 기본값(ma=3) 복원 완료

### 🔍 핵심 발견
- **roc_ma_cross ma 방향 완전 소진**: ma=3(rank2/Sh=0.34) vs ma=5(rank15/Sh=-0.91)
  - 다음 탐색: roc_period=10 (짧은 ROC → 빠른 신호, 빈도 ↑ 가능)
- **PaperConnector tiered_slippage**: use_tiered_slippage=False(기본값) 유지 권장
  - SOL 합성 데이터 slippage HIGH(39%) 이미 synthetic 특성 — tiered 적용해도 동일 문제
  - 실 거래 투입 시에는 True로 전환 (BTC 0.05%, SOL 0.20%)
- **53연속 FAIL**: 1h 구조적 한계 지속 — 4h Bundle OOS로 보완 (5/5 PASS)

## 다음 우선순위 (Cycle 369 — D+E+F, 369 mod 5 = 4)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | D(ML) | dema_cross dist_pct=0.003 또는 rsi_dir_threshold=40 실험 |
| 2 | E(실행) | walk_forward optimize_dema_cross() 호출 시간 프로파일링 |
| 3 | F(리서치) | roc_ma_cross roc_period=10 실험 (빠른 신호, 빈도 ↑ 기대) |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `tests/test_exchange.py` | PaperConnector tiered_slippage 6개 테스트 추가 | 368 E |
| `tests/test_phase_d.py` | optimize_dema_cross 엣지케이스 2개 테스트 추가 | 368 A |
| `scripts/paper_simulation.py` | roc_ma_cross ma=5 실험 주석 + 복원 | 368 F |

## 환경 상태

- 테스트: 전체 **8457** passed (+8 from 8449)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5 (Cycle367 실데이터 기준): cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=2.64+), vwap_cross(Sh=2.47+), value_area
- dema_cross 현재 파라미터: fast=8, slow=20, rsi_dir_filter=True, rsi_dir_threshold=45 (확정)
- roc_ma_cross 현재: ma_period=3(기본값), roc_period=12 — ma 방향 탐색 완료
