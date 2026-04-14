# Next Steps

_Last updated: 2026-04-14 (Cycle 121 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관. 100줄 초과 시 요약/정리.

## 다음 사이클 (Cycle 122) 힌트

### 로테이션 기준 다음 카테고리
- MASTER_PLAN 로테이션에 따라 A(품질) + C(데이터) + F(리서치) 예상

### 우선 작업
1. **[A] 품질**: PASS 전략 22개 중 실전 FAIL 20개 재검증 — 과최적화 원인 분석
2. **[C] 데이터**: WebSocket feed 안정성 점검, OrderFlow/VPIN 정확도 검증
3. **[F] 리서치**: walk-forward 검증 기반 배포 전략 선정 사례 조사

### Cycle 121에서 남긴 후속 과제
- ML 피처 17개로 증가 → 실제 모델 재학습 필요 (다음 D 사이클에)
- linear_channel_rev v4, price_action_momentum v2 → 실전 데이터 재백테스트 필요
- 슬리피지 bps 추적 적용 → paper trading 실행 후 실제 bps 분포 분석 필요
- engulfing_zone, relative_volume 외 수익 전략 발굴 시급
