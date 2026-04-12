# Cycle 121 Todo

## wick_reversal 2차 강화 결과 (Cycle 120)
- Sharpe 0.49 (< 1.0) ❌
- Profit Factor 1.10 (< 1.5) ❌
- Trades 48 (>= 30) ✅
- **Verdict: FAIL** — 라이브 실행 금지

### 개선 사항 (Cycle 120)
1. RSI 오버부스트/오버셀드 필터 추가 (선택적)
2. 기본 거래 조건 유지 (0.8배 볼륨)
3. 추세 필터 강화 (14기간 고점/저점)

### 근본 원인
- 패턴 기반 신호만으로는 신뢰도 부족
- 모멘텀/추세 강도 지표 부재
- Sharpe 개선을 위해 승률 향상 또는 손실 관리 필요

## Cycle 121 옵션
1. **wick_reversal 3차 개선**
   - MACD 신호 추가 (추세 확인)
   - Bollinger Band 밴드폭 필터 (변동성 확인)
   - 거래당 조정 손절/익절 동적 계산

2. **신 전략 개발** (더 우선)
   - Volume Cluster + Support/Resistance
   - RSI Divergence 감지
   - 다중 시간틀 확인

3. **포트폴리오 최적화**
   - 상위 전략들의 상관관계 분석
   - 균등/가중 배분 vs 최적화 배분

## 파일 경로
- 전략: /home/user/Trading/src/strategy/wick_reversal.py
- 테스트: /home/user/Trading/tests/test_wick_reversal.py
- 시뮬 리포트: /home/user/Trading/.claude-state/PAPER_SIMULATION_REPORT.md
