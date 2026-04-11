# src/risk — Risk Management Layer

리스크 에이전트가 사용하는 모든 포지션 사이징·차단 로직.  
**코드 변경 없이** 이 디렉토리만으로 거래 안전 장치가 완성된다.

---

## 파일 구성

| 파일 | 클래스 / 함수 | 역할 |
|------|--------------|------|
| `manager.py` | `RiskManager`, `CircuitBreaker` (내장) | 메인 진입점. 평가(evaluate) → `RiskResult` 반환 |
| `drawdown_monitor.py` | `DrawdownMonitor` | 실시간 MDD 추적, 3층 서킷브레이커 |
| `circuit_breaker.py` | `CircuitBreaker` | 독립형 다층 차단기 (ATR surge, correlation) |
| `kelly_sizer.py` | `KellySizer` | Risk-Constrained Half-Kelly 포지션 사이저 |
| `position_sizer.py` | `kelly_position_size()` | KellySizer 단순 함수 래퍼 |
| `vol_targeting.py` | `VolTargeting` | 목표 변동성 기반 사이즈 스케일러 |
| `portfolio_optimizer.py` | `PortfolioOptimizer` | 멀티에셋 비중 최적화 (Mean-Variance / Risk Parity / EW) |

---

## 1. DrawdownMonitor — 3층 낙폭 서킷브레이커

```
일일 DD > daily_limit (기본 3%)   → WARNING + 거래 중단
주간 DD > weekly_limit (기본 7%)  → HALT   + 거래 중단
월간 DD > monthly_limit (기본 15%)→ FORCE_LIQUIDATE (수동 해제만 가능)
```

- `update(current_equity)` 호출 시 자동 판정
- `is_halted()` / `alert_level()` 로 상태 조회
- 자정 `reset_daily()`, 수동 `force_halt()` / `force_resume()` 지원

---

## 2. CircuitBreaker (circuit_breaker.py) — 다층 차단

| 조건 | 동작 | `size_multiplier` |
|------|------|-------------------|
| 플래시 크래시 (단일 캔들 ≥ 10%) | **완전 차단** | 0.0 |
| 일일 낙폭 ≥ `daily_drawdown_limit` | **완전 차단** | 0.0 |
| 전체 낙폭 ≥ `total_drawdown_limit` | **완전 차단** | 0.0 |
| ATR surge (현재 ATR ≥ baseline × 2.0) | 포지션 50% 축소 | 0.5 |
| 전략 상관관계 ≥ 0.7 | 포지션 70% 축소 | 0.7 |
| ATR surge + 상관관계 동시 | 더 보수적 적용 | 0.5 |

플래시 크래시 → 낙폭 → ATR/correlation 순으로 우선 체크.  
일일 트리거는 `reset_daily()`로 해제, 전체 낙폭 트리거는 `reset_all()`만 가능.

---

## 3. KellySizer — Risk-Constrained Half-Kelly

```
Full Kelly  = (win_rate × avg_win − (1−win_rate) × avg_loss) / avg_win
Half-Kelly  = Full Kelly × 0.5  (crypto 변동성 대응)
DD 제약     = max_drawdown / (avg_loss × leverage)
final_frac  = min(Half-Kelly, DD 제약)  [min_fraction, max_fraction] 클리핑
```

- ATR 조정: `atr_factor = target_atr / current_atr` (≤ 1.0), 변동성 높을수록 축소
- `from_trade_history(trades, ...)` 로 거래 기록에서 승률 자동 계산
- `position_sizer.py`의 `kelly_position_size()` 는 단순 함수 인터페이스 래퍼

---

## 4. RiskManager (manager.py) — 메인 진입점

`evaluate(action, entry_price, atr, account_balance, ...)` → `RiskResult`

**처리 순서:**
1. HOLD 신호 → 즉시 APPROVED (주문 없음)
2. 내장 `CircuitBreaker.check()` → 위반 시 BLOCKED
3. `check_total_exposure()` — 다중 포지션 총 노출 ≥ 30% → BLOCKED
4. 포지션 사이징
   - `adaptive_stop_multiplier()`: 실현 변동성으로 ATR 배수 자동 조정 (1.2 / 1.5 / 2.5)
   - `sl_distance = ATR × sl_mult`, `risk_amount = balance × risk_per_trade`
   - `position_size = risk_amount / sl_distance`, 최대 비율 클램프
5. 주문 지터 (`jitter_pct`, 최대 ±5%) — AMM 착취 방지
6. 세션 필터 (`session_filter=True`): 아시아/비활성 세션 50% 축소, 주말 30% 축소

**config.yaml 매핑 (risk 섹션):**

| config 키 | 기본 | 적용 위치 |
|-----------|------|----------|
| `risk_per_trade` | 0.01 | RiskManager |
| `stop_loss` (ATR 배수) | 1.5 | RiskManager |
| `take_profit` (ATR 배수) | 3.0 | RiskManager |
| `max_position_size` | 0.10 | RiskManager |
| `max_daily_loss` | 0.03 | CircuitBreaker |
| `max_drawdown` | 0.05 | CircuitBreaker + DrawdownMonitor |
| `max_consecutive_losses` | 5 | CircuitBreaker |
| `flash_crash_pct` | 0.10 | CircuitBreaker |

---

## 5. VolTargeting — 목표 변동성 스케일러

```
vol_scalar     = target_vol / realized_vol   (연환산, 1h 기준: sqrt(252×24))
adjusted_size  = base_size × clip(vol_scalar, min_scalar=0.1, max_scalar=2.0)
```

- `adjust(base_size, df)` — 단일 호출 인터페이스
- 변동성 급등 시 자동 축소, 저변동 시 확대 (레버리지 한계 내)

---

## 6. PortfolioOptimizer — 멀티에셋 비중 최적화

3가지 방법 선택 (`method` 파라미터):

| 방법 | 설명 |
|------|------|
| `mean_variance` | Markowitz 최대 Sharpe |
| `risk_parity` | 각 자산 리스크 기여도 균등화 (iterative) |
| `equal_weight` | 동일 비중 (기준선) |

scipy 미사용, numpy only.

---

## RiskResult 출력 구조

```
status: APPROVED | BLOCKED
reason: [BLOCKED 시 필수]
position_size: [수량]
stop_loss: [가격]
take_profit: [가격]
risk_amount: [USD]
portfolio_exposure: [0~1]
```

BLOCKED 시 파이프라인은 즉시 중단. 우회 없음.
