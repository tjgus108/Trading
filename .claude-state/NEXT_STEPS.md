# Next Steps

_Last updated: 2026-05-31 (Cycle 253 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 250, 251, 252, 253

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 250 | A+C+SIM+F | GARCH(1,1) 합성데이터 개선, elder_impulse ATR 검증, MSGARCH/CPCV 리서치 |
| 251 | B+D+F | wick_reversal ATR 필터, Deflated Sharpe Ratio 유틸리티, 데이터 확보 방안 |
| 252 | E+A+F | validate_ohlcv() 헬퍼, DSR→BundleOOS 통합, 레짐감지 실패패턴 리서치 |
| 253 | C+B+F | load_csv_ohlcv/resample_ohlcv, 전환쿠션, RollingOOS max_oos_sharpe_std 파라미터화 |

### 🎯 Cycle 254 작업 방향 (254 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): narrow_range 파라미터 최적화 신호 분석
- narrow_range는 Cycle 253 Bundle OOS에서 최고점 (fold 4 PASS, PF 1.645)
- ML 피처로 narrow_range의 핵심 조건 파악: ATR 임계값, 봉 수 등
- RF feature importance로 narrow_range 생성 조건의 예측 변수 분석
- 단, 새 전략 파일 생성 금지 → 기존 피처 선택 모듈 활용

#### E(실행): load_csv_ohlcv 활용 백테스트 파이프라인 연동
- BacktestEngine에 CSV fallback 경로 추가: 거래소 연결 실패 시 data/historical/ 자동 탐색
- paper_simulation.py에 --csv-dir 옵션 추가 (로컬 CSV 사용 모드)
- validate_ohlcv() → resample_ohlcv() → BacktestEngine 체인 검증

#### F(리서치): CPCV PBO 구현 + 실 데이터 파이프라인
- PBO(Probability of Backtest Overfitting) 실제 계산 방법
- narrow_range fold 4 PASS 재현 가능성 분석 (합성 vs 실 데이터 차이)
- CryptoDataDownload 수동 CSV 다운로드 방법 정리

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단 (합성 데이터만 사용 가능)
- 합성 데이터 한계: OOS Sharpe std 3.7~7.7 (기준 1.5 대비 과대)
- 실 데이터 필요: CryptoDataDownload/Kaggle CSV 수동 다운로드
- load_csv_ohlcv() 구현 완료 → CSV만 있으면 즉시 활용 가능

### 핵심 메트릭 (Cycle 253)
- 테스트: 320+107=427 passed (신규 10개)
- 신규: load_csv_ohlcv(), resample_ohlcv(), transition_cushion, max_oos_sharpe_std 파라미터
- 시뮬: 0/5 PASS (합성 데이터 한계 지속), narrow_range 최근접 (1/9 fold PASS)
- 리서치: CPCV 인프라 완비, 실 데이터 CSV 로더로 연동 준비 완료
