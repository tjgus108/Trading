# Next Steps

_Last updated: 2026-04-17 (Cycle 137 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 138
- 138 mod 5 = 3 → **E(실행) + A(품질) + SIM + F(리서치)**
- `python3 scripts/cycle_dispatcher.py` 실행하면 자동 배정

### 최우선 과제 (이번 세션에서 도출)
1. **Regime Detection 구현**: `src/data/regime_detector.py` — HMM k=2 (추세/횡보), 리서치 3회 완료, 설계안 준비됨. 실패 사례 분석에서 최우선 권고
2. **Volatility Targeting 포지션 사이징**: 고정 비율 → ATR 기반 동적 사이징 전환 (리서치 C137 권고)
3. **전략 간 상관관계 모니터링**: 활성 전략 상관관계 ≤ 0.5 제한 (군집 매도 방지)
4. **테스트 33개 실패 수정**: 다음 A(품질) 사이클에서 처리
5. **PASS 전략 재평가**: MIN_TRADES 50 + WFE > 0.5 적용 후 PASS 수 변화 확인

### Cycle 137 주요 성과
- **리스크**: DrawdownMonitor 연속손실 감지(3연패→50% 축소) + 쿨다운(1시간)
- **ML**: MIN_TRADES 50, WFE>0.5 필터, DSR 과최적화 보정
- **SIM**: roc_ma_cross/volatility_cluster 파라미터 최적화, Python 3.7 호환 수정
- **리서치**: 실패 사례 3건(슬리피지/regime/군집매도), Volatility Targeting 권고

### 후속 과제 (미착수)
- Regime Detection 구현 (설계안 3회 리서치 준비 완료)
- Volatility Targeting 포지션 사이징
- 전략 상관관계 모니터링/제한
- engulfing_zone/relative_volume 심화 개선
- Paper Trading 실전 검증
