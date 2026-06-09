# Next Steps

_Last updated: 2026-06-09 (Cycle 293 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 293

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 291 | B+D+F | 레짐 기반 kill switch, 음수 OOS 비례 패널티, 9-fold 데이터 변화 분석 |
| 292 | B+D+F | supertrend_multi std threshold 2.5→3.0, --start-date 옵션, Bundle OOS 0→2 PASS |
| 293 | C+B+F | --verbose-windows 옵션, VolTargeting.for_timeframe(), Paper Sim FAIL 원인 분석 완료 |

### 🎯 Cycle 294 작업 방향 (294 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): cmf PF 개선 및 앙상블 신호 강화
- **핵심 이슈**: cmf의 PF=1.24 (Paper Sim 기준, 목표 ≥1.5) — 대부분 윈도우 FAIL 원인
  - Paper Sim verbose-windows 분석: cmf는 bull 구간만 PASS (W1 only)
  - sideways/bear 구간에서 cmf 신호 약화 → 손실 거래 비중 증가
  - 앙상블 가중치에서 cmf 레짐 필터링 강화 검토: bull 구간만 cmf 사용
  - `src/ml/trainer.py`: cmf 레짐 조건부 가중치 조정

#### E(실행): supertrend_multi 거래 빈도 진단
- **핵심 이슈**: supertrend_multi W5-W7에서 0 거래 (sideways 구간 완전 신호 소멸)
  - Bundle OOS avg_trades=6.4 (목표 ≥15)
  - Paper Sim W2-W3: trades=13/12 (1-2 trades 부족으로 FAIL)
  - `src/execution/` 또는 `src/strategy/` 내 신호 생성 로직 검토
  - TWAP 실행기와 supertrend_multi 통합 테스트 (신호 빈도 측정)

#### F(리서치): ML 앙상블에서 레짐별 전략 할당 최적화
- **Cycle 293 분석 결론**:
  - cmf: bull 구간 전문 전략 (W1: Sharpe=6.97, W7: Sharpe=0.06 — bull vs bull 격차)
  - supertrend_multi: 추세장 전용, sideways에서 신호 없음
  - 제안: 레짐별 전략 포트폴리오 구성
    - BULL: cmf + supertrend_multi 병행 활성화
    - BEAR: 별도 bear 전략 필요 (현재 PASS 전략 없음)
    - SIDEWAYS: 현재 0 전략 PASS → 신호 완화 필요
  - Paper Sim vs Bundle OOS 불일치 결론 정리 및 평가 기준 단일화 방안 검토

### ⚠️ 주의 사항 (Cycle 294)
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **cmf PF 목표**: Paper Sim PASS 기준 PF≥1.5 — 현재 평균 PF=1.24 (0.26 gap)
- **supertrend_multi trades 목표**: trades≥15 — 현재 평균 8/8 windows (7 trade gap)
- **Paper Sim --verbose-windows 필수**: FAIL 원인 윈도우별 상세 진단

### 핵심 메트릭 (Cycle 293)
- 테스트: **8392 passed** — 회귀 없음
- Paper Sim BTC 4h (8 windows, --verbose-windows): 0/22 PASS (Cycle 292와 동일)
  - rank1: cmf (score=68.3, Sharpe=1.25, trades=23) — PF=1.24 < 1.5
  - rank5: supertrend_multi (score=54.6, Sharpe=2.14, trades=8) — trades < 15
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116
  - **총 PASS: 2/5** (Cycle 292와 동일 유지)

### 주요 코드 변경 이력 (Cycle 293)
1. `scripts/paper_simulation.py` — `--verbose-windows` 옵션 추가 (C 데이터)
   - `VERBOSE_WINDOWS` 모듈 레벨 플래그 + argparse `--verbose-windows`
   - `generate_report()` 내 상위 5 전략 윈도우별 상세 테이블 출력
   - 기존 FAIL 원인 집계 보완 → 윈도우별 정확한 원인 진단 가능
2. `src/risk/vol_targeting.py` — `VolTargeting.for_timeframe()` classmethod 추가 (B 리스크)
   - `_TF_CANDLES_PER_DAY` 딕트 + `for_timeframe(timeframe)` classmethod
   - 4h 캔들에서 기본 annualization(252×24=1h 전용) 사용 시 vol 2배 과장 방지
   - `VolTargeting.for_timeframe("4h")` → annualization=1512 자동 설정

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 8-10분 소요
- Paper simulation 4h + --verbose-windows: 상위 5 전략 윈도우별 분석 포함
