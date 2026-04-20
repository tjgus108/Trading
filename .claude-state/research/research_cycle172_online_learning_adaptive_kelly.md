# Cycle 172 Research: Online Learning + Adaptive Kelly

Date: 2026-04-21

---

## 핵심 인사이트 (5개)

- **ML 봇 실패 1위 원인은 레짐 변화 미대응**: 백테스트 Sharpe와 실전 성과의 R²가 0.025 미만. 44%의 전략이 out-of-sample에서 복제 실패. 2025년 5월 플래시 크래시에서 AI 봇들이 3분 만에 20억 달러 매도 — 정상 조건에 고정된 파라미터가 레짐 변화에 취약함을 실증.
- **River ADWIN이 현재 프로젝트에 즉시 적용 가능**: ADWIN(ADaptive WINdowing)은 슬라이딩 윈도우 내 통계 변화를 감지해 드리프트 경보. River 라이브러리는 `learn_one()` 인터페이스로 한 행씩 증분 학습 — 전체 재학습 없이 모델 적응 가능. 현재 PSI 드리프트 모니터와 병행 사용 가능.
- **Bayesian Kelly가 소자본 가장 현실적 대안**: 파라미터 불확실성 하에서 베팅 크기를 사전 확률(Beta 분포)로 시작해 실거래 결과로 업데이트. 불확실성이 높을수록 자동으로 포지션 축소. 현재 Kelly 레짐 스무딩(Cycle 167 구현)에 Bayesian 레이어 추가 가능.
- **소자본 Kelly 권장: 전체 Kelly의 10~25%**: 크립토 변동성에서 full Kelly는 실질적으로 위험. Fractional Kelly 25~50%에서도 MDD 급증. 소자본(< $10K)에서는 Kelly보다 고정 퍼센트(0.5~1% per trade) + 변동성 조정 방식이 더 안정적. Kelly는 엣지 추정 정확도에 극단적으로 민감 — 10% 과추정만으로도 포지션 크기 2배.
- **성공적 live 전환의 공통 패턴**: (1) 보수적 파라미터 + 동시 활성 거래 1개 제한, (2) 과최적화 회피 — 예외적 백테스트 성과는 오히려 경고 신호, (3) 단계적 전환: 페이퍼 트레이딩 → 소액 실전 → 점진적 증액, (4) API 업타임 99.9%+ 인프라 확보.

---

## 1. ML 트레이딩봇 실패/성공 사례

### 실패 패턴

| 패턴 | 상세 |
|------|------|
| 오버피팅 | 백테스트 Sharpe와 실전 성과 R² < 0.025. 44% 전략 out-of-sample 복제 실패 |
| 레짐 변화 미대응 | 불 마켓 전략이 횡보/변동성 구간에서 붕괴. 2024 파라미터가 2026 시장에 무효 |
| 피처 드리프트 | 온체인/소셜 지표의 의미가 시간에 따라 변화. 구조적 변화(규제, 매크로)에 적응 불가 |
| 거래비용 과소평가 | 슬리피지, 수수료 실제값과 백테스트 차이. 고빈도 전략에서 특히 치명적 |
| 보안/API 취약 | 2024~2025년 상반기 보안 침해로 25억 달러 손실. API 권한 최소화 미적용 |

### 성공 패턴

- 동시 활성 거래 최소화 + 보수적 안전 주문 설정
- DCA 봇이 2024~2026년 대부분의 시나리오에서 65% 이상 outperform
- 페이퍼 트레이딩 → 소액 실전 단계적 전환 필수
- 예외적 백테스트 성과를 경계 (curve-fitting 신호)

---

## 2. Online Learning / Incremental RL

### River 라이브러리 핵심 기능

```
pip install river
```

- `learn_one(x, y)`: 단일 샘플로 증분 학습 — 전체 재학습 불필요
- `predict_one(x)`: 실시간 예측
- ADWIN: 슬라이딩 윈도우 기반 개념 드리프트 감지
- EDDM, Page-Hinkley: 추가 드리프트 감지 알고리즘

### 현재 시스템 적용 방안

```
현재: PSI 드리프트 모니터 (Cycle 165 구현)
추가 가능: River ADWIN으로 실시간 피처 분포 변화 감지
           → 드리프트 감지 시 Kelly fraction 자동 감소 + 모델 재적응 트리거
```

### Incremental RL 최신 동향 (2025)

- Meta-RL-Crypto: 3중 루프 학습 (단일 LLM이 3가지 역할) — 메타 보상 기반 자기 개선
- FinRL: 동적 시장 데이터 처리 파이프라인 + RL 에이전트 직접 연결
- DQN 기반 전략 선택: 5개 사전 정의 전략 중 최적 선택 — 완전 자율 학습보다 해석 가능성 높음
- XGBoost + DDQN + LSTM/GRU 조합이 2025년 크립토에서 높은 성과

### 개념 드리프트 대응 프레임워크

```
감지 레이어 (PSI + ADWIN)
    ↓ 드리프트 감지
적응 레이어 (Kelly fraction 감소 + 모델 재학습 트리거)
    ↓
검증 레이어 (새 데이터로 성과 재확인 후 파라미터 복구)
```

---

## 3. Adaptive Kelly Criterion

### Fractional Kelly with Regime-Dependent Fraction

| 레짐 | 권장 Kelly 분수 |
|------|----------------|
| 강한 추세 (Sharpe > 1.5) | Full Kelly의 25~50% |
| 중립/횡보 | Full Kelly의 10~25% |
| 고변동성/불확실 | Full Kelly의 5~10% |
| 드리프트 감지 후 | Full Kelly의 5% 이하 또는 0 |

### Bayesian Kelly 메커니즘

```python
# 개념적 구조
alpha, beta = prior_beliefs  # Beta 분포 초기값
for trade in live_trades:
    if trade.profit > 0:
        alpha += 1  # 성공 업데이트
    else:
        beta += 1   # 실패 업데이트
kelly_fraction = alpha / (alpha + beta)  # 사후 승률
position_size = kelly_fraction * uncertainty_discount
```

- 초기 불확실성 높을수록 보수적 시작
- 실거래 누적으로 자동 수렴
- 현재 Kelly 레짐 스무딩(Cycle 167)에 Bayesian 레이어 추가 가능

### Distributional Robust Kelly

- 확률 분포가 불확실한 경우: worst-case 분포 집합에서 기대 로그 성장 최대화
- 크립토 블랙스완 대응에 이론적으로 우수
- 구현 복잡도 높음 — 소규모 시스템에는 과도할 수 있음

### 소자본 Kelly 적용 한계 및 대안

**한계:**
- 엣지(승률, 배당률) 추정 오류에 극단적으로 민감
- 10% 과추정 → 권장 포지션 크기 2배 → MDD 급증
- 크립토 변동성에서 full Kelly는 실질적 파산 위험

**권장 대안 (소자본 < $10K):**
1. 고정 퍼센트 리스크: 거래당 자본의 0.5~1%
2. 변동성 조정 포지션 사이징: ATR 기반 크기 조정
3. Fractional Kelly 10~25% + Kelly fraction의 상한선 하드코딩 (예: 최대 2%)

---

## 다음 사이클 적용 제안

1. **River ADWIN 통합**: 기존 PSI 드리프트 모니터에 ADWIN 추가 — 피처 수준 드리프트 실시간 감지
2. **Bayesian Kelly 레이어**: Cycle 167 Kelly 레짐 스무딩에 Beta 분포 기반 승률 업데이트 추가
3. **Kelly 상한선 강화**: 현재 Kelly fraction에 절대 상한 (예: 2%) 하드코딩 검토

---

## 참고 자료

- [ML 봇 실패 패턴: 과적합/레짐 변화](https://www.blockchain-council.org/cryptocurrency/backtesting-ai-crypto-trading-strategies-avoiding-overfitting-lookahead-bias-data-leakage/)
- [River GitHub: Online ML in Python](https://github.com/online-ml/river)
- [River 개념 드리프트 감지 공식 문서](https://riverml.xyz/dev/introduction/getting-started/concept-drift-detection/)
- [Bayesian Kelly: Self-Learning Algorithm](https://medium.com/@jlevi.nyc/bayesian-kelly-a-self-learning-algorithm-for-power-trading-2e4d7bf8dad6)
- [Distributional Robust Kelly (arXiv)](https://arxiv.org/pdf/1812.10371)
- [Kelly Criterion Parameter Uncertainty (ResearchGate)](https://www.researchgate.net/publication/262425087_Optimal_Betting_Under_Parameter_Uncertainty_Improving_the_Kelly_Criterion)
- [Fractional Kelly Simulations](https://matthewdowney.github.io/uncertainty-kelly-criterion-optimal-bet-size.html)
- [FinRL: Financial Reinforcement Learning](https://github.com/AI4Finance-Foundation/FinRL)
- [Meta-RL-Crypto 2025 (arXiv)](https://arxiv.org/html/2509.09751v1)
- [소자본 Kelly 크립토 적용](https://www.lbank.com/explore/mastering-the-kelly-criterion-for-smarter-crypto-risk-management)
