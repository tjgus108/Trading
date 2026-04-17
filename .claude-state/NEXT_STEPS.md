# Next Steps

_Last updated: 2026-04-17 (Cycle 139 오버피팅 분석 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 140
- 140 mod 5 = 0 → **A(품질) + D(ML) + SIM + F(리서치)**

### ⚠️ 긴급 과제: 오버피팅 대응 (Cycle 139 분석 완료)

**분석 결과**: 22개 PASS 전략이 합성 데이터에서만 작동, 실제 데이터에서 전부 실패.

**5가지 근본 원인** (우선순위):
1. 비현실적 슬리피지 (0.05% → 실제 0.2-1.0%)
2. 합성 데이터 특성 불일치 (두터운 꼬리, 간격, 레짐 체인지 없음)
3. 신호 조건 파라미터 미스매치 (ATR 범위 0.3-5.0 합성에만 맞춤)
4. Walk-Forward 검증 부재 (합성만으로 PASS 판정)
5. MIN_TRADES 임계값 과도히 높음 (50 → 품질 높은 저신호 전략 제외)

### 즉시 실행 (이번 사이클 140)

1. **MIN_TRADES 조정**: 50 → 15 (저신호 고품질 전략 재평가)
2. **Slippage 현실화**: 0.05% → 0.2% (백테스트 신뢰도 상향)
3. **Real Data PASS 기준**: Walk-Forward 일관성 50% 이상 (합성 제외)
4. **ATR 조건 동적화**: 0.3-5.0 범위 → ATR 20~80 percentile

**파일 수정 필요**:
- `src/backtest/engine.py`: MIN_TRADES 15, slippage 0.002 (0.2%)
- `scripts/quality_audit.py`: Walk-Forward 로직 추가 또는 합성 데이터만 사용 명시
- `scripts/paper_simulation.py`: Real data PASS 기준 명확화

### 최우선 과제 (1-2주)

**Regime Detection 구현** (논문 완료):
- HMM k=2 (추세/횡보) 인식
- 모드별 파라미터 적응
- 효과: 실제 데이터 성과 10-20% 개선

**합성 데이터 생성 개선**:
- Fat-tail 분포 (Student-t df=5)
- GARCH 변동성 클러스터링
- Regime switch 자동 전환
- Overnight gap 모뮬레이션

### 후속 과제 (미착수)

- Rolling Sharpe 모니터 (30일 < 0.5 시 비활성화)
- 전략 상관관계 모니터링/제한
- 테스트넷/실전 환경 명시적 분리
- 정적 데이터 → 실시간 업데이트로 마이그레이션

---

## 상태 요약

**Cycle 139 완료**:
- [SIM] 오버피팅 근본 원인 5가지 파악
- [SIM] Volume Breakout 등 신호 생성 분석 (0% ATR 매치)
- [SIM] 합성 vs 실제 데이터 차이 정량화
- [SIM] 백테스트 vs 실행 갭 분석 (3% 수익 손실)

**다음 어젠다** (Cycle 140):
- MIN_TRADES/Slippage 즉시 수정 (+ 테스트)
- Walk-Forward 통합 (quality_audit.py)
- Regime Detection 구현
