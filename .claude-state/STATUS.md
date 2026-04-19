# Trading Bot Status

_Last updated: 2026-04-20 (Cycle 160)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (전략 약점, 엔진 정상)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS (유일한 유효 경로)
- **ML 파이프라인**: ✅ 재학습+PFI+예측+live+cal분리+SHAP선택+ExtraTrees 완비
- **Walk-Forward**: WFE > 0.5 + Trades >= 15 + MC p<0.05
- **테스트**: 7,200+ passed (risk 93, feed 93, exchange 98, trainer 49, FR/OI 24, kelly 77 포함)
- **리스크**: Kelly(quarter-cap+레짐+MDD step-down) + VaR + DrawdownMonitor(4단계) + VolTargeting + CircuitBreaker
- **실행**: TWAP + ML필터 + 레짐필터 + 레짐 포지션사이징 + CircuitBreaker
- **데이터**: 실데이터+GARCH합성+레짐캐시+품질모니터링+DataFeed CB+FR/OI 수집 완비

## 최근 작업 (Cycle 160)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| D (ML) | ✅ | SHAP 피처 선택 + ExtraTrees 옵션, 10개 테스트 추가 |
| E (실행) | ✅ | Kelly quarter-cap(0.25) + MDD step-down 통합, 20개 테스트 |
| SIM (검증) | ✅ | TWAP 통합 실패 3건 수정 (cooldown 분리), 전체 236 PASS |
| F (리서치) | ✅ | SHAP-select 패턴, 레짐별 피처 역전, RF vs ExtraTrees |

## 완료된 대응 (Cycle 140~160)
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
- ✅ FR delta + OI 파생 피처 수집/통합 (3계층)

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — ML 경로가 유일한 희망
- 다음 우선: XGBoost 앙상블, 레짐→피처가중치 동적 연동
- live_paper_trader 7일 테스트 준비
- 레짐별 피처 중요도 역전 대응 필요 (동적 파이프라인)
