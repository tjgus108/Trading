# Trading Bot Project Rules

- 답변과 설명은 짧게. 필요한 것만.
- 수정 전 반드시 Read/Grep으로 현재 코드 확인. 보지 않고 수정하지 말 것.
- 변경 전 `tests/` 확인. 수정 후 관련 테스트 실행.
- 작업 끝나면 `.claude-state/NEXT_STEPS.md` 업데이트.
- 새 파일 생성은 꼭 필요할 때만. 기존 파일 수정 우선.
- `logs/`, `node_modules/`, `__pycache__/`, `.env`, `config/secrets.json`은 읽지 말 것.

## Stack
- Python 3.11+
- 거래소 API: ccxt
- 데이터: pandas, numpy
- 설정: python-dotenv + config/

## Key Dirs
- `src/strategy/` — 매매 전략 로직
- `src/exchange/` — 거래소 연결/주문 실행
- `src/risk/` — 리스크 관리 (포지션 사이즈, 손절)
- `src/data/` — 시세 수집/전처리
- `tests/` — 단위/통합 테스트
- `config/` — 설정 파일 (secrets 제외)
- `.claude-state/` — 작업 재시작용 상태 저장
