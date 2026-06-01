# Next Steps

_Last updated: 2026-06-01 (Cycle 255 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 251, 252, 253, 254, 255

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 251 | B+D+F | wick_reversal ATR 필터, Deflated Sharpe Ratio 유틸리티 |
| 252 | E+A+F | validate_ohlcv() 헬퍼, DSR→BundleOOS 통합 |
| 253 | C+B+F | load_csv_ohlcv/resample_ohlcv, 전환쿠션, RollingOOS max_oos_sharpe_std 파라미터화 |
| 254 | D+E+F | nr_range_ratio/nr_atr_ratio 피처, --csv-dir 옵션, **MC 버그 수정** |
| 255 | A+C+F | GARCH CSV 생성, 0-trade score 버그 수정, SOL 6/22 PASS 확인 |

### 🎯 Cycle 256 작업 방향 (256 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): Profit Factor 개선을 위한 리스크 파라미터 조정
- SOL 시뮬에서 fail 원인 1위: profit_factor < 1.5 (PF 1.0~1.45 범위)
- atr_multiplier_tp 현재값 확인 → TP를 더 넓게 설정하면 PF 개선 가능성
- BacktestEngine 기본 파라미터: atr_multiplier_sl, atr_multiplier_tp 최적화 실험
  - 단, 전략 파일 수정 없이 engine level에서만 조정
- Kelly sizer 파라미터 검토: f* = (p*b - q) / b 공식에서 b(odds) 계산 정확성 확인

#### D(ML): price_action_momentum, momentum_quality 신호 품질 향상
- SOL 시뮬 TOP 전략 (sharpe 4.18, 3.67) 분석 → ML 피처로 이 신호 조건 학습
- FeatureBuilder에 모멘텀 강도 피처 추가 검토:
  - `mom_quality_score`: price_action_momentum의 핵심 조건 (return_5 > threshold) 피처화
  - `trend_strength`: momentum_quality의 EMA alignment score
- run_bundle_oos.py GARCH 데이터에서 narrow_range mc_p 추가 분석

#### F(리서치): PF 개선 전략 리서치
- profit_factor 1.5 기준: 1 손실당 1.5 이익 필요 → win_rate 41%에서 달성 조건 분석
- Exit logic 개선: trailing stop vs ATR-based TP 비교 실험
- data/historical GARCH CSV로 paper_simulation --csv-dir 재실행 (BTC 결과 개선 확인)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단 (합성 데이터만 사용 가능)
- BTC CSV (GARCH, 12000 rows): 아직 미실행 (이번 사이클에 CSV 생성 후 시간 부족)
- 합성 데이터 한계: OOS Sharpe std 3.7~7.7 (기준 1.5 대비 과대) — 실 데이터 PASS 필수

### 핵심 메트릭 (Cycle 255)
- 테스트: 8367 passed, 23 skipped + 1 신규 (silent strategy score test)
- 신규: GARCH CSV (data/historical/binance/BTCUSDT/1h.csv), 0-trade score 버그 수정
- Paper Sim: BTC 0/22, ETH 1/22 (linear_channel_rev), **SOL 6/22 PASS**
  - PASS: price_action_momentum(4.18), momentum_quality(3.67), roc_ma_cross(3.84), cmf(2.59), supertrend_multi(2.80), acceleration_band(2.17)
- Bundle OOS: 0/5 PASS — narrow_range #1 (Score 85.2, OOS Sharpe std 5.458)
- 주요 fail 원인: profit_factor < 1.5 (binding constraint)
