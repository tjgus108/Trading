# Next Steps

_Last updated: 2026-05-31 (Cycle 252 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 250, 251, 252

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 250 | A+C+SIM+F | GARCH(1,1) 합성데이터 개선, elder_impulse ATR 검증, MSGARCH/CPCV 리서치 |
| 251 | B+D+F | wick_reversal ATR 필터, Deflated Sharpe Ratio 유틸리티, 데이터 확보 방안 |
| 252 | E+A+F | validate_ohlcv() 헬퍼, DSR→BundleOOS 통합, 레짐감지 실패패턴 리서치 |

### 🎯 Cycle 253 작업 방향 (253 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): 히스토리컬 CSV 로더 구현
- data/historical/ 디렉토리 구조: {exchange}/{pair}/{timeframe}.csv
- BacktestEngine 또는 DataFeed에 CSV fallback 경로 추가
- 1분봉→4h 리샘플링 유틸리티 (pandas resample)
- validate_ohlcv() 자동 호출 연동

#### B(리스크): 레짐 전환 쿠션 로직
- 리서치 결과: 전환 구간에서 포지션 0.5x "전환 쿠션" 필요
- DrawdownMonitor 또는 RiskManager에 transition_cushion 옵션 추가
- regime 확률 < 70%일 때 자동 포지션 축소

#### F(리서치): CPCV(Combinatorial Purged CV) 구현 가이드
- N=6, k=2 조합 시작점
- PBO(Probability of Backtest Overfitting) 산출 방법
- 합성 데이터에서의 CPCV 적용 사례

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 한계: IS Sharpe 음수 지속 → 실 데이터 필요
- CryptoDataDownload/Kaggle CSV 수동 다운로드로 해결 가능

### 핵심 메트릭 (Cycle 252)
- 테스트: 8356+ passed
- 신규: validate_ohlcv(), DSR→BundleOOS 통합, wick_reversal ATR 필터
- 리서치: 레짐 감지 지연 ~25일, smoothed/filtered 혼동 주의, 데이터 품질 검증 필수
