# Next Steps

_Last updated: 2026-05-27 (Cycle 219 C+B+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 219 완료
- 219 mod 5 = 4 → **C(데이터) + B(리스크) + F(리서치)** ✅
- 다음 Cycle 220: **220 mod 5 = 0 → D(ML) + E(실행) + F(리서치)**

### 🔥 Cycle 219 주요 성과
- **RiskManager CF-VaR 체인 완성**: KellySizer → PortfolioOptimizer → RiskManager 포지션 축소
- **RiskManager trailing_stop 통합**: trailing_stop_signal() True 시 포지션 50% 축소
- **DataFeed 중복 타임스탬프 제거 + 레짐별 캐시 만료 + 스테일 캐시 자동 무효화**
- **VPIN 극단 불균형 감지**: validate_extreme_imbalance()
- **narrow_range 신호 3~4배 증가**: NR_SCAN_WINDOW=3, ATR 0.95, NR봉 기준 돌파

### 🎯 Cycle 220 권장 작업 (220 mod 5 = 0 → D(ML) + E(실행) + F(리서치))

#### D(ML): EWMA early warning 활용 + 모델 개선
- DualGateADWINMonitor EWMA accuracy < 0.50 감지 시 자동 재학습 트리거 로직 검토
- WalkForwardTrainer CPCV 결과 → 전략 선별 자동화 검토

#### E(실행): PaperTrader 실전 통합 검증
- PaperTrader에 RiskManager 새 기능(CF-VaR, trailing_stop) 연결 확인
- 플래시 크래시 circuit breaker: 15분 내 -10% 감지 → 신규 진입 중단 (리서치 권장)
- orchestrator RiskManager 생성 시 kelly_sizer / drawdown_monitor 주입

#### F(리서치): 레짐 필터 레이어 + 실전 데이터 검증 방안
- base.py generate() 전 단계 레짐 체크 레이어 설계 (구현 전 리서치)
- narrow_range 개선 효과 실데이터 검증 방안 (Bybit 데이터 필요)
- Multi-regime adaptive 전략 트렌드 추가 조사

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터 결과는 방향성 참고만 가능

**상태**: Cycle 219 완료 → Cycle 220 D(ML) + E(실행) + F(리서치)
**최우선 과제**: PaperTrader에 CF-VaR/trailing_stop 연결 + 플래시 크래시 circuit breaker
