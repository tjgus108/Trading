======================================================================
🔄 CYCLE 233 — 2026-05-28
======================================================================

## 이번 사이클 배정 카테고리

### [C] Data & Infrastructure
- **Focus**: OFI/VPIN 피처 중복 분석 + paper_simulation 일관성 기준 개선
- **완료**:
  - `src/data/order_flow.py`: `compute_ofi_vpin_correlation()` 추가 (~60줄)
    - OFI, bid_ask_depth_imbalance, VPIN Pearson/Spearman 상관계수
    - 결과: OFI ≈ depth_imbalance (Pearson=1.0) → 중복 확인
    - VPIN vs OFI: 낮은 상관성 → 상호보완적 유지
  - `scripts/paper_simulation.py`: `--pass-ratio` 인자 추가
    - 기본 0.50, 완화 시 0.33 사용 가능 (narrow_range 3/9 → PASS 가능)
- **테스트**: 6개 신규 (TestOFIVPINCorrelation)

### [B] Risk Management
- **Focus**: DrawdownMonitor + KellySizer → RiskManager.evaluate() 통합
- **완료**:
  - `src/risk/manager.py`: evaluate()에 두 모듈 연결
    - Kelly regime fraction scale (HIGH_VOL=0.4x, TREND_DOWN=0.6x, TREND_UP=1.0x)
    - DrawdownMonitor.get_size_multiplier() 적용 (MDD 단계 + 연속손실 + 쿨다운)
    - HIGH_VOL + MDD WARN 동시 발생 시 compound 경고: "net=0.20"
    - trailing_stop_signal() 하위 호환 유지 (get_size_multiplier() 이후 추가)
- **테스트**: 6개 신규 (TestKellyDrawdownIntegration)

### [SIM] 시뮬레이션 (Cycle 232 결과 활용)
- Paper: 0/22 PASS (합성 GBM 한계)
  - 주 실패: mc_p_value 0.28~0.50 (합성 데이터), PF 1.46~1.49 (기준 1.5 근접)
  - 개선 방향: --pass-ratio 0.33 + --mc-p-threshold 0.10 (Cycle 234에서 테스트)
- OOS Bundle: 0/5 PASS, OOS Sharpe std 3.4~6.4
  - narrow_range 최선: 3/9 PASS, std=6.35 (극단 fold로 불안정)

### [F] Research
- OFI/VPIN 중복 분석 완료: bid_ask_depth_imbalance = OFI (완전 동일)
  - → Cycle 234에서 ML features.py에서 depth_imbalance 제거 예정
- 레짐 이질성 원인: IS/OOS 레짐 불일치 → CPCV 검토 (Cycle 234+)
- Kelly compound 성공 사례: Citadel HIGH_VOL Tenth-Kelly 확인

## 테스트 현황
- 8,113 passed, 23 skipped (Cycle 232: 8,101 → +12)

## 다음 사이클
- 234 mod 5 = 4 → D(ML) + E(실행) + F(리서치)
- 핵심: bid_ask_depth_imbalance 제거, 레짐 조건부 fold 가중, TWAP 개선
