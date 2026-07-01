# Current Cycle Briefing

_Last updated: 2026-07-01 (Cycle 379 완료)_

## 현재 상태

- **완료된 사이클**: 379
- **다음 사이클**: 380 (380 mod 5 = 0 → A+C+F)
- **연속 PASS 실패**: 64연속 (0/19 1h paper_sim)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 379 주요 결과

### D(ML): roc_ma_cross volume_filter 파라미터 추가
- `src/strategy/roc_ma_cross.py`: `volume_filter=False`, `vol_ratio_min=1.5` 파라미터 추가
  - 거래량 > volume_sma20 * 1.5 일 때만 BUY/SELL 신호 허용
- 실험 결과: **Sharpe=0.72(+0.38↑), PF=1.68(+0.68↑, 목표 1.5 달성!), Trades=10(<15 FAIL)**
- **핵심 발견**: volume_filter 개념 유효! PF 목표 달성했으나 임계값 1.5가 너무 공격적
- vol_ratio_min=1.5: trades 36→10 (73% 감소), PF 목표 달성, Sharpe↑
- **다음 방향**: vol_ratio_min=1.2 시도 (Cycle380 A)

### E(실행): 슬리피지 모델 검증
- BTC 1h HL ratio mean=1.496%, p25=0.915%
- 실제 BTC/USDT 스프레드: ~0.01-0.03% (유동성 충분)
- 현재 slippage_pct=0.05%/leg = 0.10% round-trip → **보수적/적정 (2-3배 과대 설정)**
- adaptive_slippage=True ATR 레짐 자동 조정 이미 최적
- **결론**: 슬리피지 설정 변경 불필요. 주석 추가로 근거 문서화.

### F(리서치): price_cluster min_cluster_strength_ratio dead param 확정
- `src/strategy/price_cluster.py`: `min_cluster_strength_ratio=0.0` 파라미터 추가
- 실험 결과: ratio=0.30 → **Sharpe=0.72(-0.15 악화), PF=1.18(유사), Trades=35(-6)**
- **결론**: 클러스터 강도 비율이 bounce 품질 예측 불가. dead param 확정.
- 다음 price_cluster 방향: `confirmation_bars` 탐색 (Cycle380 C)

## 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| paper_sim (1h BTC) | 0/19 PASS (64연속 실패) — dema_cross Sh=0.85, PF=1.38, Trades=26 |
| bundle_oos (4h BTC) | 5/5 PASS 유지 — cmf, ofi_v2, supertrend_multi, vwap_cross, value_area |

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `src/strategy/roc_ma_cross.py` | `volume_filter` + `vol_ratio_min` 파라미터 + 신호 필터 로직 (D) |
| `src/strategy/price_cluster.py` | `min_cluster_strength_ratio` 파라미터 + 필터 로직 (F) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["roc_ma_cross"] `volume_filter=[False,True]` + 주석 (D) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["price_cluster"] dead param 주석 (F) |
| `src/backtest/walk_forward.py` | `optimize_roc_ma_cross()` factory에 `volume_filter` 전달 (D) |
| `scripts/paper_simulation.py` | 슬리피지 검증 주석 + 실험 결과 문서화 (D+E+F) |

## Cycle 380 예고 (380 mod 5 = 0 → A+C+F)

- **A(품질)**: roc_ma_cross vol_ratio_min=1.2 실험 — trades ≥ 15 + PF ≥ 1.5 동시 만족 탐색
- **C(데이터)**: price_cluster `confirmation_bars` 파라미터 탐색 — bounce 후 N봉 확인 진입
- **F(리서치)**: roc_ma_cross volume_filter 임계값 시퀀스 분석 (1.2→1.5→2.0)
