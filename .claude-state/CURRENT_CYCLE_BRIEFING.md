# Current Cycle Briefing

_Cycle 324 | 2026-06-17 | D(ML) + E(실행) + F(리서치)_

## 완료된 작업

### D(ML): supertrend_multi 1h cmf_confirm 실험 → 역효과 롤백
- `scripts/paper_simulation.py` cmf_confirm=True 실험: Sharpe 0.32→0.02 악화
- 롤백 완료. 1h에서 CMF 필터 부적합 재확인.

### E(실행): live_paper_trader 4h 타임프레임 지원
- `scripts/live_paper_trader.py` `--timeframe {1m,5m,15m,1h,4h,1d}` CLI 옵션 추가
- LivePaperTrader(timeframe=) 파라미터 추가, 3개소 fetch_latest_candles 전파
- interval 자동 설정: 4h → 14400s, 1h → 3600s

### F(리서치): 레짐 기반 전략 스위칭 분석
- Bundle 5개 4h PASS 전략 레짐 적합성 매핑 완료

## 시뮬레이션 결과 (Cycle 324)
- Paper Sim 1h: **0/22 PASS** (유지)
- Bundle OOS 4h: **5/5 PASS** (유지)

## 다음 사이클 (325): A(품질) + C(데이터) + F(리서치)
- supertrend_multi 1h: atr_threshold=0.3 또는 레짐 기반 BUY 필터 실험
- live_paper_trader 4h CSV 데이터 경로 확인
- 1h vs 4h 타임프레임 적합성 리서치
