# Next Steps

_Last updated: 2026-06-08 (Cycle 289 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 289

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 287 | B+D+F | regime_transition_is_min=2.0 추가 → supertrend_multi **첫 PASS** (avg=3.674, std=1.860) |
| 288 | C+B+F | resample_ohlcv partial bucket 제거, regime_transition 경고 로깅 강화, cmf 16회 PASS 유지 |
| 289 | D+E+F | detect_regime 벡터화, oos_sharpes 앙상블 파라미터 추가, paper_sim fee 오표기 수정 |

### 🎯 Cycle 290 작업 방향 (290 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 전략 백테스트 품질 재검증
- **탐색 방향**:
  - supertrend_multi 1h 파라미터 재검토 (Sharpe=0.60, PF=1.17 → PASS 기준 1.5 미달)
  - Walk-Forward 테스트 커버리지 점검 (현재 8380 passed)
  - QUALITY_AUDIT.csv 상위 전략 IS Sharpe vs OOS Sharpe 괴리 분석

#### C(데이터): 4h Paper Simulation 도입 검토
- **탐색 방향**:
  - `scripts/paper_simulation.py`에 `--timeframe 4h` 옵션 추가 가능성
  - 현재 1h Paper Sim 0/22 PASS → 4h에서 cmf/supertrend_multi PASS 확인 필요
  - `scripts/run_bundle_oos.py` 방식을 Paper Sim에도 반영 가능성 검토

#### F(리서치): 1h FAIL 원인 정밀 분석
- **탐색 방향**:
  - cmf 전략: Bundle OOS 4h Sharpe=2.508 PASS vs Paper Sim 1h Sharpe=-1.24 FAIL
  - 동일 전략의 1h/4h PF 분포 비교 (1h PF=0.90 vs 4h PF=1.387)
  - 신호 발생 조건 완화 가능성: CMF threshold 조정 (현재 0.1 → 0.05 시도)

### ⚠️ 주의 사항 (Cycle 290)
- **supertrend_multi regime_transition_ratio=20% 경고 발동 중**: fold4 레짐 전환 마커 포함
  - fold3 (trades<3) + fold4 (레짐 전환) = 현재 2/5 fold 미사용
- **Bundle OOS: `--csv-dir data/historical` 필수** (미지정 시 합성 데이터로 fallback)
- **Paper Sim 0/22 PASS 지속**: 1h 전략 개선 또는 4h Paper Sim 도입 전까지 예상 유지

### 핵심 메트릭 (Cycle 289)
- 테스트: **8380 passed** (2개 추가) — 회귀 없음
- Paper Sim BTC 1h (8 windows): 0/22 PASS
  - rank1: supertrend_multi (score=73.9, +6.73%, Sharpe=0.60, PF=1.17, 2/8)
- Bundle OOS BTC 4h (5-fold, CSV):
  - cmf: **PASS** avg=2.508, std=1.888 ← **17회 연속 PASS**
  - supertrend_multi: **PASS** avg=3.674, std=1.860 ← **3회 연속 PASS**
    - fold3 excluded (trades<3, 구조적) / fold4 excluded (레짐 전환 IS=2.51>2.0, WFE<0)
  - elder_impulse: FAIL | narrow_range: FAIL | value_area: FAIL
  - **총 PASS: 2/5 유지**

### 주요 코드 변경 이력 (Cycle 289)
1. `src/ml/features.py` — detect_regime() 채널폭 중앙값 계산 벡터화 (D ML)
   - Python 리스트 컴프리헨션 → pandas rolling max/min (O(n))
   - 기존 결과와 완전 동일한 수치 검증 (20개 랜덤 시드)
2. `src/ml/trainer.py` — compute_ensemble_weight_recency() oos_sharpes 파라미터 (D ML)
   - Bundle OOS Sharpe → 앙상블 가중치 배율 반영 ([0.5, 2.0] 클리핑)
   - 음수 OOS Sharpe: 0.5배 패널티 / 양수 고성능: 최대 2.0배 증폭
3. `tests/test_trainer.py` — oos_sharpes 관련 테스트 2개 추가 (D ML)
4. `src/exchange/twap.py` — dead variable 제거 + slippage 주석 정확화 (E 실행)
5. `scripts/paper_simulation.py` — fee 보고 정확화 (E 실행)
   - 리포트: "Fee: 0.1%" → "Fee: 0.055%/leg (0.11% round-trip)"
   - metadata fee_rate: 0.001 → 0.00055

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조)
- Paper simulation: 22 전략 × 8 windows → 약 15분 소요 (Bash timeout 주의)
