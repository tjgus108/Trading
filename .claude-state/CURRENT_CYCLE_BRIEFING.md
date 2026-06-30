# Current Cycle Briefing

_Last updated: 2026-06-30 (Cycle 371 완료)_

## 현재 상태

- **완료된 사이클**: 371
- **다음 사이클**: 372 (372 mod 5 = 2 → B+D+F)
- **연속 PASS 실패**: 56연속 (0/19 1h paper_sim)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 371 주요 결과

### B(리스크): dema_cross thr=45 재실험 → thr=40 우위 확정
- thr=45 실험: Sh=0.55, PF=1.35, Trades=26, rank2
- thr=40 비교: Sh=0.80, PF=1.38, Trades=30, rank1
- WFO thr=45 선호 원인: IS 3개월 윈도우 편향 (짧은 평가 기간에서 보수적 필터가 유리)
- **결론**: thr=40 우위 확정. WFO IS 편향 메커니즘 이해 완료

### D(ML): frama atr_period=10 실험 → 중립 확정
- atr_period=10: Sh=0.24, PF=1.12, Trades=40 (기본값 atr_period=14와 동일)
- **결론**: BTC 1h에서 ATR 기간 10-14 범위는 성능에 무영향. 기본값(14) 유지, 실험 제거

### F(리서치): dema_cross EMA slope 필터 방향 식별
- feed.py에 `df["ema20_slope"]` 이미 계산됨 (line 1054-1057) — 구현 준비 완료
- 다음 방향: `ema_slope_min_buy=0.0003` 필터 (BUY 시 양의 slope 요구)
- 현재 PF=1.38 → 목표 PF=1.50 (+0.12 필요)

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `src/backtest/walk_forward.py` | optimize_dema_cross() factory 기본값 + 주석 업데이트 |
| `scripts/paper_simulation.py` | frama atr=10 실험 제거 + thr=45/thr=40 결과 주석 |

## Cycle 372 예고

- **D(ML)**: dema_cross `ema_slope_min_buy` 파라미터 추가 + 실험 (0.0003 임계값)
- **B(리스크)**: risk 모듈 현황 점검 (DrawdownMonitor, CircuitBreaker, KellySizer)
- **F(리서치)**: EMA slope 필터 효과 분석 및 dema_cross PF 1.50 목표 경로 확인
