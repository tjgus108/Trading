# Trading Bot Status

_Last updated: 2026-04-20 (Cycle 159)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (전략 약점, 엔진 정상)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS (유일한 유효 경로)
- **ML 파이프라인**: ✅ 자동 재학습 + PFI + 예측 + live + calibration 분리 완비
- **Walk-Forward**: WFE > 0.5 + Trades >= 15 + MC p<0.05
- **테스트**: 7,100+ passed (risk 85, feed 93, exchange 98, trainer 39, FR/OI 24 포함)
- **리스크**: Kelly(레짐조정) + VaR + DrawdownMonitor(4단계 MDD) + VolTargeting + CircuitBreaker
- **실행**: TWAP + ML필터 + 레짐필터 + 레짐 포지션사이징 + CircuitBreaker
- **데이터**: 실데이터+GARCH합성+레짐캐시+품질모니터링+DataFeed CB+FR/OI 수집 완비

## 최근 작업 (Cycle 159)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| C (데이터) | ✅ | FR+OI 3계층 구현 (connector/feed/features), 24개 테스트 |
| B (리스크) | ✅ | MDD 4단계 서킷브레이커 (5%/10%/15%/20%), 31개 테스트 추가 |
| SIM | ✅ | calibration hold-out 분리 (60/15/15/10), val_acc 누출 수정 |
| F (리서치) | ✅ | 포지션 사이징 실패/성공 리서치, Kelly quarter-cap 권장 |

## 완료된 대응 (Cycle 140~159)
- ✅ 슬리피지 0.1% / MIN_TRADES 15 / MC Permutation gate
- ✅ Regime Detection + 레짐 필터 (RANGING 차단)
- ✅ CircuitBreaker + DrawdownMonitor (4단계 MDD: 5%/10%/15%/20%) + 경계값 테스트 완비
- ✅ Kelly Sizer 레짐 조정 + 레짐 기반 포지션 사이징
- ✅ VaR/CVaR 검증 + DataFeed 레짐 캐시
- ✅ ML 재학습 + 예측 + live 연동 + PFI 분석
- ✅ TWAP 검증 + 합성 데이터 GARCH 교체 + 품질 모니터링
- ✅ LSTM 버그 수정 + Drift Detector (PHT+CUSUM+AccuracyDriftMonitor)
- ✅ Triple Barrier + CPCV 구현 + AccuracyDriftMonitor live 연동
- ✅ DataFeed Circuit Breaker (cascading failure 방지)
- ✅ RF 과적합 수정 (min_samples_leaf + val_acc 누출)
- ✅ Exchange 모듈 테스트 완비 (connector + paper_connector 98개)
- ✅ Trainer 단위 테스트 39개 + calibration hold-out 분리
- ✅ FR delta + OI 파생 피처 수집/통합 (3계층)
- ✅ MDD 4단계 서킷브레이커 (MddLevel enum + size_multiplier)

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — ML 경로가 유일한 희망
- 다음 우선: SHAP 피처 선택, ExtraTrees 시도, XGBoost 앙상블
- Kelly quarter-cap + step-down 축소 구현 필요
- 레짐→사이징 레이어 연결 확장 필요
- live_paper_trader 7일 테스트 준비
