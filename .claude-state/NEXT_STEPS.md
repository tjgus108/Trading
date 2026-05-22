# Next Steps

_Last updated: 2026-05-22 (Cycle 195 A+C+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 195 완료
- 195 mod 5 = 0 → **A(품질) + C(데이터) + F(리서치)** 패턴 ✅
- 다음 Cycle 196: **196 mod 5 = 1 → B(리스크) + D(ML) + F(리서치)**

### 🔥 Cycle 195 주요 성과
- **RollingOOSValidator PASS 경로 테스트**: mock BacktestEngine으로 all_passed=True 코드 패스 검증
- **WalkForwardOptimizer fold_decay E2E**: fold_decay=1.0 실행 시 weighted_oos_sharpe 반환 확인
- **RegimeAwareFeatureBuilder.build_with_cached_regime() 4개 테스트**: 정상/None/invalid/features_only 경로
- **WebSocket stale watchdog**: _stale_watchdog() + asyncio.wait(FIRST_EXCEPTION) → 자동 재연결 트리거
- **BacktestEngine PF 상한 999.99**: 손실 0건 fold의 무한대 PF 방지 (BundleOOS avg 정상화)

### 🎯 Cycle 196 권장 작업 (196 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): Risk Manager 개선
- `DrawdownMonitor` 롤링 윈도우 MDD 계산 추가 (전체 기간 MDD와 별도 트래킹)
- `KellySizer` 파라미터 안정성 테스트: rolling_window 크기별 kelly_fraction 변화 검증
- `CircuitBreaker` 연속 손실 횟수 리셋 조건 명확화 (현재 일부 엣지케이스 미처리)

#### D(ML): ML 파이프라인 개선
- `drift_detector.py` PSIDriftMonitor 단위 테스트 추가 (현재 미테스트)
- `DualGateADWINMonitor` 피처 drift 검출 → 재학습 트리거 로직 E2E 테스트
- AccuracyDriftMonitor.set_feature_reference() 실제 피처 배열로 검증

#### F(리서치): 레짐 기반 전략 스위칭
- DataFeed.fetch_with_regime() → RegimeAwareFeatureBuilder 통합 파이프라인 리서치
- bear 레짐 감지 시 short 신호 가중치 증가 아이디어 정리
- PaperTrader shadow mode 설계: 동일 데이터로 live vs shadow 신호 비교

### 🔥 Cycle 194 주요 성과
- **FeatureBuilder 온체인 피처**: exchange_netflow_norm + sopr_delta (선택적, Cycle 193 리서치 반영)
- **KellySizer(rolling) + VolTargeting(EWMA) + PaperTrader 통합 테스트 5개**: E2E 검증
- **RollingOOSValidator min_oos_trades=3**: 저거래 fold 집계 제외 → 더 정확한 전략 판정
- **BundleOOSResult summary() 버그 수정**: 중복 oos_sharpe_std 라인 제거
- **ML 트레이딩 프로덕션 배포 리서치**: PSI+Page-Hinkley drift 감지 + shadow→canary 파이프라인

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단 (원격 사이클에서는 합성 SIM만 가능)
- DataFeed.DEFAULT_FALLBACK_EXCHANGES = ["binance", "okx", "bitget"] 준비됨
- 로컬 환경에서 `DataFeed(connector, fallback_exchange_ids=DataFeed.DEFAULT_FALLBACK_EXCHANGES)` 활성화

### ⚠️ 핵심 문제: 전략 전부 OOS FAIL (합성 데이터 한계 확인)

**SIM 결과 패턴 (Cycle 195):**
- Bundle OOS (4h): 5/5 FAIL — 합성 GBM 데이터에서 IS Sharpe 음수, OOS std 3~6 (불안정)
- Paper SIM (1h): 22/22 FAIL consistency — BTC=ETH=SOL 동일 결과 (GBM 랜덤워크 특성)
- narrow_range: OOS 0거래 (4h에서 신호 조건 너무 엄격)
- **결론: 실제 Bybit 데이터 확보가 최우선 병목**

### 📋 Paper Trading 자동화 판정 기준

| 지표 | Go 조건 | No-Go 트리거 |
|------|---------|-------------|
| Profit Factor | ≥ 1.4 | < 1.0 즉시 중단 |
| MDD | ≤ 15% | > 20% 즉시 중단 |
| Sharpe (rolling 4주) | ≥ 0.8 | < 0.3 |
| WFE (OOS/IS 수익 비율) | ≥ 0.50 | < 0.30 |
| 주간 승률 | ≥ 45% | < 30% |

---

### 📊 Strategy Performance Reference (Real Data — ⚠️ IS only, OOS 미검증)

| Strategy | Sharpe | Win% | PF | Trades | MDD | Regime |
|----------|--------|------|-------|--------|-----|--------|
| cmf | 6.85 | 57% | 2.29 | 28 | 4.3% | TREND |
| wick_reversal | 6.51 | 54% | 2.03 | 35 | 3.5% | RANGE |
| volume_breakout | 5.91 | 60% | 2.66 | 15 | 2.2% | TREND |
| elder_impulse | 6.29 | 63% | 2.70 | 16 | 3.5% | TREND |
| value_area | 5.24 | 53% | 1.84 | 30 | 5.0% | RANGE |

**⚠️ 위 수치는 IS(In-Sample) 성과. OOS 검증 시 전략 전부 FAIL.**

---

### 🔧 /schedule 원격 에이전트 설정됨
- 5시간마다 자동 실행 (UTC 0/5/10/15/20시)
- 루틴 ID: trig_0145pyi9PxaqL9fbfd25nzEL

---

**상태**: Cycle 195 완료 → Cycle 196 B(리스크) + D(ML) + F(리서치)
**최우선 과제**: 로컬 환경에서 DataFeed fallback 활성화 → WF 파라미터 최적화 + 실데이터 조합으로 OOS PASS 전략 발굴
