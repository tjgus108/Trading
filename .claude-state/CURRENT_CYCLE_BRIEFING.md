# Current Cycle Briefing

_Updated: 2026-06-14 | Cycle 308 완료_

## 완료된 작업

### 1. C(데이터) — CMFStrategy warmup 버그 수정
- `src/strategy/cmf.py`: `min_rows = max(_MIN_ROWS, self.period + 5)` 수정
  - 기존: 고정 25봉, period=105에서 warmup 중 불완전한 CMF 계산 허용
  - 수정: period 기반 동적 min_rows — period=105 → 110봉 요구
- `tests/test_cmf.py`: warmup 방어 테스트 2개 추가

### 2. B(리스크) — DrawdownMonitor WARN 히스테리시스
- `src/risk/drawdown_monitor.py`:
  - `mdd_warn_hysteresis_pct=0.015` 파라미터 추가 (기본 1.5%)
  - WARN→NORMAL 복귀 기준: `mdd_warn_pct - hysteresis = 3.5%`
  - BTC MDD 5% 경계 oscillation으로 인한 size_multiplier 0.5/1.0 급등락 방지
  - BLOCK_ENTRY 이상에서 복귀 시는 히스테리시스 미적용 (기존 동작 보존)
  - `to_dict/from_dict` 직렬화에 `mdd_warn_hysteresis_pct`, `_in_warn_mode` 추가
- `tests/test_drawdown_monitor.py`: 히스테리시스 테스트 3개 추가

### 3. F(리서치) — Bundle OOS 분석
- cmf 5/5 PASS (avg OOS Sharpe=2.508, std=1.888) — 매우 안정적
- supertrend_multi 3/5 PASS (avg OOS Sharpe=3.674)
- narrow_range fold3 OOS=-10.794 지속 → EMA slope/ROC 필터 방향 연구
- value_area OOS std=2.018 (2.0 임계값 극소 초과) FAIL 지속

## 시뮬레이션 결과
- 테스트: **8400 passed, 23 skipped** (+5 신규)
- Paper Sim BTC 1h: 0/22 PASS (price_cluster rank1=75.7, supertrend rank2=68.3, cmf rank15=48.8)
- Bundle OOS BTC 4h: **2/5 PASS** (cmf=2.508, supertrend_multi=3.674)

## 다음 사이클 (309 = 309 mod 5 = 4 → D+E+F)
- D: cmf paper_sim 효과 검증 (PAPER_SIM_STRATEGY_PARAMS["cmf"]["buy_thresh"]=0.10 추가)
- E: supertrend_multi 4h vs 1h 성능 격차 분석
- F: narrow_range EMA slope 필터 실험 (walk_forward.py grids에 파라미터 추가)
