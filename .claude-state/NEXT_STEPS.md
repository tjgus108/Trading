# Next Steps

_Last updated: 2026-04-16 (Cycle 134 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 사이클 (Cycle 135) 힌트

### 로테이션 기준 다음 카테고리
- 135 mod 5 = 0 → **A(품질) + E(인프라)**

### 우선 작업
1. **[A] 품질**: 테스트 33개 실패 수정
2. **[E] 인프라**: Python 환경 3.11+ 격리, CI/CD 점검

### Cycle 134 완료 사항
- paper_simulation: 전략 로드 실패/평가 오류 카운트 추적 및 경고 출력
- paper_simulation: run_simulation() 전체 심볼 실패 시 exit code 1 반환
- paper_connector: create_order(price=None) 시 $1.0 기본값 제거 → ValueError로 변경
- VPIN: zero-volume 윈도우 replace(0,1) 버그 수정 → NaN 처리 (잘못된 VPIN 값 방지)
- DataFeed: max_cache_size(128) LRU 퇴거 추가 → 무제한 메모리 증가 방지
- **[B] Risk**: KellySizer input validation (NaN/inf/범위외 win_rate 방어) + from_trade_history 소표본 Bayesian shrinkage
- **[B] Risk**: VaR/CVaR 소표본(T<30) parametric 크로스체크 보정 추가

### 이전 사이클 후속 과제
- Regime Detection 구현 필요 (리서치에서 업계 표준 확인)
- engulfing_zone/relative_volume 2개 전략 심화 개선 대기
- TWAP 비대칭 슬리피지 모델 실전 데이터 검증 필요
- paper_connector balance 수정 후 실제 paper trading 검증 필요
