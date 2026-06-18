# Current Cycle Briefing

_Cycle 324 | 2026-06-18 | D(ML) + E(실행) + F(리서치)_

## 완료된 작업

### D(ML): supertrend_multi 1h 분석 + walk_forward 그리드 추가
- 1h Paper Sim (0/22 PASS) 원인 분석:
  - rank1 supertrend_multi: Sharpe=0.32, PF=1.14 (4h avg=3.892 대비 크게 낮음)
  - FAIL 원인: 4h 최적화 파라미터(trend_confirm_bars=2-3, atr_threshold=0.5-0.7) 가 1h 노이즈에 취약
- `src/backtest/walk_forward.py` `DEFAULT_GRIDS`에 `supertrend_multi_1h` 추가:
  - atr_threshold: [0.3, 0.4, 0.5] (1h ATR 값 특성 반영)
  - trend_confirm_bars: [4, 6, 8] (1h에서 4-8시간 확인 기간)
  - cmf_confirm=True 고정 (노이즈 필터 강화)

### E(실행): live_paper_trader 4h 타임프레임 지원
- `scripts/live_paper_trader.py` 변경:
  - `--timeframe {1h, 4h, 1d}` 인수 추가 (기본: 1h)
  - 4h 선택 시 interval 자동 14400s (4시간) 설정
  - fetch_latest_candles() + _auto_retrain()에 self.timeframe 전달
  - Bundle 전략(4h OOS PASS)을 4h로 실행하는 경로 완성

### F(리서치): 레짐 기반 전략 스위칭 코드화
- `src/strategy/rotation.py` `recommend_for_regime()` 개선:
  - Bundle PASS 전략 레짐 친화도 매핑 (하드코드→런타임 적용):
    - TREND_UP: OFI v2 + supertrend_multi 우선
    - TREND_DOWN: vwap_cross + value_area 우선
    - HIGH_VOL: cmf 우선 (볼륨 필터 강함)
    - RANGING: 상위 2개만 (포지션 최소화)
  - 기존 키워드 폴백 로직 유지

## 시뮬레이션 결과

| 구분 | 결과 |
|------|------|
| 테스트 | **8413 passed, 23 skipped** |
| Paper Sim 1h (BTC, 22전략) | **0/22 PASS** (유지) |
| Paper Sim rank1 | supertrend_multi (+5.26%, Sharpe=0.32) |
| Bundle OOS 4h (5-fold) | **5/5 PASS** (유지) |
| Bundle rank1 | OFI v2 (avg=4.345, std=0.907) |

## 다음 사이클 (325)

**325 mod 5 = 0 → A(품질) + C(데이터) + F(리서치)**

우선순위:
1. A(품질): supertrend_multi 1h PASS 경계값 분석 — 추가된 `supertrend_multi_1h` 그리드 활용
2. C(데이터): Bundle 4h 리샘플링 데이터 품질 검증
3. F(리서치): 레짐별 전략 성과 사후 분석 (fold별 레짐 추정 + 전략 성과 매칭)
