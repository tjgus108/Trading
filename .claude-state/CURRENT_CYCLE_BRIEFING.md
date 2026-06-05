# Current Cycle Briefing

_Cycle 275 완료 | 2026-06-05_

## 완료된 사이클: 275 (A+C+F)

### 카테고리별 작업

**A(품질) — CMF fold2 RSI 분석 및 파라미터화**
- 원인 파악: CMF fold2 (2023-10~12 불마켓) OOS=0.642 약점은 RSI>75 시 BUY 차단
- 해결: `rsi_max_buy` 파라미터 추가 → WFO 그리드 [75,78,80]으로 최적화 허용
- `src/strategy/cmf.py`: rsi < self.rsi_max_buy (기본값 75 유지, 하위 호환)

**C(데이터) — wick_reversal min_wick_ratio 그리드 강화**
- 원인 파악: fold1(2023-08), fold2(2023-10) 추세장에서 약한 wick 오신호
- 해결: min_wick_ratio 그리드 [0.50-0.60]→[0.55-0.65] 상향
- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["wick_reversal"] 업데이트

**F(리서치) — 포트폴리오 구조 분석**
- cmf(모멘텀 추종) + wick_reversal(반전) 독립 알파 구조 유지 정당성 확인
- wick_reversal PASS 구간(fold0 2023-06~08, fold3 2023-12~2024-02)이 cmf와 다름
- 다음 단계: wick_reversal 근본적 문제(추세장 오신호) 해결 방법 리서치

### 시뮬레이션 결과 요약
| 항목 | 결과 |
|------|------|
| 테스트 | 8369 passed, 23 skipped |
| Paper Sim BTC 1h | 0/22 PASS |
| Bundle OOS BTC 4h | 1/5 PASS (cmf ✅) |
| cmf avg OOS Sharpe | 2.508 (std=1.888) |
| wick_reversal avg OOS | 1.200 (std=4.842 FAIL) |

### 다음 사이클: 276 (B+D+F)
- rsi_max_buy 그리드 효과 검증 (run_bundle_oos 재실행)
- wick_reversal min_wick_ratio 그리드 효과 검증
- wick_reversal 개선 방향 리서치 (Shooting Star 조건 강화 검토)
