# AI 트레이딩봇 리서치 리포트 v2

_작성일: 2026-04-10 | 출처: 웹 검색 (ChatGPT/Copilot/Cursor/Claude 봇 사례 포함)_

---

## 1. 실패 사례 Top 5

### Case 1: Quantopian 셧다운 (2020)
- 규모: 사용자 300,000명, Steven Cohen $250M 투자
- 원인: 크라우드소싱 전략 대부분 과최적화(curve-fitting). 전략이 "왜 작동하는지" 이해 없는 데이터 마이닝
- **교훈: 전략에는 논리적 근거 필요. 데이터 마이닝과 가설 검증은 다름**

### Case 2: Knight Capital Group ($440M 손실, 2012)
- 45분 만에 $440M 손실. 구버전 코드가 프로덕션에 배포됨, 킬스위치 없음
- **교훈: 배포 전 검증 필수. 즉각 킬스위치/서킷 브레이커 구현 필수**

### Case 3: Solana AI 토큰 봇 (Reddit, 2024)
- 초기 자금 60% 손실
- 원인: 백테스트 없이 라이브 배포, 유동성 부족, 슬리피지 0% 가정
- 실제 사례: $9M dogwifhat 지정가 주문 → $5.7M 슬리피지 손실
- **교훈: 얇은 오더북에서 대형 주문은 위험. 슬리피지 반드시 계산**

### Case 4: Joe Tay 4년 실험 (Medium 2025)
- 2020~2024: Grid trading, arbitrage, momentum, mean reversion 모두 실패
- 레버리지 미관리로 청산 반복
- **전환점: Donchian Channel(단순) + 7개월 백테스트 + Kelly Criterion → 43.8% APR (승률 34.3%에도 불구)**
- **교훈: 복잡한 전략 < 단순하고 논리적인 전략 + 엄격한 리스크 관리**

### Case 5: ML 전략 과최적화 집단 실패
- 통계: 888개 알고리즘 전략 연구 → 백테스트 Sharpe ratio와 실거래 성과의 R² = 0.025 미만
- 통계: 73%의 자동화 크립토 거래 계정이 6개월 내 실패
- 15개 이상 파라미터 최적화 전략은 라이브에서 거의 100% 실패
- 라이브 대비 30~50% 성과 저하 (슬리피지, 스프레드, 레이턴시)
- **교훈: 파라미터 수 최소화. 파라미터 ±10% 변경 시 성과 안정적이어야**

---

## 2. 성공 패턴

### 단순성 원칙
- 단순하고 논리적인 시스템 > 복잡한 다중 지표 시스템
- 성공 전략: Trend following (Donchian, Turtle), Mean reversion (BB), Arbitrage

### 백테스트 원칙
- Walk-forward validation (롤링 학습/테스트 윈도우)
- 현실적 수수료(0.1%) + 슬리피지(0.05~0.5%) 포함
- Paper trading 최소 1~3개월 후 라이브

### 리스크 관리 > 전략
- 단일 트레이드 최대 자본의 1~2% 리스크
- Kelly Criterion의 25~50%만 사용
- Max Drawdown 한도 → 자동 중단

---

## 3. AI 툴별 봇 현황

| 툴 | 활용 강점 | 한계 |
|----|---------|------|
| ChatGPT/GPT-4o | 전략 아이디어, 코드 생성 속도 | 실거래 판단력 없음, 단독 의사결정 부적합 |
| GitHub Copilot | 보일러플레이트, API 연동 코드 | 아키텍처/전략 검증 취약 |
| Cursor AI | 대규모 리팩토링, 멀티파일 변경 | 신규 전략 설계는 인간 필요 |
| Claude Code | 전략 설계~구현 전범위 | 최종 검증은 인간 필수 |
| Freqtrade | 성숙한 커뮤니티, lookahead analysis 내장 | 복붙 사용자는 시장 변화 무방비 |

---

## 4. 현재 봇 개선 권고사항

### P1 (즉시)
1. **Walk-forward validation 도입**: 전체 기간 최적화 → rolling train/test window
2. **슬리피지/수수료 현실화**: 0.1% fee + 0.05~0.2% slippage (이미 구현됨, 기본값 확인 필요)
3. **Max Drawdown 자동 중단**: -5% 일일, -15% 전체 시 즉시 거래 중단

### P2 (단기)
4. **Kelly Criterion 실제 연결**: kelly_sizer.py가 포지션 사이징에 실제로 연결되는지 확인
5. **Lookahead bias 감사**: pandas shift() 오류, rolling() 윈도우 정렬 오류 검토
6. **전략 수 현실화**: 100개+ 전략 중 백테스트 검증된 10~15개만 메인으로

### P3 (중기)
7. **성과 저하 감지**: 라이브 Sharpe ratio vs 백테스트 대비 40% 하락 시 자동 알림
8. **Paper trading 의무화**: 새 전략 최소 4주 paper trading 후 승격
9. **단순 전략 우선**: LSTM/ML은 보조, Donchian/EMA cross 등 단순 전략 메인

---

## 5. 즉시 적용 체크리스트

**배포 전:**
- [ ] 수수료(0.1%) + 슬리피지(0.05~0.2%) 백테스트 포함
- [ ] Out-of-sample 기간 검증
- [ ] 파라미터 10개 이하, ±10% 민감도 안정
- [ ] Kelly Criterion의 25~50% 포지션 사이징
- [ ] 단일 트레이드 최대 리스크 2% 이하
- [ ] Max Drawdown 자동 중단 활성화
- [ ] Lookahead bias 검토
- [ ] Paper trading 4주+
- [ ] 즉각 킬스위치 존재

**운영 중:**
- [ ] Sharpe ratio 주기적 비교 (백테스트 vs 라이브)
- [ ] 실제 슬리피지 vs 예상 슬리피지 모니터링
- [ ] 전략별 성과 분리 추적
- [ ] 시장 레짐 변화 감지

---

_Sources: Medium, Reddit, dev.to, LuxAlgo, London Post, QuantRocket, Freqtrade GitHub, Jesse, Blockchain Council_
