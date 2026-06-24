# Current Cycle Briefing

_Last updated: 2026-06-24 (Cycle 352 완료)_

## 현재 상태 요약

- **완료 사이클**: 352
- **카테고리**: B(리스크) + D(ML) + F(리서치)
- **1h PASS 연속 FAIL**: 32연속 0/20 (BTC 실데이터 기준)
- **4h PASS**: 0/22 (consistency 부족, 32연속)
- **Bundle OOS**: 5/5 PASS 유지 (SSL 차단으로 재실행 불가)

## Cycle 352 핵심 발견

### B(리스크): supertrend_multi no-trades 근본 원인 = Supertrend 방향 불일치
- ATR 필터는 원인이 아님: atr_threshold=0.5 변경 → 효과 없음 확인
- W4(2023 Q4), W5(2024 Q1), W7(2024 Q2): 60일 전체 구간 동안 3개 Supertrend 단 한 번도 동시 합의 없음
- 근본 원인: BTC 4h 횡보/축적 구간에서 다른 ATR 기간(10/14/20)의 Supertrend가 diverge
- 해결 방향: `min_agree_count=2` 파라미터 추가 (2/3 합의로 완화) — 다음 사이클 검토

### D(ML): atr_threshold_max=1.5 → SOL HIGH 슬리피지 개선
- SOL 4h supertrend_multi: avg_trades 16→13, Sharpe -1.92→-1.16
- HIGH% 순위: #3 (46.4%) → top-10 밖 이탈
- BTC에는 영향 없음 (HIGH%=0% 이미)

## 코드 변경 (Cycle 352)

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["supertrend_multi"] = {"atr_threshold": 0.5, "atr_threshold_max": 1.5}` |

## 다음 사이클 (353) 방향

- 353 mod 5 = 3 → **C(데이터) + B(리스크) + F(리서치)**
- C: ETH/SOL 합성 데이터 ATR 분포 재검토 (HIGH% 과도 문제)
- B: supertrend_multi `min_agree_count=2` 파라미터 추가 및 효과 측정
- F: 4h PASS 전략 구조 분석 (32연속 FAIL 근본 원인 탐색)
