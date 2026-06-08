# Next Steps

_Last updated: 2026-06-08 (Cycle 288 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 288

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 286 | B+D+F | atr_threshold=0.5 무효 확인(cmf binding), cmf_period=10 역효과, DEFAULT_GRIDS 하향 조정 |
| 287 | B+D+F | regime_transition_is_min=2.0 추가 → supertrend_multi **첫 PASS** (avg=3.674, std=1.860) |
| 288 | C+B+F | resample_ohlcv partial bucket 제거, regime_transition 경고 로깅 강화, cmf 16회 PASS 유지 |

### 🎯 Cycle 289 작업 방향 (289 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): ML 신호 품질 개선
- **탐색 방향**:
  - ML 앙상블 가중치 재검토 (supertrend_multi OOS 기여도 반영)
  - Paper Sim에서 supertrend_multi Sharpe=0.60 → 1h 타임프레임 파라미터 검토
  - RF 모델 피처 중요도 분석 (cmf 피처가 중요도 높은지 확인)

#### E(실행): Paper Trading 모드 안정화
- **탐색 방향**:
  - TWAP 실행기 slippage 모델 검증 (Paper Sim 기준 slippage=0.05%)
  - Paper Sim 0/22 PASS 지속 원인 추가 분석
    - 1h 신호 PF 분포 확인 (1.17 ← PF threshold 1.5에 미달)
    - 가능한 접근: 수수료 모델 검토 (0.1% 1h 봉 → 신호 대비 높은 거래비용)

#### F(리서치): 거래비용 최적화 리서치
- 1h 봉 + 0.1% 수수료가 Paper Sim FAIL에 미치는 영향 정량화
  - 4h 봉과 비교: 4h에서 PASS인 전략이 1h에서 FAIL → 수수료 배율 차이 4x
  - 탐색: 4h Paper Sim 도입 가능성 (현재 1h만 있음)

### ⚠️ 주의 사항 (Cycle 289)
- **supertrend_multi regime_transition_ratio=20% 경고 발동 중**: 새 경보 로직 추가됨
  - fold3 (trades<3) + fold4 (레짐 전환) = 현재 2/5 fold 미사용
  - 파라미터 변경 시 fold3/4 패턴 변화 모니터링 필수
- **Bundle OOS: `--csv-dir data/historical` 필수** (미지정 시 합성 데이터로 fallback)
- **Paper Sim 0/22 PASS 지속**: 1h 전략 개선 전까지 예상 유지

### 핵심 메트릭 (Cycle 288)
- 테스트: **8310 passed** (walk_forward 70 추가) — 회귀 없음
- Paper Sim BTC 1h (8 windows): 0/22 PASS
  - rank1: supertrend_multi (score=73.9, +6.73%, Sharpe=0.60, PF=1.17, 2/8)
- Bundle OOS BTC 4h (5-fold, CSV):
  - cmf: **PASS** avg=2.508, std=1.888 ← **16회 연속 PASS**
  - supertrend_multi: **PASS** avg=3.674, std=1.860 ← **2회 연속 PASS**
    - fold3 excluded (trades<3, 구조적) / fold4 excluded (레짐 전환 IS=2.51>2.0, WFE<0)
  - elder_impulse: FAIL | narrow_range: FAIL | value_area: FAIL
  - **총 PASS: 2/5 유지**

### 주요 코드 변경 이력 (Cycle 288)
1. `src/data/data_utils.py` — resample_ohlcv partial bucket 제거 (C 데이터)
   - `drop_incomplete=True` 파라미터 추가
   - 버킷 당 캔들 수 < 최빈값이면 partial 버킷 드롭 (backtest 왜곡 방지)
2. `src/backtest/walk_forward.py` — regime_transition_ratio 경고 로깅 (B 리스크)
   - 항상 logger.info로 ratio 출력
   - ratio >= 20%이면 logger.warning 발동 (40% 경계 조기 경보)
3. `tests/test_data_utils.py` — 3개 resample 테스트 추가 (C 데이터)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조)
- Paper simulation: 22 전략 × 8 windows → 약 15분 소요 (Bash timeout 주의)
