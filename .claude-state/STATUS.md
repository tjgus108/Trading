# Trading Bot Status

_Last updated: 2026-04-20 (Cycle 161)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (전략 약점, 엔진 정상)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS (유일한 유효 경로)
- **ML 파이프라인**: ✅ 재학습+PFI+예측+live+cal분리+SHAP선택+ExtraTrees 완비
- **Walk-Forward**: WFE > 0.5 + Trades >= 15 + MC p<0.05
- **테스트**: 7,300+ passed (risk 93+5, feed 93, exchange 98, trainer 49, FR/OI 24+25, kelly 77 포함)
- **리스크**: Kelly(quarter-cap+레짐+MDD step-down) + VaR + DrawdownMonitor(4단계) + VolTargeting + CircuitBreaker
- **실행**: TWAP + ML필터 + 레짐필터 + 레짐 포지션사이징 + CircuitBreaker
- **데이터**: 실데이터+GARCH합성+레짐캐시+품질모니터링+DataFeed CB+FR/OI 수집+E2E 검증 완비
- **라이브**: live_paper_trader 78% 준비 (917줄, 34개 테스트)

## 최근 작업 (Cycle 161)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| A (품질) | ✅ | connector.py 버그 2건 수정, drawdown 테스트 5건, 307 PASS |
| C (데이터) | ✅ | FR/OI E2E 통합 테스트 25개, 파이프라인 정상 |
| SIM (라이브) | ✅ | live_paper_trader 리뷰 78%, 최대 손실 한계 추가 권장 |
| F (리서치) | ✅ | Paper→Live 전환 사례, 킬 스위치/드리프트/슬리피지 |

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
- ✅ live_paper_trader 코드 리뷰 (78% 배포 준비)

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — ML 경로가 유일한 희망
- ⚠️ live_paper_trader 최대 손실 한계 미구현 (50% 자동 중단 필요)
- 다음 우선: XGBoost 앙상블, 최대 손실 한계 추가, live 7일 테스트
- 레짐별 피처 중요도 역전 대응 필요 (동적 파이프라인)
- min_accuracy 임계값 0.52→0.55 상향 권장
