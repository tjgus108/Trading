# Research Log

## [2026-04-11] Cycle 1 Research

### 신규 실패 사례

- **October 2025 암호화폐 청산 연쇄 붕괴** / 2025-10-10 / 원인: 50~100x 레버리지 봇들의 자동청산이 연쇄 반응 유발, 60초 안에 $3.21B 증발, 14시간 총 $19B 청산. 스프레드 1,321x 폭등, 호가창 깊이 98% 소실. 봇들이 비정상 변동성 시 멈추지 않고 계속 매도 집행 / 교훈: 일일 3% 드로다운 서킷브레이커 필수, 레버리지 포지션 규모 엄격 제한 / 출처: https://blog.amberdata.io/how-3.21b-vanished-in-60-seconds-october-2025-crypto-crash-explained-through-7-charts

- **May 2025 AI 봇 플래시 크래시 가속** / 2025-05 / 원인: 정상 시장 조건용으로 설계된 AI 봇들이 갑작스러운 변동성에 적응 못하고 2분 안에 $2B 자산 매도. 레짐 감지 로직 부재 / 교훈: 변동성 레짐 필터(VIX/ATR 기반) 없이 단일 전략 운영 금지 / 출처: https://www.crypto-reporter.com/press-releases/most-crypto-trading-bots-promised-easy-money-the-market-killed-them-here-is-what-the-survivors-built-instead-123004/

- **OKX 토큰 50% 플래시 크래시** / 2024-01-23 / 원인: 청산 연쇄로 단시간 50% 폭락, 얕은 유동성에서 대형 봇 매도가 slippage 폭발적 확대 유발 / 교훈: 저유동성 자산에서의 포지션 크기는 시장 깊이(depth) 대비 최대 0.1% 이하로 제한 / 출처: https://www.coindesk.com/business/2024/01/23/crypto-exchange-okxs-token-suffers-50-flash-crash-amid-liquidation-cascade

- **2024~2025 암호화폐 봇 73% 6개월 내 실패** / 2024~2025 / 원인: CoinGecko 연구에 따르면 13.4M 프로젝트 중 53.2% 소멸. 자동화 거래 계좌의 73%가 6개월 내 실패, 52%는 3개월 내 실패. 주요 원인: 리스크 관리 부재, 과최적화, 레짐 변화 무대응 / 교훈: 출시 전 최소 3개 시장 레짐(상승/하락/횡보)에서 walk-forward 검증 필수 / 출처: https://awards.finance-monthly.com/do-trading-bots-fail/

---

### 신규 성공 사례

- **AutoPilot Trader V3 (2024~2025)** / 조건: 1,045개 백테스트 트레이드, 다중 거래소(Binance, Bybit, 3개 DEX) 24/7 운영 / 성과: Sharpe 3.58, 연환산 42% 수익, MDD 9% / 교훈: 다중 거래소 분산 + 낮은 레버리지 + 엄격한 포지션 사이징(1% 룰)의 조합이 핵심 / 출처: https://redhub.ai/ai-trading-bots-2025/

- **SuperTrend AI 봇 (2024-01~2025-01)** / 조건: AI 기반 SuperTrend 전략, 111개 트레이드 / 성과: 순이익 95.94%, Sharpe 0.558(양의 위험조정 수익). 주의: Sharpe가 낮아 리스크 대비 수익 효율은 중간 / 교훈: 높은 절대 수익이라도 Sharpe < 1.0이면 변동성 대비 수익이 불안정함을 의미, 백테스트 지표 종합 판단 필요 / 출처: https://www.researchgate.net/publication/388448293_Algorithmic_Trading_Bot_Using_Artificial_Intelligence_Supertrend_Strategy

- **ML 기반 다중 레짐 전략 (2024~2025 기관급)** / 조건: 머신러닝 모델, 상승/하락/횡보 3개 레짐 대응 / 성과: Sharpe 2.5 이상 유지, 업계 평균(1.0~2.0)을 크게 상회 / 교훈: 레짐 전환 감지 + 전략 스위칭이 일관된 성과의 핵심 / 출처: https://redhub.ai/ai-trading-bots-2025/

---

### 최신 리스크 관리 기법 (2024~2025)

- **다층 서킷브레이커**: 일일 드로다운 3% + 주간 7% 초과 시 자동 거래 중단
- **변동성 기반 포지션 사이징**: ATR/VIX 기반으로 포지션 크기를 동적 조정, 고변동성 시 축소
- **Kelly Criterion 적용**: 포트폴리오 노출 6% 이하, 단일 트레이드 1% 이하
- **ADL(Auto-Deleveraging) 회피**: 거래소의 강제 청산 메커니즘 분석 후 청산가격 완충 설정
- **레짐 감지 필터**: 추세/횡보/고변동성 레짐 구분 후 전략 전환 또는 일시 중단

---

### 우리 봇에 적용 가능한 개선점 3개

1. **다층 서킷브레이커 구현**: `src/risk/` 에 일일 드로다운 3%, 주간 7% 초과 시 자동 중단 로직 추가. October 2025 사태처럼 봇이 폭락 중 계속 매도하는 사태 방지.

2. **변동성 레짐 필터**: ATR(14) 기준 고변동성 감지 시 포지션 크기를 50% 자동 축소하거나 BUY 신호를 억제하는 레짐 레이어를 `src/strategy/base.py` 또는 `src/risk/` 에 추가. May 2025 AI 봇 플래시 크래시 가속 방지.

3. **슬리피지/유동성 검증 강화**: 백테스트 엔진에 호가창 깊이(market depth) 기반 슬리피지 시뮬레이션 추가. OKX 사례처럼 저유동성에서의 대형 포지션은 실제 체결가가 백테스트와 크게 달라짐.

---

### 참고 자료

- https://blog.amberdata.io/how-3.21b-vanished-in-60-seconds-october-2025-crypto-crash-explained-through-7-charts
- https://www.ainvest.com/news/october-2025-crypto-crash-19b-leverage-liquidation-event-2602/
- https://aurpay.net/aurspace/crypto-crash-october-2025-bitcoin-liquidation-explained/
- https://www.soliduslabs.com/post/when-whales-whisper-inside-the-20-billion-crypto-meltdown
- https://www.crypto-reporter.com/press-releases/most-crypto-trading-bots-promised-easy-money-the-market-killed-them-here-is-what-the-survivors-built-instead-123004/
- https://www.coindesk.com/business/2024/01/23/crypto-exchange-okxs-token-suffers-50-flash-crash-amid-liquidation-cascade
- https://awards.finance-monthly.com/do-trading-bots-fail/
- https://redhub.ai/ai-trading-bots-2025/
- https://www.researchgate.net/publication/388448293_Algorithmic_Trading_Bot_Using_Artificial_Intelligence_Supertrend_Strategy
- https://3commas.io/blog/ai-trading-bot-risk-management-guide-2025
- https://www.luxalgo.com/blog/risk-management-strategies-for-algo-trading/
