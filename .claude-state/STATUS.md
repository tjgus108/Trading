# Trading Bot Status

_Last updated: 2026-04-20 (Cycle 165)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (전략 약점, 엔진 정상)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS (유일한 유효 경로)
- **ML 파이프라인**: ✅ 재학습+PFI+예측+live+cal분리+SHAP선택+ExtraTrees+XGBoost+PSI드리프트+PSI-AccDrift통합 완비
- **Walk-Forward**: WFE > 0.5 + Trades >= 15 + MC p<0.05
- **테스트**: 7,300+ passed (risk 93+5, feed 93, exchange 98, trainer 53+3skip, FR/OI 24+25, kelly 77, feature_builder 29, drift 53, backtest 48 포함)
- **리스크**: Kelly(quarter-cap+레짐+MDD step-down) + VaR + DrawdownMonitor(4단계) + VolTargeting + CircuitBreaker
- **실행**: TWAP + ML필터 + 레짐필터 + 레짐 포지션사이징 + CircuitBreaker
- **데이터**: 실데이터+GARCH합성+레짐캐시+품질모니터링+DataFeed CB+FR/OI+현실적 수수료(0.055%)+adaptive 슬리피지 완비
- **라이브**: live_paper_trader 90% 준비 (max_loss_pct+PSI통합+XGBoost, 37개 테스트)

## 최근 작업 (Cycle 165)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| D (ML) | ✅ | XGBoost model_type 추가 (fallback+early_stopping), 테스트 7개 |
| E (실행) | ✅ | PSI→AccuracyDriftMonitor 통합 (양방향 감지), 테스트 6개 |
| F (리서치) | ✅ | 모니터링 3계층 + Paper→Live 전환 체크리스트 |

## 완료된 대응 (Cycle 140~161)
- ✅ 슬리피지 0.1% / MIN_TRADES 15 / MC Permutation gate
- ✅ Regime Detection + 레짐 필터 (RANGING 차단)
- ✅ CircuitBreaker + DrawdownMonitor (4단계 MDD + cooldown 분리) + 경계값 테스트
- ✅ Kelly Sizer: 레짐 조정 + quarter-cap(0.25) + MDD step-down 통합
- ✅ VaR/CVaR 검증 + DataFeed 레짐 캐시
- ✅ ML: 재학습+예측+live+PFI+SHAP 피처 선택+ExtraTrees 옵션
- ✅ TWAP 검증 + 합성 데이터 GARCH 교체 + 품질 모니터링
- ✅ LSTM 버그 수정 + Drift Detector (PHT+CUSUM+AccuracyDriftMonitor)
- ✅ Triple Barrier + CPCV 구현 + AccuracyDriftMonitor live 연동
- ✅ DataFeed Circuit Breaker (cascading failure 방지)
- ✅ RF 과적합 수정 + calibration hold-out 분리 (60/15/15/10)
- ✅ Exchange 모듈 테스트 완비 (connector + paper_connector 98개)
- ✅ Trainer 테스트 49개 (SHAP+ExtraTrees 포함)
- ✅ FR delta + OI 파생 피처 수집/통합 (3계층) + E2E 검증 25개
- ✅ connector.py Python 3.7 호환 + Mock 호환 수정
- ✅ live_paper_trader max_loss_pct 구현 + min_accuracy 0.55 (85% 배포 준비)
- ✅ FeatureBuilder 테스트 29개 추가 (커버리지 갭 해소)
- ✅ 수수료 현실화: Bybit taker 0.055% 기본값, adaptive_slippage 레짐별 가변
- ✅ PSI 드리프트 모니터: input drift 감지 (PSI > 0.2 재학습 트리거)
- ✅ XGBoost 모델 옵션 추가 (미설치 시 RF fallback)
- ✅ PSI → AccuracyDriftMonitor 통합 (양방향 드리프트 감지)

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — ML 경로가 유일한 희망
- 다음 우선: XGBoost 다시간 앙상블 stacking (30/60/90일), live 7일 테스트
- 레짐별 피처 중요도 역전 대응 필요 (동적 파이프라인)
