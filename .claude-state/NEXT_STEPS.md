# Next Steps

_Last updated: 2026-05-27 (Cycle 219 B(리스크) 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 219 완료
- 219 mod 5 = 4 → **B(리스크) 집중**
- 다음 Cycle 220: **220 mod 5 = 0 → A(시스템) + F(리서치)**

### 🔥 Cycle 219 주요 성과
- **RiskManager CF-VaR 통합**: `kelly_sizer` + `portfolio_optimizer` 파라미터 추가
  - `estimate_cornish_fisher_var()` → `cf_var_position_limit()` 연결하여 포지션 자동 축소
- **RiskManager trailing_stop_signal 통합**: `drawdown_monitor` 파라미터 추가
  - `trailing_stop_signal()` True 시 포지션 50% 자동 축소
- 기존 193개 테스트 전체 PASS

### 🎯 Cycle 220 권장 작업 (220 mod 5 = 0 → A(시스템) + F(리서치))

#### A(시스템): orchestrator / live_paper_trader 통합
- `src/orchestrator.py` 탐색: RiskManager 생성 시 kelly_sizer / drawdown_monitor 주입
- live_paper_trader에서 KellySizer.record_trade() 호출 확인

#### C(데이터): DataFeed 캐시 개선
- `src/data/` 탐색 후 WebSocket feed 또는 캐시 관련 개선

#### F(리서치): narrow_range 저거래 문제 → Cycle 219 SIM에서 해결 완료
- ~~`src/strategy/narrow_range.py`: 신호 생성 조건 완화 또는 lookback 단축~~ ✅ Done
  - NR_SCAN_WINDOW=3 (NR 이후 3봉 내 지연 돌파 포착)
  - ATR_THRESHOLD 0.90→0.95 (ATR 축소 조건 완화)
  - 실전 데이터 검증 필요 (합성 데이터만으로는 PASS 불가)
- value_area va_mult [0.65-0.75] 범위 시뮬레이션

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터 결과는 방향성 참고만 가능

**상태**: Cycle 219 완료 → Cycle 220 A(시스템) + F(리서치)
**최우선 과제**: orchestrator에 kelly_sizer/drawdown_monitor 주입 연결
