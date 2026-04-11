# Cycle 22 - Category B: Risk Management

## 완료: position_sizer 극단 케이스 스트레스 테스트

### 이번 작업 내용
`tests/test_position_sizer_stress.py` 신규 생성 (9개 테스트)

**커버한 극단 케이스:**
1. **Zero balance** — `capital=0` 입력 시 ZeroDivision 없이 0.0 반환
2. **Excessive volatility** — `atr=10000` (target 100배) → 사이즈 축소 검증, `atr=0` → 조정 스킵
3. **Tiny stop distance** — `avg_loss=1e-10` → max_fraction 상한 클리핑, `avg_win=0` guard
4. **Negative Kelly** — 저승률+저비율 → 0, `win_rate=0` → 0

### 변경 파일
- `tests/test_position_sizer_stress.py` — 신규 (9개 테스트, 전체 통과)

### 테스트 결과
```
9 passed in 0.32s
```

## 다음 단계
- RiskManager 설정 validation (Cycle 22 옵션 2)
- risk_per_trade > 0.1 경고 로직 추가 후보
