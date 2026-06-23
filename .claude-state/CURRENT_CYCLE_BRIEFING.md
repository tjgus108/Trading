# Current Cycle Briefing

_Last updated: 2026-06-23 (Cycle 347 완료)_

## 현재 상태 요약

- **현재 사이클**: 347 완료 (B(리스크) + D(ML) + F(리서치))
- **1h Paper Sim**: 0/20 PASS — 27연속 FAIL streak
- **4h Bundle OOS**: 5/5 PASS 안정 유지 (OFI Sharpe=4.345)
- **테스트**: 8434 passed, 23 skipped

## 이번 사이클 핵심 변경

| 변경 | 파일 | 내용 |
|------|------|------|
| B(리스크) | `src/risk/manager.py` | evaluate()에 RANGING 레짐 시 ema50_slope→set_ranging_macro_neutral() 자동 연동 |
| 테스트 | `tests/test_risk_manager.py` | RANGING 매크로 manager 통합 테스트 4개 추가 |

## 핵심 인사이트

1. **RANGING 매크로 실전 연동 완료**:
   - manager.py evaluate()에서 regime='RANGING' + candle_df → ema50_slope 자동 계산
   - DrawdownMonitor.set_ranging_macro_neutral() 호출로 cooldown 동적 조정 활성화
   - neutral(|slope|≤0.0005): 0.9x, directional: 1.5x

2. **narrow_range 1h 분석 (D(ML))**:
   - BTC 1h 전체: ema_slope ≥ 0.0005 통과율 70% (차단율 30%)
   - IS 기간(2023 Q1 bull): neutral zone = 33.2%
   - 0.0005 필터로도 PF=0.97 (평균) → 1h 수수료 구조가 근본 병목
   - paper_sim narrow_range: Sharpe=-0.51, 0/8 (변화 없음)

3. **27연속 0/20 FAIL 구조**:
   - 핵심: PF < 1.5. 1h 수수료 0.11% round-trip = 연 7.9% 드래그 (월 6거래 기준)
   - price_cluster PF=1.20 (best, 갭 0.30), roc_ma_cross PF=1.22
   - ETH 합성 dema_cross High% = 94.9% (이상값, BTC: 8.3%) → 합성 데이터 신뢰도 제한

4. **4h Bundle OOS 5/5 PASS 유지**:
   - 4h에서는 수수료 상대비중 1/4 → PF ≥ 1.5 달성 가능
   - 4h paper_sim 검토가 근본 해결 경로

## 다음 사이클 (348, mod 5 = 3 → C+B+F)

- C: ETH 합성 데이터 슬리피지 High% 94.9% 이상 진단
- B: paper_simulation.py ↔ DrawdownMonitor 연결 여부 확인
- F: 4h paper_sim 데이터/지원 확인 및 타당성 평가
