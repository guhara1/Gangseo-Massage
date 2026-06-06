# 굿데이 강서출장마사지

서울 강서구 방문 건강관리(마사지) 예약 안내 정적 웹사이트입니다.
순수 HTML + 인라인 CSS/JS로 구성되어 **런타임 의존성이 0개**이며, 빌드 없이 그대로 배포할 수 있습니다.

## 구조

```
/                         홈
/about/                   굿데이 소개
/gangseo-gu/              강서출장마사지 (강서 대표)
/gangseo-gu/area/         지역별 안내 (허브)
/gangseo-gu/<권역>-area/  5개 권역 페이지
/gangseo-gu/<동>-dong/    12개 동 페이지
/course/                  코스안내
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
python3 tools/build.py      # 모든 HTML + sitemap/robots/manifest 생성
python3 tools/gen_icons.py  # 파비콘 / PWA 아이콘 / OG 이미지 생성 (Pillow 필요)
```

## 배포 전 교체할 항목 (tools/build.py 상단 상수)

| 상수 | 현재값(placeholder) | 설명 |
|---|---|---|
| `BASE_URL` | `https://www.gangseo-massage.com` | 실제 도메인 |
| `PHONE_DISP` / `PHONE_TEL` | `0507-1234-5678` | 실제 전화번호 |
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
