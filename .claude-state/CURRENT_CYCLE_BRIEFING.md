# Current Cycle Briefing

_Last updated: 2026-06-23 (Cycle 348 완료)_

## 현재 상태 요약

- **현재 사이클**: 348 완료 (C(데이터) + B(리스크) + F(리서치))
- **1h Paper Sim**: 0/20 PASS — 28연속 FAIL streak
- **4h Bundle OOS**: 5/5 PASS 안정 유지 (OFI Sharpe=4.345)
- **테스트**: 8434 passed, 23 skipped

## 이번 사이클 핵심 변경

| 변경 | 파일 | 내용 |
|------|------|------|
| C(데이터) | `scripts/generate_garch_csv.py` | sigma cap 10x→4x, vol_spike 2.5x→1.5x, wick cap base_vol*3 |
| C(데이터) | `data/historical/synthetic/ETHUSDT/1h.csv` | 재생성: HL ratio 4.30%→2.12%, HIGH regime 39.3%→21.0% |
| C(데이터) | `data/historical/synthetic/SOLUSDT/1h.csv` | 재생성 (SOL 특성상 HIGH regime 잔존) |

## 핵심 인사이트

1. **ETH 합성 데이터 HL 과장 수정**:
   - GARCH vol_spike (sigma2 *= 2.5 × 8-15봉 + 10x cap) → HL ratio 4.3% (BTC 1.5% 대비 2.88x 과장)
   - 수정 후: HL ratio 2.12% (1.4x BTC), HIGH regime 21%→ 실제 ETH 변동성에 근접
   - dema_cross High%: 94.9%→80.8% (아직 높은 이유: EMA crossover 특성상 큰 이동 후 신호 = 고변동 구간)

2. **paper_sim ↔ DrawdownMonitor 분리 확인**:
   - paper_sim은 BacktestEngine 직접 사용 (설계상 의도적 분리)
   - Cycle 347의 manager.py RANGING 연동은 live trading 전용
   - BacktestEngine 내 consec_loss_scale (threshold=5) = 백테스팅용 리스크 대체

3. **4h paper_sim 타당성 확인**:
   - `--timeframe 4h` 지원 ✓ (1h CSV resample → 3000 4h 캔들, 8 WFO 윈도우)
   - 다음 사이클(349): 4h paper_sim 실행 → 수수료 드래그 1/4 효과 검증

4. **28연속 0/20 FAIL 지속**:
   - 근본: PF < 1.5. 1h 수수료 0.11% round-trip = 연 7.9% 드래그
   - price_cluster PF=1.20 (best, 갭 0.30), roc_ma_cross PF=1.22
   - 해결 경로: 4h paper_sim (Cycle 349)

## 다음 사이클 (349, mod 5 = 4 → D(ML) + E(실행) + F(리서치))

- D(ML): 4h paper_sim 소규모 테스트 실행 (`--timeframe 4h --csv-dir data/historical`)
- E(실행): 4h max_hold=48봉(8일) vs 24봉(4일) 비교 검토
- F(리서치): ETH dema_cross High% 80.8% 잔여 원인 (EMA crossover 특성) 분석
