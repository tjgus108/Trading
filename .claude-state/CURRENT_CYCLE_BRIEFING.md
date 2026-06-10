# Current Cycle Briefing

_Cycle 294 — D(ML) + E(실행) + F(리서치)_
_Completed: 2026-06-10_

## 완료 항목

### D(ML): OOSFoldResult 레짐 감지 추가
- `src/backtest/walk_forward.py`: `_detect_oos_regime(df)` 함수 추가
  - EMA20 기울기 기반 bull/bear/sideways 분류 (slope threshold ±3%)
- `OOSFoldResult.oos_regime: Optional[str]` 필드 추가
- `RollingOOSValidator.validate()` 내 fold별 레짐 감지 및 로깅
- `BundleOOSResult.summary()` 레짐별 OOS Sharpe 요약 추가
- `DEFAULT_GRIDS["cmf"]`에 `vol_percentile: [0.85, 1.0, 1.1]` 추가 (최적화 탐색용)

### E(실행): 파라미터 실험 및 역효과 원복
- cmf vol_percentile=1.0 실험: PF 1.24→1.10, Sharpe 1.25→-0.12 (역효과 → 원복)
- supertrend_multi Bundle OOS 파라미터 동기화: trades 8→7 (역효과 → 원복)
- 발견: 고볼륨 필터가 cmf 품질 개선에 불효과, cmf_confirm+confidence_filter 조합이 trades 감소

### F(리서치): Bundle OOS 레짐별 분석
- `scripts/run_bundle_oos.py`: Fold Details 테이블에 Regime 컬럼 추가
- cmf: bull(0,1,4) + bear(2,3) 모두 PASS → "bull 전용" 가설 수정
- supertrend_multi: bull+bear PASS 가능, fold3(2023-12~2024-02 bear) 0 거래가 문제
- "레짐별 전략 스위칭"보다 bear 구간 신호 개선이 더 현실적 방향

## 시뮬레이션 결과
- Paper Sim BTC 4h: 0/22 PASS (Cycle 293과 동일)
  - rank1: lob_maker (score=63.8, Sharpe=1.18)
  - rank2: price_cluster (score=60.3, Sharpe=2.51)
- Bundle OOS BTC 4h: 2/5 PASS (cmf, supertrend_multi) — Cycle 293과 동일
  - 신규: 레짐 컬럼으로 fold별 시장 환경 가시화

## 다음 사이클 (295): A(품질) + C(데이터) + F(리서치)
- A: cmf bear 구간 PF 개선 (sell_thresh 강화 검토: -0.10→-0.12)
- C: _detect_oos_regime() 임계값 최적화, EMA slope vs EMA cross 방식 비교
- F: Paper Sim PASS 기준 완화(PF≥1.3) vs cmf bear PF 개선 tradeoff 분석
