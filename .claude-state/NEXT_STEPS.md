# Next Steps

_Last updated: 2026-05-31 (Cycle 251 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 250, 251

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 250 | A+C+SIM+F | GARCH(1,1) 합성데이터 개선, elder_impulse ATR 검증, MSGARCH/CPCV 리서치 |
| 251 | B+D+F | wick_reversal ATR 필터, Deflated Sharpe Ratio 유틸리티, 데이터 확보 방안 |

### 🎯 Cycle 252 작업 방향 (252 mod 5 = 2 → E(실행) + A(품질) + F(리서치))

#### E(실행): validate_ohlcv() 데이터 검증 헬퍼 추가
- 리서치 결과: 데이터 파이프라인 실패 최다 원인은 중복/갭/타임존
- `src/data/` 내 기존 파일에 validate_ohlcv(df) 추가
- 중복 타임스탬프 검출, 갭(기대 interval 불일치) 검출, UTC 정규화 검증
- 갭 비율 >1% 시 경고 로그

#### A(품질): DSR을 Bundle OOS에 통합
- Cycle 251에서 구현한 is_sharpe_significant()를 RollingOOSValidator에 연결
- BundleOOSResult에 dsr_pvalue 필드 추가
- 기존 pass/fail 판정에 DSR 보조 지표 추가 (즉시 강제 적용은 아닌 정보성)

#### F(리서치): 히스토리컬 데이터 로딩 아키텍처
- CryptoDataDownload CSV → BacktestEngine 연결 구조 설계
- data/historical/ 디렉토리 구조 정의
- 1분봉→4h 리샘플링 파이프라인 설계

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 GARCH(1,1) 개선 완료, 하지만 IS Sharpe 음수 지속
- 실 데이터 확보가 다음 돌파구 (CryptoDataDownload/Kaggle CSV)

### 핵심 메트릭 (Cycle 251)
- 테스트: 8351+ passed (Cycle 251 +5)
- 신규: wick_reversal ATR 필터, Deflated Sharpe Ratio
- 리서치: MSGARCH(hmmlearn+arch 2단계), 데이터 소스 3건 확인
