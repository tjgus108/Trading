# Trading Bot Agent Team

리서치 기반 (TradingAgents 논문, arXiv 2512.02227, 실전 사례) 설계.

## 파이프라인 흐름

```
사용자/스케줄러
      │
 [orchestrator]  ← 메인 Sonnet, 전체 조율
      │
      ├─ [data-agent]       Haiku  시세 수집 + 지표 계산
      │
      ├─ [alpha-agent]      Sonnet 신호 생성 (Bull vs Bear 내부 토론)
      │
      ├─ [risk-agent]       Sonnet 포지션 사이징 + 서킷 브레이커  ← GATEKEEPER
      │
      ├─ [execution-agent]  Haiku  주문 실행 + 체결 확인  (risk APPROVED 후에만)
      │
      ├─ [backtest-agent]   Haiku  전략 검증 (라이브 전 필수)
      │
      ├─ [memory-agent]     Haiku  세션 간 상태 저장/복원
      │
      ├─ [researcher]       Haiku  코드베이스 탐색 (개발 보조)
      └─ [reviewer]         Haiku  코드 검토 (개발 보조)
```

## 에이전트별 역할 요약

| 에이전트 | 모델 | 핵심 역할 | 권한 |
|---|---|---|---|
| orchestrator | Sonnet | 파이프라인 조율, 작업 분배 | Agent 호출 가능 |
| data-agent | Haiku | OHLCV 수집, 지표 계산 | Read, Bash |
| alpha-agent | Sonnet | 신호 생성 (Bull/Bear 토론) | Read, Bash |
| risk-agent | Sonnet | 포지션 사이징, 게이트키퍼 | Read, Bash |
| execution-agent | Haiku | 주문 라우팅, 체결 확인 | Read, Bash |
| backtest-agent | Haiku | 백테스트, 전략 감사 | Read, Bash |
| memory-agent | Haiku | 상태 저장, 컨텍스트 요약 | Read, Write, Edit |
| researcher | Haiku | 코드 탐색 (개발용) | Read, Grep, Glob |
| reviewer | Haiku | 코드 검토 (개발용) | Read, Grep, Glob |

## 핵심 설계 원칙

1. **risk-agent는 항상 execution-agent 앞에** — 절대 스킵 불가
2. **LLM은 추론, 수치는 코드** — 에이전트가 직접 계산 안 함, 도구/코드 호출
3. **Bull-Bear 토론** — alpha-agent 내부에서 확증 편향 제거
4. **서킷 브레이커는 하드코드** — LLM 판단 아닌 config 기반 규칙
5. **backtest PASS 없이 라이브 없음** — backtest-agent FAIL이면 파이프라인 중단
6. **memory-agent로 세션 연속성** — 컨텍스트 오버플로우 시 복구 가능

## 사용 방법

```
# 전체 파이프라인 실행
orchestrator에게: "BTC/USDT 1h 신호 파이프라인 실행"

# 전략 검증만
backtest-agent에게: "src/strategy/ema_cross.py 백테스트 실행"

# 상태 복원
memory-agent에게: ".claude-state/ 읽고 현재 상태 요약"

# 코드 리뷰
reviewer에게: "src/risk/ 변경사항 검토"
```
