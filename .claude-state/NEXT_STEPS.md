# Next Steps

_Last updated: 2026-05-31 (Cycle 250 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 250

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 250 | A+C+SIM+F | GARCH(1,1) 합성데이터 개선, elder_impulse ATR 검증, MSGARCH/CPCV 리서치, 데이터 대안 발견 |

### 🎯 Cycle 251 작업 방향 (251 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): wick_reversal 변동성 필터 강화
- Cycle 250 분석 결과: vol_mult=0.8 너무 느슨, ATR 기반 최소 변동성 필터 없음
- elder_impulse 방식의 min_volatility(0.002) 추가 고려
- 기존 테스트 깨뜨리지 않으면서 변동성 필터링 강화

#### D(ML): MSGARCH 또는 CPCV 도입 검토
- 리서치 결과: MSGARCH(2-regime)가 BTC 분포에 가장 적합
- `arch` 패키지로 MSGARCH 구현 가능성 검토
- CPCV: N=6, k=2 조합으로 PBO/DSR 지표화 시작
- Deflated Sharpe Ratio 유틸리티 추가

#### F(리서치): 히스토리컬 데이터 확보 방안
- CryptoDataDownload: BTC 4h CSV 수동 다운로드 → data/historical/에 저장
- Kaggle: BTC OHLCV intraday dataset 확인
- 로컬 data loader 수정으로 SSL 차단 우회

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- GARCH(1,1) 개선 후에도 IS Sharpe 음수 유지 → 실데이터 필요성 재확인
- Paper SIM 타임아웃 지속

### 핵심 메트릭 (Cycle 250)
- Bundle OOS: 0/5 PASS (합성 한계), cmf Rank #1
- GARCH(1,1) 합성 데이터: vol clustering + spike 블록 추가됨
- 테스트: 8346+ passed
- 리서치: MSGARCH > GARCH > GBM 순서로 실 크립토 분포 근접
