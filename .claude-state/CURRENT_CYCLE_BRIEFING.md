# Current Cycle Briefing

_Cycle 345 | 2026-06-22 | A(품질) + C(데이터) + F(리서치)_

## 완료된 사이클: 345

### 핵심 변경사항

1. **price_cluster WFO 그리드 버그 수정** (`walk_forward.py`)
   - `vol_atr_trend_min`이 `vol_regime_filter=False`(기본값)로 무효화 → 54조합 모두 동일 결과 낭비
   - `vol_regime_filter: [True]` 추가 → 레짐 필터 실제 활성화, 54조합 모두 유의미한 탐색
   - 기대 효과: W2-W5 고변동성 RANGING에서 신호 억제 → Sharpe 분산 감소

2. **ccxt 설치 타이밍 버그 수정** (`tests/test_exchange.py`)
   - `if not HAS_CCXT:` 조건이 ccxt 설치 후 connector.py 참조 교체 방지
   - 조건 제거 → `_conn_mod.ccxt is None` 만으로 동적 교체 보장
   - test_timeout_raises_request_timeout PASS 복원

3. **enrich_indicators ema20_slope 동기화** (`scripts/paper_simulation.py`)
   - `feed.py._add_indicators()`와 `paper_simulation.py.enrich_indicators()` 불일치
   - narrow_range 전략의 EMA slope 필터가 paper_sim에서 비활성화 상태 → 추가

### 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| Paper Sim 1h BTC | 0/20 PASS (25연속) |
| Bundle OOS 4h | 5/5 PASS |
| price_cluster Sharpe | 0.87 (유지) |
| Bundle OOS MDD | OFI 3.4%, ST 2.2%, VA 1.9% (개선) |

### 연구 결과 (F)

- **RANGING 실패 근본 원인 재확인**: 1h RANGING은 노이즈 비율이 높아 mean-reversion 신호 신뢰도 낮음
- **price_cluster W6 PASS 가설**: 저변동성 RANGING(ATR/ATR_MA < vol_atr_trend_min) 환경에서만 cluster bounce 신뢰도 높음
  - vol_regime_filter=True 활성화로 이 환경만 선택 가능 → 다음 시뮬에서 검증 예정
- **4h vs 1h 격차 원인**: 4h는 봉당 TP 거리 확장으로 수수료 비중 낮음 + 레짐 전환 구조적 필터

### 다음 사이클 (346)

- **카테고리**: B(리스크) + D(ML) + F(리서치) (346 mod 5 = 1)
- **핵심 확인**: price_cluster vol_regime_filter=True 효과 → paper_sim Sharpe std 감소 여부
- **D(ML)**: WFO 그리드 수정 효과 검증 + frama 전략 파라미터 분석
