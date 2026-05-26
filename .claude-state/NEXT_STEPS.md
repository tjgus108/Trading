# Next Steps

_Last updated: 2026-05-26 (Cycle 213 C+B+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 213 완료
- 213 mod 5 = 3 → **C(데이터) + B(리스크) + F(리서치)** ✅
- 다음 Cycle 214: **214 mod 5 = 4 → D(ML) + E(실행) + F(리서치)**

### 🔥 Cycle 213 주요 성과
- **volume_breakout ATR 버그 수정**: 절대값($10) → 퍼센트 ATR(atr/close*100) 변경
  - 효과: 0 trades → 72 trades (WF 1h 시뮬, Sharpe 6.09, PF 2.31)
- **DrawdownMonitor.compare_rolling_mdd()**: 단기(50봉) vs 장기 MDD 비교 메서드 추가
  - ratio > 1.5 & short_mdd > 5% → deteriorating=True
- **F(리서치) 발견**: GBM uptrend 출현율 57.6% → 정상 (0 trades 원인은 ATR 버그였음)
- **시뮬 결과**: 0/22 WF + 0/5 Bundle (합성 GBM 한계)

### 🎯 Cycle 214 권장 작업 (214 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): ML 모델 피처 분석
- `src/ml/features.py` 피처 중요도: atr_pct 신규 피처 효과 분석
- RF 모델 재학습 필요 여부 확인 (volume_breakout ATR 수정으로 신호 패턴 변화)
- Walk-Forward 토너먼트 파이프라인 연결 상태 점검

#### E(실행): Paper Trading TWAP 검증
- `src/execution/` TWAP 실행기 smoke 테스트
- 슬리피지 모델: 현재 고정 0.05% vs ATR 기반 동적 슬리피지 비교
- Telegram 알림 모듈 연결 상태 확인

#### F(리서치): narrow_range 4h 저거래 구조 분석
- 4h봉에서 narrow_range 조건 출현 빈도 계산 (GBM 시뮬)
- min_trades 기준을 3 → 2로 완화하는 대신 Sharpe 기준 강화 검토
- 실데이터 PASS 기준 재검토: Bundle OOS에서 저거래 기준 4h vs 1h 차별화

### ⚠️ 핵심 인사이트 (Cycle 213 시뮬)
- **volume_breakout**: ATR 버그 수정 후 3위로 부상 (Sharpe 6.09, PF 2.31, MDD 6.9%)
  - GBM에서도 건전한 지표 → 실데이터 검증 가치 있음
- **price_action_momentum, cmf**: 지속적 TOP 성과 (Sharpe 7.62, 5.62)
- **Bundle OOS 4h**: cmf IS Sharpe 100% 음수 → GBM 합성 단방향 추세 의존 전략 불리
- **narrow_range 저거래**: 4h봉 구조적 문제 → D(ML) 사이클에서 해결책 탐색

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터(GBM) 결과는 방향성 참고만 가능 (PASS/FAIL 판정 불가)
- 거래소 SSL 타임아웃: 5000ms

### 📋 시뮬레이션 파라미터 현황 (Cycle 213 기준)

| 설정 | 값 | 변경 사유 |
|------|----|---------| 
| TRAIN_HOURS | 5040h (210일) | Cycle 211에서 확대 (IS 충분 확보) |
| TEST_HOURS | 1440h (60일) | Cycle 211에서 확대 (fold당 trades ↑) |
| STEP_HOURS | 720h (30일) | 유지 (겹침 허용) |
| WF Windows | 4개 | Cycle 211에서 확대 (통계 신뢰도 향상) |
| SSL Timeout | 5000ms | 빠른 fallback |
| price_cluster BOUNCE_THRESHOLD | 2% | Cycle 212에서 0.5%→2% 완화 |
| volume_breakout ATR 필터 | 퍼센트 ATR (0.1%~10%) | Cycle 213에서 절대값→% 변경 |

**상태**: Cycle 213 완료 → Cycle 214 D(ML) + E(실행) + F(리서치)
**최우선 과제**: narrow_range 4h 저거래 구조 분석 + TWAP 실행기 검증
