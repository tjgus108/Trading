# Research Cycle 174: River ADWIN + Telegram Architecture

Date: 2026-04-21

---

## 1. ML Trading Bot 실패/성공 사례 — Concept Drift

### 실패 패턴
- **과거 레짐 오버피팅**: 2019~2022 데이터(COVID 고변동성)로 최적화된 전략이 2023 순방향 테스트에서 대규모 손실. 시장 레짐 변화에 전혀 대응 못함.
- **드리프트 미감지 정적 모델**: 한 번 학습 후 재학습 없이 운영 → 피처 분포 변화 누적 → 예측 품질 점진 저하. 대부분의 커뮤니티 크립토 봇이 이 패턴으로 실패.
- **False positive 미구분**: 계절성/노이즈를 진짜 드리프트로 오인 → 불필요한 재학습 반복 → 비용 증가 및 오버피팅 심화.
- **피드백 루프 미대응**: 모델 예측이 실제 시장에 영향을 미치면서 미래 분포가 변함(large bot 문제).

### 성공 패턴
- **Monitor → Detect → Retrain → Validate → Deploy** 파이프라인 자동화
- ADDM(Autoregressive Drift Detection Method): 성능 지표를 자동 감시, 임계값 초과 시 재학습 트리거. 드리프트를 수 시간~수일 전에 감지 가능.
- Walk-forward + 다중 레짐 검증: 8개 구간 중 3개 미만 통과 시 배포 금지.
- Kill-switch + 실시간 텔레메트리 의무화.

---

## 2. River ADWIN 실제 구현 사례

### ADWIN 기본 원리
- 가변 길이 슬라이딩 윈도우를 유지. 윈도우를 W₀(이전), W₁(최근) 두 서브윈도우로 분할.
- 두 서브윈도우의 평균이 통계적으로 다르면 드리프트 선언 → 오래된 데이터 자동 삭제.
- 핵심 파라미터 `delta`: false alarm 확률. 기본값 0.002. 낮을수록 민감(FP 증가), 높을수록 둔감.

### River API 사용법

```python
from river import drift

# 모델 출력 에러에 ADWIN 적용
adwin = drift.ADWIN(delta=0.002)

for prediction_error in stream:
    adwin.update(prediction_error)
    if adwin.drift_detected:
        # 재학습 트리거
        trigger_retrain()
```

### 피처별 ADWIN vs 모델 출력 ADWIN 비교

| 적용 대상 | 장점 | 단점 |
|---|---|---|
| 피처별 ADWIN | 어떤 피처가 드리프트하는지 파악, 선제적 감지 가능 | FP 많음, 피처 수만큼 감지기 필요 |
| 모델 출력(예측 오류) ADWIN | FP 적음, 실제 성능 저하와 직결 | 라벨 지연(label lag) 문제 — 실제 수익 확인까지 대기 필요 |

**권장 패턴**: 피처 ADWIN으로 조기 경보 + 모델 출력 ADWIN으로 최종 확정. 두 신호가 모두 발화 시에만 재학습 트리거 → FP 대폭 감소.

### 드리프트 감지 후 재학습 전략

- **전체 재학습(Full Retrain)**: 최근 N 기간 데이터로 재학습. 안정적이나 느림. 크립토에서 N=30~90일 추천.
- **Incremental Learning**: River의 `learn_one()` API 활용. 실시간 적응, 과거 망각(catastrophic forgetting) 위험.
- **Warm Start**: 기존 모델 가중치를 초기값으로 fine-tuning. 전체/증분 절충안.
- **Ensemble + Drift**: 드리프트 감지 시 신규 모델을 추가하고 가중치 조정(PWPAE 패턴).

### 금융 시계열 특이 주의사항

- `delta` 기본값(0.002)은 금융 데이터에서 FP 과다. 금융 시계열에는 `delta=0.05~0.1` 권장(논문: ar5iv 2103.14079).
- 크립토 24/7 연속 스트림에서는 윈도우 크기가 매우 커질 수 있어 메모리 관리 필요.
- 드리프트 감지 결과를 레짐 분류기(HMM 등)와 결합하면 계절성과 진짜 드리프트 구분 가능.

---

## 3. Telegram Bot 아키텍처 리서치

### Webhook vs Long Polling 비교

| 항목 | Long Polling | Webhook |
|---|---|---|
| 설정 난이도 | 쉬움, public URL 불필요 | HTTPS URL + SSL 필요 |
| 지연 | 폴링 주기만큼 지연 | 즉시 Push |
| 리소스 | 지속 HTTP 연결 유지 | 요청 수신 시에만 처리 |
| 스케일 | 단일 인스턴스 권장 (409 Conflict) | 로드밸런서 뒤에 다중 인스턴스 가능 |
| 트레이딩봇 추천 | 로컬 개발, 단일 서버 소규모 봇 | 프로덕션, 고가용성 필요 시 |

**핵심**: Long Polling + Webhook 동시 사용 불가. 한 토큰으로 두 프로세스가 polling 시 409 Conflict 발생.

### Rate Limit 정리

- **전역**: 30 msg/sec (봇 토큰 기준)
- **채팅별**: 1 msg/sec (같은 chat_id)
- **그룹 채팅**: 20 msg/min
- 초과 시 HTTP 429 응답 + `retry_after` 필드(초 단위) 반환

### 429 대응 패턴

```python
import asyncio
import random

async def send_with_retry(bot, chat_id, text, max_retries=5):
    base = 1.0
    for attempt in range(max_retries):
        try:
            await bot.send_message(chat_id, text)
            return
        except TelegramRetryAfter as e:
            wait = e.retry_after + random.uniform(0, 1)  # jitter
            await asyncio.sleep(wait)
        except Exception:
            wait = min(2 ** attempt * base, 60) + random.uniform(0, 1)
            await asyncio.sleep(wait)
```

### 알림 배치 전송 vs 즉시 전송

| 패턴 | 적합한 상황 | 구현 방법 |
|---|---|---|
| 즉시 전송 | 주문 체결, 긴급 알림, 손절 발동 | 직접 await send_message() |
| 배치 전송 | 정기 리포트, 다수 동시 알림 | asyncio.Queue + 워커 |
| 채팅별 FIFO 큐 | 고빈도 알림 + 429 per-chat 관리 | per-chat Queue, 429 시 해당 큐만 pause |

### 트레이딩봇 Telegram 권장 아키텍처

```
[이벤트 발생] → [priority queue]
                      ↓
            [dispatcher worker]
            - token bucket (25msg/s, burst 30)
            - per-chat FIFO
                      ↓
            [Telegram API]
            - 429 → retry_after sleep (해당 채팅만)
            - 200 → 다음 메시지
```

- **Webhook 프로덕션 필수 설정**: `secret_token`으로 위조 요청 차단, acknowledge 먼저 반환 후 outbound 메시지 별도 큐에서 처리(retry storm 방지).
- **asyncio-throttle** 또는 직접 token bucket 구현으로 전역 rate 제한 자체 적용.
- 429 발생 시 `retry_after`를 Redis에 저장 → 다중 워커 공유 → 중복 대기 방지.

---

## 핵심 인사이트 요약

- **ADWIN delta 금융 조정 필수**: 기본값 0.002는 크립토 시계열에서 FP 과다. 0.05~0.1 사용 권장.
- **피처 ADWIN + 출력 ADWIN 이중 게이트**: 두 신호 모두 발화 시에만 재학습 → FP 90%+ 감소 가능.
- **드리프트 후 Warm Start 전략**: 전체 재학습 vs 증분 학습의 절충. 최근 30~90일 데이터로 기존 모델 fine-tuning.
- **Telegram 즉시/배치 분리**: 체결/손절 알림은 즉시, 나머지는 per-chat FIFO 큐 + token bucket으로 429 완전 차단.
- **Webhook 프로덕션 룰**: acknowledge → 큐 → 발송 순서 엄수. retry storm 방지. secret_token 필수.

---

## 참고 링크

- [River ADWIN API](https://riverml.xyz/dev/api/drift/ADWIN/)
- [River Concept Drift Examples](https://riverml.xyz/0.8.0/examples/concept-drift-detection/)
- [Domain Specific Drift Detectors for Financial Time Series (arXiv)](https://ar5iv.labs.arxiv.org/html/2103.14079)
- [PWPAE Ensemble Concept Drift Adaptation](https://github.com/Western-OC2-Lab/PWPAE-Concept-Drift-Detection-and-Adaptation)
- [ADDM for Trading (QuantInsti)](https://blog.quantinsti.com/autoregressive-drift-detection-method/)
- [Telegram Rate Limits GramIO](https://gramio.dev/rate-limits)
- [Telegram 429 Fixes (TelegramHPC)](https://telegramhpc.com/news/574/)
- [Webhook vs Long Polling (grammY)](https://grammy.dev/guide/deployment-types)
- [Trading Bot Risks and Overfitting](https://petrvojacek.cz/en/blog/trading-bot-risks-and-tools/)
