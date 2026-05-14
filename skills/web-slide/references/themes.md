# 테마 카탈로그 — 10+1 컬러 팔레트

> 모든 테마는 dark/light 양쪽 정의. `:root` (dark) + `[data-theme="light"]` (light) 두 블록만 단일 출처.

## 토큰 스키마 (모든 테마 공통)

```css
:root {
  /* 배경 3단 */
  --bg:     /* 가장 어두운 */;
  --bg-2:   /* 카드 안 */;
  --bg-3:   /* 카드 안 + 1 단계 강조 */;

  /* 텍스트 3단 */
  --text:   /* primary */;
  --text-2: /* secondary */;
  --text-3: /* tertiary, captions */;

  /* 선 */
  --line:   /* divider, faint */;
  --line-2: /* card stroke */;

  /* 강조 */
  --accent:   /* primary accent */;
  --accent-2: /* secondary accent (optional) */;

  /* 레이어 색 (architecture diagram 용) */
  --layer-1: /* purple-ish */;
  --layer-2: /* teal-ish */;
  --layer-3: /* orange-ish */;
  --layer-4: /* red/pink-ish */;
}
[data-theme="light"] {
  /* 모든 토큰 light 버전 override */
}
```

## 1. Ocean Depths (default, professional)

- 출처: theme-factory 의 Ocean Depths
- 분위기: navy + teal + seafoam + cream — 차분, 신뢰

| 토큰 | dark | light |
|---|---|---|
| --bg | `#1a2332` | `#f1faee` |
| --bg-2 | `#22304a` | `#ffffff` |
| --bg-3 | `#2a3a55` | `#e6f3ec` |
| --text | `#f1faee` | `#1a2332` |
| --text-2 | `#a8dadc` | `#2d8b8b` |
| --text-3 | `#7eb5b7` | `#5a7a7a` |
| --line | `#2d8b8b` | `#a8dadc` |
| --accent | `#2d8b8b` | `#2d8b8b` |

폰트: Inter / Source Sans Pro (Heading) + JetBrains Mono (label)

## 2. Tech Innovation (default, engineering)

- 출처: theme-factory 의 Tech Innovation
- 분위기: 전기 청색 + 사이언, dark 우선

| 토큰 | dark | light |
|---|---|---|
| --bg | `#0b0f1a` | `#fafafa` |
| --bg-2 | `#131826` | `#ffffff` |
| --bg-3 | `#1c2335` | `#f0f4f8` |
| --text | `#e6ecf5` | `#1e1e1e` |
| --text-2 | `#9aa8be` | `#444a52` |
| --text-3 | `#6b7791` | `#777d85` |
| --line | `#2a3550` | `#dde2eb` |
| --accent | `#00ffff` | `#0066ff` |
| --layer-1 | `#a78bfa` | `#7c3aed` |
| --layer-2 | `#2dd4bf` | `#0d9488` |
| --layer-3 | `#fb923c` | `#ea580c` |
| --layer-4 | `#f87171` | `#dc2626` |

폰트: -apple-system / Pretendard / Noto Sans KR + JetBrains Mono

**cobot2 architecture-playground.html 의 dark 모드가 이 팔레트.**

## 3. Modern Minimalist (default, general)

- 분위기: 흑백 + 그레이 + 단일 액센트
- 어떤 콘텐츠와도 잘 어울림

| 토큰 | dark | light |
|---|---|---|
| --bg | `#1a1a1a` | `#ffffff` |
| --bg-2 | `#252525` | `#f8f8f8` |
| --bg-3 | `#303030` | `#efefef` |
| --text | `#ffffff` | `#36454f` |
| --text-2 | `#d3d3d3` | `#708090` |
| --text-3 | `#999999` | `#a0a0a0` |
| --line | `#444444` | `#d3d3d3` |
| --accent | `#36454f` | `#36454f` |

폰트: Helvetica Neue / Arial + Inter

## 4. Golden Hour (warm)

mustard `#f4a900` + terracotta `#c1666b` + warm beige `#d4b896` + chocolate `#4a403a`

## 5. Arctic Frost (cool)

ice blue `#d4e4f7` + steel blue `#4a6fa5` + silver `#c0c0c0` + white `#fafafa`

## 6. Botanical Garden (natural)

fern `#4a7c59` + marigold `#f9a620` + terracotta `#b7472a` + cream `#f5f3ed`

## 7. Desert Rose (muted warm)

dusty rose `#d4a5a5` + clay `#b87d6d` + sand `#e8d5c4` + burgundy `#5d2e46`

## 8. Forest Canopy (HOMIE-inspired, calm sage)

forest `#2d4a2b` + sage `#7d8471` + olive `#a4ac86` + ivory `#faf9f6`

light 변형: bg `#F2F1EB` + bg-2 `#FFFFFF` + bg-4 `#DDE3D6` + text `#1F1F1B` + accent `#6F8060` + layer-main `#7B8A6E` — **cobot2 light 모드가 이 톤.**

## 9. Sunset Boulevard (vibrant)

burnt orange `#e76f51` + coral `#f4a261` + warm sand `#e9c46a` + deep purple `#264653`

## 10. Midnight Galaxy (mystical dark)

deep purple `#2b1e3e` + cosmic blue `#4a4e8f` + lavender `#a490c2` + silver `#e6e6fa`

## 11. Anthropic (brand)

- 출처: brand-guidelines

| 토큰 | 값 |
|---|---|
| --bg | `#141413` |
| --text | `#faf9f5` |
| --text-2 | `#e8e6dc` |
| --text-3 | `#b0aea5` |
| --accent | `#d97757` (orange) |
| --accent-2 | `#6a9bcc` (blue) |
| --accent-3 | `#788c5d` (green) |

폰트: Poppins (24pt+) + Lora (body)

---

## 한영 폰트 페어 (web-safe + Google Fonts)

| 분위기 | 영문 | 한글 |
|---|---|---|
| Modern / tech | `-apple-system, Inter, sans-serif` | `Pretendard, Noto Sans KR` |
| Editorial / serif | `Lora, Georgia` | `Noto Serif KR, Nanum Myeongjo` |
| Mono / code label | `JetBrains Mono, ui-monospace` | (영문만 권장) |
| Display | `Poppins, Outfit` | `Black Han Sans, Pretendard` |

**한글 보정**: 한글이 영문 대비 시각적으로 1~2 px 작아 보임. 한글 위주 라벨은 `font-size` 를 + 1~2 px 권장.

---

## 빠른 선택 가이드

| 콘텐츠 | 권장 테마 |
|---|---|
| 코드/엔지니어링 (ROS, AI, robotics) | **Tech Innovation** |
| 비즈니스/제안 / 신뢰 | Ocean Depths / Anthropic |
| 친환경/자연 (cobot2 light 모드) | Forest Canopy |
| 미니멀/일반 | Modern Minimalist |
| 따뜻한 톤 / 마케팅 | Golden Hour / Sunset Boulevard |
| 다크 + 미스터리 (게임/엔터테인먼트) | Midnight Galaxy |

사용자 선호 없으면 **Tech Innovation** (default) 사용.
