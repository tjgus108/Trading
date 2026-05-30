======================================================================
🔄 CYCLE 249 — 2026-05-30
======================================================================

## 이번 사이클 배정 카테고리

249 mod 5 = 4 → D(ML) + E(실행) + F(리서치)

## 핵심 작업 완료

### [D] elder_impulse._calculate_atr() 버그 수정 (코드 정확성)
- 버그: `_calculate_atr()` 이 period=14 파라미터를 무시하고 마지막 봉 단일 TR만 반환
- 수정: numpy 기반 True Range 배열 계산 → 14기간 단순 평균으로 교체
- 영향: 변동성 필터(min_volatility=0.002)가 노이즈 없는 안정적 ATR 기반으로 작동
- 신규 테스트 3개: period 평균 검증, 범위 검증, short df 경계조건

### [D] run_bundle_oos.py --use-quality-data 옵션 추가
- `_generate_quality_synthetic_data()` 헬퍼: quality_audit.make_synthetic_data() (GARCH) 사용
- --use-quality-data 플래그: 실거래소 차단 + dry-run 시 GARCH+regime 합성 데이터 활용
- 비교 실험 가능: `python3 scripts/run_bundle_oos.py --dry-run --use-quality-data`

### [E] avg_slippage_per_trade 정량화 검증 (슬리피지 모델)
- BacktestResult.avg_slippage_per_trade 필드 정상 동작 확인
- 신규 테스트 3개: total/count 일치, zero-slippage → zero avg, 비례 증가

### [F] CMF 합성 데이터 우위 분석 완료
- CMF = volume-weighted 가격 위치: GBM bull 레짐에서 볼륨↑ → CMF 양수 방향 일치
- EMA 필터(close>ema50, ema20>ema50)도 bull 80% 구조에서 더 자주 충족
- BlockBootstrap 데이터에서도 CMF 우위 유지 가능성 높음 (volume 패턴 보존)

## 시뮬레이션 결과

### Bundle OOS BTC 4h (합성 GBM, Cycle 249)
- 0/5 PASS
- Rank #1: cmf (Score 76.6, OOS Sharpe -1.270, Avg Trades 12.4, OOS MDD 7.64%)
- IS Sharpe 음수: elder_impulse 100%, narrow_range 100%, cmf 89%, wick_reversal 89%
- ATR 버그 수정은 다음 사이클 OOS 결과에서 elder_impulse 개선 기대

### Paper SIM BTC 1h
- 타임아웃 (300s). 실거래소 차단으로 합성 fallback 연산 과부하.

## 테스트
8346 passed, 23 skipped (신규 6개: ATR 3개 + avg_slippage 3개)

## 다음 사이클: 250 (A+C+F)
- A: elder_impulse ATR 버그 수정 효과 + wick_reversal 변동성 필터 검토
- C: --use-quality-data vs GBM 합성 데이터 IS Sharpe 비교표 작성
- F: BlockBootstrap + 실거래소 없는 환경에서 신뢰가능 validation 방법론
