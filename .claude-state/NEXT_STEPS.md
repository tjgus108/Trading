# Next Steps

_Last updated: 2026-04-15 (Cycle 122 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관. 100줄 초과 시 요약/정리.

## 다음 사이클 (Cycle 123) 힌트

### 로테이션 기준 다음 카테고리
- MASTER_PLAN 로테이션에 따라 A(품질) + C(데이터) + E(실행) 예상

### 우선 작업
1. **[A] 품질**: PASS 전략 22개 중 실전 FAIL 20개 재검증 — 과최적화 원인 분석
2. **[C] 데이터**: WebSocket feed 안정성 점검, OrderFlow/VPIN 정확도 검증
3. **[E] 실행**: 슬리피지 bps 추적 결과 분석, 체결 최적화

### Cycle 122에서 남긴 후속 과제
- DrawdownMonitor 수정 → 실전 paper trading에서 에스컬레이션 시나리오 검증 필요
- 앙상블 가중치 compute_ensemble_weight() → 실제 Bybit 데이터로 모델 재학습 후 검증
- dema_cross, acceleration_band, roc_ma_cross RSI 필터 추가 → 실전 데이터 재백테스트 필요
- Regime Detection 로직 설계 검토 (리서치에서 필수성 확인됨)
- Delta Neutral 전략 구조 연구 (성공 사례에서 MDD 0.80% 기록)
- Python 환경: 3.7→3.11+ 업그레이드 또는 docker/venv 격리 필요
