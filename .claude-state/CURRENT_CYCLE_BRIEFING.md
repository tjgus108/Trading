======================================================================
🔄 CYCLE 238 — 2026-05-28T20:17:00Z
======================================================================

## 이번 사이클 배정 카테고리 (238 mod 5 = 3 → C + B + F)

### [C] Data & Infrastructure
- **Agent**: data-agent
- **Focus**: run_bundle_oos.py OOS Sharpe std 임계값 합성/실데이터 분리, DataFeed 캐시 개선

### [B] Risk Management
- **Agent**: risk-agent
- **Focus**: perturbation_check() WalkForwardEngine 통합, DrawdownMonitor+KellySizer dual dampening

### [SIM] Paper Simulation & Auto-improve
- **Agent**: backtest-agent
- **Focus**: scripts/paper_simulation.py 실행 → momentum_quality, volume_breakout 안정성 분석

### [F] Research
- **Agent**: strategy-researcher-agent
- **Focus**: GAN 기반 합성 데이터(TimeGAN) vs GBM 비교, rolling Sharpe 실전 모니터링 사례

## 이전 사이클 현황
**Cycle 237 COMPLETED — B + D + SIM + F** (2026-05-28)
  **[B] Risk:** perturbation_check() 추가 (FRAGILE/ROBUST 판정, ±10%/±20% 섭동)
  **[D] ML:** get_all_regime_importances() 추가 (4레짐 RF 피처 중요도 비교)
  **[SIM] 0/5 Bundle OOS PASS** narrow_range 3/9, value_area 2/9 fold pass (GBM 한계)
  **[F] Research:** 현재 구현 상태 재확인 — vol_scaling, check_regime_death, perturbation_check 모두 구현

## ⛔ 금지 사항
- 새 전략 파일 생성 금지 (현재 ~355개로 충분)
- 한 카테고리에 2 사이클 연속 집중 금지
- 합성 데이터만으로 전략 PASS 판정 금지

## 📋 사이클 종료 시 필수 수행
1. .claude-state/WORKLOG.md 업데이트 (이번 사이클 작업 기록)
2. .claude-state/NEXT_STEPS.md 업데이트 (다음 작업 힌트)
3. .claude-state/CURRENT_CYCLE_BRIEFING.md 업데이트
4. git add -A && git commit -m '[Cycle N] 카테고리 요약 + SIM결과' && git push
5. CYCLE_STATE.txt 다음 사이클 번호로 업데이트 후 재커밋

## 🚀 실행 지침
1. CYCLE_STATE.txt 읽어 N 확인 → N mod 5로 카테고리 결정
2. NEXT_STEPS.md 참고해 구체 작업 수행
3. 시뮬레이션 2종 실행: paper_simulation.py + run_bundle_oos.py
4. 결과 기반 코드 개선 1-2건 수행
5. 모든 수정 후 pytest tests/ -x -q 실행 확인
