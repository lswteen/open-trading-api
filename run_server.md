# Alpha Algo AI 서버 실행 가이드 🚀

대시보드 서버를 중지하거나 재시작할 때 사용하는 명령어 모음입니다.

### 1. 서버 시작 (Start)
터미널에서 아래 명령어를 실행하여 서비스를 시작합니다.

```bash
PYTHONPATH=. uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 서버 중지 (Stop)
`Address already in use` 메시지가 나오거나 서버를 완전히 끄고 싶을 때 사용합니다.

```bash
lsof -ti:8000 | xargs kill -9
```

### 3. 문제 해결 (Troubleshooting)
- **포트 충돌**: 위 2번 명령어를 실행한 후 다시 1번을 실행하세요.
- **의존성 오류**: `uv sync` 명령어를 입력하여 라이브러리를 업데이트하세요.
