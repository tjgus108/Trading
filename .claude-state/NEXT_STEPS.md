# Cycle 33 - Execution 모듈 README

## 이번 작업 내용
`src/exchange/README.md` 신규 작성 (79줄, 코드 변경 없음).

### 생성 파일
**src/exchange/README.md**
- ExchangeConnector: ccxt 기반 실거래소 연결, API 권한 체크, wait_for_fill
- PaperTrader: 슬리피지/부분체결/타임아웃 시뮬레이션 모의거래 엔진
- PaperConnector: PaperTrader를 ExchangeConnector 인터페이스로 래핑
- MockExchangeConnector: API 키 없이 demo 모드 전체 파이프라인 테스트
- TWAPExecutor: n_slices 분할 주문, Almgren-Chriss 슬리피지 추정

## 다음 단계
- RiskManager와 ExchangeConnector 연동 흐름 검토 (signal → risk → execute)
- PaperConnector.fetch_ticker() NotImplementedError 개선 고려 (mock price 반환)
