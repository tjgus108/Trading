# 🎯 Master Plan — 트레이딩 봇 개선 로드맵

_Last updated: 2026-04-11_
_이 파일은 5시간마다 실행되는 스케줄러가 읽어서 작업을 배정합니다._

## ⚠️ 핵심 원칙 — 균형 유지

**금지 사항:**
- ❌ 새 전략 추가 (이미 355개 등록됨, 더 이상 추가 금지)
- ❌ 한 카테고리에 2 사이클 이상 연속 집중

**권장 사항:**
- ✅ 6개 카테고리를 로테이션으로 순환
- ✅ 각 사이클마다 리서치 1건 포함 (트레이딩봇 실패/성공 케이스)
- ✅ 매 사이클 STATUS.md, WORKLOG.md 업데이트 → push

---

## 📅 작업 카테고리 (로테이션)

### Category A — Quality Assurance (품질)
- 전략 백테스트 품질 재검증
- 중복/저성능 전략 추가 정리
- 테스트 커버리지 향상
- 기존 실패 테스트 수정 (`pair_trading` chained assignment 등)
- **담당 에이전트**: `backtest-agent`, `reviewer`

### Category B — Risk Management (리스크)
- DrawdownMonitor 로직 개선
- Kelly Sizer 파라미터 튜닝
- CircuitBreaker 룰 확장
- VaR/CVaR 계산 정확도 검증
- **담당 에이전트**: `risk-agent`, `reviewer`

### Category C — Data & Infrastructure (데이터/인프라)
- WebSocket feed 안정성 개선
- DataFeed 캐시 전략 최적화
- OrderFlow/VPIN 정확도 검증
- 온체인 데이터 추가
- **담당 에이전트**: `data-agent`, `onchain-agent`

### Category D — ML & Signals (ML/신호)
- LSTM 모델 재학습 (새 데이터)
- RF 모델 피처 중요도 분석
- 앙상블 가중치 최적화
- Walk-Forward 통합 (토너먼트 파이프라인에)
- **담당 에이전트**: `ml-agent`, `alpha-agent`

### Category E — Execution & Paper Trading (실행)
- Paper Trading 모드 테스트
- TWAP 실행기 검증
- 슬리피지 모델 정확도 점검
- Telegram 알림 활성화
- **담당 에이전트**: `execution-agent`

### Category F — Research (리서치)
- **트레이딩봇 실패/성공 케이스 리서치** ← 필수 매 사이클 포함
- 최신 퀀트 전략 논문 조사 (구현 X, 리서치만)
- 경쟁 봇/플랫폼 벤치마크
- **담당 에이전트**: `news-agent`, `strategy-researcher-agent`, `sentiment-agent`

---

## 🔄 로테이션 스케줄

5시간마다 다음 카테고리 중 3개를 병렬로 선택 (각각 subagent에게 배정):

| Cycle | Primary (3개 카테고리) | Research 포함 |
|-------|----------------------|-------------|
| 1 | A (품질) + C (데이터) + **F (리서치)** | ✅ |
| 2 | B (리스크) + D (ML) + **F (리서치)** | ✅ |
| 3 | E (실행) + A (품질) + **F (리서치)** | ✅ |
| 4 | C (데이터) + B (리스크) + **F (리서치)** | ✅ |
| 5 | D (ML) + E (실행) + **F (리서치)** | ✅ |

그 다음 Cycle 1로 돌아감. `CYCLE_STATE.txt`에 현재 사이클 저장.

---

## 📋 사이클별 Deliverables

각 사이클 종료 시 반드시 수행:

1. **WORKLOG.md 업데이트** — 이번 사이클에 한 일, 결과, 문제점
2. **STATUS.md 업데이트** — 전체 상태 현황 (전략 수, 테스트, 주요 지표)
3. **NEXT_STEPS.md 업데이트** — 다음 사이클에 할 작업 힌트
4. **git commit + push** — 변경사항을 remote에 반영
5. **CYCLE_STATE.txt 업데이트** — 다음 사이클 번호 저장

---

## 🎯 장기 목표 (6~8 사이클 내)

1. **통과 전략 100% 검증** — 상위 23개 → 실제 데이터 재백테스트
2. **Walk-Forward 파이프라인 통합** — 토너먼트에 연결
3. **Paper Trading 실전 투입** — 1주일 테스트 후 결과 리포트
4. **레짐 기반 전략 스위칭** — 불/베어/횡보에 따라 다른 전략 조합 활성화
5. **실시간 알림 완비** — Telegram 활성화, 이상치 즉시 알림

---

## 📚 필수 읽기 파일 (매 사이클)

- `.claude-state/MASTER_PLAN.md` — 이 파일
- `.claude-state/CYCLE_STATE.txt` — 현재 사이클 번호
- `.claude-state/STATUS.md` — 프로젝트 현황
- `.claude-state/NEXT_STEPS.md` — 다음 단계
- `.claude-state/WORKLOG.md` — 최근 작업 로그 (마지막 20줄)
