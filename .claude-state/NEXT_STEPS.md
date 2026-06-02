# Next Steps

_Last updated: 2026-06-02 (Cycle 264 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 264

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 263 | C+B+F | cmf 파라미터 범위 축소, DrawdownMonitor 컴포넌트 로그 |
| 264 | D+E+F | feature importance 경고 로그, wick_reversal 활성화, WFE 0.5 마커 |

### 🎯 Cycle 265 작업 방향 (265 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): wick_reversal 1h 노이즈 문제 분석
- Cycle 264에서 min_wick_ratio 0.65→0.55로 낮춤 → 4h에서 활성화되었으나 1h에서 Sharpe=-2.79 악화
- 방향: `src/strategy/wick_reversal.py`에 타임프레임별 적응 필터 추가 검토
  - vol_mult 임계값 상향 (현재 0.8) 또는 체결 캔들 바디 비율 필터 추가
  - 최소 ATR 임계값 상향 (min_volatility=0.002 → 0.004): 1h 저변동 노이즈 차단
- 주의: 4h 성능(17.3거래, Sharpe=1.211) 유지하면서 1h 개선

#### C(데이터): cmf PASS fold 안정화
- Cycle 264 Bundle OOS: cmf PASS fold 4개 (fold 1,4,7,8) — 개선됨
- 여전히 5/9 fold가 FAIL — OOS Sharpe std=3.854 여전히 높음
- 방향: cmf grids를 더 좁혀서 std 감소
  - period [18,20,22] → [19,20,21] (더 보수적)
  - 또는 sell_thresh 범위 추가 검토 (현재 없음)

#### F(리서치): Paper Sim PF < 1.5 근본 원인 분석
- 전체 22개 전략 모두 PF < 1.5가 1등 실패 원인
- 분석 방향: 슬리피지+수수료(0.15%)가 1h에서 PF를 끌어내리는 구조적 문제인지 확인
  - 1h 기준 거래 1건당 왕복 0.3% 손실 → PF=1.5 달성에 최소 win_rate 55%+ AND R:R 1:1 필요
  - `scripts/paper_simulation.py`의 fee/slippage 현실 검토

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 가능 (data/historical/binance/BTCUSDT/1h.csv)
- ETH/SOL: synthetic CSV 사용 (data/historical/synthetic/ETHUSDT|SOLUSDT/1h.csv)
- Bundle OOS: `--csv-dir data/historical` 필수

### 핵심 메트릭 (Cycle 264)
- 테스트: 8369 passed, 23 skipped (변경 없음)
- Paper Sim BTC: 0/22 (top: supertrend_multi 72.6점, Sharpe=0.43, PF=1.13)
- Bundle OOS BTC 4h: 0/5 PASS (wick_reversal #1: 88.3점, avg Sharpe=1.211, std=6.129)
  - cmf: 4/9 fold PASS (WFE=0.5 마커 적용 후 개선)

### 주요 코드 변경 이력 (Cycle 264)
1. `src/ml/model.py` — 모델 로드 시 importance<0.01 피처 WARNING 로그
2. `src/strategy/wick_reversal.py` — min_wick_ratio 기본값 0.65 → 0.55
3. `src/backtest/walk_forward.py` — wick_reversal 그리드 [0.60-0.70]→[0.50-0.60]
4. `src/backtest/walk_forward.py` — WFE regime change 마커 (IS<-1.0 AND OOS>2.0 → WFE=0.5)
5. `tests/test_wick_reversal.py` — test_hammer_with_trend_up_false에 min_wick_ratio=0.65 명시
