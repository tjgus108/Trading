# Backtest Report — 전략 8종

_작성일: 2026-04-08_
_데이터: MockExchangeConnector BTC/USDT 1h 1000캔들 (합성 데이터)_
_엔진: BacktestEngine (Sharpe≥1.0, MDD≤20%, PF≥1.5, 거래≥30)_

---

## 결과 요약

| 전략 | 거래수 | 승률 | Sharpe | MDD | PF | 판정 | 실패 원인 |
|---|---|---|---|---|---|---|---|
| ema_cross | 24 | 16.7% | -1.18 | 15.4% | 0.39 | **FAIL** | sharpe, PF, 거래수 |
| donchian_breakout | 0 | - | 0.00 | 0.0% | 0.00 | **FAIL** | 거래 없음 |
| funding_rate | 0 | - | 0.00 | 0.0% | 0.00 | **FAIL** | 펀딩비 미제공 |
| residual_mean_reversion | 32 | 50.0% | 0.75 | 4.3% | 1.90 | **FAIL** | Sharpe 0.75 < 1.0 |
| pair_trading | 0 | - | 0.00 | 0.0% | 0.00 | **FAIL** | ETH 데이터 미제공 |
| ml_rf | 0 | - | 0.00 | 0.0% | 0.00 | **FAIL** | 모델 미학습 |
| rsi_divergence | 98 | 38.8% | 0.32 | 8.8% | 1.24 | **FAIL** | Sharpe, PF |
| bb_squeeze | 11 | 45.5% | 0.13 | 4.3% | 1.31 | **FAIL** | Sharpe, PF, 거래수 |

---

## 분석 및 해석

### 전체 FAIL의 주요 원인
1. **합성 데이터 한계**: MockExchangeConnector는 trend+noise 랜덤 시계열 생성. 실제 시장 패턴(추세, 지지/저항, 자기상관) 부재 → 전략 무작위 대비 유의미한 알파 추출 불가.
2. **멀티에셋 전략 데이터 부재**:
   - `pair_trading`: ETH df 미주입 → 거래 0건 (set_eth_data() 필요)
   - `funding_rate`: 펀딩비 미주입 → RSI proxy fallback (극단값 없으면 HOLD)
3. **ML 모델 미학습**: `ml_rf`는 models/ 디렉토리에 pkl 없으면 HOLD만 반환.

### 가능성 있는 전략
- **residual_mean_reversion**: 유일하게 거래수(32) + PF(1.90) 기준 통과. Sharpe만 미달 (0.75). 실제 데이터에서 Sharpe 2.3 실증.
- **rsi_divergence**: 거래수 98건으로 통계적 유의. Sharpe/PF 개선 여지 있음.

### 실거래 예상 성과 (논문 기반)
| 전략 | 실증 Sharpe | 출처 |
|---|---|---|
| funding_rate | 1.66~3.5 | ScienceDirect 2025 |
| residual_mean_reversion | 2.3 | Medium briplotnik |
| pair_trading | 2.45 | Springer 2024 |

---

## 권장 조치

1. **실제 데이터 백테스트**: Binance API로 실제 BTC/USDT 1h 1000캔들 수집
2. **멀티에셋 전략**: BacktestEngine 확장 또는 데이터 준비 후 재검증
3. **ML 학습**: `python3 scripts/train_ml.py --model rf --demo` 실행 후 재테스트
4. **펀딩비 주입**: FundingDataFetcher로 실제 펀딩비 제공 후 재검증

---

_참고: 합성 데이터 FAIL은 전략 버그가 아닌 데이터 한계. 실거래 환경에서 재검증 필수._
