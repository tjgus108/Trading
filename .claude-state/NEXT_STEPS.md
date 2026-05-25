# Next Steps

_Last updated: 2026-05-25 (Cycle 195 D+E+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 195 완료
- 195 mod 5 = 0 → **D(ML) + E(실행) + F(리서치)** 패턴 ✅
- 다음 Cycle 196: **196 mod 5 = 1 → A(품질) + C(데이터) + F(리서치)**

### 🔥 Cycle 195 주요 성과
- **ML 추론 벤치마크**: predict() 호출마다 latency 추적, benchmark_stats() p50/p95/p99
- **OnChainFeatureStub**: exchange_netflow, sopr, defi_tvl 합성 폴백 인터페이스
- **PaperTrader KellySizer 통합**: BUY→compute_dynamic(), SELL→record_trade() 자동
- **Tiered Slippage**: BTC/ETH 0.05%, SOL/BNB 0.2%, 기타 1.0% (리서치 수치 반영)
- **SIM 66개 전부 FAIL**: value_area ETH Sharpe 0.92 최근접
- **리서치**: IS 승률 80%+는 과적합 신호, 파라미터 5개↑ OOS FAIL 필연

### 🎯 Cycle 196 권장 작업 (196 mod 5 = 1 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 과적합 감사 + 파라미터 민감도 테스트
- 355개 전략 중 파라미터 5개 초과 전략 스캔 → 과적합 위험 분류
- value_area 전략 ±15% 퍼터베이션 테스트 (smooth degradation 확인)
- IS Sharpe > 5.0 전략 자동 경고 플래그 추가

#### C(데이터): 합성 데이터 seed 다양화 + DataFeed 개선
- paper_simulation.py에서 심볼별 동일 seed(42) 사용 문제 → seed 다양화
- BacktestEngine O(n²) 병목: generate(df.iloc[:i+1]) → 증분 방식 검토
- WebSocket HealthMonitor 실전 통합 검증

#### F(리서치): 파라미터 민감도 테스트 방법론
- Walk-Forward 파라미터 perturbation 리서치
- 성공한 OOS 전략의 공통 파라미터 구조 분석

### ⚠️ 핵심 문제
- 실데이터 PASS 전략 0개 — IS→OOS 괴리 심각
- 합성 데이터 동일 seed(42) → 3심볼 사실상 동일 데이터
- Python 3.7 환경 SSL 차단 → 실데이터 확보 불가 (로컬 3.11+ 필요)

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단 (원격 사이클에서는 합성 SIM만 가능)
- DataFeed.DEFAULT_FALLBACK_EXCHANGES = ["binance", "okx", "bitget"] 준비됨

### 📋 Paper Trading 자동화 판정 기준

| 지표 | Go 조건 | No-Go 트리거 |
|------|---------|-------------|
| Profit Factor | ≥ 1.4 | < 1.0 즉시 중단 |
| MDD | ≤ 15% | > 20% 즉시 중단 |
| Sharpe (rolling 4주) | ≥ 0.8 | < 0.3 |
| WFE (OOS/IS 수익 비율) | ≥ 0.50 | < 0.30 |
| 주간 승률 | ≥ 45% | < 30% |

**상태**: Cycle 195 완료 → Cycle 196 A(품질) + C(데이터) + F(리서치)
**최우선 과제**: 과적합 감사 + 합성 데이터 seed 다양화 → OOS PASS 확률 향상
