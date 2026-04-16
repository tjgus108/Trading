# Next Steps

_Last updated: 2026-04-16 (Cycle 133 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 사이클 (Cycle 134) 힌트

### 로테이션 기준 다음 카테고리
- 134 mod 5 = 4 → **C(데이터) + B(리스크) + SIM + F(리서치)**

### 우선 작업
1. **[C] 데이터**: WebSocket feed 안정성 점검, OrderFlow/VPIN 정확도 검증
2. **[B] 리스크**: DrawdownMonitor 실전 검증, Kelly Sizer 파라미터 재튜닝
3. **[SIM]**: paper_simulation 실행 → 결과 분석
4. **[F] 리서치**: Regime Detection HMM/GMM 구현 방향 구체화 리서치

### Cycle 133 후속 과제
- 테스트 33개 실패 — 다음 A(품질) 사이클에서 수정
- Regime Detection 구현 필요 (리서치에서 업계 표준 확인)
- engulfing_zone/relative_volume 2개 전략 심화 개선 대기
- TWAP 비대칭 슬리피지 모델 실전 데이터 검증 필요
- paper_connector balance 수정 후 실제 paper trading 검증 필요
- Python 환경: 3.7→3.11+ 업그레이드 또는 docker/venv 격리 필요
