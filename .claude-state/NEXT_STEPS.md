# Next Steps — Paper Simulation 필수 실행

## 🚨 다음 세션 최우선 작업

**집 노트북(Bybit API 접근 가능) 에서 실제 데이터로 Paper Simulation 실행:**

```bash
cd ~/Trading
git pull origin main
python3 scripts/paper_simulation.py
```

### 목적
- 웹 세션에서는 Bybit API 접근 불가 → 합성 데이터로만 테스트됨
- 집 노트북에서는 실제 BTC/USDT 1h 1000캔들(최근 41일) 가져와서 PASS 22개 전략 실전 수익률 측정
- 결과를 `.claude-state/PAPER_SIMULATION_REPORT.md`에 기록 후 커밋+푸시

### 스크립트가 하는 일 (scripts/paper_simulation.py)
1. Bybit에서 BTC/USDT 1h 1000개 캔들 fetch
2. 지표 자동 계산 (ATR, EMA, RSI, BB, MACD, Donchian, VWAP)
3. QUALITY_AUDIT.csv의 PASS 22개 전략 로드
4. BacktestEngine으로 각 전략 백테스트 (fee 0.1%, slippage 0.05%)
5. 수익률/Sharpe/MDD/Trades 기록
6. Top 10 표 + 균등배분 포트폴리오 수익률 계산
7. 리포트 저장

### 주의사항
- **dry_run 유지** (config.yaml의 dry_run: true) — 실제 주문 금지
- **public API만** 사용 (API key 불필요, fetch_ohlcv만 호출)
- 결과가 실제 운영과 100% 일치하지는 않음 (슬리피지 근사)

---

## 이전 작업 (Cycle 33 완료)
- 품질 감사: PASS 22개 (Sharpe avg 4.79, MDD avg 3.62%, PF avg 1.95) — Cycle 13 대비 품질 동일
- 32 사이클 완료, 6 CRITICAL 버그 수정, 5998 tests passing
- 로테이션 자동화 인프라 (MASTER_PLAN.md, cycle_dispatcher.py)

## Paper Simulation 이후 작업 (Cycle 34+)
1. **실제 데이터 수익률 확인** → 전략 최종 선별
2. **Walk-Forward Validation** — 상위 전략에 IS/OOS 70/30 검증
3. **포트폴리오 최적화** — 상관관계 분석으로 다양성 확보
4. **Telegram 알림 활성화** (config.yaml)
5. **실거래 배포 전 1주 paper 추가 모니터링**

---
_Generated: 2026-04-11_
