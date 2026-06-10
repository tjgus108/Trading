# Next Steps

_Last updated: 2026-06-10 (Cycle 294 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 294

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 292 | B+D+F | supertrend_multi std threshold 2.5→3.0, --start-date 옵션, Bundle OOS 0→2 PASS |
| 293 | C+B+F | --verbose-windows 옵션, VolTargeting.for_timeframe(), Paper Sim FAIL 원인 분석 완료 |
| 294 | D+E+F | OOSFoldResult oos_regime 필드 추가, 레짐별 Sharpe 분석, 파라미터 실험 역효과 원복 |

### 🎯 Cycle 295 작업 방향 (295 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): cmf PF 개선 방향 재탐색
- **핵심 이슈**: cmf Paper Sim PF=1.24 (목표 ≥1.5) — vol_percentile 실험 역효과 확인됨
  - 레짐별 분석: bull fold avg=3.47, bear fold avg=1.06 — bear에서 OOS 낮음
  - Bundle OOS에서 cmf는 bear fold도 PASS하지만 OOS Sharpe가 bull 대비 절반
  - bear fold에서 PF < 1.5인지 확인 필요 → bear 구간 SELL 신호 선택성 강화
  - 다음 시도: `sell_thresh: -0.10 → -0.12` (SELL 임계값 강화, PF 개선 목표)
  - `walk_forward.py DEFAULT_GRIDS["cmf"]`: sell_thresh [-0.12, -0.10, -0.09] 로 조정 검토
- **품질 검증**: tests/ 관련 테스트 실행, 8392 PASS 유지 확인

#### C(데이터): 레짐 감지 정확도 향상
- **이번 사이클 결과**: `_detect_oos_regime()` 추가 완료
  - 현재 임계값: slope > 3% = bull, < -3% = bear
  - 개선: bear 임계값을 -5%로 강화 (노이즈 제거), sideways 범위 확대
  - 또는: EMA slope 대신 EMA20 > EMA50 기준 사용 (더 안정적)
- supertrend_multi fold3(2023-12~2024-02): `oos_regime=bear` 확인 → 신호 0건 연계
  - bear 구간에서 Supertrend 3개 합의 불가 → sideways/bear 신호 완화 방안 탐색
  - 단, Bundle OOS PASS 유지 필수

#### F(리서치): 레짐별 전략 할당 최적화
- **Cycle 294 분석 결론** (Bundle OOS 레짐 컬럼 기준):
  - cmf: 전 레짐 PASS (bull+bear 모두) — "bull 전용" 가설 수정
  - supertrend_multi: bull+bear 모두 PASS 가능, 문제는 극단 bear 구간(0 거래)
  - elder_impulse: bear(fold2,3)에서 FAIL — bear 전용 아님
  - 제안: 레짐별 전략 스위칭보다 각 전략의 bear 구간 신호 개선이 우선
- Paper Sim vs Bundle OOS 평가 기준 차이:
  - Paper Sim PF≥1.5 요구 → cmf bear fold PF가 해당 임계 미충족
  - Bundle OOS PF는 참고만 (Sharpe/WFE가 핵심 기준)
  - 통일 방안: Paper Sim PASS 기준 완화 (PF≥1.3) 또는 cmf bear 구간 PF 개선

### ⚠️ 주의 사항 (Cycle 295)
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **cmf sell_thresh 변경 시**: fold2(-0.642), fold3(1.480) OOS 영향 모니터링
- **_detect_oos_regime() 임계값**: slope 3%가 4h 봉에서 적절한지 검증 필요
- **walk_forward.py DEFAULT_GRIDS["cmf"] vol_percentile 추가됨**: [0.85, 1.0, 1.1] — 최적화 탐색 가능

### 핵심 메트릭 (Cycle 294)
- 테스트: **8392 passed** — 회귀 없음
- Paper Sim BTC 4h (8 windows): 0/22 PASS (Cycle 293과 동일)
  - rank1: lob_maker (score=63.8), rank2: price_cluster (score=60.3)
- Bundle OOS BTC 4h (5-fold):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116
  - **총 PASS: 2/5** (Cycle 293과 동일 유지)

### 주요 코드 변경 이력 (Cycle 294)
1. `src/backtest/walk_forward.py` — `_detect_oos_regime()` 함수 추가 (D/ML)
   - EMA20 slope 기반 bull/bear/sideways 레짐 감지
   - `OOSFoldResult.oos_regime: Optional[str]` 필드 추가
   - `RollingOOSValidator.validate()` 내 fold별 레짐 자동 기록
   - `BundleOOSResult.summary()` 레짐별 OOS Sharpe 요약 출력
   - `DEFAULT_GRIDS["cmf"]`에 `vol_percentile: [0.85, 1.0, 1.1]` 추가
2. `scripts/run_bundle_oos.py` — Fold Details 테이블에 Regime 컬럼 추가 (E/실행 진단)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 8-10분 소요
