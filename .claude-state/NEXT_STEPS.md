# Next Steps

_Last updated: 2026-05-26 (Cycle 217 B+D+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 217 완료
- 217 mod 5 = 2 → **B(리스크) + D(ML) + F(리서치)** ✅
- 다음 Cycle 218: **218 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치)**

### 🔥 Cycle 217 주요 성과
- **DrawdownMonitor.trailing_stop_signal()**: 단기/장기 MDD 속도 비교 조기 경보
- **PortfolioOptimizer.cf_var_position_limit()**: CF-VaR 기반 포지션 한도 배수
- **DualGateADWINMonitor.update_accuracy()**: EWMA(alpha=0.05) accuracy trend
- **paper_simulation CPCV 섹션**: run_cpcv_global() + 리포트 ML 예측 가능성 섹션
- **테스트**: 13개 신규 추가, 전체 7965개+ PASS

### 🎯 Cycle 218 권장 작업 (218 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): DataFeed 캐시 / 데이터 수집 개선
- `src/data/` 탐색 후 WebSocket feed 또는 캐시 관련 개선
- OHLCV 수집 시 중복 제거 로직 강화 (paper_simulation 페이지네이션 참고)
- 온체인 데이터 stub 확인: `src/data/` 내 VPIN/OrderFlow 정확도 검증

#### B(리스크): RiskManager CF-VaR 통합
- `src/risk/manager.py`: position_size 계산 시 cf_var_position_limit() 호출
  - KellySizer.estimate_cornish_fisher_var() → PortfolioOptimizer.cf_var_position_limit()
  - 두 모듈 연결하는 통합 로직
- DrawdownMonitor.trailing_stop_signal() → RiskManager에 trailing stop 강화 로직 추가

#### F(리서치): narrow_range 저거래 문제 해결 방안
- `src/strategy/narrow_range.py` 탐색: 신호 생성 조건 확인
- 4h봉에서 fold당 2-4 trades → 신호 조건 완화 또는 lookback 단축
- value_area va_mult [0.65-0.75] 범위 시뮬레이션: SharpeStd 감소 가능성

### ⚠️ 핵심 인사이트 (Cycle 217)
- **trailing_stop_signal 속도 비교**: short_rate/long_rate ≥ 1.5이면 낙폭 가속 중
- **EWMA early warning**: ADWIN 전 accuracy 0.50 미만 조기 감지 가능
- **CF-VaR position limit**: fat-tail_ratio > 1.0 + absolute CF-VaR > 3% 시 포지션 축소
- **narrow_range 저거래 4h**: fold당 2.8 trades 평균 → 신호 조건 완화 필요
- **value_area SharpeStd=6.589**: va_mult 범위 [0.65-0.75]로 축소 시 안정화 가능

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터 결과는 방향성 참고만 가능
- CPCV 실행 시 ML 학습 실패 (데이터 부족/합성 데이터 한계)

**상태**: Cycle 217 완료 → Cycle 218 C(데이터) + B(리스크) + F(리서치)
**최우선 과제**: RiskManager CF-VaR 통합 + narrow_range 저거래 해결
