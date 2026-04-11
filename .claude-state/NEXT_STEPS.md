# Cycle 20 - 진행 상황

## 완료: Dashboard Impl Shortfall 표시 연동

### 작업 내용
`src/dashboard.py` — Implementation Shortfall 메트릭 대시보드 연동

1. **`OrchestratorStatusProvider.get_status()`** (line 72-76)
   - `impl_shortfall_avg_bps` 필드 추가
   - `orch._impl_shortfall_samples` 평균값 계산해 반환
   - 샘플 없으면 `None`

2. **`_render_html()`** (line 165-167, 218-219)
   - `sf_str`, `sf_color` 변수 추출
   - 5bps 초과 → 빨강, 1bps 초과 → 주황, 이하 → 초록
   - "Impl Shortfall (avg)" stat 블록 HTML 추가

### 변경 파일
- `src/dashboard.py` — lines 72-76, 165-167, 218-219
- `tests/test_dashboard.py` — `test_render_html_impl_shortfall`, `test_render_html_impl_shortfall_none` 2개 추가

### 테스트 결과
```
8 passed in 3.02s (test_dashboard.py 전체)
```

## 다음 단계
- Telegram notifier 포맷 개선 (옵션 2)
- heston_lstm 테스트 커버리지 보강
