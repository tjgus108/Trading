# Next Steps

_Last updated: 2026-04-17 (Cycle 139 — Data Infrastructure)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 140
- 140 mod 5 = 0 → **A(품질) + E(실행) + SIM + F(리서치)**

### 우선순위: ⚠️ 실제 데이터 기반 전략 재검증

**Cycle 139 완료 사항** (Data & Infrastructure):
- ✅ `src/data/data_utils.py`: 실제 거래소 데이터 다운로드 + 검증 유틸리티
  - Paginated fetching with Bybit support
  - Multi-timeframe (1h, 4h, 1d)
  - Gap/anomaly detection with quality scores
  - Parquet caching

- ✅ `src/data/feed.py`: Auto-reconnection + data validation
  - `ensure_connected()`: Health check → auto-reconnect → cache invalidation
  - `validate_fetch_result()`: Quality threshold checks (min 50 candles, ≤5% missing)
  - Fixed error classification for test environments

- ✅ 14/16 new tests pass (826+ existing pass)

**다음 세션 할일**:

1. **[A] Quality Audit** — 새로운 데이터 기반으로 현존 전략 재평가
   - paper_simulation.py 실행 (이제 실제 Bybit 데이터 기반)
   - 이전 22개 PASS 전략 중 실제 데이터에서 통과하는 전략 식별
   - Sharpe ≥ 1.0, PF ≥ 1.5, Trades ≥ 15, MDD ≤ 20% 기준 재확인

2. **[E] Execution** — Regime Detection 또는 새로운 신호 로직
   - HMM k=2 (추세/횡보) 구현 (리서치 완료상태)
   - 또는 데이터 기반 신호 검증 (rolling backtest)

3. **[SIM] Paper Simulation** — Real Bybit data로 Walk-Forward 재실행
   - 6개월 실제 데이터로 walking-forward test
   - Multi-timeframe regime 적용

4. **[F] Research** — 실패 이유 분석
   - Cycle 138의 22개 전략 실패 원인 (합성 vs 실데이터)
   - 새 전략 설계 원칙 정리

### 기술 부채 (낮은 우선순위):
- WebSocket feed 안정성 (이미 REST fallback 있음)
- OrderFlow 정확도 (VPIN zero-volume 버그는 C134에서 수정함)
- Rolling Sharpe 모니터링 (구현 가능하지만 전략 재검증이 선행)

### 주의사항:
- `[!] 새 전략 파일 생성 금지` — 현재 355+개로 충분
- `[!] 합성 데이터만으로 최적화 금지` — 반드시 실제 Bybit 데이터 사용
- `[!] 한 카테고리에 2 사이클 연속 집중 금지` — 로테이션 준수
