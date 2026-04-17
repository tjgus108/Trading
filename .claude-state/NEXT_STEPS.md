# Next Steps

_Last updated: 2026-04-17 (멀티심볼 live paper trader 배포)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 143
- 143 mod 5 = 3 → **C(데이터) + B(리스크) + F(리서치)** (표 기준 Cycle 4 패턴)

### ⚠️ 핵심 문제: 전략 엣지 부재

22개 전략 모두 실데이터 6개월 WF에서 0 PASS. 인프라/리스크/검증 파이프라인은 완성됐으나 **전략 자체에 엣지가 없음**이 확인됨.

**완료:**
- ~~슬리피지 현실화~~: 0.1% (Cycle 140)
- ~~MIN_TRADES 조정~~: 15 (Cycle 140)
- ~~MC Permutation gate~~: 500 perms, p<0.05 (Cycle 140)
- ~~Regime Detection~~: ADX+EMA+ATR (이전 세션)
- ~~CircuitBreaker 통합~~: live paper trader (Cycle 140)
- ~~실패 테스트 수정~~: 14개 → 0개 (Cycle 142)

**남은 과제:**
1. **전략 엣지 확보**: 기존 전략 파라미터 최적화 또는 새로운 접근 (WFA 기준 유지)
2. 합성 데이터 GARCH 교체
3. ML RF 모델 개선 (3-class → 2-class, test acc 37% → 55%+)
4. 전략 상관관계 모니터링
5. OOS 기간 확장 (1개월 → 3개월)

### 최근 완료
- **Live Paper Trader 멀티심볼**: BTC/ETH/SOL 3심볼 동시 운영 (7일, 1시간 간격)
- **리스크 수정**: 슬리피지 0.05→0.0005, RISK 1%→0.5%, SL ATR*2.5, TP ATR*4, MAX_POS=5
- **Regime Detection**: ADX+EMA+ATR 기반 시장 상태 분류 (TREND_UP/DOWN, RANGING, HIGH_VOL)
- **Strategy Rotation**: 30일 주기 재검증, rotation_state.json 기반 PASS/FAIL 관리

### 후속 과제 (미착수)
- ~~슬리피지 현실화~~ → Cycle 140 완료 (0.05→0.1%)
- ~~Monte Carlo Permutation gate~~ → Cycle 140 완료 (500 perms, p<0.05)
- 합성 데이터 GARCH 교체
- ~~Regime Detection 구현~~ → 이전 세션 완료 (ADX+EMA+ATR)
- 전략 상관관계 모니터링
- OOS 기간 확장 (1개월 → 3개월)
- ML RF 모델 개선: 3-class → 2-class, threshold 0.003→0.01, max_depth 제한
- live paper trader에 ML 시그널 연동 (모델 PASS 이후)
