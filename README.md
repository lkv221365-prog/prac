# Samsung Smartphones QA Automation

삼성전자 스마트폰 PLP(전체 스마트폰) 페이지를 대상으로 Playwright 기반 크롤링과 pytest 자동화 테스트를 수행하는 프로젝트입니다.

## 사전 준비

```powershell
# 가상환경 생성 및 활성화
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

`.env` 파일에 Slack 테스트 결과 알림용 webhook을 설정할 수 있습니다.

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

## 프로젝트 구조

```
prac/
├── config.py          # 공통 URL, 경로, 타임아웃 상수
├── conftest.py        # pytest fixture 및 Slack 리포트
├── pytest.ini         # pytest 설정
├── crawlers/          # 데이터 수집 스크립트
├── utils/             # 필터 검증·공통 유틸
├── tests/             # Playwright / 데이터 pytest
└── data/              # 크롤링 결과 JSON
```

### `crawlers/`

| 모듈 | 설명 |
|---|---|
| `__init__.py` | 크롤러 공개 API re-export |
| `gnb_crawler.py` | GNB 메뉴 URL 추출 후 `data/gnb_urls.json` 저장 |
| `product_crawler.py` | 스마트폰 PLP 상품 정보 크롤링 후 `data/products.json` 저장 |

### `utils/`

| 모듈 | 설명 |
|---|---|
| `__init__.py` | 유틸·필터 실행 함수 re-export |
| `converters.py` | JSON 필드용 `as_int`, `as_float` 변환 |
| `filter_counts.py` | 용량 필터 bitmask 조합별 기대 상품 수 계산 |
| `filters_execute.py` | 필터 조합 테스트를 pytest 없이 CLI로 실행 |
| `utils.py` | lazy-load 스크롤, 더보기 버튼 클릭 등 Playwright 헬퍼 |

### `tests/`

| 모듈 | 설명 |
|---|---|
| `test_gnb.py` | `gnb_urls.json` URL 목록 접근·응답 검증 |
| `test_filters.py` | 타입/용량/가격 필터 단일 그룹 조합 검증 |
| `test_filters_multi.py` | 타입+가격+용량 복합 필터 시나리오 검증 |
| `test_data.py` | `products.json` 상품 코드·비즈니스 규칙 검증 |
| `test_card.py` | 상품 카드 색상/용량 옵션·비교하기 UI 검증 |
| `test_menu.py` | LNB 네비 링크 및 랜딩 페이지 타이틀 검증 |
| `test_tabs.py` | 갤럭시 S/Z/A 탭 및 액세서리 버튼 검증 |
| `test_tmp.py` | Slack/터미널 로그 확인용 의도적 실패 테스트 |

### `data/`

| 파일 | 설명 |
|---|---|
| `products.json` | `product_crawler`가 수집한 상품 목록 |
| `gnb_urls.json` | `gnb_crawler`가 수집한 GNB URL 목록 |

### 루트 파일

| 파일 | 설명 |
|---|---|
| `config.py` | `SMARTPHONES_URL`, `PRODUCTS_PATH`, 타임아웃 등 공유 설정 |
| `conftest.py` | 브라우저 fixture, 상품 parametrization, Slack 요약 리포트 |
| `pytest.ini` | 테스트 탐색 경로(`tests/`) 등 pytest 설정 |

## 실행 명령어

### 크롤러

```powershell
# GNB URL 수집 → data/gnb_urls.json
python -m crawlers.gnb_crawler

# 상품 정보 수집 → data/products.json
python -m crawlers.product_crawler
```

### 필터 조합 (pytest 없이)

```powershell
# 타입 필터만
python -m utils.filters_execute type

# 용량 필터
python -m utils.filters_execute memory

# 가격 필터
python -m utils.filters_execute price

# 전체 실행
python -m utils.filters_execute all --headed

# 브라우저 화면 표시
python -m utils.filters_execute type --headed
```

### pytest

```powershell
# 전체 테스트
pytest

# GNB URL 테스트만
pytest tests/test_gnb.py

# 특정 파일
pytest tests/test_filters.py
pytest tests/test_data.py

# 브라우저 UI 표시
pytest --headed

# Slack 리포트 비활성화
pytest --no-slack-report
```

### tmp.md 명령어

```powershell
# 실패했던 GNB URL만 재실행
pytest tests/test_gnb.py -k "galaxy-buds4_buy or galaxy-book6-series_buy or sec_shop or galaxy-z-fold7_buy or galaxy-tab-s11_buy" -v

# GNB URL 크롤링
python -m crawlers.gnb_crawler

# GNB 테스트
pytest tests/test_gnb.py
```
