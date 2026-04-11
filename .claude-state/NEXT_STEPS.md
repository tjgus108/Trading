# Cycle 32 - Category B: Risk Management 문서화

## 이번 작업 내용
`src/risk/README.md` 신규 작성 (코드 변경 없음).

### 생성 파일
**src/risk/README.md** (135줄)
- DrawdownMonitor 3층 서킷브레이커 (일일/주간/월간) 설명
- CircuitBreaker 다층 차단 조건 및 size_multiplier 표 정리
- KellySizer Risk-Constrained Half-Kelly 공식 정리
- RiskManager evaluate() 처리 순서, config.yaml 매핑 표
- VolTargeting 공식 및 사용법
- PortfolioOptimizer 3가지 방법론 정리
- RiskResult 출력 구조

## 다음 단계
- RiskManager와 DrawdownMonitor/CircuitBreaker(circuit_breaker.py) 통합 연결 검토
- VolTargeting을 RiskManager.evaluate()에 연동하는 옵션 추가 고려
