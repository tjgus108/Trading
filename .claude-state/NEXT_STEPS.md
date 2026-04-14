# Next Steps

_Last updated: 2026-04-15 (Cycle 122 SIM 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## Cycle 122 완료 사항

### [SIM] Paper Simulation & Auto-improve
- ✅ Python 3.8 호환성 수정: `tuple[]` → `Tuple[]`, `list[]` → `List[]` 변환 (30개 파일)
- ✅ pair_trading.py 타입 힌트 수정 (Tuple import 추가)
- ✅ 3개 PASS 전략 하위 성과 개선:
  1. **dema_cross**: RSI 필터 + 거리 필터 강화 (PF 1.696→개선 목표)
  2. **acceleration_band**: RSI 필터 + 밴드 폭 필터 (0.015→0.025) (PF 1.511→개선 목표)
  3. **roc_ma_cross**: RSI 필터 + ROC 절대값 요구 (>0.5%) + EMA200 (PF 1.577→개선 목표)

### 근거
- paper_simulation.py 실행 불가 (Python 3.7 환경 제약, ccxt 설치 불가)
- QUALITY_AUDIT.csv 기반 분석: PASS 전략 중 하위 3개 (PF<1.7) 타겟팅
- 공통 개선책: RSI 과매수/과매도 필터 추가, 신호 신뢰도 강화

---

## 다음 사이클 힌트 (Cycle 123+)

### 로테이션 기준 다음 카테고리
- MASTER_PLAN에 따라 B(정시) + D(ML) + E(슬리피지) 예상

### 우선 작업
1. **[B] 정시**: 개선된 3개 전략 + 기존 고성과 전략 (engulfing_zone, relative_volume) 실전 재검증
2. **[D] ML**: 피처 17개 상태로 모델 재학습 (Cycle 121 미완료)
3. **[E] 슬리피지**: bps 추적 시스템 실제 배포 후 데이터 수집 (paper trading 필요)

### 잔여 이슈
- paper_simulation.py: Python 버전 업그레이드 또는 docker/venv 격리 필요
- walk-forward 검증: 3개 개선 전략 최소 2개 윈도우 테스트 필요
- 포트폴리오 균형: 현재 PASS 전략 22개 중 실제 배포 가능 전략 선정 (top 5-10개 추천)
