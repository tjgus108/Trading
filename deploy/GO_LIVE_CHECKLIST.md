# Go-Live Checklist

## API Setup
- [ ] API 키 권한: 읽기 + 거래만 (출금 권한 절대 금지)
- [ ] IP 화이트리스트 설정 (서버 고정 IP만)
- [ ] `.env` 파일에 키 저장, 코드에 하드코딩 없음 확인
- [ ] API 키 만료일 확인 (Bybit: 미설정 시 3개월 후 자동 만료)

## Pre-deployment Testing
- [ ] 테스트넷에서 최소 2주 Paper Trading 완료
- [ ] Walk-Forward 검증 통과 (6개월 데이터, 복수 윈도우)
- [ ] 네트워크 단절 시나리오 테스트
- [ ] 거래소 점검/다운타임 시나리오 테스트
- [ ] Flash crash (10%+ 급변) 시나리오 테스트

## Risk Management
- [ ] `config/config.yaml`에서 dry_run: true -> false 전환
- [ ] max_drawdown: 5%, max_daily_loss: 3% 확인
- [ ] flash_crash_pct: 10% 서킷 브레이커 활성화
- [ ] max_consecutive_losses: 5 확인
- [ ] 초기 자금: 전체의 5~10% 이하로 시작

## Monitoring
- [ ] Telegram 알림 활성화 (config.yaml telegram.enabled: true)
- [ ] TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID 환경변수 설정
- [ ] 로그 로테이션 활성화 (RotatingFileHandler, 10MB x 5)
- [ ] systemd 서비스 등록 (deploy/trading-bot.service)

## Safety Mechanisms
- [ ] SL/TP 보호 주문이 거래소에 실제 제출되는지 확인
- [ ] SL 실패 시 emergency close 동작 확인
- [ ] Connector halt (연속 5회 실패) 동작 확인
- [ ] 재시작 시 포지션 동기화 (sync_positions) 동작 확인
- [ ] Kill switch: 수동 중단 명령어 준비

## Legal / Tax
- [ ] 거래 내역 전량 로깅 (세무 신고 대비)
- [ ] 해외 거래소 자산 이전 신고 의무 확인
