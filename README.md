# 굿데이 강서출장마사지

서울 강서구 방문 건강관리(마사지) 예약 안내 정적 웹사이트입니다.
순수 HTML + 인라인 CSS/JS로 구성되어 **런타임 의존성이 0개**이며, 빌드 없이 그대로 배포할 수 있습니다.

## 구조

```
/                         홈
/about/                   굿데이 소개
/gangseo-gu/              강서 출장마사지 (강서 대표)
/gangseo-gu/area/         지역별 안내 (허브)
/gangseo-gu/<권역>-area/  5개 권역 페이지
/gangseo-gu/<동>-dong/    12개 동 페이지
/gangseo-gu/hours/ checklist/ safety/ faq/   강서 안내 개별 페이지(각 ~2000자)
/course/                  코스안내 (전체 코스 허브)
/course/fatigue/ aroma/ sports/ couple/ group/ price/ guide/  코스 개별 페이지(각 ~2000자)
/reservation/             예약안내
/guide/                   이용가이드
/reviews/                 고객후기
/customer/                고객센터
/privacy/ /terms/ /youth/ 정책 페이지
sitemap.xml robots.txt site.webmanifest  메타 파일
favicon.svg favicon.ico icon-*.png assets/og-cover.jpg  브랜드 이미지
```

지역 메뉴 구조는 권역 → 동 2단계로, 상단 메뉴에 동명을 과다 노출하지 않고
`지역별 안내` 드롭다운에서 권역으로 펼치도록 설계했습니다 (SEO 권고 반영).
화곡1~8동·방화1~3동 등 숫자 행정동은 별도 페이지를 만들지 않고 대표 동 본문에서
통합 안내해 도어웨이 페이지 리스크를 회피했습니다.

## 빌드 (선택)

배포에는 빌드가 필요 없습니다. 공통 헤더/푸터/SEO 블록을 일괄 수정할 때만 사용합니다.

```bash
python3 tools/build.py      # 모든 HTML + sitemap/robots/manifest + IndexNow 키 파일 생성
python3 tools/gen_icons.py  # 파비콘 / PWA 아이콘 / OG 이미지 생성 (Pillow 필요)
```

## 색인 즉시 통보 (IndexNow / Google / sitemap)

### 1) IndexNow — 빙·네이버·얀덱스 즉시 통보 (권장, 무료·무설정)
- 인증 키 파일은 빌드 시 자동 생성: `da13fc2a62ee6d42f722420f9353f628.txt`
  → 배포되면 `https://gangseo-massage.pages.dev/da13fc2a62ee6d42f722420f9353f628.txt` 로 노출
- 수동 제출:
  ```bash
  python3 tools/indexnow.py --all        # sitemap 전체
  python3 tools/indexnow.py --changed    # 직전 커밋 대비 바뀐 페이지만
  python3 tools/indexnow.py --all --dry-run   # 전송 없이 목록 확인
  ```
- **자동화**: `.github/workflows/indexnow.yml` 가 `main` 에 페이지/사이트맵이 바뀌어
  푸시될 때마다 변경 URL을 IndexNow로 통보합니다. (별도 시크릿 불필요)
- 네이버는 [서치어드바이저](https://searchadvisor.naver.com)에 사이트 등록 + IndexNow 사용 설정을 한 번 해두면 더 확실합니다.

### 2) Google Indexing API (선택, 보조)
- ⚠️ 공식적으로 **JobPosting / BroadcastEvent** 페이지만 지원합니다. 일반 페이지는
  무시될 수 있으므로, 구글은 **Search Console 등록 + sitemap 제출**이 정공법입니다.
- 사용하려면: Google Cloud에서 Indexing API 사용 설정 → 서비스계정 JSON 발급 →
  Search Console 속성에 서비스계정 이메일을 '소유자'로 추가 → `pip install google-auth`
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS=서비스계정.json
  python3 tools/google_indexing.py --all
  ```
- CI 자동화: 위 JSON 전체를 GitHub 시크릿 `GOOGLE_INDEXING_SA` 로 넣으면
  워크플로가 IndexNow와 함께 자동 호출합니다.

### 3) sitemap ping
- **Google·Bing의 sitemap ping 엔드포인트는 2023년 폐지**되었습니다(404). 더 이상
  유효하지 않으므로, 대신 **Search Console / Bing Webmaster에 sitemap을 한 번 제출**하면
  자동으로 주기적 재크롤되고, 즉시 통보는 위 IndexNow가 대체합니다.

## 배포 전 교체할 항목 (tools/build.py 상단 상수)

| 상수 | 현재값(placeholder) | 설명 |
|---|---|---|
| `BASE_URL` | `https://gangseo-massage.pages.dev` | 메인 도메인(Cloudflare Pages, 설정됨) |
| `PHONE_DISP` / `PHONE_TEL` | `0508-202-4743` | 예약 전화번호(설정됨) |
| `EMAIL` | `help@gangseo-massage.com` | 실제 이메일 |
| `COMPANY.biz_no` | `000-00-00000` | 사업자등록번호 |
| `COMPANY.sales_no` | `2026-서울강서-0000` | 통신판매업신고번호 |
| `COMPANY.ceo` / `privacy_officer` | `김도현` | 대표 / 개인정보보호책임자 |

값을 바꾼 뒤 `python3 tools/build.py`를 다시 실행하면 전 페이지에 반영됩니다.

## SEO / 적법성

- 페이지별 고유 `title` / `description` / `canonical`
- JSON-LD: Organization · WebSite · LocalBusiness · Service · BreadcrumbList · FAQPage · ItemList
- 모든 페이지 탐색경로(Breadcrumb) + 구조화 데이터
- 푸터에 사업자 정보 6필드 + 비의료·만 19세 이상 고지
- `content-visibility` / 시스템 폰트 / 인라인 자원으로 Core Web Vitals 최적화
