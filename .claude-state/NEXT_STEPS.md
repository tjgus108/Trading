# Next Steps

_Last updated: 2026-04-20 (Cycle 169 품질검증 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 170

### ✅ Cycle 169 완료 사항 (품질 검증)

#### 테스트 실패 수정: 15 failed → 0 failed ✅ COMPLETE
- `test_result_split_info_populated`: split_info 합계에 `n_cal` 누락 수정
- `test_generate_buy/sell_signal_without_model`: models/ 디렉토리 pkl 파일 존재 시 auto-load되는 문제 → `load_latest` mock 적용
- `test_ml_rf_min_trades`: 동일 auto-load 문제 mock 수정
- `test_connect_calls_check_permissions`: `__new__` 사용 시 `_timeout_ms` 등 누락 속성 추가
- `pyyaml` 패키지 설치로 registry 테스트 10건 해소
- **결과: 7188 passed, 0 failed, 17 skipped**

### ✅ Cycle 168 완료 사항

#### E(실행): HealthChecker + Notifier 스켈레톤 ✅ COMPLETE
- `src/exchange/health_check.py`: 5분 간격 liveness check, 데이터 지연 감지, 자동 재연결(최대 3회), 보호 모드
- `src/exchange/notifier.py`: Critical/Silent/Suppress 3계층 알림 인터페이스 (Telegram API 미연동 스텁)
- `scripts/live_paper_trader.py`: HealthChecker 통합 (tick에서 health check, 보호 모드 시 주문 차단)
- 테스트 35개 추가 (health_check 23개 + notifier 10개 + 기존 통합 2개) → 70 passed

#### F(리서치): Health Check 패턴 + API 장애 사례 ✅ COMPLETE
- Hyperliquid 27분 장애(2025.07), XTB 수 시간 장애 → Kill Switch 독립성 필수 확인
- 권장 인터벌: API liveness 5분, WebSocket heartbeat 10~30s, 포지션 일관성 5분, Watchdog 15분
- Exponential backoff: base=1s, max=30s, full jitter, 최대 10회
- Graceful Degradation 3단계: 지연 감지→진입 차단→Kill Switch+청산
- 성공 스택: Prometheus + Grafana + Telegram (RESEARCH_CYCLE168.md)

### ✅ Cycle 167 완료 사항

#### B(리스크): Kelly 레짐 스무딩 + CF VaR ✅ COMPLETE
- `regime_smooth_alpha` EMA 블렌딩 (opt-in, 기본 0.0)
- Cornish-Fisher expansion: 왜도/첨도 반영 꼬리위험 VaR
- 테스트 4개 추가 → 174 passed (risk)

#### D(ML): MultiWindowEnsemble ✅ COMPLETE
- 30/60/90일 윈도우 RF/ExtraTrees/XGBoost 독립 학습
- softmax 동적 가중치 (temp=1.5), rolling 20거래 갱신
- 테스트 9개 추가

#### F(리서치): 실패/성공 사례 + 앙상블 실증 ✅ COMPLETE
- 자동화 계좌 73% 6개월 내 실패 (RESEARCH_CYCLE167.md)
- Stacking > Blending > Voting 실증 확인

### ⚠️ 핵심 문제: 전략 엣지 부재 → 해법 확인됨

22개 전략 모두 실데이터 6개월 WF에서 0 PASS. **유효한 경로:**

#### 경로 1: ML 2-class (UP/DOWN) — **PASS 확인 (42일 WF)**
- BTC 1000캔들: test acc 63.5%, val 67.3% → **PASS**

**다음 구현 과제 (우선순위):**
1. ~~FR delta + OI~~ ✅ | 2. ~~SHAP~~ ✅ | 3. ~~calibration~~ ✅ | 4. ~~ExtraTrees~~ ✅
5. ~~XGBoost 모델~~ ✅ | 6. ~~XGBoost 다시간 앙상블~~ ✅
7. ~~MDD CB~~ ✅ | 8. ~~max_loss_pct~~ ✅ | 9. ~~PSI~~ ✅ | 10. ~~수수료~~ ✅
11. ~~PSI-AccDrift 통합~~ ✅ | 12. **live_paper_trader 7일 운영** ← 다음 E 사이클
13. ~~Telegram 알림~~ ✅ (스켈레톤) — 실제 API 연동은 추후
14. ~~Health check 루프~~ ✅ — 5분 liveness + 데이터 지연 + 보호 모드
15. ~~Kelly 레짐 스무딩~~ ✅ | 16. ~~CF VaR~~ ✅
