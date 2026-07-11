# Next Steps

_Last updated: 2026-07-11 (Cycle 416 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 416

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 416 | B+D+F | DM kelly_fraction+sharpe_decay, streak+sharpe_decay, HIGH_VOL+decay_recovery 복합 3케이스(+3) + optimize_donchian 2케이스+select_features_pfi 반환검증 2케이스(+4→8707 총계, 8684 passed), **roc_ma_cross AvgTrades=14 구조적 ceiling 확정**(PASS=BTC 급등기 Q4/Q1, FAIL=저거래량 H1/Q2), walk_forward.py roc_ma_cross Cycle416 F 분석 주석 추가, 1h PASS 1/19 유지, Bundle OOS 5/5 유지 |
| 415 | A+C+F | apply_wfe 미커버 3케이스+feed 지표 경계 3케이스(+6→8700 총계, 8677 passed), **price_cluster 2/8 ceiling 구조 확정**(PASS=RANGING진성 2구간, FAIL=TREND_UP), walk_forward.py atr_bounce_factor [0.0,0.3,0.5,1.0]→[0.5] 단일값(75% 그리드 감소), 1h PASS 1/19 유지, Bundle OOS 5/5 유지 |
| 409 | D+E+F | select_features_pfi n99/2feat/subset 3개+optimize_narrow_range type 1개+PaperConnector 3개(+7→8655 총계, 8632 passed), **price_action_momentum 1h 구조적한계 확정**(Sh=-1.08, PF=0.97<1.0, roc5+body_strength가 RANGING에서 14%/bar 과다 신호), walk_forward.py DEFAULT_GRIDS["price_action_momentum"]={} 추가, 1h PASS 1/19 유지, Bundle OOS 5/5 유지 |
| 410 | A+C+F | apply_wfe 미커버3개+DataFeed 지표경계3개(+6→8661 총계, 8638 passed), **relative_volume 1h 구조적한계 확정**(Sh=-0.99, PF=0.92<1.0, RANGING 볼륨스파이크→즉각반전→음의엣지), walk_forward.py DEFAULT_GRIDS["relative_volume"]={} 추가, 1h PASS 1/19 유지, Bundle OOS 5/5 유지 |
| 411 | B+D+F | transition_cushion+set_regime 복합3개+optimize strategyname/bestparams3개(+6→8667 총계, 8644 passed), **volume_breakout 1h 구조적한계 확정**(Sh=-0.74, PF=0.96<1.0, SL부재+spike1.5x과다+RANGING), walk_forward.py DEFAULT_GRIDS["volume_breakout"]={} 추가, 1h PASS 1/19 유지, Bundle OOS 5/5 유지 |
| 412 | B+D+F | CB max_daily+consec_loss 복합3개+optimize_roc_ma_cross oos_std/roc_min_abs/fold_pass_rate 3개(+6→8679 총계, 8656 passed), **momentum_quality 1h 구조적한계 확정**(Sh=-1.19, PF=0.96<1.0, consistency_buy_threshold=0.3 DEAD PARAM, RANGING 47.3% 모멘텀 노이즈), walk_forward.py DEFAULT_GRIDS["momentum_quality"]={} 추가, 1h PASS 1/19 유지, Bundle OOS 5/5 유지 |
| 413 | C+B+F | DataFeed atr14경계/ema50반응속도/return_5부호 3개+DM trailing_stop경계/threshold1.0/kelly+mdd_warn복합 3개(+6→8685 총계, 8662 passed), **positional_scaling 1h 구조적한계 확정**(Sh=-0.38, pullback==rally 동일조건→BUY/SELL 방향성에지없음, mult 파라미터화 불가), 1h PASS 1/19 유지, Bundle OOS 5/5 유지 |
| 414 | D+E+F | optimize_donchian 3개+select_features_pfi 경계값 3개+PaperConnector 3개(+9→8694 총계, 8671 passed), **narrow_range 1h 구조적한계 재확정**(Sh=-0.51, PF=0.97<1.0, atr_mult/range_lookback 파라미터화 불가-RANGING에서 동일 구조 문제), walk_forward.py 주석 추가, 1h PASS 1/19 유지, Bundle OOS 5/5 유지 |

### 🎯 Cycle 417 작업 방향 (417 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): CircuitBreaker 또는 DrawdownMonitor 추가 미커버 케이스

- **배경**: 리스크 카테고리 로테이션 (Cycle416 B DrawdownMonitor compound 완료)
- **작업 방향**: `tests/test_circuit_breaker.py` 또는 `tests/test_drawdown_monitor.py`
  - CircuitBreaker 경계값 검토 (is_halted 임계값, window 만료 등)
  - DrawdownMonitor 추가 미커버 복합 케이스 (BLOCK+sharpe_decay, streak+ATR compound 등)

#### D(ML): optimize_price_cluster 또는 optimize_frama 미커버 케이스

- **배경**: ML 카테고리 로테이션 (Cycle416 D optimize_donchian + pfi 반환 검증 완료)
- **작업 방향**: `tests/test_phase_d.py`
  - optimize_price_cluster 기본 호출 + fold_pass_rate 타입 검증
  - optimize_frama 추가 경계값 (avg_oos_sharpe float, fold_pass_rate range 등)

#### F(리서치): frama 4/8+ Consistency 가능성 분석

- **배경**: Cycle416 F에서 roc_ma_cross AvgTrades=14 구조적 ceiling 확정; frama (Sh=0.44, 0/8) 다음 탐색 대상
- **작업 방향**: frama (BTC 1h: Sh=0.44, PF=1.11, Trades=65, 0/8 Consistency)
  - weak_rsi_buy_max=50 확정 후에도 0/8 유지: WFO 27-combo 그리드가 최적 파라미터 자동 선택하는지 확인
  - WFO 그리드에서 weak_rsi_buy_max=[40,50,60] 중 어떤 값이 선택되는지 분석
  - frama 0/8 ceiling 원인: gap<1% RANGING 지배 vs 선택된 파라미터 문제 구분
  - 결론: frama 추가 탐색 가능성 vs 완전 보류 재확인

### ⚠️ 주의 사항 (Cycle 416 이후)

- **roc_ma_cross AvgTrades=14 구조적 ceiling 확정** (Cycle416 F):
  - PASS 구간: 2023 Q4(BTC 27k→44k 급등) + 2024 Q1(44k→73k 상승) — 볼륨 스파이크 동반
  - FAIL 구간: 2023 H1(15k→30k 저거래량 회복) + 2024 Q2(73k→65k 조정) — vol_ratio at signals=0.89-0.97(<1.2)
  - AvgTrades=14 ceiling = BTC 1h 60d × vol_ratio_min=1.2 → ~10% 통과율 (구조적)
  - **결론**: vol_ratio 조정(1.1→2/8 Cycle382), 필터 추가(→역효과) 모두 확인. 4/8 Consistency가 구조적 최적점. roc_ma_cross 추가 탐색 완전 종료.
  - walk_forward.py roc_ma_cross Cycle416 F 분석 주석 추가 완료

### ⚠️ 주의 사항 (Cycle 415 이후)

- **price_cluster 2/8 Consistency ceiling 구조 확정** (Cycle415 F):
  - PASS 구간: 2023 Q2(BTC 25k-31k 횡보) + 2023 Q4(Oct 펌프 공고화) — 진성 RANGING 2개 구간
  - FAIL 구간: 2023 H1 상승(15k→30k) + 2024 H1 상승(40k→60k) — TREND_UP 시 cluster sweep
  - vol_regime_filter=True 적용에도 TREND_UP 일부 신호 발생 → PF<1.5 → FAIL
  - **결론**: RANGING 47.3% BTC 1h에서 2/8 ceiling이 구조적 한계. 추가 파라미터 탐색 완전 종료.
  - walk_forward.py atr_bounce_factor 단일값화 ([0.0,0.3,0.5,1.0]→[0.5]) 완료 (Cycle415 F)
  - price_cluster는 보조 전략으로 보존 (roc_ma_cross 비활성 시 대체 역할)

### ⚠️ 주의 사항 (Cycle 414 이후)

- **narrow_range 1h 탐색 완전 종료** (Cycle414 F):
  - BTC 1h Sh=-0.51, PF=0.97(<1.0=음의에지), Trades=46, 0/8 Consistency
  - atr_mult 파라미터화: `_atr_threshold` 강화해도 RANGING에서 ATR 낮아 조건 과다 충족 → 에지 불변
  - range_lookback(nr_lookback=5→7): RANGING에서 NR7도 빈발 → BUY/SELL 대칭성 유지 → 에지 없음
  - **결론**: Cycle406 F 확정 재확인. narrow_range 1h BTC 추가 파라미터 탐색 완전 종료.

### ⚠️ 주의 사항 (Cycle 413 이후)

- **positional_scaling 탐색 완전 보류** (Cycle413 F):
  - `pullback == rally` 동일 조건 (`-threshold <= deviation <= threshold`) — BUY/SELL 진입 구간 완전 동일
  - BTC 1h Sh=-0.38, PF=1.09(**break-even**), Trades=34, 1/8 Consistency, SharpeStd=2.82
  - pullback_atr_mult 파라미터화 불가: 구간 넓혀도 BUY/SELL 대칭성 유지 → 에지 없음
  - **결론**: 방향성 에지가 구조적으로 없음 (pullback=rally 동일). 추가 탐색 금지.
  - walk_forward.py DEFAULT_GRIDS["positional_scaling"]={} 기존 유지

### ⚠️ 주의 사항 (Cycle 412 이후)

- **momentum_quality 탐색 완전 보류** (Cycle412 F):
  - quality_score = consistency*2-1 + (acceleration>0) → RANGING(47.3%) BTC 1h에서 빈발
  - consistency_buy_threshold=0.3: DEAD PARAM (quality_score>0.8 조건이 이미 consistency>0.4 함의)
  - BTC 1h Sh=-1.19, PF=0.96(**<1.0, 음의 엣지**), Trades=71, 1/8 Consistency, SharpeStd=3.29
  - quality_score_buy_threshold=1.5 → Trades<15 위험, 구조 미해결
  - **결론**: RANGING 47.3% BTC 1h에서 모멘텀 품질 전략 구조적 실패. 추가 탐색 금지.
  - walk_forward.py DEFAULT_GRIDS["momentum_quality"]={} 추가 (구조적 한계 주석)

### ⚠️ 주의 사항 (Cycle 411 이후)

- **volume_breakout 탐색 완전 보류** (Cycle411 F):
  - _SPIKE_MULT=1.5 하드코딩 → RANGING(47.3%) BTC 1h에서 신호 빈발 (Trades=72)
  - SL 파라미터 없음 → MDD 22.1% > 20% 구조적 초과 (BacktestEngine max_hold_candles만으로 관리)
  - EMA50 추세 필터가 confidence에만 사용 (신호 차단 불가) → RANGING BUY/SELL 동등 발생
  - BTC 1h Sh=-0.74, PF=0.96(**<1.0, 음의 엣지**), Trades=72, 0/8 Consistency
  - 파라미터화 방향: spike_mult=2.0 → Trades<15 위험, SL 추가 → 음의 엣지 구조 미해결
  - **결론**: RANGING 47.3% BTC 1h에서 구조적 실패. 추가 탐색 금지.
  - walk_forward.py DEFAULT_GRIDS["volume_breakout"]={} 추가 (구조적 한계 주석)

### ⚠️ 주의 사항 (Cycle 410 이후)

- **relative_volume 탐색 완전 보류** (Cycle410 F):
  - RANGING(47.3%) BTC 1h에서 rvol>1.2 조건이 단기 거래량 노이즈로도 빈번히 충족
  - RSI<68 허용 범위 과다 → RANGING RSI 중립(40-60) 구간 거의 모두 통과
  - BTC 1h Sh=-0.99, PF=0.92(**<1.0, 음의 엣지**), Trades=64, 0/8 Consistency
  - 파라미터 개선 방향: rvol≥1.6 → Trades<15 가능; RSI<50 강화 → 음의 엣지 더 나빠짐; bull_only → Trades 감소
  - **결론**: 추세 추종 볼륨 전략이 RANGING 47.3% BTC 1h에서 구조적 실패. 추가 탐색 금지.
  - walk_forward.py DEFAULT_GRIDS["relative_volume"]={} 추가 (구조적 한계 주석)

### ⚠️ 주의 사항 (Cycle 409 이후)

- **price_action_momentum 탐색 완전 보류** (Cycle409 F):
  - roc5 > 0.005 + body_strength >= 0.50 AND 조건이 RANGING(47.3%) BTC 1h에서 14%/bar 빈도 충족
  - BTC 1h Sh=-1.08, PF=0.97(**<1.0, 음의 엣지**), Trades=73, 1/8 Consistency
  - 파라미터화 가능 요소: body_strength_threshold, roc5_threshold 하드코딩
    → 강화 시 이미 음의 엣지에서 더 나쁜 timing → 개선 불가
  - **결론**: 모멘텀 추종 전략이 RANGING 47.3% BTC 1h에서 구조적 실패. 추가 탐색 금지.
  - walk_forward.py DEFAULT_GRIDS["price_action_momentum"]={} 추가 (구조적 한계 주석)

### ⚠️ 주의 사항 (Cycle 408 이후)

- **htf_ema 탐색 완전 보류** (Cycle408 F):
  - iloc[::4] 다운샘플링 = 실제 4h 캔들 OHLCV와 불일치 (open/high/low/close 기준 다름)
  - BTC 1h RANGING 47.3% → EMA9 크로스 신호 양방향 빈발 → Sh=-0.72, PF=0.91<1.0
  - 파라미터화 가능 요소 없음 (span, threshold 하드코딩)
  - **결론**: 실제 4h 데이터 없이 1h 다운샘플링으로 htf_ema PASS 불가. 추가 탐색 금지.
  - walk_forward.py DEFAULT_GRIDS["htf_ema"]={} 추가 (구조적 한계 주석)

### ⚠️ 주의 사항 (Cycle 405 이후)

- **lob_maker 탐색 완전 보류** (Cycle405 F):
  - OFI proxy = (close-open)/(high-low) — 실제 LOB 불균형 측정 불가
  - VPIN도 OHLCV 추정 → fallback=0.5 불확실
  - BTC 1h Sh=-0.04, Trades=75, MDD=17%, 0/8 Consistency (rank5 점수는 거래 빈도 기여)
  - 파라미터 조정 불가: ofi_buy_threshold 상향 → Trades 감소 → Sh 추가 악화
  - **결론**: LOB 인프라(WebSocket bid/ask) 없이 lob_maker PASS 불가. 추가 탐색 금지.
  - walk_forward.py DEFAULT_GRIDS["lob_maker"] 추가 (구조적 한계 주석)

### ⚠️ 주의 사항 (Cycle 404 이후)

- **engulfing_zone / volatility_cluster Bundle OOS 후보 부적합 확정** (Cycle404 F):
  - engulfing_zone BTC 1h: Sh=-0.79, Trades=657 → 구조적 실패 (noise 거래 과다)
  - engulfing_zone BTC 4h: Sh=-2.74, MDD=44.9% → 더 나쁨 → 추가 탐색 불가
  - volatility_cluster BTC 4h: Sh=0.32, PF=1.06 → PASS 기준(Sh≥1.0, PF≥1.5) 미달
  - **결론**: Bundle OOS 6번째 후보 현재 없음. 기존 5/5 강화 집중.

### ⚠️ 주의 사항 (Cycle 403 이후)

- **positional_scaling 탐색 보류** (Cycle403 F):
  - 구조적 문제: triple EMA alignment(RANGING 47.3%에서 정렬 빈도 낮음), pullback/rally 조건 동일, pullback_atr_mult=0.3 하드코딩
  - Sh=-0.38(음수), PF=1.09(Break-even) → 파라미터화 완료 전 탐색 의미 없음
  - walk_forward.py DEFAULT_GRIDS["positional_scaling"] 추가됨 (빈 dict, 파라미터화 후 탐색 예정)
  - **positional_scaling 파라미터 탐색 완전 보류. strategy.py 수정 없이 실험 금지.**

### ⚠️ 주의 사항 (Cycle 401 이후)

- **frama 탐색 완전 종료** (Cycle401 F):
  - 근본 원인: RANGING(47.3%) → gap<1% 지배 → weak_signal 경로 → RSI 중립(40-60) 구간 차단
  - atr_contracting 재확인 DEAD PARAM (BUY/SELL 조건 미사용, 로그 전용)
  - WFO 그리드 [40,50,60] 유지 (자동 선택 보존), paper_sim weak_rsi_buy_max=50 확정 유지
  - **frama 추가 파라미터 탐색 영구 종료. frama는 보조 신호로 보존.**
- **DrawdownMonitor set_sharpe_decay 복합 조합 완전 커버리지** (Cycle401 B):
  - ATR elevated + Sharpe decay, MDD WARN + Sharpe decay 복합 케이스 모두 검증 완료
  - get_size_multiplier()는 min() 기반 → 가장 낮은 multiplier가 지배

### ⚠️ 주의 사항 (Cycle 399 이후)

- **frama weak_rsi_buy_max=50 확정** (Cycle399 F):
  - paper_sim BTC 1h: Sh=0.44(↑0.24), Trades=65(↑40), PF=1.11, 0/8 Consistency
  - 50 > 40 확정. paper_simulation.py 설정 50 유지. 추가 탐색: 60 실험 대기 중
  - 0/8 Consistency는 frama 구조적 한계 (파라미터로 해결 불가)
  - WFO 그리드 [40,50,60] 유지 — WFO에서 최적값 자동 결정

### ⚠️ 주의 사항 (Cycle 398 이후)

- **frama weak_rsi_buy_max 파라미터화 완료** (Cycle398 F):
  - frama.py: `weak_rsi_buy_max=40` (기본값), `weak_rsi_sell_min=60` 파라미터 추가
  - walk_forward.py: `weak_rsi_buy_max=[40, 50, 60]` WFO 그리드 추가 (9→27 combos)
  - paper_simulation.py: `weak_rsi_buy_max=50` 실험 추가
  - 다음 사이클 paper sim에서 효과 확인 필요

### ⚠️ 주의 사항 (Cycle 397 이후)

- **frama atr_period DEAD PARAM 확정** (Cycle397 F): atr_contracting은 BUY/SELL 조건 미사용
  - frama.py: `atr_contracting` 계산은 되지만 로그 문자열(`atr_str`)에만 사용
  - WFO 그리드 atr_period=[10,14,18] 전부 신호 생성에 무효과
  - atr_period 탐색 완전 종료 / walk_forward.py 그리드 주석화 완료
  - Cycle363 F + Cycle371 D atr_period 실험 "효과 없음" 원인 확인됨
- **frama 다음 방향**: weak signal RSI 임계값 파라미터화 (40→완화)
  - 현재 gap<1%일 때 RSI<40(BUY) 하드코딩 → RANGING 47.3%에서 신호 차단
  - frama.py에 `weak_rsi_buy_max` 파라미터 추가 필요

### ⚠️ 주의 사항 (Cycle 395 이후)

- **price_cluster 최적화 완전 종료** (Cycle395 F): 추가 실험 금지
  - 확정 파라미터: `{"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.2, "atr_bounce_factor": 0.5}`
  - Consistency ceiling=2/8 (구조적 한계). 1h BTC에서 4/8 달성 불가 확인
  - atr_bounce_factor: 0.3(DEAD), 0.5(best:Sh=1.06,SharpeStd=1.67), 1.0(Sh=1.17,Consist↓) 모두 검증
- **atr_bounce_factor 탐색 완전 종료** (Cycle395 F): 추가 실험 금지
- **confirmation_bars 탐색 완전 종료** (Cycle393 F): bars=0 확정 불변, 추가 실험 금지
  - bars=0(Sh=0.95,PF=1.33,Tr=34,2/8) / bars=1(Sh=0.50,혼재) / bars=2(Sh=-0.36,DEAD,0/8)
  - **WFO grid도 [0]으로 축소 완료** (walk_forward.py 갱신됨)

- **close_window 탐색 완전 종료** (Cycle392 D): 50 최적 확정, 추가 탐색 금지
  - 40(Cycle360: 대폭 악화) / 50(최적: Sh=0.95, PF=1.33) / 60(역효과: Sh=0.55↓0.40!)
  - **현재 최적**: `{"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.2}` (close_window 명시 불필요, default=50)
  - 추가 close_window 실험 금지

- **vol_atr_trend_min 탐색 완전 종료** (Cycle391 D): 1.2 최적 확정, 추가 탐색 금지
  - 1.0(dead: Sh=-0.93↓1.88!, Tr=22↓12) / 1.2(최적: Sh=0.95, Tr=34) / 1.5+(Cycle355 이전 검증)

- **bounce_pct 탐색 완전 종료** (Cycle390 C): 0.006 최적 확정, 추가 탐색 금지
  - 0.010(Tr=41,Sh=0.87,PF=1.20) → 0.008(38,1.21,1.27) → 0.006(34,0.95,1.33) → 0.004(27,0.66,1.27) 패턴 확인

- **price_cluster vol_regime_filter=True+bounce_pct=0.006 전체 WFO 결과** (Cycle389 D):
  - Sh=0.95, PF=1.33, Tr=34, Consistency=2/8 → FAIL
  - baseline(filter=F, bp=0.010) 대비 Sh+0.08, PF+0.13 — 방향 유효 확인됨
- **PaperTrader load_state 스키마 검증 테스트 완료** (Cycle389 E):
  - invalid balance/initial_balance, positions mismatch, kelly 복원, schema_version > 1 모두 검증
- **vol_regime_filter=True+bounce_pct=0.006 PASS 발견** (Cycle388 F): 최근 100일 한정
  - Cycle389 D에서 전체 WFO로 확인 — favorable period 효과 확인됨
- **consec_loss_scale_threshold 테스트 완료** (Cycle388 A): BacktestEngine 2단계 스케일링 커버리지
- **KellySizer Bayesian shrinkage 경계값 테스트 완료** (Cycle388 B): MIN_TRADES_FOR_KELLY=15

### ⚠️ 주의 사항 (Cycle 388 이후)

- **bounce_pct 탐색 한계 도달** (Cycle387 C): bounce_pct=0.006이 최고(Sh=0.77) — 단독 PASS 불가
  - PF<1.5(1.17)와 MDD>20%(28.7%) 동시 binding constraint
  - **새 경로**: vol_regime_filter=True + bounce_pct=0.006 조합 (Cycle388 F 발견)
- **roc_ma_cross SL/TP 탐색 종료** (Cycle387 F): 전 조합 FAIL
  - sl=1.2가 최고 Sh(0.28), sl=2.0이 유일 MDD<20%(19.8%) 달성
  - 전체 데이터셋 Sh=-0.17 (baseline) — regime-dependent 전략 한계 확인
  - roc_ma_cross paper_sim PASS(Sh=1.81)는 최근 favorable period 한정
  - roc_ma_cross 파라미터 변경 탐색 종료. 현 파라미터(vol_ratio_min=1.2) 유지
- **connector is_halted 테스트 완료** (Cycle387 E): 30개 테스트
  - is_halted 임계값(5회), create_order 거부, success 시 리셋 완전 커버리지

### ⚠️ 주의 사항 (Cycle 387 이후)

- **DrawdownMonitor set_atr_state/set_sharpe_decay 테스트 완료** (Cycle386 B)
  - 110개 테스트 (94→110, +16개)
  - ATR 변동성 필터 + Sharpe decay 필터 완전 커버리지 완료
- **n_bins 방향 탐색 종료** (Cycle386 D): n_bins=4/5/6 IS 선택 빈도 동일(3/3/2)
  - WFO compact(14일 OOS)에서 OOS trades=4-11 → 구조적 Trades<15 제약
  - n_bins는 trade frequency에 무영향 → n_bins 탐색 종료
  - price_cluster 개선 방향: bounce_pct 하향 한계 → vol_regime_filter 방향으로 전환
- **roc_ma_cross IS-선택 분석 완료** (Cycle386 F): vol_ratio_min=1.2 edge 재확인
  - IS optimizer 선택: volume_filter=False 5/8 vs vol_ratio_min=1.2 3/8
  - vol_ratio_min=1.2 선택 시 IS Sharpe 더 높음(3.11, 1.55) → real edge 확인
  - WFO compact 결과로 확정 파라미터(vol_ratio_min=1.2) 변경 불가

### ⚠️ 주의 사항 (Cycle 384 이후)

- **roc_min_abs 탐색 종료** (Cycle384 F): 0.3 최적 확정
  - 0.4 실험: Consistency 4/8→2/8 (PASS→FAIL!) 치명적 역효과
  - 원인: borderline Trades(avg=14) 일부 윈도우가 0.4 차단으로 Trades<15 전락
  - **roc_min_abs=0.3 확정 불변. 추가 탐색 금지**
- **price_cluster rsi_oversold_filter dead param** (Cycle384 D): 0 trades, PF=0.00
  - RSI<40 조건이 cluster bounce 타이밍과 구조적으로 맞지 않음
  - cluster bounce는 RSI 중립(40-60)에서 발생 — RSI 추가 탐색 방향 종료
  - 파라미터 코드 유지 (가능성은 남겨둠), WFO 그리드에서 제거됨
- **roc_ma_cross grid 대폭 축소** (Cycle384 E): 54→6 combos (88% 감소)
  - roc_period=12, ma_period=3 단일값 확정 (탐색 완료)
  - volume_filter=[False,True], vol_ratio_min=[1.0,1.2,1.5] 유지
- **roc_ma_cross atr_expand_filter dead param 확정** (Cycle385 F): 역효과
  - atr_expand_filter=True: Sh=1.43(↓-0.38), PF=1.84(↓-0.18), Consistency=2/8(4/8→FAIL!)
  - 핵심 교훈: roc_ma_cross는 추가 signal filter 절대 금지 — Trades=14 최소 기준 경계
  - 파라미터 코드는 유지 (atr_expand_filter=False 기본값), paper_sim 복원 완료
- **FAIL 윈도우 분석 완료** (Cycle385 C): vol_ratio at signals mean=0.89-0.97 (PASS: 1.14-1.19)
  - W3/W4 vol>=1.2 통과 신호: 14건 (Trades<15 경계)
  - 신호 품질은 양호(W4 24h fwd ret +2.10%), Trades 부족이 FAIL 원인
  - 남은 방향: SL/TP 실험 (Trades에 무영향, Sharpe/PF 개선 가능) 또는 WFO best params 분석

- **🎉 roc_ma_cross FIRST PASS 확정** (Cycle380 A): vol_ratio_min=1.2 → Sh=1.81, PF=2.02, Trades=14 avg, 4/8
  - **확정 파라미터**: `{"volume_filter": True, "vol_ratio_min": 1.2}` (변경 금지)
  - 65+ 사이클 만에 첫 PASS — volume_filter 개념의 효과 입증
  - **vol_ratio_min 탐색 완전 종료** (Cycle382 B): 1.0/1.1/1.2/1.5 모두 검증
    - 1.1 실험: Sh=1.51, Consist=2/8 → 역효과 (노이즈↑ PF↓)
    - **1.2 최종 최적값 확정. 추가 vol_ratio_min 실험 금지**
  - 주의: AvgTrades=14 (15 기준 경계). 일부 윈도우 trades<15 가능성 존재
- **price_cluster confirmation_bars 결과** (Cycle380 C): 혼재
  - confirmation_bars=1: Sharpe 0.87→0.50(-43%), PF 유지(1.18), Trades 39
  - 타이밍 지연이 손익 감소 유발 → confirmation_bars=0(기본값) 복원
  - 파라미터 코드는 유지 (confirmation_bars=2 향후 실험 가능)
- **min_cluster_strength_ratio dead param 확정** (Cycle379 F): ratio=0.30 → Sh=0.72(-0.15), PF=1.18(동일)
  - 파라미터 코드는 유지, 탐색 종료
- **슬리피지 모델 검증됨** (Cycle379 E): 0.05%/leg 보수적/적정 (실제 BTC 스프레드 0.01-0.03%)
  - adaptive_slippage=True + ATR 레짐 자동 조정. 슬리피지 설정 변경 불필요

- **ema200_filter dead param 확정** (Cycle377 D): ema200_filter=True → Sh=0.56(-34%), PF=1.34, Trades=22
  - dema_cross ema200_filter 탐색 완전 종료. default=False 유지
  - 원인: 2023초 BTC 회복 구간(EMA200 미만) 수익 신호 차단 + 200봉 워밍업 감소
- **dema_cross 탐색 완전 종료** (Cycle377 F): 모든 방향 소진
  - fast=8, slow=20, rsi_dir_filter=True, rsi_dir_threshold=40, bb_width_min_filter=0.04, dist_pct_min=0.002
  - 탐색 완료: ema_slope, macd_hist, bb_width, SL=1.2, TP, slow=25, fast=7, rsi_thr=35, ema200_filter
  - **결론**: PF=1.38 → 목표 1.50 (gap=0.12) 달성 불가. dema_cross 최적화 종료
  - 향후: dema_cross 설정 고정 (변경 금지). 다른 전략 개선으로 전환
- **ema200 피처 추가됨** (Cycle377 D): `src/data/feed.py` `_add_indicators()` + `scripts/paper_simulation.py` `enrich_indicators()`
  - 향후 다른 전략의 EMA200 필터 활용 가능 (인프라 보존)
- **rsi_dir_threshold 탐색 완전 종료** (Cycle376 D): 35(dead), 40(최적), 45(worse) 모두 검증
  - thr=40 확정 불변. 추가 rsi_dir_threshold 실험 금지
- **kelly_sizer.py MIN_TRADES_FOR_KELLY 중복 제거** (Cycle376 B): line 609 제거, line 451 유지
- **bb_width_min_filter=0.04 확정** (Cycle374 D, Cycle375 C 재확인): Sharpe=0.85, Trades=26
  - 0.05 실험: 동일 결과 (dead param) → 0.04 유지 확정. bb_width_min_filter 탐색 완전 종료
- **atr_multiplier_sl=1.2 역효과 확정** (Cycle375 F): PF 1.38→1.34(-0.17 WF context)
  - 전체 데이터셋 긍정적 결과(PF+5%)와 WF 컨텍스트 역효과 불일치 → SL=1.5 유지 확정
  - SL/TP 방향 탐색 종료 (SL: 1.5 확정, TP: 3.5 확정 from earlier cycles)
- **dema_cross thr=40 우위 확정** (Cycle371 B): thr=45 재검증에서도 thr=40(Sh=0.85) > thr=45(Sh=0.55)
  - WFO IS 편향 확정: WFO 3개월 윈도우에서 thr=45 선호 vs 전체 기간 평가 thr=40 우세
  - DEFAULT_GRIDS["dema_cross"] rsi_dir_threshold=[40,45] 유지 (WFO 그리드 탐색 지속)
- **dema_cross dist_pct_min=0.003 역효과 확정** (Cycle370 C): Sh=-0.35, Trades=15 (0.002 대비 절반 감소)
  - dist_pct_min 탐색 완료 — 0.002 유지 확정. dist_pct 방향 탐색 종료
- **roc_ma_cross roc_period 탐색 완료** (Cycle370 F): 10(Sh=-1.45), 12(Sh=0.34 최적), 15(Sh=-0.33)
  - roc_period=12 최적 확정. roc_period 탐색 종료
  - roc_ma_cross 다음 개선 방향: 현재 확정 (ma=3, roc=12, 기본값)
- **roc_ma_cross roc_period=10 역효과 확정** (Cycle369 F): Sh=-1.45 (12: Sh=0.34 대비 대폭 악화)
- **WalkForwardOptimizer 타이밍 로깅** (Cycle369 E): run()에 IS_opt/total 시간 측정 추가됨
- **roc_ma_cross ma=5 역효과 확정** (Cycle368 F): rank15(Sh=-0.91) vs ma=3 rank2(Sh=0.34)
  - ma 스무딩 강화 = 신호 지연 → roc_ma_cross PF 개선 방향은 roc_period 탐색으로 전환
- **PaperConnector tiered_slippage** (Cycle368 E): use_tiered_slippage=False(기본)는 trades 수에 무영향
  - slippage는 P&L에만 영향, 신호 생성과 무관 → paper_sim 결과에 영향 없음 확인
- **optimize_dema_cross() 엣지케이스 테스트** (Cycle368 A): single_window, result_fields 추가
- **dema_cross slow=20 확정** (Cycle367 D): slow=15/20/25 전부 검증, slow=20이 최적
  - fast=8, slow=20, rsi_dir_filter=True, rsi_dir_threshold=40: Sharpe=0.80, PF=1.38, rank1 (Cycle369)
  - PF 1.38 < 목표 1.50 — dist_pct 탐색 또는 추가 파라미터 발굴 필요
- **dema_cross threshold=45 확정** (Cycle366 D): Sharpe 0.55, PF 1.35, Trades 26, rank2
- **optimize_dema_cross() 함수 추가됨** (Cycle365 C): DEFAULT_GRIDS 활성화
  - rsi_dir_threshold=[40,45] 그리드 포함 (Cycle369 업데이트) → WFO 탐색 가능
  - test_optimize_dema_cross_helper 테스트 추가됨 (Cycle366 D)
- **dema_cross dist_pct=0.002 확정** (Cycle 358 F): SharpeStd 2.69→2.32, trades 48→31
  - 목표(SharpeStd<2.5) 달성. 유지.
  - ETH: Sharpe=-2.07 (합성 데이터 특성상 BTC만 평가)
- **price_cluster n_bins=5, close_window=50 확정** (Cycle 359-360):
  - n_bins=6: Sharpe 0.72→-0.84 악화 (Cycle 359 F)
  - close_window=40: Sharpe 0.72→0.07 악화 (Cycle 360 C) — Cycle303과 동일 결론 재확인
  - bounce_pct=0.010, vol_regime_filter=False, n_bins=5, close_window=50(default) 모두 확정
  - price_cluster 탐색 방향: 추가 파라미터 발굴 필요 (현 설정이 1h BTC 최적)
- **dema_cross rsi_dir_filter=True 확정** (Cycle 360 A):
  - PF 1.26→1.45 (↑+0.19, 1.5 목표까지 +0.05), Sharpe 0.37→0.40 (↑+0.03)
  - Trades 31→18 (-13, avg>15 유지 OK; 단 2윈도우 14<15 경계 주의)
  - `scripts/paper_simulation.py` dema_cross params: `{"fast": 8, "slow": 20, "rsi_dir_filter": True}` 확정
- **dema_cross atr_vol_min_pct 코드 추가** (Cycle 359 D): BTC 1h는 dead param (ATR ~1.49%)
- **DrawdownMonitor 직렬화 수정** (Cycle 357 B): 5개 필드 누락 수정 완료
  - `cooldown_active` 주석 보완 완료 (Cycle 358 B)
- **walk_forward DEFAULT_GRIDS["dema_cross"] 추가됨** (Cycle 356 D): [8,10,12] x [15,20,25]
- **walk_forward DEFAULT_GRIDS["dema_cross"] rsi_dir_filter=[False,True] 추가** (Cycle 359 D)
- **walk_forward DEFAULT_GRIDS["price_cluster"] vol_regime_filter=[False,True] 추가** (Cycle 357 F)
- **wick_reversal 1h 제외 확정** (Cycle 353 C): `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 추가됨
- **min_trades_override=8 (4h)**: `engine.min_trades` 1h=15, 4h=8
- **supertrend_multi atr_threshold=0.5**: paper_sim `PAPER_SIM_STRATEGY_PARAMS`에 반영
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지

### 핵심 메트릭 (Cycle 416 업데이트)

| 지표 | Cycle 415 | Cycle 416 | 변화 |
|------|-----------|-----------|------|
| 1h 테스트 전략 수 | 19개 | **19개** | 유지 |
| 1h BTC dema_cross Sharpe | 0.85 | **0.85** | 유지 |
| 1h BTC dema_cross PF | 1.38 | **1.38** | 유지 |
| 1h BTC dema_cross Trades | 26 | **26** | 유지 |
| 1h BTC price_cluster Sharpe | 1.06 | **1.06** | 유지 |
| 1h BTC price_cluster Consistency | 2/8 | **2/8** | 구조적 한계 확정 (Cycle415 F) |
| 1h BTC roc_ma_cross Sharpe | 1.81 | **1.81** | 유지 |
| 1h BTC roc_ma_cross Consistency | 4/8 PASS | **4/8 PASS** | 구조적 최적점 확정 (Cycle416 F) |
| 1h BTC frama Sharpe | 0.44 | **0.44** | 유지 (탐색 종료) |
| 1h BTC narrow_range Sharpe | -0.51 | **-0.51** | 구조적 실패 확정 |
| 1h BTC positional_scaling Sharpe | -0.38 | **-0.38** | 구조적 실패 확정 |
| 1h BTC momentum_quality Sharpe | -1.19 | **-1.19** | 구조적 실패 확정 |
| 1h BTC volume_breakout Sharpe | -0.74 | **-0.74** | 구조적 실패 확정 |
| 1h BTC relative_volume Sharpe | -0.99 | **-0.99** | 구조적 실패 확정 |
| 1h BTC price_action_momentum Sharpe | -1.08 | **-1.08** | 구조적 실패 확정 |
| 1h BTC lob_maker Sharpe | -0.04 | **-0.04** | 유지 (탐색 보류) |
| 1h BTC htf_ema Sharpe | -0.72 | **-0.72** | 구조적 실패 확정 |
| 1h BTC acceleration_band Sharpe | -0.94 | **-0.94** | 구조적 실패 확정 |
| frama WFO combos | 27 | **27** | 유지 |
| price_cluster WFO combos | 18 | **18** | 유지 |
| 1h PASS 수 | 1/19 (roc_ma_cross) | **1/19** | 유지 |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 |
| 테스트 수 (passed) | 8677개 | **8684개 passed** | +7 추가 |
| 테스트 수 (총계) | 8700개 | **8707개 총계** (+7) | +7 추가 |

### Cycle 397 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_drawdown_monitor.py` | transition_cushion_multiplier 경계값 3개 테스트 추가 (Cycle397 B): confidence=0/threshold/1.0 |
| `tests/test_drawdown_monitor.py` | should_liquidate_all 3개 테스트 추가 (Cycle397 B): LIQUIDATE/FULL_HALT=True, BLOCK_ENTRY=False |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["frama"] atr_period 탐색 종료 주석 + dead code 설명 (Cycle397 D+F) |
| `src/backtest/walk_forward.py` | frama WFO 그리드 atr_period 라인 주석화 (27→9 combos, Cycle397 D) |

### Cycle 396 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_drawdown_monitor.py` | HIGH_VOL/RANGING/TREND_DOWN 레짐 kill 테스트 3개 추가 (Cycle396 B) |
| `tests/test_drawdown_monitor.py` | 알 수 없는 레짐 fallback + size_mult 조합 테스트 3개 추가 (Cycle396 B) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"] 파라미터별 DEAD 인라인 주석 + 탐색 종료 문서화 (Cycle396 D) |

### Cycle 395 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_backtest_engine.py` | test_atr_zero_skips_signal_adds_fail_reason 추가 (Cycle395 A): ATR=0 신호스킵+fail_reasons 검증 |
| `tests/test_backtest_engine.py` | test_small_initial_balance_engine_no_crash 추가 (Cycle395 A): initial_balance=$1 크래시없음 |
| `tests/test_feed_boundary.py` | test_bb_width_non_negative_for_normal_prices 추가 (Cycle395 C): bb_width>=0 검증 |
| `tests/test_feed_boundary.py` | test_macd_hist_equals_macd_minus_signal 추가 (Cycle395 C): macd_hist=macd-macd_signal 일관성 |
| `scripts/paper_simulation.py` | atr_bounce_factor=0.3→0.5→확정 실험 + 탐색 종료 주석 (Cycle395 F) |
| `src/backtest/walk_forward.py` | atr_bounce_factor 탐색 완전 종료 주석 추가 (Cycle395 F) |

### Cycle 392 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_circuit_breaker.py` | rapid_decline_oldest_price_exits_window 테스트 추가 (Cycle392 B): window 만료 시 감지 해제 |
| `tests/test_drawdown_monitor.py` | reset_weekly_does_not_clear_warning 테스트 추가 (Cycle392 B): WARNING→reset_weekly→유지 |
| `tests/test_drawdown_monitor.py` | set_regime_high_vol_tightens_daily_limit 테스트 추가 (Cycle392 B): HIGH_VOL→일일 한도 2%→WARNING |
| `scripts/paper_simulation.py` | close_window 50→60 실험→DEAD 확정→50 복원 + 결과 주석 (Cycle392 D) |
| `src/backtest/walk_forward.py` | close_window=60 dead param 주석 + 탐색 완전 종료 (Cycle392 D+F) |

### Cycle 391 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_circuit_breaker.py` | max_daily_trades 3개 테스트 추가 (Cycle391 B): limit 트리거, 0=무제한, reset_daily 초기화 |
| `tests/test_drawdown_monitor.py` | set_ranging_macro_neutral 2개 테스트 추가 (Cycle391 B): neutral_slope=True, directional_slope=False |
| `scripts/paper_simulation.py` | vol_atr_trend_min 1.2→1.0 실험→DEAD 확정→1.2 복원 + 결과 주석 (Cycle391 D) |
| `src/backtest/walk_forward.py` | vol_atr_trend_min=1.0 dead param 주석 + 탐색 완전 종료 + 다음 방향 명시 (Cycle391 D+F) |

### Cycle 390 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_phase_d.py` | optimize_roc_ma_cross 헬퍼 3개 테스트 추가 (Cycle390 A): helper, single_window, result_fields |
| `tests/test_roc_ma_cross.py` | volume_filter 파라미터 2개 테스트 추가 (Cycle390 A): filter=True 저거래량 차단, 고거래량 허용 |
| `scripts/paper_simulation.py` | bounce_pct 0.006→0.004 실험→dead param 확정→0.006 복원 + 결과 주석 (Cycle390 C) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS price_cluster bounce_pct 탐색 종료 주석 추가 (Cycle390 C+F) |

### Cycle 389 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | price_cluster 파라미터 업데이트: `{"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.2}` (Cycle389 D) |
| `tests/test_paper_trader.py` | load_state 스키마 검증 5개 테스트 추가 (Cycle389 E): invalid balance, mismatch union, kelly 복원, schema_v99 |

### Cycle 388 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_backtest_engine.py` | consec_loss_scale_threshold 5개 테스트 추가 (Cycle388 A): threshold=0 미발생, half/full 스케일 트리거, 저장 검증, 음수 클램핑 |
| `tests/test_kelly_sizer_regime_edge_cases.py` | TestKellySizerBayesianShrinkage 4개 테스트 추가 (Cycle388 B): MIN_TRADES=15 경계 shrinkage, empty 반환, 공식 검증 |

### Cycle 385 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_price_cluster.py` | n_bins=4 유효성, bin_width 수학 검증, rsi_oversold dead param 문서화 테스트 추가 (Cycle385 A) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["roc_ma_cross"] FAIL 윈도우 분석 주석 + ATR filter dead param 기록 (Cycle385 C/F) |
| `src/strategy/roc_ma_cross.py` | atr_expand_filter=False, atr_expand_min=0.8 파라미터 추가 + BUY/SELL 조건 atr_ok 포함 (Cycle385 F) |
| `scripts/paper_simulation.py` | atr_expand_filter=True 실험→dead param 확정→복원 + 결과 주석 (Cycle385 F) |

### Cycle 384 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["roc_ma_cross"] roc_period=[10,12,15]→[12], ma_period=[3,5,7]→[3] dead param 정리 (Cycle384 E) |
| `src/backtest/walk_forward.py` | optimize_roc_ma_cross() factory에 roc_min_abs 전달 추가 (Cycle384 F) |
| `src/strategy/roc_ma_cross.py` | _ROC_MIN_ABS 하드코딩→roc_min_abs 파라미터화 (기본값 0.3, Cycle384 F) |
| `src/strategy/price_cluster.py` | rsi_oversold_filter, rsi_buy_max, rsi_sell_min 파라미터 추가 (코드 유지, dead param, Cycle384 D) |
| `scripts/paper_simulation.py` | rsi_oversold_filter=True 실험→dead param→복원 + 결과 주석 (Cycle384 D) |
| `scripts/paper_simulation.py` | roc_min_abs=0.4 실험→dead param→복원 + 결과 주석 (Cycle384 F) |

### Cycle 379 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/roc_ma_cross.py` | `volume_filter=False`, `vol_ratio_min=1.5` 파라미터 추가 + 신호 필터 로직 (Cycle379 D) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["roc_ma_cross"]에 `volume_filter=[False,True]` 추가 + 실험 결과 주석 (Cycle379 D) |
| `src/backtest/walk_forward.py` | `optimize_roc_ma_cross()` factory에 `volume_filter` 전달 추가 (Cycle379 D) |
| `src/strategy/price_cluster.py` | `min_cluster_strength_ratio=0.0` 파라미터 추가 + 필터 로직 (Cycle379 F) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["price_cluster"] dead param 주석 (min_cluster_strength_ratio) (Cycle379 F) |
| `scripts/paper_simulation.py` | 슬리피지 검증 주석 추가 + 두 실험 결과 문서화 후 기본값 복원 (Cycle379 D+E+F) |

### Cycle 377 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/data/feed.py` | `_add_indicators()`에 `ema200` EMA(close,200) 추가 (Cycle377 D) |
| `scripts/paper_simulation.py` | `enrich_indicators()`에 `ema200` 동기화 추가 (Cycle377 D) |
| `src/strategy/dema_cross.py` | `ema200_filter=False` 파라미터 + BUY 차단 로직 추가 (Cycle377 D) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"]에 `ema200_filter=[False,True]` 추가 (Cycle377 D) |
| `scripts/paper_simulation.py` | ema200_filter=True 실험 → dead param → 복원 + 결과 주석 (Cycle377 D) |

### Cycle 376 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/risk/kelly_sizer.py` | `MIN_TRADES_FOR_KELLY: int = 10` 중복 정의 제거 (line 609, Cycle376 B) |
| `scripts/paper_simulation.py` | rsi_dir_threshold=35 실험 → dead param → 40 복원 + 결과 주석 추가 (Cycle376 D) |

### Cycle 375 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_phase_d.py` | `TestDemaCrossBbWidthFilter` 클래스 4개 테스트 추가 (Cycle375 A) |
| `scripts/paper_simulation.py` | bb_width_min_filter=0.05 실험 → dead param → 0.04 복원 (Cycle375 C) |
| `scripts/paper_simulation.py` | atr_multiplier_sl=1.2 실험 → 역효과 → 복원 + 결과 주석 추가 (Cycle375 F) |

### Cycle 374 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/dema_cross.py` | `bb_width_min_filter=0.0` 파라미터 추가 + generate() BB squeeze 차단 로직 (Cycle374 D) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"]에 `bb_width_min_filter=[0.0, 0.04]` 추가 (Cycle374 D) |
| `src/backtest/walk_forward.py` | `optimize_dema_cross()` factory에 `bb_width_min_filter` 전달 (Cycle374 D) |
| `scripts/paper_simulation.py` | dema_cross params에 `bb_width_min_filter=0.04` 추가 — mild positive 확정 (Cycle374 D) |

### Cycle 373 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/data/feed.py` | compute_indicators()에 `macd_hist` = macd-signal, `bb_width` = (bb_upper-bb_lower)/sma20 추가 (Cycle373 C) |
| `scripts/paper_simulation.py` | enrich_indicators()에 `macd_hist`, `bb_width` 동기화 추가 (Cycle373 C, feed.py 누락 버그 수정) |
| `src/strategy/dema_cross.py` | `macd_hist_filter=False` 파라미터 추가 + generate() BUY/SELL 필터 로직 (Cycle373 F) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"]에 `macd_hist_filter=[False,True]` 추가 (Cycle373 F) |
| `src/backtest/walk_forward.py` | `optimize_dema_cross()` factory에 `macd_hist_filter` 전달 (Cycle373 F) |
| `scripts/paper_simulation.py` | macd_hist_filter=True 실험 → dead param 확정 → 복원 (Cycle373 F) |
| `tests/test_drawdown_monitor.py` | transition_cushion 직렬화/역직렬화 테스트 4개 추가 (Cycle373 B) |

### Cycle 372 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/dema_cross.py` | `ema_slope_min_buy=0.0` 파라미터 추가 + BUY 필터 로직 (Cycle372 D) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"]에 `ema_slope_min_buy=[0.0, 0.0003]` 추가 (Cycle372 D) |
| `src/backtest/walk_forward.py` | `optimize_dema_cross()` factory에 `ema_slope_min_buy` 전달 (Cycle372 D) |
| `scripts/paper_simulation.py` | ema_slope_min_buy=0.0003 실험 후 복원 (역효과 확정, Cycle372 F) |

### Cycle 371 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/backtest/walk_forward.py` | `optimize_dema_cross()` factory 기본값: rsi_dir_filter=True, threshold=40 (Cycle371 B) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"] Cycle371 B 결과 주석 (Cycle371 B) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["frama"] Cycle371 D 실험 기록 주석 (Cycle371 D) |
| `scripts/paper_simulation.py` | thr=45 실험→복원 + frama atr=10 실험→제거 (Cycle371 B+D) |

### Cycle 370 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/dema_cross.py` | `dist_pct_min=0.002` 파라미터 추가 (Cycle370 C) |
| `src/backtest/walk_forward.py` | `optimize_dema_cross()` factory에 dist_pct_min 전달 (Cycle370 C) |
| `src/backtest/walk_forward.py` | Cycle370 A/C/F WFO 결과 주석 업데이트 |
| `scripts/paper_simulation.py` | dist_pct_min=0.003 실험→복원 + roc_period=15 실험→복원 (Cycle370 C+F) |

### Cycle 369 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | dema_cross rsi_dir_threshold=40 확정 + roc_ma_cross roc_period=10 실험→복원 (Cycle369 D+F) |
| `src/backtest/walk_forward.py` | `import time as _time` + run()에 윈도우별 타이밍 로깅 추가 (Cycle369 E) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"] rsi_dir_threshold [45,50]→[40,45] (Cycle369 D) |

### Cycle 368 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_exchange.py` | PaperConnector tiered_slippage 6개 테스트 추가 (Cycle368 E) |
| `tests/test_phase_d.py` | optimize_dema_cross 엣지케이스 2개 테스트 추가 (Cycle368 A) |
| `scripts/paper_simulation.py` | roc_ma_cross ma_period=5 실험 후 복원 + 결과 주석 (Cycle368 F) |

### Cycle 367 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_kelly_integration.py` | BTC 1h 시나리오 4개 테스트 추가 (Cycle367 B) |
| `scripts/paper_simulation.py` | dema_cross slow=25 실험 후 slow=20 복원 + 결과 주석 (Cycle367 D) |

### Cycle 366 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_drawdown_monitor.py` | 일중 DD 회복 → WARNING 자동 해제 테스트 추가 (Cycle366 B) |
| `tests/test_drawdown_monitor.py` | 주간 DD HALT 유지/reset_weekly() 해제 테스트 추가 (Cycle366 B) |
| `tests/test_phase_d.py` | `test_optimize_dema_cross_helper` 테스트 추가 (Cycle366 D) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"] 주석 업데이트: Cycle366 threshold=45 결과 반영 (Cycle366 D) |

### Cycle 365 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/dema_cross.py` | `rsi_dir_threshold=50` 파라미터 추가 — BUY/SELL RSI 임계값 가변화 (Cycle365 A) |
| `src/backtest/walk_forward.py` | `optimize_dema_cross()` 함수 추가 — DEFAULT_GRIDS["dema_cross"] 활성화 (Cycle365 C) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"]에 `rsi_dir_threshold=[45,50]` 추가 (Cycle365 A/C) |
| `scripts/paper_simulation.py` | dema_cross `rsi_dir_threshold=45` 실험 설정 (Cycle366 D 검증 완료) |

### Cycle 363 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | dema_cross fast=8→7 (신호빈도 +37%, trades<15 해결 실험) (Cycle363 C) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"] fast=[8,10,12]→[7,8,10,12] (Cycle363 C) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["frama"] atr_period=[10,14,18] 추가 (Cycle363 F) |
| `src/risk/circuit_breaker.py` | 독스트링+파라미터 주석: BTC 1h 실증 데이터 반영 (window=5 pct=5% 77h당1회) (Cycle363 B) |

### Cycle 362 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/risk/kelly_sizer.py` | `__init__`에 kelly_cap > max_fraction 시 debug 로그 추가 (dead param 명시) (Cycle362 B) |
| `src/ml/trainer.py` | `select_features_pfi()`: X_train < 100행 시 n_repeats=10 자동 증가 (Cycle362 D) |

### Cycle 361 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/roc_ma_cross.py` | EMA200 조건 `"ema50" in df.columns` 제거 (중복 체크), `rsi_val` dead code 제거, bare except → Exception (Cycle361 F) |
| `src/backtest/walk_forward.py` | roc_ma_cross 주석 업데이트: rank1 상태 반영, Cycle361 F 수정 기록 (Cycle361 F) |

### Cycle 360 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | dema_cross `rsi_dir_filter=True` 추가 확정 (PF 1.26→1.45, Sharpe 0.37→0.40) (Cycle360 A) |
| `scripts/paper_simulation.py` | close_window=40 실험 → Sharpe 0.72→0.07 악화 → 기본값(50) 복원 (Cycle360 C) |
| `src/backtest/walk_forward.py` | close_window=40 Cycle360 재확인 악화 주석 추가 (Cycle360 C) |

### Cycle 359 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/dema_cross.py` | `atr_vol_min_pct=0.0` 파라미터 추가 (BTC에서 dead param 확인) (Cycle359 D) |
| `src/strategy/dema_cross.py` | `rsi_dir_filter=False` 파라미터 추가 (BUY시RSI>50/SELL시RSI<50) (Cycle359 D) |
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["dema_cross"]`에 `rsi_dir_filter=[False,True]` 추가 (Cycle359 D) |
| `src/exchange/paper_connector.py` | `use_tiered_slippage=False` 파라미터 노출 → PaperTrader 전달 (Cycle359 E) |
| `scripts/paper_simulation.py` | n_bins=6 실험 → Sharpe 0.72→-0.84 악화 확인 → default(n_bins=5) 복원 (Cycle359 F) |
| `scripts/paper_simulation.py` | atr_vol_min_pct=0.005 실험 → 효과없음 확인 → 제거 (Cycle359 D) |

### Cycle 358 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/dema_cross.py` | 거리 필터 0.001→0.002 (SharpeStd 2.69→2.32 개선, trades 48→31) (Cycle358 F) |
| `src/risk/drawdown_monitor.py` | `cooldown_active` 필드 주석: single loss cooldown만 반영 명확화 (Cycle358 B) |
| `scripts/paper_simulation.py` | bounce_pct=0.020 실험 후 악화 확인 → 기본값(0.010) 복원 (Cycle358 C) |
| `src/backtest/walk_forward.py` | price_cluster bounce_pct=0.020 paper_sim 악화 기록 주석 추가 (Cycle358 C) |

### Cycle 357 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/risk/drawdown_monitor.py` | `to_dict()` 5개 ATR/Sharpe/regime 필드 + transition_cushion 2개 추가 (Cycle357 B) |
| `src/risk/drawdown_monitor.py` | `from_dict()` 동일 필드 복원 + transition_cushion_enabled/threshold 인자 추가 (Cycle357 B) |
| `src/strategy/dema_cross.py` | BUY 차단 RSI 임계값 70→65 (Cycle357 D, 효과없음 확인) |
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["price_cluster"]` vol_regime_filter=True,1.2→False (Cycle357 F) |
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["price_cluster"]` vol_regime_filter=[False,True] 추가 (Cycle357 F) |

### Cycle 356 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["dema_cross"]` fast=8, slow=20 추가 (Cycle356 D) |
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["price_cluster"]` vol_atr_trend_min 1.2→1.0→1.2 복원 (Cycle356 F) |
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["dema_cross"]` 추가: fast=[8,10,12], slow=[15,20,25] (Cycle356 D) |
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["price_cluster"]` vol_atr_trend_min에 1.0 추가 (Cycle356 F) |

### Cycle 355 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["price_cluster"]` vol_atr_trend_min 1.5→1.2 (Cycle355 A) |
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["price_cluster"]` vol_atr_trend_min에 1.2 추가 (Cycle355 A) |
| `src/strategy/dema_cross.py` | 거리 필터 0.5%(0.005)→0.1%(0.001) 완화 (Cycle355 F) |

### Cycle 354 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["price_cluster"]`에 `"vol_regime_filter": [True]` 추가 (dead parameter 버그 수정) |
| `src/strategy/dema_cross.py` | `convergence_signal=False`, `convergence_threshold=0.02` 파라미터 추가 (기본값 False, 실험용) |
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["price_cluster"]` 추가 (vol_regime_filter=True, 1.5) |

### F(리서치) BTC 1h 레짐별 특성 (Cycle 346 확정)

| 레짐 | 캔들 비율 | avg return/봉 | ema50 slope mean | 중립(<0.0005) 비율 |
|------|---------|------------|----------------|----------------|
| TREND_UP | 31.3% | +0.0250% | +0.001391 | 14.4% |
| TREND_DOWN | 21.4% | +0.0377% | -0.001266 | 18.9% |
| RANGING | 47.3% | +0.0217% | +0.000110 | 45.1% |

**핵심 결론**: RANGING에서만 neutral macro 비율 45.1% 확보 → mean-reversion 조건 충족

### 4h 슬리피지 임계값 (Cycle 351 확인)

| 타임프레임 | LOW 임계값 | NORMAL 임계값 | HIGH 임계값 | BTC 분류 | SOL 분류 |
|-----------|-----------|--------------|-----------|---------|---------|
| 1h | < 0.5% | 0.5~3.0% | >= 3.0% | NORMAL | HIGH(32%) |
| 4h | < 1.0% | 1.0~6.0% | >= 6.0% | NORMAL (3.0%) | NORMAL avg, HIGH 24%캔들 |
| 1d | < 2.5% | 2.5~14.7% | >= 14.7% | — | — |

### min_trades 기준 (Cycle 351 확정)

| 타임프레임 | min_trades | 근거 |
|-----------|-----------|------|
| 1h | 15 | 60일 window, 30일 train, 충분한 신호 |
| 4h | 8 | 60일 window, max_hold=24봉(4일), 이론 최대 15, 실제 8-10; n=8 Sharpe=1.0 → p=0.013 |

### ETH/SOL 합성 데이터 슬리피지 레짐 (Cycle 351 확인)

| 데이터 | HL ratio mean | ATR14/close | HIGH regime |
|--------|-------------|-------------|-------------|
| BTC real 1h | 1.50% | 1.49% | 0.7% (>=3%) |
| ETH synthetic 1h | 2.12% | 2.12% | 21.0% (>=3%) |
| SOL synthetic 1h | 3.17% | ~3.2% | 39.0% (>=3%) |
| SOL synthetic 4h | 5.42% | 5.45% | 24.0% (>=6%) |

### EMA slope 차단 비율 분석 (Cycle 346 D(ML) 확정)

| ema_slope_min_buy 임계값 | 전체 BUY pass | RANGING BUY pass | 판단 |
|------------------------|-------------|----------------|------|
| 0.0 (필터 없음) | 54.7% | 50.8% | 기본값 |
| 0.0005 | 44.3% | 38.2% | ✅ 중간 균형점 |
| 0.001 | 34.5% | 27.1% | ⚠️ RANGING 과도 차단 |

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 340 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 최적 확정 (delta_window=10 기본값)

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 330 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 389 업데이트)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← 1h paper_sim에서 제외됨
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원
- `cmf: {"buy_thresh": 0.10}`
- `supertrend_multi: {"atr_threshold": 0.5}` ← Cycle 352 B 추가
- `price_cluster: {"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.2}` ← Cycle 389 D 실험 (전체 WFO: Sh=0.95, PF=1.33, Tr=34, 2/8 FAIL)
- `dema_cross: {"fast": 8, "slow": 20, "rsi_dir_filter": True, "rsi_dir_threshold": 40, "bb_width_min_filter": 0.04}` ← **Cycle 377 확정** (ema200_filter dead param 확정, 탐색 종료)

### PAPER_SIM_REGIME_FILTER 현재 설정 (Cycle 339 롤백 유지)
- `set()` ← 빈 집합 (레짐 필터 비활성화)

### STRATEGIES_TIMEFRAME_EXCLUDE 현재 설정 (Cycle 353 업데이트)
- `"1h": {"value_area", "supertrend_multi", "wick_reversal"}`
  - value_area: 1h 구조적 실패 (Cycle 325), 4h Bundle PASS
  - supertrend_multi: 1h 구조적 실패 (Cycle 325), 4h Bundle PASS
  - wick_reversal: ETH/SOL 0 trades x8, BTC Sharpe=-2.64 (Cycle 353 C)

### 핵심 메트릭 (Cycle 338: MAX_HOLD 분리 아키텍처, 유지)

| 구분 | max_hold_candles | 설정 위치 |
|------|-----------------|---------|
| 1h paper_sim | 48봉 (48시간) | `paper_simulation.py`: `max_hold_candles_override=48` |
| 4h paper_sim | 24봉 (96시간=4일) | `paper_simulation.py`: `ACTIVE_TIMEFRAME=="4h"` 자동 |
| 4h Bundle OOS | 24봉 (96시간=4일) | `BacktestEngine` 기본값 `MAX_HOLD_CANDLES=24` |

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH: synthetic CSV (data/historical/synthetic/ETHUSDT/1h.csv) — NaN 없음, HL ratio 2.12% (Cycle 348 재생성)
- SOL: synthetic CSV (data/historical/synthetic/SOLUSDT/1h.csv) — NaN 없음, HL ratio 3.17% (Cycle 350 재생성)
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
  - SSL 차단으로 실거래소 데이터 수집 불가 → 새 Bundle OOS 실행 시 synthetic fallback → 리포트 덮어쓰기 방지
- Paper simulation 4h: 22 전략 × 3 심볼 × 8 windows → 약 5분 소요
