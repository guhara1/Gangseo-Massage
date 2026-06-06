# -*- coding: utf-8 -*-
"""
굿데이 강서출장마사지 — static site generator.

One-time generator that emits PURE static HTML (inline CSS/JS, zero runtime
dependencies). The published site needs no build step or framework; this script
only exists to keep the shared header/footer/SEO blocks consistent across pages.

Run:  python3 tools/build.py
Output: HTML files + sitemap.xml + robots.txt + site.webmanifest at repo root.
"""

import os
import json
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Brand / business constants  (replace placeholders before going live)
# ---------------------------------------------------------------------------
BASE_URL   = "https://www.gangseo-massage.com"   # TODO: 실제 도메인으로 교체
BRAND      = "굿데이 강서출장마사지"
BRAND_SHORT= "굿데이"
PHONE_DISP = "0507-1234-5678"                    # TODO: 실제 번호로 교체
PHONE_TEL  = "+8250712345678"                    # tel: 링크용
EMAIL      = "help@gangseo-massage.com"          # TODO: 실제 이메일로 교체
HOURS      = "연중무휴 · 24시간 상담"

COMPANY = {
    "name": "굿데이 헬스케어",
    "ceo": "김도현",
    "biz_no": "000-00-00000",            # TODO
    "addr": "서울특별시 강서구",
    "sales_no": "2026-서울강서-0000",    # TODO
    "privacy_officer": "김도현",
}

# ---------------------------------------------------------------------------
# Data model — 권역 / 동
# ---------------------------------------------------------------------------
REGIONS = [
    {
        "slug": "yeomchang-deungchon-area",
        "name": "염창·등촌권역",
        "summary": "한강과 9호선 라인을 따라 이어지는 주거·업무 혼합 권역입니다.",
        "dongs": [
            {"slug": "yeomchang-dong", "name": "염창동", "arrival": 28,
             "landmarks": "염창역(9호선), 한강공원, 강서한강자이 일대",
             "character": "한강 조망 아파트 단지가 밀집한 정주형 주거 권역"},
            {"slug": "deungchon-dong", "name": "등촌동", "arrival": 31,
             "landmarks": "등촌역(9호선), 강서구청, 등촌중앙시장 일대",
             "character": "행정·생활 인프라가 모인 강서 중심 생활권"},
        ],
    },
    {
        "slug": "hwagok-ujangsan-area",
        "name": "화곡·우장산권역",
        "summary": "강서구 최대 주거 밀집지로 검색 수요가 가장 큰 핵심 권역입니다.",
        "dongs": [
            {"slug": "hwagok-dong", "name": "화곡동", "arrival": 27,
             "landmarks": "화곡역(5호선), 까치산역, 화곡본동시장 일대",
             "character": "강서구에서 인구가 가장 많은 대표 주거 밀집 권역",
             "sub_note": "화곡본동, 화곡1동, 화곡2동, 화곡3동, 화곡4동, 화곡6동, 화곡8동 일대 "
                         "방문 가능 여부는 예약 시간과 위치에 따라 안내드립니다."},
            {"slug": "ujangsan-dong", "name": "우장산동", "arrival": 30,
             "landmarks": "우장산역(5호선), 우장산근린공원 일대",
             "character": "공원과 학군이 어우러진 조용한 주거 권역"},
        ],
    },
    {
        "slug": "gayang-magok-area",
        "name": "가양·마곡권역",
        "summary": "마곡 업무지구와 한강변 주거가 만나는 신·구 혼합 권역입니다.",
        "dongs": [
            {"slug": "gayang-dong", "name": "가양동", "arrival": 29,
             "landmarks": "가양역(9호선), 허준박물관, 가양대교 일대",
             "character": "한강과 대단지 아파트가 어우러진 주거 권역"},
            {"slug": "magok-dong", "name": "마곡동", "arrival": 26,
             "landmarks": "마곡나루역, 마곡역, 발산역, LG사이언스파크, 서울식물원 일대",
             "character": "기업·연구시설이 밀집한 강서 대표 업무·신주거 권역"},
        ],
    },
    {
        "slug": "balsan-area",
        "name": "발산권역",
        "summary": "발산역을 중심으로 생활권이 이어지는 업무·주거 혼합 권역입니다.",
        "dongs": [
            {"slug": "balsan-dong", "name": "발산동", "arrival": 28,
             "landmarks": "발산역(5호선), 강서구민회관 일대",
             "character": "마곡 업무지구와 인접한 교통 요지",
             "sub_note": "발산역 인근 방문은 발산권역 본문 기준으로 안내드리며, "
                         "내발산동·외발산동 생활권을 함께 포함합니다."},
            {"slug": "naebalsan-dong", "name": "내발산동", "arrival": 30,
             "landmarks": "내발산동 주거단지, 우장산 인근",
             "character": "주거와 학군이 안정된 정주형 권역"},
            {"slug": "oebalsan-dong", "name": "외발산동", "arrival": 33,
             "landmarks": "KBS스포츠월드, 수명산 인근",
             "character": "체육시설과 녹지가 인접한 외곽 생활권"},
        ],
    },
    {
        "slug": "gonghang-banghwa-area",
        "name": "공항·방화권역",
        "summary": "김포공항과 개화산을 끼고 생활권이 묶이는 서부 권역입니다.",
        "dongs": [
            {"slug": "gonghang-dong", "name": "공항동", "arrival": 32,
             "landmarks": "김포공항, 공항시장역 일대",
             "character": "공항 배후 생활권과 상업시설이 공존하는 권역"},
            {"slug": "banghwa-dong", "name": "방화동", "arrival": 34,
             "landmarks": "방화역(5호선), 방화근린공원, 개화산 일대",
             "character": "공원과 대단지 주거가 어우러진 서부 주거 권역",
             "sub_note": "방화1동, 방화2동, 방화3동 일대는 방화동 페이지에서 통합 안내드립니다."},
            {"slug": "gaehwa-dong", "name": "개화동", "arrival": 36,
             "landmarks": "개화산역, 개화산, 김포공항 인근",
             "character": "녹지 비중이 높은 강서 서쪽 끝 생활권"},
        ],
    },
]

# 코스
COURSES = [
    {"slug": "fatigue", "kicker": "RELAX · 피로 회복", "name": "피로 회복 관리",
     "desc": "전신의 긴장을 부드럽게 풀어주는 스웨디시 계열 기본 관리입니다.",
     "prices": [("60분", "70,000원"), ("90분", "100,000원"), ("120분", "130,000원")]},
    {"slug": "aroma", "kicker": "AROMA · 아로마", "name": "아로마 관리",
     "desc": "블렌딩 오일을 사용해 향과 함께 심신을 이완하는 관리입니다.",
     "prices": [("60분", "80,000원"), ("90분", "110,000원"), ("120분", "140,000원")], "best": True},
    {"slug": "sports", "kicker": "SPORTS · 스포츠", "name": "스포츠 관리",
     "desc": "운동 후 뭉친 근육과 컨디션 회복에 초점을 맞춘 관리입니다.",
     "prices": [("60분", "90,000원"), ("90분", "120,000원"), ("120분", "150,000원")]},
    {"slug": "couple", "kicker": "COUPLE · 커플/가족", "name": "커플/가족 관리",
     "desc": "두 분이 함께 같은 공간에서 동시에 받는 동반 관리입니다.",
     "prices": [("60분", "150,000원~"), ("90분", "200,000원~"), ("120분", "250,000원~")]},
    {"slug": "group", "kicker": "GROUP · 기업/단체", "name": "기업/단체 관리",
     "desc": "워크숍·행사 등 단체 인원을 위한 사전 협의형 방문 관리입니다.",
     "prices": [("협의", "별도 견적"), ("협의", "별도 견적"), ("협의", "별도 견적")]},
]

# 코스별 기본 요금 (시간 기준 메뉴 — 메인/모든 지역 페이지 공통)
TIME_PRICING = [
    {"name": "60분 코스", "price": "90,000", "dur": "60분", "desc": "기본 컨디션·릴랙스 케어"},
    {"name": "90분 코스", "price": "150,000", "dur": "90분", "desc": "아로마 포함 추천 구성", "best": True},
    {"name": "120분 코스", "price": "180,000", "dur": "120분", "desc": "전신 집중 프리미엄 케어"},
]

# ---------------------------------------------------------------------------
# Shared CSS  (design system from BLUEPRINT.md)
# ---------------------------------------------------------------------------
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0b0b0e;--surface:#13131a;--surface-2:#1a1a23;--line:rgba(255,255,255,.08);
  --text:#f3f3f5;--muted:#9a9aa3;--dim:#6c6c75;
  --gold:#d6b274;--rose:#e9b8a7;--copper:#c98a6b;
  --grad:linear-gradient(135deg,#f4d29c 0%,#e9b8a7 45%,#c98a6b 100%);
  --grad-soft:linear-gradient(135deg,rgba(244,210,156,.14),rgba(201,138,107,.06));
}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);line-height:1.65;letter-spacing:-.01em;
  font-family:"Pretendard","Apple SD Gothic Neo","Noto Sans KR",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  -webkit-font-smoothing:antialiased;overflow-x:hidden}
a{color:inherit;text-decoration:none}
img{max-width:100%;display:block}
.serif,.note-num,.step .n{font-family:"Cormorant Garamond","Noto Serif KR",Georgia,serif;font-weight:300;font-style:italic}
.grad{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.wrap{max-width:1240px;margin:0 auto;padding:0 24px}
section.block{padding:96px 0}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:11.5px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--gold);font-weight:700}
.pulse{width:7px;height:7px;border-radius:50%;background:var(--rose);box-shadow:0 0 0 0 rgba(233,184,167,.6);animation:pulse 2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(233,184,167,.55)}70%{box-shadow:0 0 0 9px rgba(233,184,167,0)}100%{box-shadow:0 0 0 0 rgba(233,184,167,0)}}
h2.sec{font-size:clamp(28px,4vw,46px);letter-spacing:-.03em;font-weight:800;margin:14px 0 10px}
.sec-lead{color:var(--muted);max-width:660px;font-size:15px}
/* header */
header{position:sticky;top:0;z-index:60;backdrop-filter:blur(14px);
  background:rgba(11,11,14,.78);border-bottom:1px solid var(--line)}
.nav{max-width:1240px;margin:0 auto;padding:14px 24px;display:flex;align-items:center;gap:18px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;letter-spacing:-.02em}
.brand .mark{width:34px;height:34px;border-radius:10px;background:var(--grad);display:grid;place-items:center;
  color:#1a1208;font-weight:800;font-family:"Cormorant Garamond",serif;font-style:italic;font-size:20px}
.brand small{display:block;font-size:10.5px;letter-spacing:.16em;color:var(--gold);font-weight:700}
.menu{list-style:none;display:flex;align-items:center;gap:4px;margin-left:auto}
.menu>li{position:relative}
.menu>li>a{display:block;padding:10px 13px;font-size:14px;color:var(--text);border-radius:9px;font-weight:600}
.menu>li>a:hover{background:rgba(255,255,255,.05)}
.menu>li>a.active{color:var(--gold)}
.submenu{position:absolute;top:calc(100% + 6px);left:0;min-width:212px;list-style:none;padding:8px;
  background:linear-gradient(160deg,var(--surface),var(--surface-2));border:1px solid var(--line);
  border-radius:14px;box-shadow:0 20px 48px rgba(0,0,0,.45);opacity:0;visibility:hidden;transform:translateY(6px);
  transition:.22s;z-index:70}
.menu>li:hover>.submenu,.menu>li:focus-within>.submenu{opacity:1;visibility:visible;transform:none}
.submenu li a{display:block;padding:9px 12px;font-size:13.5px;color:var(--muted);border-radius:9px}
.submenu li a:hover{background:rgba(255,255,255,.05);color:var(--text)}
.cta-pill{margin-left:6px;padding:11px 18px!important;background:var(--grad);color:#1a1208!important;
  border-radius:999px;font-weight:800!important}
.toggle{display:none;margin-left:auto;background:none;border:1px solid var(--line);color:var(--text);
  font-size:20px;width:44px;height:44px;border-radius:11px;cursor:pointer}
/* hero */
.hero{position:relative;overflow:hidden;border-bottom:1px solid var(--line)}
.hero::before{content:"";position:absolute;inset:0;z-index:0;
  background:radial-gradient(60% 70% at 80% 10%,rgba(233,184,167,.16),transparent 60%),
             radial-gradient(50% 60% at 10% 90%,rgba(214,178,116,.12),transparent 60%),
             radial-gradient(40% 50% at 50% 50%,rgba(201,138,107,.08),transparent 70%)}
.hero-inner{position:relative;z-index:1;display:grid;grid-template-columns:1.12fr .88fr;gap:48px;
  align-items:center;max-width:1240px;margin:0 auto;padding:88px 24px}
.hero h1{font-size:clamp(36px,6vw,70px);font-weight:800;letter-spacing:-.038em;line-height:1.06;margin:18px 0}
.hero .lead{color:var(--muted);font-size:16px;max-width:520px;margin-bottom:26px}
.actions{display:flex;gap:12px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:8px;padding:14px 22px;border-radius:12px;font-weight:700;
  font-size:14.5px;transition:.25s;border:1px solid transparent}
.btn-primary{background:var(--grad);color:#1a1208}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 14px 34px rgba(201,138,107,.35)}
.btn-ghost{border-color:var(--line);color:var(--text)}
.btn-ghost:hover{border-color:rgba(244,210,156,.4);transform:translateY(-2px)}
.trust{margin-top:24px;display:flex;flex-wrap:wrap;gap:8px 18px;color:var(--muted);font-size:13px}
.trust b{color:var(--text)}
.hero-visual{position:relative}
.glass{position:relative;z-index:2;border-radius:20px;padding:26px;
  background:linear-gradient(160deg,rgba(255,255,255,.06),rgba(255,255,255,.02));
  border:1px solid rgba(255,255,255,.12);backdrop-filter:blur(20px);transform:rotate(1.5deg)}
.glass h3{font-size:13px;color:var(--gold);letter-spacing:.04em;margin-bottom:14px}
.glass h3 b{display:block;font-size:21px;color:var(--text);letter-spacing:-.02em;margin-top:4px}
.book-row{display:flex;justify-content:space-between;padding:11px 0;border-top:1px solid var(--line);font-size:14px}
.book-row span:first-child{color:var(--muted)}
.bk{display:block;text-align:center;margin-top:16px;padding:13px;border-radius:12px;background:var(--grad);color:#1a1208;font-weight:800}
.floating{position:absolute;z-index:3;padding:11px 14px;border-radius:12px;font-size:12px;font-weight:600;
  background:linear-gradient(160deg,var(--surface),var(--surface-2));border:1px solid var(--line);
  box-shadow:0 14px 34px rgba(0,0,0,.4)}
.fl-1{top:-18px;left:-14px;transform:rotate(-4deg)}
.fl-2{bottom:-16px;right:-10px;transform:rotate(3deg)}
.fl-1 .dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#6fe3a1;margin-right:6px}
/* marquee */
.marquee{overflow:hidden;border-bottom:1px solid var(--line);background:var(--surface)}
.marquee-track{display:flex;gap:0;white-space:nowrap;width:max-content;animation:scroll 34s linear infinite}
.marquee-track span{padding:14px 26px;color:var(--muted);font-size:13px;letter-spacing:.04em}
.marquee-track span::after{content:"·";margin-left:26px;color:var(--dim)}
@keyframes scroll{to{transform:translateX(-50%)}}
/* cards grid */
.grid{display:grid;gap:16px}
.g4{grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.g2{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.card{padding:24px;border-radius:16px;border:1px solid var(--line);
  background:linear-gradient(135deg,var(--surface),var(--surface-2));transition:.3s}
.card:hover{transform:translateY(-4px);border-color:rgba(244,210,156,.28);box-shadow:0 18px 40px rgba(0,0,0,.3)}
.card .k{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);font-weight:700}
.card h3{margin:10px 0 8px;font-size:19px;font-weight:800}
.card p{color:var(--muted);font-size:14px}
.card .more{display:inline-block;margin-top:14px;color:var(--rose);font-size:13.5px;font-weight:700}
.card:hover .more{transform:translateX(4px)}
/* note card */
.note-card{display:flex;gap:22px;padding:26px 28px;border-radius:18px;position:relative;overflow:hidden;
  background:linear-gradient(135deg,var(--surface),var(--surface-2));border:1px solid var(--line);transition:.3s}
.note-card::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--grad);opacity:0;transition:.3s}
.note-card:hover::before{opacity:1}
.note-card:hover{transform:translateY(-2px);box-shadow:0 18px 44px rgba(0,0,0,.32);border-color:rgba(244,210,156,.28)}
.note-num{font-size:44px;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent;flex-shrink:0;line-height:1}
.note-title{font-size:18px;font-weight:800;margin-bottom:10px}
.note-text{max-width:660px}
.note-text p{margin:0 0 9px;color:#c8c8d0;font-size:14.5px;line-height:1.78}
.note-stack{display:flex;flex-direction:column;gap:14px}
/* chips */
.chips{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.chip{padding:9px 14px;border-radius:999px;border:1px solid var(--line);background:var(--surface);
  font-size:12.5px;color:var(--muted)}
.chip b{color:var(--gold)}
/* price */
.price-card{padding:24px;border-radius:16px;border:1px solid var(--line);position:relative;overflow:hidden;
  background:linear-gradient(135deg,var(--surface),var(--surface-2));transition:.3s}
.price-card::after{content:"";position:absolute;left:0;right:0;top:0;height:2px;background:var(--grad);opacity:.5}
.price-card:hover{transform:translateY(-3px);border-color:rgba(244,210,156,.3)}
.price-card.best{border-color:rgba(244,210,156,.45)}
.best-badge{position:absolute;top:14px;right:14px;font-size:10.5px;font-weight:800;letter-spacing:.1em;
  padding:5px 10px;border-radius:999px;background:var(--grad);color:#1a1208}
.price-card .k{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);font-weight:700}
.price-card h3{margin:8px 0 6px;font-size:20px;font-weight:800}
.price-card>p{color:var(--muted);font-size:13.5px;margin-bottom:14px}
.time-rows>div{display:flex;justify-content:space-between;padding:9px 0;border-top:1px solid var(--line);font-size:14px}
.time-rows span:last-child{font-weight:700}
/* 코스별 기본 요금 메뉴 */
.pmenu{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:28px}
.pmenu-card{position:relative;text-align:center;padding:36px 24px 26px;border-radius:18px;
  background:linear-gradient(135deg,var(--surface),var(--surface-2));border:1px solid var(--line);transition:.3s}
.pmenu-card:hover{transform:translateY(-4px);border-color:rgba(244,210,156,.3);box-shadow:0 18px 42px rgba(0,0,0,.32)}
.pmenu-card.best{border-color:rgba(244,210,156,.5);box-shadow:0 16px 42px rgba(201,138,107,.2)}
.pmenu-name{font-weight:800;font-size:17px;margin-bottom:16px}
.pmenu-price{font-size:clamp(30px,4vw,40px);font-weight:800;letter-spacing:-.035em;line-height:1}
.pmenu-price span{font-size:15px;font-weight:600;color:var(--muted);margin-left:3px;letter-spacing:0}
.pmenu-dur{color:var(--gold);font-size:13px;font-weight:700;margin-top:10px}
.pmenu-desc{color:var(--muted);font-size:13.5px;margin:8px 0 22px}
.pmenu-btn{display:block;padding:13px;border-radius:11px;border:1px solid var(--line);font-weight:700;font-size:14px;transition:.25s}
.pmenu-btn:hover{border-color:rgba(244,210,156,.5);transform:translateY(-1px)}
.pmenu-card.best .pmenu-btn{background:var(--grad);color:#1a1208;border-color:transparent}
.pmenu-badge{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--grad);color:#1a1208;
  font-size:11.5px;font-weight:800;padding:5px 15px;border-radius:999px;box-shadow:0 6px 16px rgba(201,138,107,.35)}
.pmenu-note{margin-top:20px;color:var(--muted);font-size:13px}
.pmenu-note a{color:var(--gold);font-weight:700;white-space:nowrap}
@media(max-width:760px){.pmenu{grid-template-columns:1fr}}
/* faq */
details{border:1px solid var(--line);border-radius:14px;padding:0;margin-bottom:12px;
  background:linear-gradient(135deg,var(--surface),var(--surface-2));overflow:hidden}
summary{list-style:none;cursor:pointer;padding:18px 22px;font-weight:700;font-size:15px;
  display:flex;justify-content:space-between;align-items:center;gap:14px}
summary::-webkit-details-marker{display:none}
summary span{color:var(--gold);font-size:22px;transition:.25s;flex-shrink:0}
details[open] summary span{transform:rotate(45deg)}
details>div{padding:0 22px 20px;color:var(--muted);font-size:14.5px;line-height:1.78}
/* breadcrumb */
.crumb{font-size:12.5px;color:var(--dim);padding:18px 0}
.crumb a{color:var(--muted)}
.crumb a:hover{color:var(--gold)}
.crumb b{color:var(--text)}
/* review */
.review{padding:22px;border-radius:16px;border:1px solid var(--line);
  background:linear-gradient(135deg,var(--surface),var(--surface-2))}
.review .stars{color:var(--gold);font-size:13px;letter-spacing:2px}
.review p{margin:10px 0;font-size:14px;color:#c8c8d0;line-height:1.7}
.review .who{font-size:12.5px;color:var(--muted)}
/* cta band */
.cta-band{position:relative;overflow:hidden;text-align:center;padding:88px 24px;border-top:1px solid var(--line)}
.cta-band::before{content:"";position:absolute;inset:0;background:radial-gradient(50% 80% at 50% 0%,rgba(233,184,167,.16),transparent 60%)}
.cta-band>div{position:relative}
.cta-band h2{font-size:clamp(26px,4vw,42px);font-weight:800;letter-spacing:-.03em}
.cta-band p{color:var(--muted);margin:12px 0 24px}
/* footer */
.site-footer{border-top:1px solid var(--line);background:var(--surface);padding:64px 0 36px;font-size:13.5px}
.footer-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:30px}
.footer-grid h4{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);margin-bottom:14px}
.footer-grid a{display:block;color:var(--muted);padding:5px 0}
.footer-grid a:hover{color:var(--text)}
.footer-brand b{font-size:17px}
.footer-brand p{color:var(--muted);margin-top:10px;max-width:280px;line-height:1.7}
.footer-ops{margin:34px 0;padding:22px;border-radius:14px;background:var(--grad-soft);
  border:1px solid var(--line);display:flex;flex-wrap:wrap;gap:14px 40px}
.footer-ops div b{color:var(--gold);display:block;font-size:11px;letter-spacing:.12em;margin-bottom:4px}
.company-info{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;color:var(--dim);font-size:12.5px;
  padding-top:24px;border-top:1px solid var(--line)}
.company-info b{color:var(--muted)}
.footer-policies{display:flex;flex-wrap:wrap;gap:8px 18px;margin:22px 0 14px}
.footer-policies a{color:var(--muted);font-size:12.5px}
.footer-bottom{color:var(--dim);font-size:12px;line-height:1.7;border-top:1px solid var(--line);padding-top:18px}
.legal-note{margin-top:8px;color:var(--dim)}
/* reveal */
.reveal{opacity:0;transform:translateY(20px);transition:.8s}
.reveal.in{opacity:1;transform:none}
/* perf */
#region,#process,#reviews,#about,#faq,.cta-band,.site-footer{content-visibility:auto;contain-intrinsic-size:auto 700px}
.card,.note-card,.review,.price-card{contain:layout style}
@media(hover:none){.glass,.floating{backdrop-filter:none}}
@media(prefers-reduced-motion:reduce){.marquee-track,.pulse{animation:none}.reveal{opacity:1;transform:none}}
@media(max-width:1100px){
  .toggle{display:block}
  .menu{position:fixed;inset:64px 0 auto 0;flex-direction:column;align-items:stretch;gap:2px;margin:0;
    padding:14px;background:var(--bg);border-bottom:1px solid var(--line);max-height:calc(100vh - 64px);
    overflow:auto;transform:translateY(-12px);opacity:0;visibility:hidden;transition:.25s}
  .menu.open{transform:none;opacity:1;visibility:visible}
  .menu>li>a{padding:13px 12px}
  .submenu{position:static;opacity:1;visibility:visible;transform:none;box-shadow:none;background:transparent;
    border:none;padding:0 0 6px 12px;min-width:0}
  .cta-pill{text-align:center}
  .hero-inner{grid-template-columns:1fr;gap:36px}
  .hero-visual{max-width:420px}
  .footer-grid{grid-template-columns:1fr 1fr}
  .company-info{grid-template-columns:1fr 1fr}
}
@media(max-width:560px){
  .footer-grid,.company-info{grid-template-columns:1fr}
  .note-card{flex-direction:column;gap:12px}
  .hero-inner{padding:56px 24px}
}
"""

# ---------------------------------------------------------------------------
# Navigation model  (top menu + dropdowns)
# ---------------------------------------------------------------------------
def menu_html(active):
    def li(key, href, label, sub=None, cta=False):
        cls = ' class="active"' if active == key else ""
        pop = ' aria-haspopup="true"' if sub else ""
        a = f'<a href="{href}"{cls}{pop}>{label}</a>'
        if cta:
            a = f'<a class="cta-pill" href="tel:{PHONE_TEL}">24시 예약</a>'
        sub_html = ""
        if sub:
            items = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in sub)
            sub_html = f'<ul class="submenu">{items}</ul>'
        return f"<li>{a}{sub_html}</li>"

    region_sub = [(f"/gangseo-gu/{r['slug']}/", r["name"]) for r in REGIONS]
    items = [
        li("home", "/", "홈"),
        li("about", "/about/", "굿데이 소개", [
            ("/about/#greeting", "굿데이 인사말"),
            ("/about/#standards", "서비스 운영 기준"),
            ("/about/#safety", "위생 및 안전 관리"),
            ("/about/#faq", "자주 묻는 질문"),
        ]),
        li("gangseo", "/gangseo-gu/", "강서출장마사지", [
            ("/gangseo-gu/#intro", "강서구 출장마사지 안내"),
            ("/gangseo-gu/#area", "출장 가능 지역"),
            ("/gangseo-gu/#hours", "예약 가능 시간"),
            ("/gangseo-gu/#check", "관리 전 확인사항"),
            ("/gangseo-gu/#safety", "위생 및 안전 안내"),
        ]),
        li("area", "/gangseo-gu/area/", "지역별 안내", region_sub),
        li("course", "/course/", "코스안내", [
            ("/course/#all", "전체 코스"),
            ("/course/#fatigue", "피로 회복 관리"),
            ("/course/#aroma", "아로마 관리"),
            ("/course/#sports", "스포츠 관리"),
            ("/course/#couple", "커플/가족 관리"),
            ("/course/#group", "기업/단체 관리"),
            ("/course/#price", "가격 안내"),
            ("/course/#guide", "코스 선택 가이드"),
        ]),
        li("reservation", "/reservation/", "예약안내"),
        li("guide", "/guide/", "이용가이드"),
        li("reviews", "/reviews/", "고객후기"),
        li("customer", "/customer/", "고객센터"),
        li("cta", "#", "", cta=True),
    ]
    return (
        '<header><nav class="nav" aria-label="주 메뉴">'
        '<a class="brand" href="/" aria-label="굿데이 강서출장마사지 홈">'
        '<span class="mark">G</span><span>굿데이<small>강서출장마사지</small></span></a>'
        '<button class="toggle" aria-expanded="false" aria-controls="primary-menu" aria-label="메뉴 열기">☰</button>'
        f'<ul id="primary-menu" class="menu">{"".join(items)}</ul>'
        "</nav></header>"
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
def footer_html():
    region_links = "".join(
        f'<a href="/gangseo-gu/{r["slug"]}/">{r["name"]}</a>' for r in REGIONS
    )
    course_links = "".join(
        f'<a href="/course/#{c["slug"]}">{c["name"]}</a>' for c in COURSES
    )
    return f"""<footer class="site-footer"><div class="wrap">
<div class="footer-grid">
  <div class="footer-brand">
    <b class="grad">{BRAND}</b>
    <p>서울 강서구 염창·등촌·화곡·우장산·가양·마곡·발산·공항·방화 일대 방문 건강관리 서비스 예약 안내입니다.</p>
  </div>
  <div><h4>지역별 안내</h4>{region_links}<a href="/gangseo-gu/area/">전체 지역 보기</a></div>
  <div><h4>코스</h4>{course_links}</div>
  <div><h4>안내</h4>
    <a href="/reservation/">예약안내</a><a href="/guide/">이용가이드</a>
    <a href="/reviews/">고객후기</a><a href="/customer/">고객센터</a></div>
</div>
<div class="footer-ops">
  <div><b>운영 시간</b>{HOURS}</div>
  <div><b>전화 상담</b><a href="tel:{PHONE_TEL}">{PHONE_DISP}</a></div>
  <div><b>이메일</b><a href="mailto:{EMAIL}">{EMAIL}</a></div>
</div>
<div class="company-info">
  <div><b>상호</b> {COMPANY['name']}</div>
  <div><b>대표</b> {COMPANY['ceo']}</div>
  <div><b>사업자등록번호</b> {COMPANY['biz_no']}</div>
  <div><b>주소</b> {COMPANY['addr']}</div>
  <div><b>통신판매업신고</b> {COMPANY['sales_no']}</div>
  <div><b>개인정보보호책임자</b> {COMPANY['privacy_officer']}</div>
</div>
<div class="footer-policies">
  <a href="/customer/#notice">공지사항</a><a href="/customer/#qna">자주 묻는 질문</a>
  <a href="/customer/#inquiry">1:1 문의</a><a href="/privacy/">개인정보처리방침</a>
  <a href="/terms/">이용약관</a><a href="/youth/">청소년보호정책</a>
</div>
<div class="footer-bottom">
  © 2026 {COMPANY['name']}. All rights reserved.
  <div class="legal-note">본 서비스는 의료 행위가 아닌 건강관리(이완·휴식) 목적의 방문 관리 서비스이며, 만 19세 이상 성인을 대상으로 합니다. 불법·퇴폐 행위는 일절 제공하지 않습니다.</div>
</div>
</div></footer>"""

# ---------------------------------------------------------------------------
# Shared JS  (idle-loaded)
# ---------------------------------------------------------------------------
JS = """
(function(){
  var t=document.querySelector('.toggle'),m=document.getElementById('primary-menu');
  if(t&&m){t.addEventListener('click',function(){
    var o=m.classList.toggle('open');t.setAttribute('aria-expanded',o);});}
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&m){m.classList.remove('open');}});
  function idle(fn){if('requestIdleCallback'in window){requestIdleCallback(fn,{timeout:1500});}else{setTimeout(fn,1);}}
  idle(function(){
    if(!('IntersectionObserver'in window)){document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('in');});return;}
    var io=new IntersectionObserver(function(es){es.forEach(function(e){
      if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.12,rootMargin:'80px'});
    document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});
  });
})();
"""

# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------
def page(path, title, desc, active, body, jsonld=None, og_type="website"):
    canonical = BASE_URL + path
    ld = ""
    if jsonld:
        if isinstance(jsonld, list):
            blocks = jsonld
        else:
            blocks = [jsonld]
        ld = "".join(
            '<script type="application/ld+json">'
            + json.dumps(b, ensure_ascii=False, separators=(",", ":"))
            + "</script>"
            for b in blocks
        )
    og_img = BASE_URL + "/assets/og-cover.jpg"
    html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0b0b0e">
<meta name="format-detection" content="telephone=no">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<meta name="googlebot" content="index,follow">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="{COMPANY['name']} 운영팀">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="ko-KR" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="ko_KR">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_img}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<style>{CSS}</style>
{ld}
</head>
<body>
{menu_html(active)}
{body}
{footer_html()}
<script>{JS}</script>
</body>
</html>"""
    return html

# ---------------------------------------------------------------------------
# Reusable body builders
# ---------------------------------------------------------------------------
def breadcrumb(items):
    # items: list of (href or None, label)
    parts = []
    for href, label in items:
        if href:
            parts.append(f'<a href="{href}">{label}</a>')
        else:
            parts.append(f"<b>{label}</b>")
    return f'<div class="wrap"><nav class="crumb" aria-label="탐색경로">{" › ".join(parts)}</nav></div>'

def breadcrumb_ld(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": label,
             "item": BASE_URL + href}
            for i, (href, label) in enumerate(items) if href
        ] + [
            {"@type": "ListItem", "position": len(items), "name": items[-1][1]}
        ][:0],  # last handled below
    }

def bc_ld(trail):
    # trail: list of (path, name); last is current page
    el = []
    for i, (p, n) in enumerate(trail):
        item = {"@type": "ListItem", "position": i + 1, "name": n}
        if p:
            item["item"] = BASE_URL + p
        el.append(item)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": el}

def faq_block(qas, heading="자주 묻는 질문"):
    rows = "".join(
        f"<details><summary>{q}<span>+</span></summary><div>{a}</div></details>"
        for q, a in qas
    )
    return f"""<section class="block" id="faq"><div class="wrap">
<span class="eyebrow"><span class="pulse"></span>FAQ</span>
<h2 class="sec">{heading}</h2>
<div style="margin-top:26px;max-width:820px">{rows}</div>
</div></section>"""

def faq_ld(qas):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in qas
        ],
    }

def notes_block(eyebrow, heading, lead, notes, _id="about"):
    cards = "".join(
        f'<div class="note-card reveal"><div class="note-num">{n:02d}</div>'
        f'<div class="note-content"><h3 class="note-title">{t}</h3>'
        f'<div class="note-text">{"".join(f"<p>{p}</p>" for p in ps)}</div></div></div>'
        for n, (t, ps) in enumerate(notes, 1)
    )
    return f"""<section class="block" id="{_id}"><div class="wrap">
<span class="eyebrow"><span class="pulse"></span>{eyebrow}</span>
<h2 class="sec">{heading}</h2>
<p class="sec-lead">{lead}</p>
<div class="note-stack" style="margin-top:30px">{cards}</div>
</div></section>"""

def price_grid(courses):
    cards = ""
    for c in courses:
        best = " best" if c.get("best") else ""
        badge = '<span class="best-badge">BEST</span>' if c.get("best") else ""
        rows = "".join(f"<div><span>{t}</span><span>{p}</span></div>" for t, p in c["prices"])
        cards += (
            f'<div class="price-card{best}" id="{c["slug"]}">{badge}'
            f'<div class="k">{c["kicker"]}</div><h3>{c["name"]}</h3>'
            f'<p>{c["desc"]}</p><div class="time-rows">{rows}</div></div>'
        )
    return f'<div class="grid g3">{cards}</div>'

def price_menu_block(anchor="pricing-menu"):
    """코스별 기본 요금 (60·90·120분) — 메인/모든 지역 페이지 공통 블록."""
    cards = ""
    for p in TIME_PRICING:
        best = " best" if p.get("best") else ""
        badge = '<span class="pmenu-badge">추천</span>' if p.get("best") else ""
        cards += (
            f'<div class="pmenu-card{best}">{badge}'
            f'<div class="pmenu-name">{p["name"]}</div>'
            f'<div class="pmenu-price">{p["price"]}<span>원</span></div>'
            f'<div class="pmenu-dur">{p["dur"]}</div>'
            f'<div class="pmenu-desc">{p["desc"]}</div>'
            f'<a class="pmenu-btn" href="tel:{PHONE_TEL}">예약 문의</a></div>'
        )
    return (
        f'<section class="block" id="{anchor}"><div class="wrap">'
        f'<span class="eyebrow"><span class="pulse"></span>요금 안내</span>'
        f'<h2 class="sec">코스별 기본 요금</h2>'
        f'<p class="sec-lead">60·90·120분 코스별 기본 요금입니다. 숨겨진 추가 비용 없이 투명하게 안내합니다.</p>'
        f'<div class="pmenu">{cards}</div>'
        f'<p class="pmenu-note">지역·예약 시간대·이동 거리에 따라 상담 시 최종 확인됩니다. '
        f'<a href="/course/">상세 요금 안내 보기 →</a></p>'
        f'</div></section>'
    )

def offer_ld():
    """코스별 기본 요금 구조화 데이터(Offer)."""
    return {
        "@context": "https://schema.org", "@type": "OfferCatalog",
        "name": "코스별 기본 요금",
        "itemListElement": [
            {"@type": "Offer", "name": p["name"],
             "price": p["price"].replace(",", ""), "priceCurrency": "KRW",
             "description": p["desc"], "url": BASE_URL + "/course/"}
            for p in TIME_PRICING
        ],
    }

def cta_band(title="오늘 밤, 가까운 곳에서 휴식을 예약하세요", sub=None):
    sub = sub or f"{HOURS} · 전화 한 통으로 방문 일정과 코스를 안내드립니다."
    return f"""<section class="cta-band"><div>
<span class="eyebrow"><span class="pulse"></span>RESERVE</span>
<h2>{title}</h2><p>{sub}</p>
<div class="actions" style="justify-content:center">
<a class="btn btn-primary" href="tel:{PHONE_TEL}">{PHONE_DISP} 전화하기 →</a>
<a class="btn btn-ghost" href="/reservation/">예약 안내 보기</a>
</div></div></section>"""

# ---------------------------------------------------------------------------
# JSON-LD: org / localbusiness / website
# ---------------------------------------------------------------------------
def org_ld():
    return {
        "@context": "https://schema.org", "@type": "Organization",
        "name": BRAND, "legalName": COMPANY["name"], "url": BASE_URL + "/",
        "email": EMAIL, "telephone": PHONE_DISP,
        "address": {"@type": "PostalAddress", "addressLocality": "강서구",
                    "addressRegion": "서울특별시", "addressCountry": "KR"},
    }

def website_ld():
    return {
        "@context": "https://schema.org", "@type": "WebSite",
        "name": BRAND, "url": BASE_URL + "/",
        "potentialAction": {"@type": "SearchAction",
            "target": BASE_URL + "/?q={search_term_string}",
            "query-input": "required name=search_term_string"},
    }

def localbiz_ld(name=None, area="서울특별시 강서구", path="/"):
    return {
        "@context": "https://schema.org",
        "@type": "HealthAndBeautyBusiness",
        "name": name or BRAND, "url": BASE_URL + path,
        "telephone": PHONE_DISP, "email": EMAIL, "priceRange": "₩₩",
        "areaServed": {"@type": "AdministrativeArea", "name": area},
        "address": {"@type": "PostalAddress", "addressLocality": "강서구",
                    "addressRegion": "서울특별시", "addressCountry": "KR"},
        "openingHoursSpecification": {"@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
            "opens": "00:00", "closes": "23:59"},
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.9",
            "reviewCount": "1280", "bestRating": "5"},
    }

def service_ld(name, desc, path):
    return {
        "@context": "https://schema.org", "@type": "Service",
        "name": name, "description": desc, "serviceType": "방문 건강관리(마사지) 서비스",
        "provider": {"@type": "Organization", "name": BRAND, "url": BASE_URL + "/"},
        "areaServed": {"@type": "AdministrativeArea", "name": "서울특별시 강서구"},
        "url": BASE_URL + path,
    }

# ===========================================================================
# PAGE BUILDERS
# ===========================================================================
def write(path, html):
    if path == "/":
        out = os.path.join(ROOT, "index.html")
    else:
        d = os.path.join(ROOT, path.strip("/"))
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

# ---- Home ----------------------------------------------------------------
def build_home():
    services = "".join(
        f'<a class="card reveal" href="/course/#{c["slug"]}"><div class="k">{c["kicker"]}</div>'
        f'<h3>{c["name"]}</h3><p>{c["desc"]}</p><span class="more">자세히 →</span></a>'
        for c in COURSES[:4]
    )
    regions = "".join(
        f'<a class="card reveal" href="/gangseo-gu/{r["slug"]}/"><div class="k">AREA</div>'
        f'<h3>{r["name"]}</h3><p>{r["summary"]}</p><span class="more">권역 보기 →</span></a>'
        for r in REGIONS
    )
    steps = [
        ("전화 또는 문의", "원하시는 지역·시간·코스를 말씀해 주세요."),
        ("일정 확정", "디스패처가 방문 가능 시간을 확정해 드립니다."),
        ("관리사 방문", "약속된 시간에 맞춰 관리사가 방문합니다."),
        ("관리 후 정리", "관리 종료 후 현장을 정돈하고 마무리합니다."),
    ]
    steps_html = "".join(
        f'<div class="card reveal"><div class="k step"><span class="n serif">{i:02d}</span></div>'
        f'<h3>{t}</h3><p>{d}</p></div>'
        for i, (t, d) in enumerate(steps, 1)
    )
    reviews = [
        ("화곡동 · 30대", "늦은 시간에 연락했는데 도착 시간을 정확히 안내해 주셔서 좋았습니다."),
        ("마곡동 · 40대", "아로마 관리 후 컨디션이 한결 가벼워졌어요. 응대가 정중했습니다."),
        ("염창동 · 30대", "예약부터 마무리까지 깔끔했고 위생 안내가 꼼꼼했습니다."),
    ]
    reviews_html = "".join(
        f'<div class="review reveal"><div class="stars">★★★★★</div><p>“{q}”</p>'
        f'<div class="who">{w}</div></div>' for w, q in reviews
    )
    marquee_items = ["연중무휴 24시간 상담", "서울 강서구 전 지역", "당일 예약 가능",
                     "여성 관리사 방문", "위생·안전 관리", "정찰 요금 안내"]
    marquee = "".join(f"<span>{x}</span>" for x in marquee_items * 2)

    about_notes = [
        ("WHO · 누가 운영하나요",
         ["굿데이 강서출장마사지는 서울 강서구 전역을 담당하는 방문 건강관리 예약 운영팀입니다.",
          "본사 디스패처가 예약 접수부터 관리사 배차까지 직접 관리합니다."]),
        ("HOW · 어떻게 진행되나요",
         ["전화 상담으로 지역·시간·코스를 확인한 뒤 방문 가능 시간을 확정합니다.",
          "관리사는 약속된 시간에 맞춰 고객이 계신 장소로 방문합니다."]),
        ("WHY · 무엇을 약속하나요",
         ["정찰 요금과 사전 안내를 원칙으로 합니다.",
          "위생·안전 가이드라인을 준수하며 정중한 응대를 약속드립니다."]),
    ]
    body = f"""
<section class="hero"><div class="hero-inner">
  <div class="hero-copy">
    <span class="eyebrow"><span class="pulse"></span>SEOUL · GANGSEO-GU 24H</span>
    <h1>강서구 어디든,<br>도착하는 <span class="grad">최상의</span><br><span class="serif">휴식 한 시간.</span></h1>
    <p class="lead">염창·화곡·마곡·발산·방화까지 — 서울 강서구 전 지역 방문 건강관리 예약을 연중무휴로 안내드립니다.</p>
    <div class="actions">
      <a class="btn btn-primary" href="tel:{PHONE_TEL}">지금 예약하기 →</a>
      <a class="btn btn-ghost" href="/gangseo-gu/area/">지역별 안내</a>
    </div>
    <div class="trust">
      <span>★★★★★ <b>4.9</b> · 후기 1,280+</span><span>·</span>
      <span><b>{HOURS}</b></span><span>·</span><span>평균 도착 <b>30분</b></span>
    </div>
  </div>
  <div class="hero-visual">
    <div class="floating fl-1"><span class="dot"></span>LIVE · 방금 마곡동 예약</div>
    <div class="glass">
      <h3>SIGNATURE<b>아로마 딥 릴렉스</b></h3>
      <div class="book-row"><span>지역</span><span>강서구 전 지역</span></div>
      <div class="book-row"><span>코스</span><span>아로마 90분</span></div>
      <div class="book-row"><span>도착</span><span>평균 30분 내외</span></div>
      <a class="bk" href="tel:{PHONE_TEL}">전화 예약 →</a>
    </div>
    <div class="floating fl-2">CUSTOMER RATING · ★ 4.9</div>
  </div>
</div></section>

<div class="marquee" aria-hidden="true"><div class="marquee-track">{marquee}</div></div>

<section class="block"><div class="wrap">
  <span class="eyebrow"><span class="pulse"></span>SIGNATURE COURSE</span>
  <h2 class="sec">대표 코스</h2>
  <p class="sec-lead">컨디션과 목적에 맞춰 고를 수 있는 굿데이의 대표 관리입니다.</p>
  <div class="grid g4" style="margin-top:28px">{services}</div>
</div></section>

{price_menu_block()}

<section class="block" id="region"><div class="wrap">
  <span class="eyebrow"><span class="pulse"></span>SERVICE AREA</span>
  <h2 class="sec">강서구 권역별 안내</h2>
  <p class="sec-lead">강서구를 5개 생활 권역으로 나누어 방문 가능 지역을 안내합니다.</p>
  <div class="grid g3" style="margin-top:28px">{regions}</div>
</div></section>

<section class="block" id="process"><div class="wrap">
  <span class="eyebrow"><span class="pulse"></span>HOW IT WORKS</span>
  <h2 class="sec">예약은 이렇게 진행됩니다</h2>
  <div class="grid g4" style="margin-top:28px">{steps_html}</div>
</div></section>

<section class="block" id="reviews"><div class="wrap">
  <span class="eyebrow"><span class="pulse"></span>CLIENT VOICES</span>
  <h2 class="sec">고객 후기</h2>
  <div class="grid g3" style="margin-top:28px">{reviews_html}</div>
</div></section>

{notes_block("ABOUT · WHO·HOW·WHY", "굿데이가 일하는 방식", "신뢰할 수 있는 방문 건강관리를 위한 운영 원칙입니다.", about_notes)}

{faq_block(HOME_FAQ)}

{cta_band()}
"""
    jsonld = [org_ld(), website_ld(), localbiz_ld(), offer_ld(), faq_ld(HOME_FAQ)]
    html = page("/", f"{BRAND} | 서울 강서구 방문 마사지 예약 안내",
                "굿데이 강서출장마사지는 서울 강서구 염창동, 등촌동, 화곡동, 마곡동, 발산동, 방화동 일대 방문 마사지 예약 안내를 제공합니다. 연중무휴 24시간 상담.",
                "home", body, jsonld)
    write("/", html)

HOME_FAQ = [
    ("강서구 어느 지역까지 방문 가능한가요?",
     "염창·등촌·화곡·우장산·가양·마곡·발산·공항·방화 등 강서구 전 지역을 안내드립니다. 정확한 방문 가능 여부는 예약 시간과 위치에 따라 상담 시 확인해 드립니다."),
    ("예약은 어떻게 하나요?",
     "전화 또는 문의로 지역·희망 시간·코스를 말씀해 주시면 디스패처가 방문 가능 시간을 확정해 안내드립니다."),
    ("운영 시간은 어떻게 되나요?",
     "연중무휴 24시간 상담을 운영합니다. 다만 시간대와 위치에 따라 방문 가능 여부가 달라질 수 있습니다."),
    ("요금은 어떻게 안내되나요?",
     "코스별 정찰 요금을 사전에 안내드립니다. 자세한 금액은 코스안내 페이지에서 확인하실 수 있습니다."),
    ("어떤 분들이 방문하나요?",
     "위생·안전 가이드라인을 준수하는 관리사가 약속된 시간에 방문합니다."),
    ("이 서비스는 의료 행위인가요?",
     "아닙니다. 본 서비스는 의료 행위가 아닌 이완·휴식 목적의 건강관리 서비스이며 만 19세 이상 성인을 대상으로 합니다."),
]


# ---- About ---------------------------------------------------------------
def build_about():
    trail = [("/", "홈"), (None, "굿데이 소개")]
    greeting = notes_block("GREETING", "굿데이 인사말",
        "방문 건강관리를 고민하는 분들께 드리는 인사입니다.",
        [("정중한 휴식을 약속드립니다",
          ["굿데이 강서출장마사지를 찾아주셔서 감사합니다.",
           "저희는 서울 강서구 전역을 대상으로 방문 건강관리 예약을 안내하는 운영팀입니다.",
           "예약부터 마무리까지 정중하고 투명한 응대를 약속드립니다."])],
        _id="greeting")
    standards = notes_block("STANDARDS", "서비스 운영 기준",
        "굿데이가 지키는 운영 원칙입니다.",
        [("정찰 요금", ["모든 코스는 정찰 요금으로 사전에 안내드립니다.",
                      "현장에서 임의로 금액이 추가되지 않습니다."]),
         ("사전 안내", ["방문 가능 시간과 코스, 소요 시간을 예약 시 명확히 안내드립니다."]),
         ("정중한 응대", ["상담과 방문 전 과정에서 정중함을 최우선으로 합니다."])],
        _id="standards")
    safety = notes_block("HYGIENE & SAFETY", "위생 및 안전 관리",
        "안심하고 받으실 수 있도록 위생·안전을 관리합니다.",
        [("위생 관리", ["관리에 사용하는 용품은 위생 기준에 맞춰 관리합니다."]),
         ("안전 가이드", ["관리사와 고객 모두의 안전을 위한 가이드라인을 운영합니다."]),
         ("비의료 고지", ["본 서비스는 의료 행위가 아닌 이완·휴식 목적의 건강관리 서비스입니다."])],
        _id="safety")
    about_faq = [
        ("굿데이는 어떤 서비스인가요?", "서울 강서구 전역을 대상으로 하는 방문 건강관리(마사지) 예약 안내 서비스입니다."),
        ("방문 관리는 어떻게 진행되나요?", "예약 확정 후 관리사가 약속된 시간에 고객이 계신 장소로 방문해 진행합니다."),
        ("미성년자도 이용할 수 있나요?", "아닙니다. 본 서비스는 만 19세 이상 성인만 이용하실 수 있습니다."),
    ]
    body = (breadcrumb(trail) +
        '<section class="block"><div class="wrap">'
        '<span class="eyebrow"><span class="pulse"></span>ABOUT GOODDAY</span>'
        '<h2 class="sec">굿데이 소개</h2>'
        '<p class="sec-lead">서울 강서구 방문 건강관리, 굿데이가 일하는 방식과 기준을 소개합니다.</p>'
        '</div></section>' + greeting + standards + safety +
        faq_block(about_faq) + cta_band())
    jsonld = [bc_ld(trail), org_ld(), faq_ld(about_faq)]
    html = page("/about/", "굿데이 소개 | 강서구 방문 건강관리 운영 기준 안내",
        "굿데이 강서출장마사지의 인사말, 서비스 운영 기준, 위생 및 안전 관리 원칙을 안내합니다. 정찰 요금과 정중한 응대를 약속드립니다.",
        "about", body, jsonld)
    write("/about/", html)


# ---- Gangseo representative page -----------------------------------------
def build_gangseo():
    trail = [("/", "홈"), (None, "강서출장마사지")]
    area_chips = "".join(f'<span class="chip"><b>{r["name"].split("권역")[0]}</b></span>' for r in REGIONS)
    intro = notes_block("INTRO", "강서구 출장마사지 안내",
        "강서구 전역을 대상으로 하는 방문 건강관리 안내입니다.",
        [("강서구 전 지역 방문",
          ["굿데이는 서울 강서구 염창동부터 방화동까지 전 지역 방문 관리를 안내합니다.",
           "생활권에 맞춰 5개 권역으로 나누어 방문 가능 지역을 안내드립니다."])],
        _id="intro")
    area_section = (
        '<section class="block" id="area"><div class="wrap">'
        '<span class="eyebrow"><span class="pulse"></span>SERVICE AREA</span>'
        '<h2 class="sec">출장 가능 지역</h2>'
        '<p class="sec-lead">강서구를 5개 권역으로 나누어 안내합니다. 권역을 눌러 동별 안내를 확인하세요.</p>'
        '<div class="grid g3" style="margin-top:26px">' +
        "".join(f'<a class="card reveal" href="/gangseo-gu/{r["slug"]}/"><div class="k">AREA</div>'
                f'<h3>{r["name"]}</h3><p>{r["summary"]}</p><span class="more">권역 보기 →</span></a>'
                for r in REGIONS) +
        f'</div><div class="chips">{area_chips}</div></div></section>')
    hours = notes_block("HOURS", "예약 가능 시간",
        "연중무휴 24시간 상담을 운영합니다.",
        [("24시간 상담", ["전화 상담은 연중무휴 24시간 가능합니다.",
                       "실제 방문 가능 시간은 시간대와 위치에 따라 안내드립니다."])],
        _id="hours")
    check = notes_block("CHECK", "관리 전 확인사항",
        "원활한 방문을 위해 미리 확인해 주세요.",
        [("방문 장소", ["방문 가능한 장소와 주소, 연락 가능한 번호를 미리 알려주세요."]),
         ("코스·시간", ["희망 코스와 소요 시간을 예약 시 함께 확인해 주세요."])],
        _id="check")
    safety = notes_block("HYGIENE & SAFETY", "위생 및 안전 안내",
        "안심하고 받으실 수 있도록 안내드립니다.",
        [("위생·안전", ["용품 위생 관리와 안전 가이드라인을 준수합니다.",
                     "본 서비스는 의료 행위가 아닌 건강관리 서비스이며 만 19세 이상을 대상으로 합니다."])],
        _id="safety")
    gangseo_faq = [
        ("강서구 출장마사지는 어디까지 되나요?", "염창·등촌·화곡·우장산·가양·마곡·발산·공항·방화 등 강서구 전 지역을 안내드립니다."),
        ("당일 예약도 가능한가요?", "가능합니다. 다만 시간대와 위치에 따라 방문 가능 시간이 달라질 수 있어 상담 시 확인해 드립니다."),
        ("화곡동처럼 동이 여러 개로 나뉜 곳도 되나요?", "네. 화곡본동·화곡1~8동 등은 화곡동 안내 기준으로 통합 안내드립니다."),
    ]
    body = (breadcrumb(trail) +
        f'<section class="hero"><div class="hero-inner"><div class="hero-copy">'
        f'<span class="eyebrow"><span class="pulse"></span>강서구 대표</span>'
        f'<h1>강서구 <span class="grad">출장마사지</span><br><span class="serif">한 곳에서.</span></h1>'
        f'<p class="lead">서울 강서구 전 지역 방문 건강관리 예약을 굿데이가 안내합니다.</p>'
        f'<div class="actions"><a class="btn btn-primary" href="tel:{PHONE_TEL}">전화 예약 →</a>'
        f'<a class="btn btn-ghost" href="/gangseo-gu/area/">지역별 안내</a></div></div>'
        f'<div class="hero-visual"><div class="glass"><h3>GANGSEO<b>강서구 전 지역</b></h3>'
        f'<div class="book-row"><span>권역</span><span>5개 생활권</span></div>'
        f'<div class="book-row"><span>상담</span><span>{HOURS}</span></div>'
        f'<a class="bk" href="tel:{PHONE_TEL}">예약 문의 →</a></div></div></div></section>' +
        intro + area_section + hours + check + safety +
        price_menu_block() + faq_block(gangseo_faq) + cta_band())
    jsonld = [bc_ld(trail), localbiz_ld(name="굿데이 강서구 출장마사지", path="/gangseo-gu/"),
              service_ld("강서구 출장마사지", "서울 강서구 전 지역 방문 건강관리 서비스", "/gangseo-gu/"),
              offer_ld(), faq_ld(gangseo_faq)]
    html = page("/gangseo-gu/", "강서구 출장마사지 | 굿데이 방문 마사지 안내",
        "강서구 출장마사지 굿데이 - 염창·화곡·마곡·발산·방화 등 서울 강서구 전 지역 방문 건강관리 예약 안내. 연중무휴 24시간 상담.",
        "gangseo", body, jsonld)
    write("/gangseo-gu/", html)


# ---- Area hub ------------------------------------------------------------
def build_area_hub():
    trail = [("/", "홈"), ("/gangseo-gu/", "강서출장마사지"), (None, "지역별 안내")]
    blocks = ""
    for r in REGIONS:
        dong_links = "".join(
            f'<a class="card reveal" href="/gangseo-gu/{d["slug"]}/"><div class="k">{r["name"]}</div>'
            f'<h3>{d["name"]} 출장마사지</h3><p>{d["character"]}</p>'
            f'<span class="more">동 안내 보기 →</span></a>' for d in r["dongs"])
        blocks += (
            f'<div style="margin-top:40px"><h3 style="font-size:22px;font-weight:800;margin-bottom:6px">'
            f'<a href="/gangseo-gu/{r["slug"]}/" class="grad">{r["name"]}</a></h3>'
            f'<p class="sec-lead">{r["summary"]}</p>'
            f'<div class="grid g3" style="margin-top:18px">{dong_links}</div></div>')
    body = (breadcrumb(trail) +
        '<section class="block"><div class="wrap">'
        '<span class="eyebrow"><span class="pulse"></span>AREA GUIDE</span>'
        '<h2 class="sec">지역별 안내</h2>'
        '<p class="sec-lead">강서구를 5개 생활 권역으로 나누어 동별 방문 안내를 제공합니다.</p>'
        + blocks + '</div></section>' + price_menu_block() + cta_band())
    item_list = {
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": "강서구 출장마사지 지역별 안내", "url": BASE_URL + "/gangseo-gu/area/",
        "hasPart": [{"@type": "WebPage", "name": r["name"],
                     "url": BASE_URL + f"/gangseo-gu/{r['slug']}/"} for r in REGIONS],
    }
    html = page("/gangseo-gu/area/", "강서구 출장마사지 가능 지역 | 굿데이 지역별 안내",
        "굿데이 강서출장마사지 지역별 안내 - 염창·등촌, 화곡·우장산, 가양·마곡, 발산, 공항·방화 5개 권역별 동별 방문 안내를 제공합니다.",
        "area", body, [bc_ld(trail), item_list, offer_ld()])
    write("/gangseo-gu/area/", html)


# ---- Area (권역) pages ----------------------------------------------------
def build_area_pages():
    for r in REGIONS:
        trail = [("/", "홈"), ("/gangseo-gu/", "강서출장마사지"),
                 ("/gangseo-gu/area/", "지역별 안내"), (None, r["name"])]
        dong_cards = "".join(
            f'<a class="card reveal" href="/gangseo-gu/{d["slug"]}/"><div class="k">동 안내</div>'
            f'<h3>{d["name"]} 출장마사지</h3><p>{d["landmarks"]}</p>'
            f'<span class="more">자세히 →</span></a>' for d in r["dongs"])
        notes = [
            ("권역의 특징", [r["summary"],
              f'{r["name"]}은 ' + ", ".join(d["name"] for d in r["dongs"]) + " 일대를 포함합니다."]),
            ("매니저 배치 및 도착 시간",
             ["권역 내 위치에 따라 평균 도착 시간이 달라집니다.",
              "예약 시 위치를 알려주시면 예상 도착 시간을 안내드립니다."]),
            ("추천 코스",
             ["피로 회복·아로마 관리가 가장 많이 선택됩니다.",
              "운동 후라면 스포츠 관리를 함께 안내드립니다."]),
        ]
        # 동별 sub-notes (발산역/방화1~3동 등)
        sub_notes = [d.get("sub_note") for d in r["dongs"] if d.get("sub_note")]
        if sub_notes:
            notes.append(("세부 지역 안내", sub_notes))
        chips = "".join(
            f'<span class="chip"><b>{d["name"]}</b> 평균 {d["arrival"]}분</span>' for d in r["dongs"])
        area_faq = [
            (f"{r['name']}은 어디까지 방문 가능한가요?",
             "권역 내 " + "·".join(d["name"] for d in r["dongs"]) + " 일대를 안내드리며, 정확한 가능 여부는 예약 시간과 위치에 따라 확인해 드립니다."),
            (f"{r['name']} 예약은 어떻게 하나요?",
             "전화 또는 문의로 동·시간·코스를 말씀해 주시면 방문 가능 시간을 확정해 드립니다."),
        ]
        body = (breadcrumb(trail) +
            f'<section class="block"><div class="wrap">'
            f'<span class="eyebrow"><span class="pulse"></span>AREA · {r["name"]}</span>'
            f'<h2 class="sec">{r["name"]} 출장마사지</h2>'
            f'<p class="sec-lead">{r["summary"]}</p>'
            f'<div class="chips">{chips}</div>'
            f'<div class="grid g3" style="margin-top:26px">{dong_cards}</div>'
            f'</div></section>' +
            notes_block("FIELD NOTES · 2026", f"{r['name']} 운영 안내",
                        "권역의 특징과 방문 운영 원칙입니다.", notes, _id="about") +
            price_menu_block() + faq_block(area_faq) + cta_band())
        jsonld = [bc_ld(trail),
                  localbiz_ld(name=f"굿데이 {r['name']} 출장마사지", area=f"서울특별시 강서구 {r['name']}",
                              path=f"/gangseo-gu/{r['slug']}/"),
                  service_ld(f"{r['name']} 출장마사지", r["summary"], f"/gangseo-gu/{r['slug']}/"),
                  offer_ld(), faq_ld(area_faq)]
        html = page(f"/gangseo-gu/{r['slug']}/",
            f"{r['name']} 출장마사지 | 강서구 {r['name']} 방문 마사지",
            f"{r['name']} 출장마사지 안내 - " + ", ".join(d['name'] for d in r['dongs']) +
            f" 일대 방문 건강관리 예약 안내입니다. {r['summary']}",
            "area", body, jsonld)
        write(f"/gangseo-gu/{r['slug']}/", html)


# ---- 동 pages -------------------------------------------------------------
def build_dong_pages():
    for r in REGIONS:
        for d in r["dongs"]:
            trail = [("/", "홈"), ("/gangseo-gu/", "강서출장마사지"),
                     ("/gangseo-gu/area/", "지역별 안내"),
                     (f"/gangseo-gu/{r['slug']}/", r["name"]),
                     (None, f"{d['name']} 출장마사지")]
            notes = [
                ("동(洞) 특징과 생활권",
                 [f"{d['name']}은 {d['character']}입니다.",
                  f"주요 위치는 {d['landmarks']}입니다."]),
                ("평균 도착 시간",
                 [f"{d['name']} 일대는 평균 {d['arrival']}분 내외로 도착합니다.",
                  "시간대와 정확한 위치에 따라 도착 시간은 달라질 수 있습니다."]),
                ("추천 코스와 예약",
                 ["피로 회복·아로마 관리가 많이 선택됩니다.",
                  "예약 시 희망 코스와 시간을 함께 말씀해 주세요."]),
            ]
            if d.get("sub_note"):
                notes.append(("세부 지역 안내", [d["sub_note"]]))
            reviews = [
                (f"{d['name']} · 30대", "도착 시간 안내가 정확하고 응대가 정중했습니다."),
                (f"{d['name']} · 40대", "아로마 관리 후 한결 가벼워졌어요. 또 이용할게요."),
            ]
            reviews_html = "".join(
                f'<div class="review reveal"><div class="stars">★★★★★</div>'
                f'<p>“{q}”</p><div class="who">{w}</div></div>' for w, q in reviews)
            dong_faq = [
                (f"{d['name']} 어디까지 방문 가능한가요?",
                 f"{d['name']} 일대 방문 가능 여부는 예약 시간과 위치에 따라 안내드립니다. " +
                 (d["sub_note"] if d.get("sub_note") else "정확한 위치를 알려주시면 확인해 드립니다.")),
                (f"{d['name']} 도착까지 얼마나 걸리나요?",
                 f"평균 {d['arrival']}분 내외이며, 시간대와 위치에 따라 달라질 수 있습니다."),
                (f"{d['name']}에서 어떤 코스를 받을 수 있나요?",
                 "피로 회복·아로마·스포츠·커플/가족 등 전 코스를 동일하게 안내드립니다."),
            ]
            chips = (f'<div class="chips">'
                     f'<span class="chip"><b>평균 도착</b> {d["arrival"]}분</span>'
                     f'<span class="chip"><b>운영</b> {HOURS}</span>'
                     f'<span class="chip"><b>권역</b> {r["name"]}</span></div>')
            body = (breadcrumb(trail) +
                f'<section class="block"><div class="wrap">'
                f'<span class="eyebrow"><span class="pulse"></span>강서구 {d["name"]}</span>'
                f'<h2 class="sec">{d["name"]} 출장마사지</h2>'
                f'<p class="sec-lead">{d["landmarks"]} 일대 방문 건강관리 예약 안내입니다.</p>'
                f'{chips}</div></section>' +
                notes_block("OVERVIEW", f"{d['name']} 방문 안내",
                            f"{d['name']} 출장마사지 이용 전 확인하세요.", notes, _id="about") +
                price_menu_block() +
                '<section class="block" id="reviews"><div class="wrap">'
                f'<span class="eyebrow"><span class="pulse"></span>REVIEWS</span>'
                f'<h2 class="sec">{d["name"]} 고객 후기</h2>'
                f'<div class="grid g2" style="margin-top:24px">{reviews_html}</div></div></section>' +
                faq_block(dong_faq) + cta_band(f"{d['name']} 방문 예약을 도와드릴까요?"))
            jsonld = [bc_ld(trail),
                      localbiz_ld(name=f"굿데이 {d['name']} 출장마사지",
                                  area=f"서울특별시 강서구 {d['name']}",
                                  path=f"/gangseo-gu/{d['slug']}/"),
                      service_ld(f"{d['name']} 출장마사지",
                                 f"강서구 {d['name']} 일대 방문 건강관리 서비스",
                                 f"/gangseo-gu/{d['slug']}/"),
                      offer_ld(), faq_ld(dong_faq)]
            html = page(f"/gangseo-gu/{d['slug']}/",
                f"{d['name']} 출장마사지 | 강서구 {d['name']} 방문 마사지",
                f"강서구 {d['name']} 출장마사지 안내 페이지입니다. {d['landmarks']} 인근 방문 가능 지역, 예약 가능 시간, 코스 선택 기준, 이용 전 확인사항을 확인해보세요.",
                "area", body, jsonld)
            write(f"/gangseo-gu/{d['slug']}/", html)


# ---- Course --------------------------------------------------------------
def build_course():
    trail = [("/", "홈"), (None, "코스안내")]
    course_faq = [
        ("코스는 어떻게 선택하나요?", "컨디션과 목적을 말씀해 주시면 피로 회복·아로마·스포츠 중 적합한 코스를 안내드립니다."),
        ("커플/가족 관리는 어떻게 진행되나요?", "두 분이 같은 공간에서 동시에 받는 동반 관리이며, 인원과 시간에 따라 요금이 달라집니다."),
        ("기업/단체 관리도 되나요?", "워크숍·행사 등 단체 인원은 사전 협의 후 별도 견적으로 안내드립니다."),
        ("표시된 요금 외 추가 비용이 있나요?", "정찰 요금을 원칙으로 하며, 변동 사항은 예약 시 사전에 안내드립니다."),
    ]
    guide_notes = [
        ("처음이라면 피로 회복 관리", ["가장 기본이 되는 전신 이완 관리입니다.", "어떤 코스를 골라야 할지 모르겠다면 피로 회복 관리를 추천드립니다."]),
        ("향과 함께라면 아로마 관리", ["블렌딩 오일의 향으로 심신을 함께 이완하고 싶을 때 좋습니다."]),
        ("운동 후라면 스포츠 관리", ["운동 후 뭉친 근육 회복에 초점을 맞춘 관리입니다."]),
    ]
    body = (breadcrumb(trail) +
        '<section class="block" id="all"><div class="wrap">'
        '<span class="eyebrow"><span class="pulse"></span>COURSE</span>'
        '<h2 class="sec">전체 코스</h2>'
        '<p class="sec-lead">목적과 컨디션에 맞춰 고를 수 있는 굿데이의 방문 관리 코스입니다.</p>'
        '<div style="margin-top:26px" id="price">' + price_grid(COURSES) + '</div></div></section>' +
        notes_block("SELECT GUIDE", "코스 선택 가이드",
                    "어떤 코스가 맞을지 고민될 때 참고하세요.", guide_notes, _id="guide") +
        faq_block(course_faq) + cta_band())
    jsonld = [bc_ld(trail),
              service_ld("방문 마사지 코스", "피로 회복·아로마·스포츠·커플/가족·기업/단체 방문 관리 코스", "/course/"),
              faq_ld(course_faq)]
    html = page("/course/", "코스안내 | 강서구 출장마사지 피로회복·아로마·스포츠 요금",
        "굿데이 강서출장마사지 코스안내 - 피로 회복, 아로마, 스포츠, 커플/가족, 기업/단체 관리의 코스 설명과 정찰 요금을 안내합니다.",
        "course", body, jsonld)
    write("/course/", html)


# ---- Reservation ---------------------------------------------------------
def build_reservation():
    trail = [("/", "홈"), (None, "예약안내")]
    notes = [
        ("예약 방법", ["전화 또는 문의로 지역·희망 시간·코스를 말씀해 주세요.", "디스패처가 방문 가능 시간을 확정해 안내드립니다."]),
        ("예약 가능 시간", ["연중무휴 24시간 상담을 운영합니다.", "방문 가능 시간은 시간대와 위치에 따라 안내드립니다."]),
        ("방문 가능 장소", ["자택, 숙소 등 방문 가능한 장소와 주소를 알려주세요."]),
        ("결제 안내", ["코스별 정찰 요금을 사전에 안내드리며, 결제 방법은 예약 시 함께 안내합니다."]),
        ("예약 변경·취소", ["일정 변경이나 취소는 가능한 한 빠르게 연락 주시면 도와드립니다."]),
        ("예약 전 체크사항", ["방문 장소·연락처·희망 코스·시간을 미리 정리해 두시면 빠르게 진행됩니다."]),
    ]
    res_faq = [
        ("당일 예약이 가능한가요?", "가능합니다. 다만 시간대와 위치에 따라 방문 가능 시간이 달라질 수 있어 상담 시 확인해 드립니다."),
        ("예약을 변경하고 싶어요.", "확정된 일정 변경은 가능한 한 빠르게 연락 주시면 조정을 도와드립니다."),
        ("결제는 어떻게 하나요?", "정찰 요금을 사전에 안내드리며 결제 방법은 예약 시 함께 안내합니다."),
    ]
    body = (breadcrumb(trail) +
        '<section class="block"><div class="wrap">'
        '<span class="eyebrow"><span class="pulse"></span>RESERVATION</span>'
        '<h2 class="sec">예약안내</h2>'
        '<p class="sec-lead">예약 방법부터 결제·변경까지 한눈에 안내드립니다.</p>'
        '</div></section>' +
        notes_block("HOW TO BOOK", "예약 진행 안내", "아래 순서대로 진행됩니다.", notes, _id="about") +
        faq_block(res_faq) + cta_band())
    html = page("/reservation/", "예약안내 | 강서구 출장마사지 예약 방법·결제 안내",
        "굿데이 강서출장마사지 예약안내 - 예약 방법, 예약 가능 시간, 방문 가능 장소, 결제와 변경·취소 안내를 제공합니다. 연중무휴 24시간 상담.",
        "reservation", body, [bc_ld(trail), faq_ld(res_faq)])
    write("/reservation/", html)


# ---- Guide ---------------------------------------------------------------
def build_guide():
    trail = [("/", "홈"), (None, "이용가이드")]
    notes = [
        ("처음 이용하시는 분", ["예약 시 지역·시간·코스만 말씀해 주시면 나머지는 안내해 드립니다."]),
        ("방문 전 준비사항", ["편하게 쉴 수 있는 공간과 연락 가능한 번호를 준비해 주세요."]),
        ("위생 및 안전 기준", ["용품 위생 관리와 안전 가이드라인을 준수합니다."]),
        ("관리 후 주의사항", ["관리 후에는 충분한 수분 섭취와 휴식을 권장드립니다."]),
        ("금지행위 안내", ["불법·퇴폐 행위 요구는 일절 제공하지 않으며, 요청 시 서비스가 중단될 수 있습니다."]),
    ]
    guide_faq = [
        ("처음인데 무엇을 준비하나요?", "편히 쉴 수 있는 공간과 연락 가능한 번호만 있으면 됩니다."),
        ("관리 후 주의할 점이 있나요?", "충분한 수분 섭취와 휴식을 권장드립니다."),
        ("이 서비스는 의료 행위인가요?", "아닙니다. 이완·휴식 목적의 건강관리 서비스이며 만 19세 이상을 대상으로 합니다."),
    ]
    body = (breadcrumb(trail) +
        '<section class="block"><div class="wrap">'
        '<span class="eyebrow"><span class="pulse"></span>GUIDE</span>'
        '<h2 class="sec">이용가이드</h2>'
        '<p class="sec-lead">처음 이용하시는 분도 안심할 수 있도록 안내드립니다.</p>'
        '</div></section>' +
        notes_block("USER GUIDE", "이용 안내", "방문 전후 확인하세요.", notes, _id="about") +
        faq_block(guide_faq) + cta_band())
    html = page("/guide/", "이용가이드 | 강서구 출장마사지 방문 전 준비·주의사항",
        "굿데이 강서출장마사지 이용가이드 - 처음 이용하시는 분을 위한 방문 전 준비사항, 위생·안전 기준, 관리 후 주의사항과 금지행위 안내입니다.",
        "guide", body, [bc_ld(trail), faq_ld(guide_faq)])
    write("/guide/", html)


# ---- Reviews -------------------------------------------------------------
def build_reviews():
    trail = [("/", "홈"), (None, "고객후기")]
    sample = [
        ("화곡동 · 30대", "아로마", "늦은 시간 연락에도 도착 안내가 정확했습니다."),
        ("마곡동 · 40대", "스포츠", "운동 후 받았는데 컨디션이 한결 가벼워졌어요."),
        ("염창동 · 30대", "피로회복", "예약부터 마무리까지 깔끔하고 정중했습니다."),
        ("발산동 · 50대", "아로마", "위생 안내가 꼼꼼해서 안심하고 받았습니다."),
        ("방화동 · 40대", "피로회복", "도착 시간을 미리 알려주셔서 좋았습니다."),
        ("가양동 · 30대", "커플", "둘이 함께 받았는데 응대가 친절했습니다."),
    ]
    cards = "".join(
        f'<div class="review reveal"><div class="stars">★★★★★</div>'
        f'<p>“{q}”</p><div class="who">{w} · {c} 코스</div></div>' for w, c, q in sample)
    region_links = "".join(
        f'<a class="chip" href="/gangseo-gu/{r["slug"]}/"><b>{r["name"]}</b></a>' for r in REGIONS)
    body = (breadcrumb(trail) +
        '<section class="block" id="reviews"><div class="wrap">'
        '<span class="eyebrow"><span class="pulse"></span>REVIEWS</span>'
        '<h2 class="sec">고객후기</h2>'
        '<p class="sec-lead">굿데이를 이용하신 고객들의 후기입니다. 권역별 후기는 각 지역 페이지에서 확인하세요.</p>'
        f'<div class="grid g3" style="margin-top:26px">{cards}</div>'
        f'<div class="chips" style="margin-top:24px">{region_links}</div>'
        '<p class="sec-lead" style="margin-top:24px">후기는 실제 이용 고객의 동의 하에 게시되며, 개인을 특정할 수 있는 정보는 표시하지 않습니다.</p>'
        '</div></section>' + cta_band())
    item_list = {
        "@context": "https://schema.org", "@type": "ItemList",
        "name": "굿데이 강서출장마사지 고객후기",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "item": {"@type": "Review", "reviewRating": {"@type": "Rating", "ratingValue": "5"},
                      "author": {"@type": "Person", "name": w}, "reviewBody": q}}
            for i, (w, c, q) in enumerate(sample)],
    }
    html = page("/reviews/", "고객후기 | 강서출장마사지 굿데이 방문 마사지 후기",
        "굿데이 강서출장마사지 고객후기 - 화곡·마곡·염창·발산·방화 등 강서구 전 지역 방문 건강관리 이용 후기를 모았습니다.",
        "reviews", body, [bc_ld(trail), item_list])
    write("/reviews/", html)


# ---- Customer center -----------------------------------------------------
def build_customer():
    trail = [("/", "홈"), (None, "고객센터")]
    notes = [
        ("공지사항", ["서비스 운영과 관련된 안내를 이곳에 게시합니다."]),
        ("1:1 문의", [f"전화 {PHONE_DISP} 또는 이메일 {EMAIL}로 문의해 주세요."]),
        ("제휴·기업 문의", ["기업·단체 방문 관리 및 제휴 문의는 이메일로 접수받습니다."]),
    ]
    cust_faq = [
        ("문의는 어디로 하나요?", f"전화 {PHONE_DISP} 또는 이메일 {EMAIL}로 문의하실 수 있습니다."),
        ("운영 시간이 어떻게 되나요?", "연중무휴 24시간 상담을 운영합니다."),
        ("개인정보는 어떻게 관리되나요?", "개인정보처리방침에 따라 안전하게 관리되며, 자세한 내용은 해당 페이지에서 확인하실 수 있습니다."),
    ]
    body = (breadcrumb(trail) +
        '<section class="block" id="notice"><div class="wrap">'
        '<span class="eyebrow"><span class="pulse"></span>CUSTOMER</span>'
        '<h2 class="sec">고객센터</h2>'
        f'<p class="sec-lead">전화 {PHONE_DISP} · 이메일 {EMAIL} · {HOURS}</p>'
        '</div></section>' +
        notes_block("HELP", "문의 안내", "궁금한 점은 언제든 문의해 주세요.", notes, _id="inquiry") +
        faq_block(cust_faq, "자주 묻는 질문") + cta_band())
    html = page("/customer/", "고객센터 | 강서출장마사지 굿데이 문의·공지",
        "굿데이 강서출장마사지 고객센터 - 공지사항, 자주 묻는 질문, 1:1 문의, 제휴·기업 문의 안내입니다. 연중무휴 24시간 상담.",
        "customer", body, [bc_ld(trail), faq_ld(cust_faq)])
    write("/customer/", html)


# ---- Policy pages --------------------------------------------------------
def policy_page(path, active_title, heading, sections, desc):
    trail = [("/", "홈"), (None, heading)]
    secs = "".join(
        f'<div class="note-card"><div class="note-content"><h3 class="note-title">{t}</h3>'
        f'<div class="note-text">{"".join(f"<p>{p}</p>" for p in ps)}</div></div></div>'
        for t, ps in sections)
    body = (breadcrumb(trail) +
        f'<section class="block"><div class="wrap">'
        f'<span class="eyebrow"><span class="pulse"></span>POLICY</span>'
        f'<h2 class="sec">{heading}</h2>'
        f'<div class="note-stack" style="margin-top:26px;max-width:820px">{secs}</div>'
        f'</div></section>')
    html = page(path, active_title, desc, "customer", body, [bc_ld(trail)])
    write(path, html)


def build_policies():
    policy_page("/privacy/", "개인정보처리방침 | 굿데이 강서출장마사지", "개인정보처리방침",
        [("수집하는 개인정보", ["예약 진행을 위해 연락처, 방문 장소 등 최소한의 정보를 수집합니다."]),
         ("이용 목적", ["수집한 정보는 예약 확정과 방문 안내 목적으로만 이용합니다."]),
         ("보유 및 파기", ["목적 달성 후에는 관련 법령에 따라 지체 없이 파기합니다."]),
         ("개인정보보호책임자", [f"{COMPANY['privacy_officer']} · {EMAIL}"])],
        "굿데이 강서출장마사지 개인정보처리방침 - 수집 항목, 이용 목적, 보유 및 파기, 개인정보보호책임자 안내입니다.")
    policy_page("/terms/", "이용약관 | 굿데이 강서출장마사지", "이용약관",
        [("목적", ["본 약관은 굿데이 강서출장마사지 예약 서비스 이용 조건을 규정합니다."]),
         ("서비스 내용", ["본 서비스는 의료 행위가 아닌 이완·휴식 목적의 방문 건강관리 예약 서비스입니다."]),
         ("이용 자격", ["본 서비스는 만 19세 이상 성인만 이용할 수 있습니다."]),
         ("금지행위", ["불법·퇴폐 행위 요구 등은 금지되며, 위반 시 서비스가 중단될 수 있습니다."])],
        "굿데이 강서출장마사지 이용약관 - 서비스 내용, 이용 자격, 금지행위 등 이용 조건을 안내합니다.")
    policy_page("/youth/", "청소년보호정책 | 굿데이 강서출장마사지", "청소년보호정책",
        [("청소년 이용 제한", ["본 서비스는 만 19세 이상 성인을 대상으로 하며 청소년은 이용할 수 없습니다."]),
         ("건전한 운영", ["굿데이는 불법·퇴폐 행위를 일절 제공하지 않으며 건전한 건강관리 서비스를 지향합니다."]),
         ("책임자", [f"청소년보호 책임자 · {COMPANY['privacy_officer']} · {EMAIL}"])],
        "굿데이 강서출장마사지 청소년보호정책 - 만 19세 이상 이용 제한과 건전한 운영 원칙을 안내합니다.")


# ---- robots / sitemap / manifest / favicon -------------------------------
def build_meta_files():
    urls = ["/", "/about/", "/gangseo-gu/", "/gangseo-gu/area/", "/course/",
            "/reservation/", "/guide/", "/reviews/", "/customer/",
            "/privacy/", "/terms/", "/youth/"]
    for r in REGIONS:
        urls.append(f"/gangseo-gu/{r['slug']}/")
        for d in r["dongs"]:
            urls.append(f"/gangseo-gu/{d['slug']}/")
    prio = {"/": "1.0"}
    items = ""
    for u in urls:
        p = prio.get(u, "0.8" if u.count("/") <= 2 else "0.75")
        freq = "daily" if u == "/" else "weekly"
        items += (f"  <url><loc>{BASE_URL}{u}</loc>"
                  f"<changefreq>{freq}</changefreq><priority>{p}</priority></url>\n")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + items + "</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    robots = ("User-agent: *\nAllow: /\nDisallow: /tools/\n\n"
              "User-agent: GPTBot\nAllow: /\n"
              "User-agent: ClaudeBot\nAllow: /\n"
              "User-agent: Google-Extended\nAllow: /\n\n"
              f"Sitemap: {BASE_URL}/sitemap.xml\n"
              f"Host: {BASE_URL.replace('https://','')}\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    manifest = {
        "name": BRAND, "short_name": "굿데이", "description": "서울 강서구 방문 건강관리 예약 안내",
        "start_url": "/", "scope": "/", "display": "standalone",
        "background_color": "#0b0b0e", "theme_color": "#0b0b0e",
        "lang": "ko-KR", "orientation": "portrait",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    with open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    favicon = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
               '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
               '<stop offset="0" stop-color="#f4d29c"/><stop offset=".5" stop-color="#e9b8a7"/>'
               '<stop offset="1" stop-color="#c98a6b"/></linearGradient></defs>'
               '<rect width="64" height="64" rx="16" fill="#0b0b0e"/>'
               '<rect x="8" y="8" width="48" height="48" rx="13" fill="url(#g)"/>'
               '<text x="32" y="44" font-family="Georgia,serif" font-style="italic" '
               'font-size="34" font-weight="700" text-anchor="middle" fill="#1a1208">G</text></svg>')
    with open(os.path.join(ROOT, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(favicon)


# ---------------------------------------------------------------------------
def main():
    build_home()
    build_about()
    build_gangseo()
    build_area_hub()
    build_area_pages()
    build_dong_pages()
    build_course()
    build_reservation()
    build_guide()
    build_reviews()
    build_customer()
    build_policies()
    build_meta_files()
    print("Build complete.")


if __name__ == "__main__":
    main()
