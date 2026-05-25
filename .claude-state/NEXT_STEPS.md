# Next Steps

_Last updated: 2026-05-26 (Cycle 209 C(Data) 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 209 SIM 분석 완료
- 209 mod 5 = 4 → **C(데이터) + B(리스크) + F(리서치)** 패턴
- 다음 Cycle 210: **210 mod 5 = 0 → A(전략 로직) + E(실행) + F(리서치)**

### 🔥 Cycle 209 SIM 분석 결과

#### Bundle OOS 재실행 (--min-trades 2, 합성 dry-run)
- **5개 전략 모두 FAIL** (cmf, elder_impulse, wick_reversal, narrow_range, value_area)
- narrow_range: fold 1,3,6 PASS (3/9), fold 4만 저거래 제외(trades<2)
- value_area: fold 0,4,6,8 PASS (4/9), 저거래 제외 0개 (--min-trades 2 효과)
- elder_impulse: fold 1만 PASS (OOS Sharpe=3.794, 3사이클 연속 동일)

#### narrow_range PASS fold 특성 분석
| Fold | OOS 구간 | OOS Sharpe | Trades | 특성 |
|------|----------|-----------|--------|------|
| 1 | 2022-09-26~11-24 | 1.422 | 4 | 횡보→소폭 하락 (레인지 축소 후 돌파 유효) |
| 3 | 2023-01-24~03-24 | 5.980 | 2 | 극소수 거래, PF=999.99 (통계 무의미) |
| 6 | 2023-07-23~09-20 | 2.809 | 4 | 여름 횡보장 (ATR 축소 빈번, NR 신호 유효) |

**핵심**: PASS fold는 모두 레인지/횡보 구간. fold 3은 2 trades with PF=999.99로 사실상 1건의 우연한 성공. **진짜 PASS는 fold 1,6 (총 8 trades)**만 의미 있음.

#### value_area OOS Sharpe std=6.152 원인 분석
- OOS Sharpe 범위: -8.100 ~ +9.516 (극심한 양극화)
- **PASS fold (0,4,6,8)**: trades 2~5건, PF 최대 999.99 → 극소 거래에서 우연 성공
- **FAIL fold (1,2,3,5,7)**: trades 2~6건, 대부분 음수 Sharpe
- **근본 원인**: OOS당 평균 3.3 trades → 통계적 유의성 없음. Sharpe가 1~2건 거래 결과에 좌우되어 std 폭등
- **va_mult=0.7은 너무 좁은 VA 밴드** → 신호 자체가 희소, 발생 시 결과 분산 극대

### 🎯 Cycle 210 권장 작업 (210 mod 5 = 0 → A(전략 로직) + E(실행) + F(리서치))

#### A(전략 로직): narrow_range/value_area 개선
- **narrow_range**: NR lookback 4→3 테스트로 신호 빈도 증가 검토 (현재 fold당 2~4 trades)
- **value_area**: va_mult 0.7→1.0~1.2 확대로 VA 밴드 넓혀 신호 빈도 개선, min_breach 1.5→1.0 완화
- 두 전략 모두 핵심 문제는 **거래 수 부족** (OOS 360봉에서 2~6 trades)

#### E(실행): 실데이터 검증 인프라
- SSL 문제 해결 후 Bybit/Binance 실데이터로 narrow_range/value_area 재검증
- 실데이터에서 fold당 15+ trades 달성 가능한지 확인

#### F(리서치): 과적합 감사
- ~~합성 GBM seed(42) 동일 문제~~ **해결됨** (Cycle 209 C: 심볼 hash 기반 seed 분리 적용)
- PASS fold의 PF=999.99는 통계적 artifact (1건 성공, 0건 손실) → PASS 기준에 min_trades 추가 필요

### ⚠️ 핵심 문제
- 실데이터 PASS 전략 0개 — IS→OOS 괴리 심각
- ~~합성 데이터 동일 seed(42) → 3심볼 사실상 동일 데이터~~ **해결됨**
- IS 승률 80%+는 과적합 역신호 (리서치 확인)
- **narrow_range/value_area: fold당 2~4 trades → 통계적 유의성 없음**
- **PF=999.99 PASS는 의미 없음** (OOS 기준에 min_trades 15 추가 필요)

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단 (원격 사이클에서는 합성 SIM만 가능)
- DataFeed.DEFAULT_FALLBACK_EXCHANGES = ["binance", "okx", "bitget"] 준비됨
- 로컬 환경에서 `DataFeed(connector, fallback_exchange_ids=DataFeed.DEFAULT_FALLBACK_EXCHANGES)` 활성화

### 📋 Paper Trading 자동화 판정 기준

| 지표 | Go 조건 | No-Go 트리거 |
|------|---------|-------------|
| Profit Factor | ≥ 1.4 | < 1.0 즉시 중단 |
| MDD | ≤ 15% | > 20% 즉시 중단 |
| Sharpe (rolling 4주) | ≥ 0.8 | < 0.3 |
| WFE (OOS/IS 수익 비율) | ≥ 0.50 | < 0.30 |
| 주간 승률 | ≥ 45% | < 30% |

### 📊 Strategy Performance Reference (Real Data — IS only, OOS 미검증)

| Strategy | Sharpe | Win% | PF | Trades | MDD | Regime |
|----------|--------|------|-------|--------|-----|--------|
| cmf | 6.85 | 57% | 2.29 | 28 | 4.3% | TREND |
| wick_reversal | 6.51 | 54% | 2.03 | 35 | 3.5% | RANGE |
| volume_breakout | 5.91 | 60% | 2.66 | 15 | 2.2% | TREND |
| elder_impulse | 6.29 | 63% | 2.70 | 16 | 3.5% | TREND |
| value_area | 5.24 | 53% | 1.84 | 30 | 5.0% | RANGE |

**narrow_range: fold 1,6 PASS는 레인지/횡보 구간 전용. 트렌드장에서는 FAIL.**
**value_area: 4/9 PASS지만 trades 2~5건 → PF=999.99 artifact. 실질 무의미.**

---

**상태**: Cycle 209 C(Data) 완료 → Cycle 210 A(전략)+E(실행)+F(리서치) 예정
**최우선 과제**: narrow_range/value_area 거래 빈도 개선 + 실데이터 OOS 검증

### Cycle 209 C(Data) 완료 사항
- `paper_simulation.py` 합성 데이터 seed 다양화: 심볼 hash 기반 seed 생성 (BTC/ETH/SOL 각각 다른 합성 데이터)
- `src/data/` graceful import 확인: ccxt try/except 이미 적용됨 (feed.py, connector.py, __init__.py lazy loading)

### Cycle 209 B(Risk) 완료 사항
- VaR/CVaR scipy fallback 검증 테스트 7개 추가 (`TestScipyFallbackVarCvar`)
- DrawdownMonitor streak_recovery_grace_seconds 통합 테스트 7개 추가 (`TestStreakRecoveryGraceSeconds`)
- `to_dict()`에 `streak_recovery_grace_seconds` 직렬화 누락 수정
