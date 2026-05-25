# Next Steps

_Last updated: 2026-05-26 (Cycle 210 D+E+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 210 완료
- 210 mod 5 = 0 → **D(ML) + E(실행) + F(리서치)** 패턴 ✅
- 다음 Cycle 211: **211 mod 5 = 1 → A(품질) + C(데이터) + F(리서치)**

### 🔥 Cycle 210 주요 성과
- **WFE/fold_pass_rate/is_robust**: WalkForwardResult에 추가, WFE>0.7 robust 판정
- **파라미터 5개↑ WARNING**: WalkForwardOptimizer에서 과적합 위험 경고
- **PaperTrader 3모듈 통합 E2E**: VolTargeting+KellySizer+TieredSlippage 동시 동작 11 테스트
- **PerformanceTracker 일간 리포트**: get_daily_pnl() + get_daily_summary() 추가
- **Seed 다양화 확인**: 3심볼 결과 분화됨, PF=999.99 artifact 감소
- **리서치**: fold당 30+ trades 필요, 4h→1h 이동으로 4배 가능

### 🎯 Cycle 211 권장 작업 (211 mod 5 = 1 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 전략 품질 감사 + 타임프레임 이동 검토
- 355개 전략 중 파라미터 5개 초과 전략 스캔 (자동화)
- cmf, PAM, momentum_quality 전략을 1h 타임프레임으로 시뮬 가능성 검토
- BacktestEngine MIN_TRADES=15 → 30 상향 검토 (학술 기준)

#### C(데이터): Walk-Forward 윈도우 크기 최적화
- 현재 train=2880h/test=720h(30일) → test=1440h(60일)로 확대 검토
- 7일 train / 28일 test 조합 테스트 (리서치 최적 조합)
- DataFeed 실데이터 접근 SSL 문제 해결

#### F(리서치): 1h 타임프레임 전략 실전 사례
- 1h 기반 크립토 전략의 실전 성과 벤치마크
- multi-timeframe 접근법 (1h 진입 + 4h 방향성 필터)

### ⚠️ 핵심 인사이트 (Cycle 210 리서치)
- fold당 최소 30 trades (우리 기준 15는 절반)
- 4h→1h 이동: 파라미터 변경 없이 거래 수 4배
- WFE>0.7 실데이터에서만 유효 (합성 낙관적 편향)
- 7일 train/28일 test가 81개 WF 조합 중 Sharpe 최고(1.252)

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- DataFeed.DEFAULT_FALLBACK_EXCHANGES = ["binance", "okx", "bitget"] 준비됨

### 📋 Paper Trading 자동화 판정 기준

| 지표 | Go 조건 | No-Go 트리거 |
|------|---------|-------------|
| Profit Factor | ≥ 1.4 | < 1.0 즉시 중단 |
| MDD | ≤ 15% | > 20% 즉시 중단 |
| Sharpe (rolling 4주) | ≥ 0.8 | < 0.3 |
| WFE (OOS/IS 수익 비율) | ≥ 0.50 | < 0.30 |
| 주간 승률 | ≥ 45% | < 30% |

**상태**: Cycle 210 완료 → Cycle 211 A(품질) + C(데이터) + F(리서치)
**최우선 과제**: 타임프레임 1h 이동 검토 + fold 최소 거래 수 30 상향 + 실데이터 확보
