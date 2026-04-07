# Next Steps

_Last updated: 2026-04-07_

## Status: 코어 구현 완료, 테스트 15/15 통과

## 완료된 작업
- [x] 프로젝트 구조 + Claude Code 에이전트 팀 (9 agents)
- [x] ExchangeConnector (ccxt, sandbox, wait_for_fill)
- [x] DataFeed (OHLCV, EMA/ATR/RSI/Donchian/VWAP)
- [x] RiskManager + CircuitBreaker (포지션 사이징, 서킷 브레이커)
- [x] EmaCrossStrategy + DonchianBreakoutStrategy
- [x] BacktestEngine (Sharpe/MDD/PF/WinRate)
- [x] TradingPipeline (data→alpha→risk→execution, dry_run)
- [x] 테스트 15개 통과

## 완료된 추가 작업
- [x] config 로더 (config.yaml → AppConfig dataclass)
- [x] main.py — `--backtest` / `--live` / `--config` CLI
- [x] 로깅 설정 (파일 + 콘솔, ccxt 노이즈 억제)
- [x] 테스트 18/18 통과

## 다음 작업 (선택)
- [ ] Telegram 알림 (파이프라인 결과 푸시)
- [ ] 스케줄러 (cron or asyncio loop로 주기적 실행)
- [ ] 실거래소 샌드박스 통합 테스트
- [ ] 전략 추가 (RSI 역추세, 볼린저밴드 등)

## 결정된 사항
- 거래소: ccxt 추상화 (환경변수로 교체 가능)
- 전략: EmaCross + DonchianBreakout (백테스트 후 선택)
- 리스크: 계좌 1%/트레이드, ATR 1.5x SL, ATR 3.0x TP
