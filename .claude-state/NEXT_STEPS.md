# Next Steps

_Last updated: 2026-05-21 (Cycle 194 D+E+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 194 완료
- 194 mod 5 = 4 → **D(ML) + E(실행) + F(리서치)** 패턴 ✅
- 다음 Cycle 195: **195 mod 5 = 0 → A(품질) + C(데이터) + F(리서치)**

### 🔥 Cycle 194 주요 성과
- **FeatureBuilder 온체인 피처**: exchange_netflow→netflow_zscore, sopr→sopr_delta (선택적)
- **PaperTrader KellySizer 통합**: compute_dynamic BUY 사이징 + SELL 후 record_trade
- **OOS Sharpe std 필터 개선**: 0-trade 폴드 제외로 노이즈 감소 (traded_sharpes 기준)

### 🎯 Cycle 195 권장 작업 (195 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): OOS std 개선 효과 검증
- Bundle OOS 재실행 후 개선된 std 수치 확인 (0-trade 폴드 제외 효과)
- value_area: 4/9 fold PASS → 개선된 std 기준으로 PASS 가능성 재평가
- narrow_range: OOS std 3.162 → traded folds만 계산 시 얼마나 줄었는지 확인

#### A(품질): drift_detector.py 재학습 트리거 추가
- `DriftDetector`에 `should_retrain(oos_sharpe_7d: float) -> bool` 메서드 추가
- threshold: rolling 7일 OOS Sharpe < 0.3 → retrain 권고
- F(리서치) 결과 반영: 월 1회 재학습 + drift 감지 시 조기 재학습

#### C(데이터): DataFeed onchain 컬럼 지원
- `DataFeed.fetch()` 결과에 exchange_netflow, sopr 컬럼 추가 (mock/real 모두)
- MockDataFeed에 `exchange_netflow`, `sopr` 컬럼 생성 (정규분포 노이즈)
- 테스트: FeatureBuilder 온체인 피처가 실제 DataFeed 파이프라인에서 동작하는지 확인

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단 (원격 사이클에서는 합성 SIM만 가능)
- DataFeed.DEFAULT_FALLBACK_EXCHANGES = ["binance", "okx", "bitget"] 준비됨
- 로컬 환경에서 실데이터 활성화 필요

### 📊 SIM 결과 기반 분석 (Cycle 194)

**Bundle OOS (BTC/USDT 4h, 합성):**
- 0/5 PASS — value_area 최선 (4/9 fold PASS, 단 std=6.152로 FAIL)
- OOS Sharpe std 과대 원인: 폴드당 2~5 trades → Sharpe 분산 폭발
- **개선**: 0-trade 폴드 제외로 std 노이즈 감소 (traded_sharpes 기준)

**Paper SIM (합성):**
- 0/22 PASS — value_area 최선 (+0.36%, 0/8 consistency)
- dema_cross, price_cluster: 여전히 0 trades → 파라미터 추가 완화 필요

**다음 액션:**
1. OOS std 개선 효과 확인 (A 카테고리 검증)
2. DataFeed onchain 컬럼 파이프라인 연결 (C 카테고리)
3. drift_detector 재학습 트리거 (A 카테고리 + F 리서치 반영)

### 🔥 Cycle 193 주요 성과
- **WebSocket ConnectionHealthMonitor**: stale 감지, 재연결 이력, health summary
- **KellySizer rolling win_rate**: record_trade() + compute_dynamic() — 실전 데이터 기반 자동 포지션 사이징
- **온체인 리서치**: Exchange Inflow 2σ→1주 하락 72%, 최우선 신호 3개 도출

### 📋 Paper Trading 자동화 판정 기준

| 지표 | Go 조건 | No-Go 트리거 |
|------|---------|-------------|
| Profit Factor | ≥ 1.4 | < 1.0 즉시 중단 |
| MDD | ≤ 15% | > 20% 즉시 중단 |
| Sharpe (rolling 4주) | ≥ 0.8 | < 0.3 |
| WFE (OOS/IS 수익 비율) | ≥ 0.50 | < 0.30 |
| 주간 승률 | ≥ 45% | < 30% |

### ⚠️ 핵심 문제: 전략 전부 OOS FAIL (합성 데이터 한계 확인)

- IS Sharpe 자체가 음수 → 합성 데이터에서는 최적화 신호 없음
- **결론: 실제 Bybit 데이터 확보가 최우선 병목**

### ✅ Cycle 194 완료 사항
- FeatureBuilder 온체인 피처 (exchange_netflow, sopr) ✅
- PaperTrader KellySizer 통합 ✅
- OOS Sharpe std 0-trade 폴드 필터 개선 ✅
- 전체 테스트 7710 PASS ✅

### 🔧 /schedule 원격 에이전트 설정됨
- 5시간마다 자동 실행 (UTC 0/5/10/15/20시)

---

**상태**: Cycle 194 완료 → Cycle 195 A(품질) + C(데이터) + F(리서치)
**최우선 과제**: OOS std 개선 효과 검증 + DataFeed onchain 컬럼 파이프라인 연결
