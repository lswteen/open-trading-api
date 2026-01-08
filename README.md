# Alpha Algo AI (오픈 트레이딩 API 프로젝트)

**[한국투자증권 샘플 코드 관련 유의사항]**
- `kis_resources/` 폴더 내의 코드는 한국투자증권 Open API(KIS Developers) 연동 예시입니다.
- 샘플 코드는 참고용으로 제공되며, 이를 활용한 프로그램 운영에 대한 책임은 사용자에게 있습니다.

## 1. 프로젝트 소개

### 🎯 제작 의도
이 프로젝트는 한국투자증권 Open API를 기반으로 **토스 증권 스타일의 현대적이고 직관적인 주식 거래 대시보드(Alpha Algo AI)**를 구현한 것입니다.
LLM(Large Language Model)이 이해하기 쉬운 구조로 설계되었으며, Python 개발자가 쉽게 확장하고 커스터마이징할 수 있도록 모듈화되어 있습니다.

### 🚀 주요 기능
- **실시간 대시보드**: KOSPI, KOSDAQ 지수 및 실시간 거래 대금 상위 종목 시각화
- **미니 차트**: HTML5 Canvas 기반의 부드러운 실시간 지수 차트
- **주식 상세 및 호가**: 실시간 호가창(Hoga), 차트, 잔고 조회
- **주문 시스템**:
    - 지정가, 시장가 주문
    - **시간외 거래 지원**: 장전 시간외, 장후 시간외, 시간외 단일가 주문 및 시세 조회 (New)
- **인메모리 캐싱**: API 속도 제한 준수 및 응답 속도 최적화를 위한 자체 캐싱 레이어

## 2. 폴더 구조 및 파일 설명

프로젝트는 크게 **구현 코드(Alpha Algo AI)**와 **한국투자증권 리소스(Resources)**로 나뉩니다.

```bash
open-trading-api/
├── app/                        # [구현 코드] Backend (FastAPI)
│   ├── api/v1/                 # API 라우터
│   ├── application/            # 비즈니스 로직 (Service Layer)
│   └── infrastructure/         # 외부 API 연동 (KIS Client)
├── frontend/                   # [구현 코드] Frontend (Vanilla JS/HTML/CSS)
│   ├── index.html              # 메인 페이지
│   └── static/                 # 스타일, 스크립트, 이미지
├── kis_resources/              # [리소스] 한국투자증권 제공 파일
│   ├── examples_user/          # 주식, 채권, 선물 등 API 호출 예제
│   ├── examples_llm/           # LLM 학습용 단위 테스트 코드
│   ├── stocks_info/            # 종목 마스터 데이터 등
│   └── docs/                   # API 문서 및 가이드
├── kis_devlp.yaml              # API 설정 파일 (앱키, 시크릿 등)
├── debug_*.py                  # 디버깅용 스크립트 (기능 테스트용)
├── run_server.md               # 서버 실행 가이드
└── project_summary.md          # 프로젝트 상세 명세서
```

### 📂 Root 파일 설명
- **`debug_balance.py`**: 잔고 조회 기능만 단독으로 테스트하는 스크립트
- **`debug_price.py`**: 현재가 조회 기능만 단독으로 테스트하는 스크립트
- **`debug_kis_api.py`**: KIS API 연동성 전반을 확인하는 종합 테스트 스크립트
- **`check_indices.py`**: 지수 관련 데이터 수신 여부를 확인하는 스크립트
- **`domestic_trading_test.py`**: 주문/거래 관련 로직 테스트

## 3. 설치 및 실행 가이드

### 3.1. 사전 준비
- **Python 3.9 이상** 설치
- **한국투자증권 Open API 신청** (앱키/시크릿 발급)
- `uv` 패키지 매니저 사용 권장

### 3.2. 환경 설정 (`kis_devlp.yaml`)
`kis_devlp.yaml` 파일을 열어 발급받은 정보를 입력하세요.

```yaml
my_app: "실전투자 앱키"
my_sec: "실전투자 시크릿"
paper_app: "모의투자 앱키"
paper_sec: "모의투자 시크릿"
my_acct_stock: "계좌번호 앞 8자리"
my_prod: "01" # 계좌번호 뒤 2자리
```

### 3.3. 서버 실행

```bash
# 1. 의존성 설치
uv sync

# 2. 서버 실행
PYTHONPATH=. uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
실행 후 브라우저에서 `http://localhost:8000`으로 접속하세요.

## 4. 문제 해결

- **API 호출 실패**: `kis_resources` 폴더로의 경로가 올바른지, `kis_devlp.yaml` 설정이 정확한지 확인하세요.
- **포트 충돌**: `run_server.md`를 참고하여 기존 프로세스를 종료하세요.
