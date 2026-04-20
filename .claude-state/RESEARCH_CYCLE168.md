# Cycle 168 Research — Health Check / Heartbeat 패턴 + 봇 실패 심화

_작성일: 2026-04-20_

---

## 1. 실시간 모니터링 실패로 인한 손실 사례

### 사례 #1: Hyperliquid API 27분 장애 (2025.07)
- 장애 시각: 14:20~14:47 UTC
- 결과: 오픈 포지션 청산 불가, 사용자가 포지션 보유 강제 유지
- 교훈: API 장애 시 봇이 독립적으로 "포지션 동결 감지 → 알림 + 수동 개입 유도"를 수행해야 함
- 출처: [TradersUnion](https://tradersunion.com/news/cryptocurrency-news/show/404781-hyperliquid-api-failure/)

### 사례 #2: XTB 플랫폼 장애 (수 시간)
- 결과: 포지션 청산 불가 → 시장 노출 지속, 손실 발생
- 교훈: 거래소 장애 시 exchange-side stop-loss만 믿으면 안 됨. 봇 레벨에서도 독립적 kill-switch 필요
- 출처: [FinanceMagnates](https://www.financemagnates.com/forex/brokers/xtb-platform-outage-leaves-traders-unable-to-close-positions-for-hours/)

### 사례 #3: 2025년 5월 플래시 크래시 ($2B 강제 청산)
- AI 봇들이 3분 만에 $2B 자산을 시장가로 매도, 시장 하락 가속
- 서킷브레이커 없이 정상 조건 기반 봇이 이상 변동성에서 오작동
- 교훈: 변동성 서킷브레이커 + ATR spike 감지 시 신호 중단 필요

### 사례 #4: 모니터링 단절 → 누적 손실 ("Silent Failure")
- API 오류가 조용히 발생, 포지션 미청산 또는 중복 주문 발생
- 교훈: missed fill, rising slippage, repeated API errors를 Health Check로 포착해야 함

### 사례 #5: Tyler Capital (2017) — 해저 케이블 단절
- 봇은 계속 실거래했으나 운영자는 모니터링 단절로 인지 불가
- 교훈: 봇 자체와 모니터링 인프라를 독립 경로로 분리해야 함

---

## 2. Health Check / Heartbeat 표준 패턴

### 2-1. Heartbeat 기본 구조

| 컴포넌트 | 설명 |
|----------|------|
| **Heartbeat Sender** | 봇이 주기적으로 외부 엔드포인트로 ping 발송 |
| **Heartbeat Monitor** | 일정 시간 내 ping 미수신 시 알림 트리거 |
| **Health Endpoint** | REST `/health` 또는 `/ping` 응답 — 마지막 heartbeat 시각 + 오류 목록 반환 |
| **sd_notify** | systemd 환경에서 keep-alive 신호 (Freqtrade 지원) |

### 2-2. 권장 인터벌

| 체크 종류 | 권장 주기 | 비고 |
|-----------|-----------|------|
| **API liveness ping** | 5분 | 거래소 REST 응답 확인 |
| **WebSocket heartbeat** | 10~30초 | PING/PONG — Bybit 10초, 일반 30초 |
| **데이터 지연 감지** | 1분 | 마지막 캔들 타임스탬프 체크 |
| **포지션 일관성 체크** | 5분 | 봇 내부 상태 vs 거래소 실제 포지션 비교 |
| **Telegram heartbeat 알림** | 1시간 | "봇 정상 작동" 확인 메시지 |
| **Watchdog 타이머** | 15분 | 봇이 이 시간 내 리셋 안 하면 재시작 트리거 |

### 2-3. 추적해야 할 핵심 메트릭

```
필수 메트릭:
  - api_latency_ms          : REST API 응답 시간 (임계값 2000ms)
  - last_candle_age_sec     : 마지막 캔들 수신 후 경과 시간 (임계값 120s)
  - position_mismatch       : 봇 내부 포지션 ≠ 거래소 실제 포지션 (bool)
  - consecutive_api_errors  : 연속 API 실패 횟수 (임계값 5)
  - daily_loss_pct          : 일간 손실률 (임계값 max_loss_pct)
  - open_order_age_sec      : 미체결 주문 대기 시간 (임계값 60s)
  - data_feed_lag_sec       : 데이터 피드 지연 (임계값 300s)

성능 메트릭:
  - sharpe_rolling_7d       : 7일 롤링 샤프지수
  - pf_rolling_7d           : 7일 롤링 PF
  - slippage_ratio          : 실제 체결가 vs 예상 체결가 비율
```

---

## 3. API 장애 시 Graceful Degradation 전략

### 3-1. 장애 대응 3단계

```
Level 1 — API 응답 지연 (latency > 2s):
  → 신규 주문 중단 (기존 포지션 유지)
  → Telegram 경고 발송
  → 캐시된 마지막 가격으로 stop-loss 계산 지속

Level 2 — API 연속 실패 (≥ 5회):
  → 모든 신규 진입 차단
  → 거래소 사이드 stop-loss 확인 (exchange-set SL)
  → 15초마다 재연결 시도 (exponential backoff)

Level 3 — 완전 단절 (> 5분 응답 없음):
  → Kill Switch 트리거: 모든 미체결 주문 취소
  → 포지션 청산 시도 (시장가)
  → 청산 실패 시 exchange-side stop으로 fallback
  → 즉시 Telegram Critical 알림 + 운영자 수동 개입 요청
```

### 3-2. Circuit Breaker 패턴

```
상태: CLOSED → OPEN → HALF-OPEN → CLOSED

CLOSED (정상): API 호출 허용
OPEN (차단): 오류율 > 임계값 시 자동 전환, 모든 API 호출 즉시 거부
HALF-OPEN (탐색): 일정 시간 후 소수 호출 허용 → 성공 시 CLOSED, 실패 시 OPEN 복귀

임계값 권장: 5회 연속 실패 → OPEN 전환
복구 대기: 30초 후 HALF-OPEN 시도
```

---

## 4. 자동 재연결 Backoff 패턴

### 4-1. Exponential Backoff with Full Jitter

```python
# 개념 코드 (구현 금지 — 리서치 목적)
def calc_backoff(attempt, base=1.0, max_delay=30.0):
    delay = min(base * (2 ** attempt), max_delay)
    jitter = random.uniform(0, delay)  # Full Jitter
    return jitter

# 시도별 최대 대기 시간 예시:
# attempt 0: 0 ~ 1s
# attempt 1: 0 ~ 2s
# attempt 2: 0 ~ 4s
# attempt 3: 0 ~ 8s
# attempt 4: 0 ~ 16s
# attempt 5+: 0 ~ 30s (cap)
```

### 4-2. WebSocket 재연결 권장값

| 파라미터 | 권장값 | 근거 |
|----------|--------|------|
| base_delay | 1.0s | WebSocket 표준 |
| max_delay | 30s | 서버 과부하 방지 |
| max_attempts | 10회 | 이후 Critical 알림 |
| jitter_type | Full Jitter | Thundering Herd 방지 |
| ping_interval | 10~30s | Bybit: 10s, 일반: 30s |
| pong_timeout | 10s | 미응답 시 재연결 트리거 |

### 4-3. 재연결 후 필수 작업

1. REST snapshot으로 order book 상태 재동기화
2. 포지션 일관성 재확인 (내부 상태 vs 거래소)
3. 미체결 주문 목록 재조회
4. 마지막 캔들 데이터 갭 채우기

---

## 5. 성공적인 봇 운영자들의 모니터링 스택

### 5-1. 표준 스택 구성

| 레이어 | 도구 | 역할 |
|--------|------|------|
| **메트릭 수집** | Prometheus | 시계열 메트릭 pull |
| **시각화** | Grafana | 실시간 대시보드 |
| **봇 통합** | freqtrade-dashboard | Grafana+Prometheus+Freqtrade |
| **알림** | Telegram Bot API | Critical/Warning/Info 3계층 |
| **Uptime** | UptimeRobot | Heartbeat 엔드포인트 외부 감시 |
| **프로세스** | systemd + sd_notify | 봇 프로세스 관리 |

### 5-2. Grafana 핵심 대시보드 패널

```
Panel 1: PnL (누적 + 일간)
Panel 2: Sharpe/PF 롤링 7일
Panel 3: API 레이턴시 p50/p99
Panel 4: 연속 오류 횟수
Panel 5: 포지션 현황 (봇 내부 vs 거래소)
Panel 6: 데이터 피드 지연
Panel 7: 일간 손실률 vs max_loss_pct 한도
Panel 8: 슬리피지 비율 (실제 vs 백테스트 가정)
```

### 5-3. Telegram 알림 3계층

```
CRITICAL (즉시 전송, 소리):
  - API 5분+ 완전 단절
  - 포지션 불일치 감지
  - max_loss_pct 초과
  - Kill Switch 발동

WARNING (즉시 전송, 무음):
  - API 레이턴시 > 2s
  - 데이터 피드 > 5분 지연
  - 연속 오류 3회
  - 슬리피지 가정치 2배 초과

INFO (배치, 1시간 주기):
  - Heartbeat "봇 정상 작동"
  - 일간 PnL 요약
  - 신호 발생/체결 이력
```

---

## 6. 우리 프로젝트 적용 방향 (NEXT_STEPS #13, #14)

### 현재 상태
- NEXT_STEPS #13: Telegram 알림 — Critical/Silent 3계층 (미구현)
- NEXT_STEPS #14: Health check 루프 — 5분 liveness + 데이터 지연 감지 (미구현)

### 구현 순서 권장

```
Phase 1 — Health Check 루프 (#14 우선):
  1. HealthChecker 클래스: API ping, 캔들 지연, 포지션 일관성
  2. 5분 주기 비동기 루프
  3. 상태 레지스터: HEALTHY / DEGRADED / CRITICAL
  4. 장애 레벨별 자동 대응 (신호 차단 / Kill Switch)

Phase 2 — Telegram 알림 (#13):
  1. TelegramNotifier: CRITICAL / WARNING / INFO 3계층
  2. HealthChecker 이벤트 → Telegram 연결
  3. 1시간 heartbeat ping

Phase 3 — Reconnection Logic:
  1. Exponential backoff (base=1s, max=30s, full jitter)
  2. 재연결 후 snapshot 재동기화
  3. WebSocket ping/pong 10~30초 주기
```

### 핵심 설계 원칙
- Kill Switch는 메인 트레이딩 로직과 **독립** 실행 (오작동하는 봇이 kill switch를 막으면 안 됨)
- Exchange-side stop-loss는 API 장애 시 최후 보루 — 항상 설정
- 재연결 중에도 기존 포지션 모니터링 지속

---

## 요약 (200단어 이내)

2025년 Hyperliquid API 27분 장애, XTB 수 시간 장애, 2025년 5월 플래시 크래시 $2B 청산 사례에서 공통점은 "봇이 이상 상황을 감지하지 못했다"는 것이다.

Health Check 핵심: API liveness 5분 주기, WebSocket heartbeat 10~30초, 포지션 일관성 5분 주기, 데이터 지연 감지 1분, Watchdog 타이머 15분. 추적 메트릭은 api_latency_ms, last_candle_age_sec, position_mismatch, consecutive_api_errors, daily_loss_pct.

Graceful Degradation은 3단계: (1) 지연 감지 → 신규 주문 중단, (2) 연속 실패 → 진입 차단 + 재연결, (3) 완전 단절 → Kill Switch + 포지션 청산.

재연결 backoff 권장값: base=1s, max=30s, full jitter, 최대 10회. 재연결 성공 후 반드시 REST snapshot으로 상태 재동기화 필요.

성공 운영자 스택: Prometheus + Grafana + Telegram. Kill Switch는 트레이딩 로직과 독립 실행, exchange-side stop-loss는 API 장애 최후 보루로 항상 유지.

우리 NEXT_STEPS #14(Health Check) → #13(Telegram) → Reconnection 순으로 구현 권장.

---

## 출처

- [Hyperliquid API 27분 장애](https://tradersunion.com/news/cryptocurrency-news/show/404781-hyperliquid-api-failure/)
- [XTB 플랫폼 장애](https://www.financemagnates.com/forex/brokers/xtb-platform-outage-leaves-traders-unable-to-close-positions-for-hours/)
- [트레이딩봇 실패 원인](https://www.fortraders.com/blog/trading-bots-lose-money)
- [Graceful Degradation Playbook](https://medium.com/@mota_ai/building-ai-that-never-goes-down-the-graceful-degradation-playbook-d7428dc34ca3)
- [WebSocket Reconnection Exponential Backoff](https://dev.to/hexshift/robust-websocket-reconnection-strategies-in-javascript-with-exponential-backoff-40n1)
- [Freqtrade Health Check 이슈](https://github.com/freqtrade/freqtrade/issues/7299)
- [freqtrade-dashboard (Grafana+Prometheus)](https://github.com/thraizz/freqtrade-dashboard)
- [Blockchain Monitoring Best Practices](https://uptimerobot.com/blog/blockchain-monitoring/)
- [Altrady 7 Hidden Risks](https://www.altrady.com/blog/crypto-bots/7-hidden-risks)
- [Amplework AI Bot Failures](https://www.amplework.com/blog/ai-trading-bots-failures-how-to-build-profitable-bot/)
