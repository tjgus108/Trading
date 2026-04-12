# Cycle 106 - price_cluster & roc_ma_cross 개선 진행

## 현재 상태
- **price_cluster** (v2): HIGH confidence 필터 적용 → 테스트 통과하나 거래량 감소로 실패
- **roc_ma_cross** (v2): ROC > 0 / < 0 추가 필터 + STD_MULT 2.0 상향 → 테스트 통과, 재시뮬레이션 진행 중

## 문제 분석
1. **price_cluster**: 필터가 과도해 신호 생성 90% 이상 감소 → -0.66% 손실
   - 차후: threshold 기반 필터링보다 거래 수익률 우선순위 분석 필요
   
2. **roc_ma_cross**: PF 1.34 → 1.5+ 목표
   - 추가 필터 (ROC 부호 확인) + STD_MULT 상향으로 고신뢰도 거래만 선별
   - 시뮬레이션 실행 중

## 파일 수정
- `/home/user/Trading/src/strategy/price_cluster.py` (v2)
- `/home/user/Trading/src/strategy/roc_ma_cross.py` (v2)

## 다음 단계
1. roc_ma_cross 재시뮬 결과 확인
2. PF < 1.5 여전하면, 다른 FAIL 전략 재평가
3. quality_audit.py 재실행

## 진행 중인 작업
- paper_simulation.py 실행 중 (23514 PID, ~50% 완료 예상)
