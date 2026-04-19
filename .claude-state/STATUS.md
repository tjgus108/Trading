# Trading Bot Status

_Last updated: 2026-04-20 (Cycle 158)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (전략 약점, 엔진 정상)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS (유일한 유효 경로)
- **ML 파이프라인**: ✅ 자동 재학습 + PFI 분석 + 예측 + live 연동 완비
- **Walk-Forward**: WFE > 0.5 + Trades >= 15 + MC p<0.05
- **테스트**: 7,000+ passed (risk 54, feed 93, exchange 98, trainer 38 포함)
- **리스크**: Kelly(레짐조정) + VaR + DrawdownMonitor(레짐연동) + VolTargeting + CircuitBreaker(경계값 검증 완료)
- **실행**: TWAP + ML필터 + 레짐필터 + 레짐 포지션사이징 + CircuitBreaker
- **데이터**: 실데이터+GARCH합성+레짐캐시+품질모니터링+DataFeed CircuitBreaker 완비

## 최근 작업 (Cycle 158)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| E (실행) | ✅ | Exchange 모듈 테스트 98개 (connector 53 + paper 27 + 기타) |
| A (품질) | ✅ | 실패 테스트 2개 수정, trainer 테스트 38개 추가 |
| SIM (시뮬레이션) | ✅ | paper_simulation.py 타입힌트 버그 수정, 코드 리뷰 |
| F (리서치) | ✅ | ML봇 실패/성공 8건 리서치, FR delta+OI 피처 권장 |

## 완료된 대응 (Cycle 140~158)
- ✅ 슬리피지 0.1% / MIN_TRADES 15 / MC Permutation gate
- ✅ Regime Detection + 레짐 필터 (RANGING 차단)
- ✅ CircuitBreaker + DrawdownMonitor (HIGH_VOL 2% 한도) + 경계값 테스트 완비
- ✅ Kelly Sizer 레짐 조정 + 레짐 기반 포지션 사이징
- ✅ VaR/CVaR 검증 + DataFeed 레짐 캐시
- ✅ ML 재학습 + 예측 + live 연동 + PFI 분석
- ✅ TWAP 검증 + 합성 데이터 GARCH 교체 + 품질 모니터링
- ✅ LSTM 버그 수정 + Drift Detector (PHT+CUSUM+AccuracyDriftMonitor)
- ✅ Triple Barrier + CPCV 구현 + AccuracyDriftMonitor live 연동
- ✅ DataFeed Circuit Breaker (cascading failure 방지)
- ✅ RF 과적합 수정 (min_samples_leaf + val_acc 누출)
- ✅ Exchange 모듈 테스트 완비 (connector + paper_connector)
- ✅ Trainer 단위 테스트 38개 추가

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — ML 경로가 유일한 희망
- 리서치 확인: FR delta + OI 피처 추가가 최우선 (SSRN+gate 검증)
- XGBoost 사용 시 max_depth≤3 + early_stopping 필수
- calibration hold-out 분리 필요 (현재 val_acc 누출 가능성)
- 다음: ML 피처 확장 (FR delta, OI), calibration 분리, live 검증 7일
