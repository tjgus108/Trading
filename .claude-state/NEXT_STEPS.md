# Next Steps

_Last updated: 2026-05-31 (Cycle 254 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 250, 251, 252, 253, 254

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 250 | A+C+SIM+F | GARCH(1,1) 합성데이터 개선, elder_impulse ATR 검증 |
| 251 | B+D+F | wick_reversal ATR 필터, Deflated Sharpe Ratio 유틸리티 |
| 252 | E+A+F | validate_ohlcv() 헬퍼, DSR→BundleOOS 통합 |
| 253 | C+B+F | load_csv_ohlcv/resample_ohlcv, 전환쿠션, RollingOOS max_oos_sharpe_std 파라미터화 |
| 254 | D+E+F | nr_range_ratio/nr_atr_ratio 피처, --csv-dir 옵션, **MC 테스트 버그 수정** |

### 🎯 Cycle 255 작업 방향 (255 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): MC 버그 수정 후 시뮬레이션 재검증
- Cycle 254에서 MC permutation test 버그 수정 (equity-curve vs trade-PnL Sharpe 스케일 불일치)
- 수정 후 paper_simulation.py 재실행 → narrow_range mc_p 개선 여부 확인
- momentum_quality, volatility_cluster의 mc_p도 개선 예상 → PASS 가능성 분석
- 기존 test_mc_narrow_range.py의 MC 테스트 케이스 업데이트 (새 기준에 맞게)

#### C(데이터): 실 데이터 CSV 파이프라인 실전 테스트
- data/historical/ 구조에 샘플 CSV 생성: `data/historical/binance/BTCUSDT/1h.csv`
- load_ohlcv_from_csv_dir() + paper_simulation.py --csv-dir 통합 검증
- resample_ohlcv(df, "4h") → BacktestEngine(timeframe="4h") 체인 검증
- 가능하면 Kaggle/CryptoDataDownload CSV 다운로드 후 실 데이터 시뮬

#### F(리서치): MC 버그 수정 영향 분석 + walk-forward 개선
- 수정된 MC 테스트로 narrow_range가 합성 데이터에서 PASS 되는지 확인
- 만약 PASS: PASS 기준 완화 없이 합성 데이터에서도 검증 가능 → 실 데이터 PASS 기대 ↑
- 만약 여전히 FAIL: 다른 fail reason (OOS Sharpe std) 분석

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단 (합성 데이터만 사용 가능)
- 합성 데이터 한계: OOS Sharpe std 3.7~7.7 (기준 1.5 대비 과대)
- MC 버그 수정으로 narrow_range mc_p 개선 예상 → 실 데이터 PASS 가능성 ↑

### 핵심 메트릭 (Cycle 254)
- 테스트: 8367 passed, 23 skipped (Cycle 254 피처 추가 후)
- 신규: nr_range_ratio, nr_atr_ratio (ML 피처), --csv-dir (paper_sim), MC 버그 수정
- 시뮬: 0/22 PASS paper (MC 버그 수정 전), 0/5 PASS Bundle OOS
- 최근접: narrow_range (Score 85.2, fold 4 OOS Sharpe 3.016, PF 1.645)
- **MC 버그 수정 효과**: 합성 데이터에서도 narrow_range mc_p ~0.007 (<<0.05) 예상
