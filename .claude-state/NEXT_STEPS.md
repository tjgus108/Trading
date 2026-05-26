# Next Steps

_Last updated: 2026-05-26 (Cycle 214 C+B+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 214 완료
- 214 mod 5 = 4 → **C(데이터) + B(리스크) + F(리서치)** ✅
- 다음 Cycle 215: **215 mod 5 = 0 → A(품질) + C(데이터) + F(리서치)**

### 🔥 Cycle 214 주요 성과
- **Block Bootstrap 합성데이터**: make_block_bootstrap_data() (자기상관+ARCH 보존)
- **VaR 소표본 경고**: PortfolioOptimizer T<30 WARNING + low_sample_warning 필드
- **CircuitBreaker config**: atr_surge_multiplier 등 4파라미터 config.yaml 확장
- **Rank Score 공유**: src/backtest/report.py 추출, bundle_oos에도 적용
- **리서치**: CPCV 구현 가이드 + BH 전략 스크리닝 + Block Bootstrap 벤치마크

### 🎯 Cycle 215 권장 작업 (215 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): BH 보정 기반 전략 스크리닝
- `scripts/strategy_screen.py` 신규: 355개 전략 Sharpe → BH 보정 → 유효 전략 목록
- Haircut Sharpe 출력으로 다중비교 오류 관리
- N=355에서 기대 false positive ≈ 18개 → BH로 FDR 5% 제어

#### C(데이터): Block Bootstrap 고도화
- Politis-White 자동 블록 크기 계산 추가
- paper_simulation.py에 Block Bootstrap 옵션 추가 (GBM/BB 선택 가능)
- 상위 5개 전략을 BB로 재검증, GBM 결과와 비교

#### F(리서치): CPCV 구현 준비
- CPCV 의사코드 → 실제 Python 코드 초안 리서치
- embargo 비율 최적화 (1% vs 2% vs 5%)
- 소규모 전략(5개)으로 CPCV vs WFO 비교 시뮬레이션 리서치

### ⚠️ 핵심 인사이트 (Cycle 213~214)
- Block Bootstrap > GBM: 자기상관+ARCH+fat tail 보존 (암호화폐 적합)
- CPCV > WFO: C(6,2)=15 경로로 PBO 측정, 과적합 확률 감소
- BH 보정: 355개 전략에서 Sharpe ≥ 1.3 필요 (다중비교 보정 후)
- volume_breakout/price_cluster 0 trades 해결 완료

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터 결과는 방향성 참고만 가능

**상태**: Cycle 214 완료 → Cycle 215 A(품질) + C(데이터) + F(리서치)
**최우선 과제**: BH 전략 스크리닝 + Block Bootstrap paper_simulation 통합
