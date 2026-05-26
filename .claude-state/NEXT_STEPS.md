# Next Steps

_Last updated: 2026-05-26 (Cycle 216 B+D+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 216 완료
- 216 mod 5 = 1 → **B(리스크) + D(ML) + F(리서치)** ✅
- 다음 Cycle 217: **217 mod 5 = 2 → B(리스크) + D(ML) + F(리서치)**

### 🔥 Cycle 216 주요 성과
- **KellySizer Cornish-Fisher VaR**: fat-tail 보정 파라메트릭 VaR (scipy 불필요, Acklam 근사)
- **CPCV 검증 통합**: WalkForwardTrainer.run_cpcv_validation() + TrainingResult.cpcv 필드
- **테스트**: 18개 신규 추가, 전체 7164개 PASS

### 🎯 Cycle 217 권장 작업 (217 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): PortfolioOptimizer 개선
- `src/risk/portfolio_optimizer.py`: CF-VaR 통합 (보유 자산의 CF-VaR 기반 포지션 한도 계산)
- DrawdownMonitor: `rolling_mdd_short_pct` 기반 early-warning 조기 경보 로직 추가
  - rolling_mdd_short >> rolling_mdd_pct이면 trailing_stop 강화 신호 발생

#### D(ML): CPCV 실무 파이프라인 연결
- `scripts/paper_simulation.py`에서 전략별 run_cpcv_validation() 결과 컬럼 추가
  - CPCV avg_test_acc 열을 리포트에 포함 → ML 기반 전략 추가 검증
- DualGateADWINMonitor: EWMA 기반 accuracy trend 추가
  - 현재: window deque → 개선: EWMA smooth accuracy (alpha=0.05)
  - 이유: ADWIN이 drift를 감지하기 전 EWMA로 early trend 확인 가능

#### F(리서치): 실거래소 데이터 검증 준비
- SSL 문제 우회 방법: ccxt proxy 설정 또는 --ssl-no-verify 옵션 검토
- supertrend_multi PF 실거래소 검증: 합성 PF=1.47 → 실거래소 PF 예측 범위
- value_area va_mult 파라미터: [0.65, 0.70, 0.75] 범위로 Sharpe std 감소 효과 시뮬레이션

### ⚠️ 핵심 인사이트 (Cycle 215~216)
- **CF-VaR**: BTC 음의 왜도(-1.2)+높은 첨도(6~10) → CF-VaR > Normal-VaR (30~50% 더 보수적)
- **CPCV + WFO 이중 검증**: train() → run_cpcv_validation() 순서로 과적합 2중 방어 가능
- **supertrend_multi PF=1.47**: 1.5 직전, 실거래소 데이터로 검증 우선
- **value_area SharpeStd=6.589**: 파라미터 범위 축소 (va_mult 현재 [0.5~0.9] → [0.65~0.75])
- **narrow_range 4h 저거래**: min_oos_trades=2로 낮추면 더 많은 fold 포함 가능 (run_bundle_oos --min-trades 2 옵션 활용)

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터 결과는 방향성 참고만 가능

**상태**: Cycle 216 완료 → Cycle 217 B(리스크) + D(ML) + F(리서치)
**최우선 과제**: PortfolioOptimizer CF-VaR 통합 + CPCV 파이프라인 연결
