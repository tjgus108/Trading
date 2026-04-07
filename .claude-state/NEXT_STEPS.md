# Next Steps

_Last updated: 2026-04-07_

## Status: 전체 5개 Phase 완료 — 테스트 114/114 통과

## 완료된 작업 (전체)

### 인프라
- [x] 프로젝트 구조 + Claude Code 에이전트 팀 (9 agents, 3 skills)
- [x] ExchangeConnector (ccxt, sandbox, wait_for_fill)
- [x] DataFeed (OHLCV, EMA/ATR/RSI/Donchian/VWAP, 이상감지)
- [x] RiskManager + CircuitBreaker
- [x] EmaCrossStrategy + DonchianBreakoutStrategy
- [x] BacktestEngine (Sharpe/MDD/PF/WinRate)
- [x] TradingPipeline (data→alpha→risk→execution, dry_run)
- [x] Config 로더, 로깅, Telegram 알림, CandleScheduler
- [x] 통합 테스트 (샌드박스, @pytest.mark.integration)

### Phase 1 — Orchestrator
- [x] BotOrchestrator: startup/run_once/run_loop
- [x] Backtest gate (live 전 PASS 필수)
- [x] main.py 경량화 (40줄)

### Phase 2 — Strategy Tournament
- [x] run_tournament(): 병렬 백테스트 → Sharpe 기준 자동 선택
- [x] --tournament 플래그

### Phase 3 — Position & P&L 추적
- [x] PositionTracker: open/close, CircuitBreaker 연동
- [x] DailyPnL: 일일 자동 리셋, 일일 리포트 → Telegram
- [x] .claude-state/POSITIONS.md 실시간 업데이트

### Phase 4 — 멀티 심볼
- [x] MultiBot: 심볼별 독립 스레드, SymbolConfig 오버라이드
- [x] 포트폴리오 노출 합산 및 한도 관리
- [x] --symbols 플래그

### Phase 5 — 대시보드
- [x] Dashboard: 표준 라이브러리 HTTP 서버 (Flask 불필요)
- [x] GET / (HTML), /status (JSON), /health
- [x] OrchestratorStatusProvider, MultiStatusProvider
- [x] --dashboard, --dashboard-port 플래그

## 다음 작업 (선택사항)
- [ ] 새 전략 추가 (RSI 역추세, 볼린저밴드)
- [ ] 전략 자동 재평가 주기 설정 (tournament_interval_hours)
- [ ] 실거래소 샌드박스 통합 테스트 실행
- [ ] 포지션 청산 조건 고도화 (trailing stop)

## 사용법
```bash
# 백테스트
python main.py --backtest

# 토너먼트 후 루프
python main.py --tournament --loop

# 멀티 심볼 + 대시보드
python main.py --symbols BTC/USDT ETH/USDT --dashboard --loop

# 실거래 (backtest gate 자동 실행)
python main.py --live --loop
```
