# Current Cycle Briefing

_Cycle 338 | 2026-06-21 | C(데이터) + B(리스크) + F(리서치)_

## 완료된 작업

### C(데이터): ETH/SOL 합성 데이터 품질 확인

- ETH/SOL synthetic CSV 모두 정상: rows=12000, NaN=0, OHLC_invalid=0
- 심볼별 전략 성능 분산 원인: 데이터 품질 문제 아님, synthetic 특성(평균복귀 성향) 차이
- price_cluster BTC Sharpe=0.90 vs ETH -1.51: BTC-calibrated 전략이 ETH synthetic에서 작동 안 함

### B(리스크): TP=2.5 실험 + 2단계 손실 스케일링

1. `paper_simulation.py`에 `--atr-multiplier-tp` CLI 옵션 추가
2. TP=2.5 vs TP=3.5 비교 (BTC, price_cluster/roc_ma_cross):
   - TP=2.5 확연히 더 나쁨 (price_cluster Sharpe 0.90→0.15, roc_ma_cross 0.25→0.19)
   - 결론: TP=3.5 확정. BEP WR 38%가 실측 WR 37-40%에 너무 근접
3. `src/backtest/engine.py` 2단계 연속 손실 스케일링:
   - 기존: N손실 시 50% 단일 스텝
   - 변경: N/2손실→75%, N손실→50% (2단계 점진적 축소)
   - threshold=5 기준: 0-1손실 100%, 2-4손실 75%, 5+손실 50%
   - roc_ma_cross Sharpe +0.07, MDD -1.2%p / price_cluster MDD -1.0%p

### F(리서치): 윈도우별 레짐 분석 (verbose-windows)

- `--verbose-windows` 옵션으로 price_cluster/roc_ma_cross 8개 윈도우 분석
- **price_cluster**: W6(sideways, Sharpe=3.17), W8(bull, Sharpe=2.23)만 PASS
  - W5(sideways): Sharpe=0.98 — 문턱값 0.02 미달 근접 FAIL
- **roc_ma_cross**: W1(bull, 4.39), W2(bull, 3.51)만 PASS, W5(sideways)=-3.91 참사
- 구조적 결론: 18사이클 0/20 PASS = 시장 국면 불일치. 훈련 레짐 ≠ 테스트 레짐

## 시뮬레이션 결과

| 항목 | 값 |
|------|-----|
| 테스트 | 8425 passed, 23 skipped (회귀 없음) |
| Paper Sim BTC 1h (20전략, 8windows) | **0/20 PASS** (18사이클 연속) |
| rank1 price_cluster | Sharpe=0.84, Return=+4.82%, MDD=9.8%, 1/8 |
| rank2 roc_ma_cross | Sharpe=0.32, Return=+2.78%, MDD=8.2%, 2/8 |
| Bundle OOS BTC 4h (5전략) | **5/5 PASS** (유지) |
| Bundle rank1 OFI_v2 | avg=4.345, std=0.907 |

## 코드 변경 사항

| 파일 | 변경 내용 |
|------|---------|
| `scripts/paper_simulation.py` | `--atr-multiplier-tp` CLI 옵션 추가 |
| `src/backtest/engine.py` | 2단계 연속 손실 스케일링 (N/2→75%, N→50%) |

## 다음 Cycle 339 (mod 5=4 → D(ML) + E(실행) + F(리서치))

- **D(ML)**: MarketRegimeDetector로 8개 윈도우 레짐 레이블 분석 → ADX 패턴에서 신호 필터 기준 도출
- **E(실행)**: 슬리피지 레짐 분포 재분석 (ETH high-slippage 62.7% 영향 정량화)
- **F(리서치)**: 레짐 전환 조기 감지 방법론 리서치 (ADX 방향성, implied vol)
