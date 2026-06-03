# Next Steps

_Last updated: 2026-06-03 (Cycle 265 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 265

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 264 | D+E+F | feature importance 경고 로그, wick_reversal 활성화, WFE 0.5 마커 |
| 265 | A+C+F | cmf 그리드 추가 보수화(sell_thresh 추가), wick_reversal min_volatility 그리드 추가, synthetic→binance 우선선택 버그픽스 |

### 🎯 Cycle 266 작업 방향 (266 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): cmf 4h PASS fold std 감소 추적
- Cycle 265 Bundle OOS: cmf PASS fold 3/5 (60%), OOS Sharpe std=1.888 (개선 방향)
- sell_thresh 그리드 [-0.09,-0.08,-0.07] 추가 효과는 다음 시뮬에서 측정
- 방향: DrawdownMonitor에서 cmf 4h 전략에 특화된 변동성 필터 검토
  - cmf fold 2,3이 FAIL: IS Sharpe 1.478/3.295인데 OOS 0.642/1.480 (Sharpe decay 심함)
  - 리스크 관점에서 OOS 성과 감소 시 포지션 축소 로직 강화

#### D(ML): wick_reversal 1h vs 4h 타임프레임 분리
- 문제: min_wick_ratio 0.55 낮춤 → 4h 이전 17.3거래 (GOOD), 현재 7.6거래 (REGRESS)
- 분석: 이번 시뮬에서 avg trades가 17.3→7.6으로 하락한 원인 파악 필요
  - min_volatility [0.003, 0.004] 옵션이 4h 신호를 차단하는 것인지?
  - 다음: walk_forward.py 그리드 0.002를 별도 1h/4h 파라미터 세트로 분리 검토

#### F(리서치): 4h 타임프레임 수수료 구조 분석
- 1h: 왕복 0.3% 손실 → PF=1.5 달성 어려움 (구조적 한계 확인됨)
- 4h: 왕복 0.3% 손실이지만 거래 1건당 이익이 더 큼 → PF 개선 가능성
- 방향: paper_simulation.py에서 4h 봉 백테스트 모드 추가 검토

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv)
- ETH/SOL: synthetic CSV (data/historical/synthetic/ETHUSDT|SOLUSDT/1h.csv)
- **중요**: paper_simulation.py + run_bundle_oos.py 이제 binance 우선 선택 (버그픽스 완료)
- Bundle OOS: `--csv-dir data/historical` 필수

### 핵심 메트릭 (Cycle 265)
- 테스트: 8369 passed, 23 skipped
- Paper Sim BTC: 0/22 (top: supertrend_multi 72.6점, Sharpe=0.43, PF=1.13)
- Bundle OOS BTC 4h: 0/5 PASS
  - cmf: 3/5 fold PASS (60%), OOS std=1.888 (이전 9-fold 3.854 대비 개선됨)
  - wick_reversal: avg 7.6 trades (4/5 <10거래, 저거래 FAIL)

### 주요 코드 변경 이력 (Cycle 265)
1. `src/backtest/walk_forward.py` — cmf period [18,20,22]→[19,20,21], sell_thresh [-0.09,-0.08,-0.07] 추가
2. `src/backtest/walk_forward.py` — wick_reversal min_volatility [0.002,0.003,0.004] 그리드 추가
3. `src/backtest/walk_forward.py` — optimize_wick_reversal factory에 min_volatility 전달
4. `scripts/paper_simulation.py` — synthetic보다 binance CSV 우선 선택 버그픽스
5. `scripts/run_bundle_oos.py` — 동일 버그픽스
