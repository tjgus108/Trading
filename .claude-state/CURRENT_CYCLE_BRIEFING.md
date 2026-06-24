# Current Cycle Briefing

_Last updated: 2026-06-24 (Cycle 353 완료)_

## 현재 상태 요약

- **완료 사이클**: 353
- **카테고리**: C(데이터) + B(리스크) + F(리서치)
- **1h PASS 연속 FAIL**: 33연속 0/22 (BTC 실데이터 기준)
- **4h PASS**: 0/22 (consistency 부족, 33연속)
- **Bundle OOS**: 5/5 PASS 유지 (SSL 차단으로 재실행 불가)

## Cycle 353 핵심 발견

### C(데이터): ETH HIGH 슬리피지 개선
- ETH vol_spike_prob: 0.28 → 0.10
- ETH 1h HIGH%: 22.4% → 7.8% (개선 ✅)
- ETH mean ATR: 2.12% → 1.68% (side effect, 허용)
- ETH synthetic 전략 성능: 전반 악화 (참고값으로만 사용)

### B(리스크): min_agree_count=2 실험 → NEGATIVE
- SupertrendMultiStrategy에 `min_agree_count` 파라미터 추가 (default=3, 코드에 유지)
- BTC 4h: min_agree_count=2 적용 시 consistency 3/8→2/8, Sharpe 1.14→0.96
- ranging 구간 진입 신호 품질 낮음 → 3/3 필터가 정확한 차단
- paper_sim 즉시 롤백 (→ default 3/3 유지)

### F(리서치): 4h 33연속 FAIL 구조 분석
- 8 min_trades × 60일 윈도우 = 통계적 신뢰도 한계
- mc_p_value 실패 빈도 높음 (우연 가능성)
- 다음 접근: 시장 레짐 명시적 필터 or 테스트 윈도우 기준 재검토

## 코드 변경 (Cycle 353)

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/supertrend_multi.py` | `min_agree_count: int = 3` 파라미터 추가 (generate() 로직 수정) |
| `scripts/generate_garch_csv.py` | ETH `vol_spike_prob`: 0.28→0.10 |
| `data/historical/synthetic/ETHUSDT/1h.csv` | 재생성 (HIGH% 22.4%→7.8%) |

## 다음 사이클 (354) 방향

- 354 mod 5 = 4 → **D(ML) + E(실행) + F(리서치)**
- D: 4h paper_sim 상위 전략(price_cluster, supertrend_multi) 개선 실험
  - supertrend_multi: 3/3 유지 상태에서 W4/W5/W7 해결 새 접근 (시장 레짐 pre-filter)
  - price_cluster: 2/8 → 4/8+ 달성을 위한 파라미터 조정
- E: 4h test 윈도우 조정 실험 (현재 60일 → ?일)
  - Cycle 312 역효과 기록 참고 (84일 확장 → price_cluster 3/8→1/12)
  - 단기 조정: 45일 → min_trades=5 로 조합 검토
- F: Bundle OOS PASS 전략 4h 성능 분석 (cmf, ofi_v2, supertrend_multi)
