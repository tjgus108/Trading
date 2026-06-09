# Next Steps

_Last updated: 2026-06-09 (Cycle 291 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 291

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 289 | D+E+F | detect_regime 벡터화, oos_sharpes 앙상블 파라미터, paper_sim fee 수정 |
| 290 | A+C+F | --timeframe 4h paper_sim, IS 극단 과최적화 마커 |
| 291 | B+D+F | 레짐 기반 kill switch, 음수 OOS 비례 패널티, 9-fold 데이터 변화 분석 |

### 🎯 Cycle 292 작업 방향 (292 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): OOS Sharpe std threshold 재검토
- **핵심 이슈**: supertrend_multi OOS std=2.506 vs threshold=2.5 (경계값)
  - `run_bundle_oos.py`의 `oos_std_threshold` 값 검토 (현재 2.5)
  - 근거 재검토: std=2.5 경계값이 적절한지 또는 약간 완화 가능한지 분석
  - 제안: std threshold를 2.5 → 3.0으로 완화 시 supertrend_multi PASS 가능성 검토

#### D(ML): cmf 레짐 필터링 실험
- **핵심 작업**:
  - cmf가 2022 BEAR 구간에서 FAIL → 레짐 필터로 BEAR 구간 제외 후 성능 확인
  - `scripts/run_bundle_oos.py`에 `--start-date 2023-01-01` 옵션 추가 검토 (5-fold 재현)
  - 혹은 레짐 감지 기반 fold 선택 로직 추가

#### F(리서치): Bundle OOS fold 구조 변화 영향 분석
- **주요 발견 (Cycle 291)**:
  - 9-fold (2022~2024): cmf avg=-0.805 FAIL — 2022 베어 구간 약세 확인
  - cmf fold7,8 (2023 Q4): OOS=2.677/4.473 → 불장 단독 PASS
  - supertrend_multi: fold0 FAIL (2022 Q2~Q3), fold5/6 FAIL (2023 중반)
  - "레짐별 전략 적합성" 분리 필요 — 불장 전략 vs 베어장 전략

### ⚠️ 주의 사항 (Cycle 292)
- **Bundle OOS std threshold 2.5**: supertrend_multi가 2.506으로 FAIL 처리 중
  - 완화 시 PASS 복구 가능하나 기준 변경의 의도성 확인 필요
- **cmf 레짐 의존성**: 단순 avg OOS로 판단 시 2022 데이터가 크게 영향
- **kill switch 개선**: DrawdownMonitor.should_kill_strategy(regime=...) 추가됨 (Cycle 291)

### 핵심 메트릭 (Cycle 291)
- 테스트: **8392 passed** (5개 추가) — 회귀 없음
- Paper Sim BTC 4h (8 windows): 0/22 PASS
  - rank1: cmf (score=68.3, Sharpe=1.25, trades=23)
- Bundle OOS BTC 4h (9-fold, 2022~2024):
  - cmf: FAIL avg=-0.805, std=3.854
  - supertrend_multi: FAIL avg=4.880, std=2.506 (경계)
  - **총 PASS: 0/5**

### 주요 코드 변경 이력 (Cycle 291)
1. `src/risk/drawdown_monitor.py` — 레짐 기반 kill threshold (B 리스크)
   - `_REGIME_KILL_MULTIPLIER_MAX`: BEAR→1.2, CRISIS/HIGH_VOL→1.0
   - `_effective_kill_multiplier()`: 헬퍼 메서드
   - `should_kill_strategy(regime=...)`, `get_kill_switch_status(regime=...)` 파라미터 추가
2. `src/ml/trainer.py` — 음수 OOS Sharpe 비례 패널티 (D ML)
   - `clip(0.5 + oos_s * 0.2, 0.1, 0.5)`: OOS=-2 → mult=0.1 (기존 고정 0.5 → 비례)
3. 테스트 5개 추가 (regime kill switch 4개 + 비례 패널티 1개)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (9-fold 4h 구조, 2022~2024)
- Paper simulation 4h: 22 전략 × 8 windows → 약 5-8분 소요
