# Cycle 191 Research — 트레이딩봇 실패/성공 사례

_작성일: 2026-05-22_

---

## 1. 실패 사례

- **Kronos Research API 해킹 (2023.11)**: 공격자가 API 키를 탈취해 OKX/BTSE/Binance 계좌에서 $25M 인출. 핵심 교훈 — API 키에 출금 권한 부여 금지, IP 화이트리스트 필수, 이상 트레이딩 즉시 감지 알림 설정. 우리 프로젝트: `config/secrets.json` 읽기 금지 정책 이미 존재, API 키 관리 점검 필요.

- **Dogwifhat 슬리피지 사건 (2024.01)**: $9M 시장가 주문이 주문창이 얕은 상황에서 실행되어 $5.7M 이상 슬리피지 발생 (가격 60% 스파이크). 교훈 — 대형 포지션은 반드시 TWAP/VWAP 분할 실행 필요.

- **AI 봇 플래시 크래시 증폭 (2025.05)**: 플래시 크래시 발생 시 AI 봇들이 3분 만에 $2B 매도 집행 → 낙폭 증폭. 레짐 탐지 없이 모멘텀 전략만 구동하는 봇들의 집단적 실패.

- **과최적화(Overfitting) 구조적 실패**: 73%의 자동화 트레이딩 계좌가 6개월 내 실패. 주 원인: 백테스트 Sharpe가 라이브에서 붕괴 — 90% 이상의 학술 전략이 실전 적용 시 FAIL. 우리 프로젝트: IS-only PASS 전략 5개가 OOS에서 전부 실패한 것과 정확히 일치.

- **Look-Ahead Bias (Freqtrade 커뮤니티 반복 신고)**: `shift()`/`rolling()` 오용으로 미래 데이터가 신호 계산에 유입. 백테스트는 우수하나 라이브에서 즉시 붕괴. Jesse는 zero look-ahead bias를 명시적 설계 원칙으로 채택.

- **상관 리스크 과소평가**: 5개 DCA 봇을 서로 다른 코인에 운용해도 BTC 15% 하락 시 전 포지션 10~25% 동시 하락. 분산 효과 없음.

---

## 2. 성공 사례

- **예측시장 레이턴시 아비트라지**: Polymarket ↔ Binance/Coinbase 가격 갭 이용 봇 — $313 → $414K (1개월). 2024.04~2025.04 동안 $40M 추출 추정. 교훈: 구조적 비효율이 존재하는 틈새시장 공략.

- **크로스체인 아비트라지 (2023.09~2024.08)**: 9개 블록체인에서 240,000건 성공, $868M 볼륨. 인프라 우위(레이턴시) + 자동화가 핵심.

- **보수적 DCA (BTC/USDT, Binance)**: 안전 주문 넓게 설정, 36건 100% 성공률, 30일 12.8% 수익. 단, 레버리지 무사용, 하락장 취약성 있음.

- **성공 봇들의 공통 설계 패턴**:
  1. 자본 50~70%만 봇에 배분 (30~50% 리저브 유지)
  2. 일일 손실 한도 + 연속 손실 Circuit Breaker 내장
  3. 코릴레이션 가드: 동일 방향 포지션 최대 3개
  4. 멀티레짐 테스트 (트렌드/레인지/크래시 모두)
  5. 최소 3~6개월 페이퍼 트레이딩 후 실전 전환

- **실전 검증 리스크 관리 방법론**:
  - 포지션 사이즈 = 자본 × (허용손실%) / (진입-손절 거리)
  - 안티-마틴게일: 손실 시 포지션 축소, 수익 시 확대
  - Circuit Breaker: MDD 7% 도달 시 당일 거래 중단 (우리: 10%/20% 임계값)

---

## 3. 최신 퀀트 리서치

- **[SSRN 2025] Quantitative Alpha in Crypto Markets** (William Mann): 팩터 모델 리뷰 — 사이즈, 모멘텀, 유동성 팩터가 크립토에서 통계적 유의성 확인. CNN-LSTM 하이브리드가 비선형 패턴 포착에서 우수.

- **[arXiv 2025] AlgoXpert Alpha Research Framework (IS→WFA→OOS)**: 3단계 검증 프로토콜. WFA에서 rolling window + purge gap으로 정보 유출 방지. 우리 프로젝트의 WalkForwardOptimizer와 동일한 방향.

- **[MDPI 2025] Bayesian vs. Evolutionary Optimization for Crypto Perpetual Trading**: 파라미터 공간 위상(topology)에 따라 베이지안(볼록 공간)과 유전 알고리즘(비볼록 공간) 선택이 다름. 우리 plateau_pct 전략과 연관 — 안정 영역 선택이 핵심.

- **[arXiv 2025] Adaptive Regime-Aware Prediction (Autoencoder + Dual Transformer + RL)**: 오토인코더로 이상 레짐 탐지 → 안정/이벤트 구동 전용 Transformer 듀얼 운용 → RL 컨트롤러가 레짐 임계값 동적 조정. 우리 MarketRegimeDetector 확장 방향과 일치.

- **[arXiv 2025] Meta-RL-Crypto**: 메타러닝 + RL 통합 Transformer — 다양한 레짐에서 자기개선. 실용적 접근: 단기적으로는 XGBoost(BTC 분류 정확도 55.9%)가 현실적.

- **[arXiv 2025] Walk-Forward 최적화 표준화**: lookback 기간 결정이 장기 트렌드 포착 vs. 단기 적응성 사이 핵심 trade-off임을 실증. 짧은 lookback = 과적합, 긴 lookback = 레짐 변화 미반영.

- **[Wiley 2025] Trading Games: Beating Passive Strategies in Bullish Crypto Market**: 불장에서 passive(B&H) 전략을 이기기 어려움. 능동 전략의 가치는 하락장/레인지장에서 집중됨.

---

## 4. 우리 프로젝트에 적용 가능한 인사이트

- **IS→OOS 붕괴 근본 원인 재확인**: 우리 5개 전략 모두 IS Sharpe 5~7이지만 OOS FAIL. 위 연구들이 정확히 같은 현상 보고. 해결책은 실데이터 WF 검증이며 이미 Cycle 190 C(데이터) 과제로 설정됨 — 방향 확인.

- **레짐 탐지 우선화**: 플래시 크래시 때 봇 집단 실패 사례 → CircuitBreaker의 `rapid_decline_pct` (Cycle 187 구현) 는 올바른 방향. 추가로 레짐별 포지션 사이즈 동적 축소 고려.

- **상관 가드 강화**: 코릴레이션 가드(동일 방향 최대 3개) — 우리 DrawdownMonitor에 상관 필터 이미 있음(ATR/상관 체크). 실전 파라미터 점검 권장.

- **Lookback 최적화**: WFA rolling window 길이 선택에 대한 연구 → 우리 `WalkForwardOptimizer`의 `window_size` 파라미터 민감도 분석 필요 (F 과제 후보).

- **XGBoost 레짐 분류기**: 단기 실용적 ML 도입으로 BTC 방향성 분류 55.9% 정확도. 현재 ML 파이프라인 확장 가능 지점.

- **API 보안**: Kronos 사례 → API 키에 출금 권한 절대 부여 금지, IP 화이트리스트 설정, secrets.json 접근 로그 모니터링.

---

## 5. 경고/주의사항

- **합성 데이터 한계 재확인**: 위 연구들 모두 "합성/백테스트 성과 ≠ 실전"을 반복 강조. 현재 프로젝트의 OOS FAIL이 구조적 문제가 아닌 데이터 한계임을 재확인 — 실데이터 확보가 최우선.

- **과도한 전략 추가 금지**: 이미 355+ 전략. 연구에 따르면 봇 수를 늘리는 것보다 기존 봇의 OOS 검증이 중요. CLAUDE.md 정책 유지 타당.

- **불장 바이어스 경계**: 2024~2025 상승장 데이터로 학습된 전략은 하락장에서 취약. 멀티레짐 스트레스 테스트 강화 필요.

- **레이턴시 아비트라지 제외**: 40ms 이하 인프라 없이는 구조적으로 접근 불가. 해당 알파는 우리 프로젝트 범위 밖.

- **LLM 트레이딩 시스템 lookahead bias**: DatedGPT 논문에 따르면 LLM 기반 시그널은 훈련 데이터의 미래 정보를 내재할 수 있음 — ML 전략 도입 시 엄격한 시점 분리(point-in-time) 검증 필수.
