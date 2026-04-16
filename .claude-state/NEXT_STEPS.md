# Next Steps

_Last updated: 2026-04-16 (Cycle 135 완료 — 세션 종료 핸드오프)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 136
- 136 mod 5 = 1 → **A(품질) + C(데이터) + SIM + F(리서치)**
- `python3 scripts/cycle_dispatcher.py` 실행하면 자동 배정

### 최우선 과제 (이번 세션에서 도출)
1. **과최적화 필터 강화**: BacktestEngine에 WFE > 0.5 조건 + Trades >= 50 상향 (리서치 C135에서 권장)
2. **Regime Detection 구현**: `src/data/regime_detector.py` 추가 (HMM k=2~3 또는 GMM, 리서치 C134에서 설계안 도출)
3. **테스트 33개 실패 수정**: 다음 A(품질) 사이클에서 처리
4. **DSR(Deflated Sharpe Ratio) 도입**: 다중 전략 선택 편향 보정 (리서치 C135)

### 이번 세션 주요 성과 (Cycle 133-135)
- **품질**: 테스트 collection errors 389→3, 6598 tests passing
- **실행**: TWAP 비대칭 슬리피지, Telegram/connector exponential backoff
- **리스크**: Kelly Bayesian shrinkage, VaR/CVaR parametric 보정
- **데이터**: VPIN zero-volume 버그, DataFeed LRU 캐시
- **ML**: RF 피처 중요도 영속화, 앙상블 recency decay
- **SIM**: paper_simulation JSON/CSV 저장, √impact 슬리피지, 에러 추적
- **리서치**: 과최적화 사례/방법론(DSR/PBO/CPCV), Regime Detection HMM/GMM

### 후속 과제 (미착수)
- Regime Detection 구현 (설계안 준비됨)
- engulfing_zone/relative_volume 심화 개선
- TWAP 비대칭 슬리피지 실전 데이터 검증
- paper_connector balance 실전 paper trading 검증
- Python 3.7→3.11+ 환경 격리
