# Next Steps

_Last updated: 2026-04-17 (멀티심볼 live paper trader 배포)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 140
- 140 mod 5 = 0 → **A(품질) + C(데이터) + SIM + F(리서치)** (표 기준 Cycle 1 패턴)
- `python3 scripts/cycle_dispatcher.py` 실행하면 자동 배정

### ⚠️ 최우선: 오버피팅 대응 (Cycle 139 분석 결과 기반)

**즉시 조치 (다음 사이클):**
1. **슬리피지 현실화**: BacktestEngine 슬리피지 0.05% → 0.2% 상향
2. **MIN_TRADES 조정**: 50 → 15 (실데이터에서 거래 수 부족 문제 해소)
3. **실데이터 기반 재검증**: data_utils.py로 Bybit 데이터 다운로드 후 전략 재평가

**중기 조치:**
4. **합성 데이터 생성기 교체**: GARCH(1,1)+Student-t 분포 (변동성 클러스터링+fat tails)
5. **Monte Carlo Permutation gate**: 1,000회 셔플, p < 0.05 시에만 PASS
6. **OOS 기간 확장**: 1개월 → 3개월 + regime 다양성 요건

**장기 과제:**
7. **Regime Detection 구현**: HMM k=2 (추세/횡보)
8. **전략 상관관계 모니터링**: ≤ 0.5 제한
9. **Rolling Sharpe 자동 비활성화**: < 0.0 시 전략 off

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
