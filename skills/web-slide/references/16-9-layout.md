# 16:9 레이아웃 — 픽셀 좌표 가이드

> 모든 슬라이드는 정확히 1320×742 viewBox 사용. 이 비율은 16:9 (1320/742 = 1.779 ≈ 16/9 = 1.778).

## 1. SVG 골격

```html
<svg class="slide" viewBox="0 0 1320 742"
     preserveAspectRatio="xMidYMin meet"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- markers, gradients, patterns -->
  </defs>
  <rect width="100%" height="100%" fill="url(#grid)"
        pointer-events="none"/>
  <g id="content"></g>  <!-- 동적 렌더 대상 -->
</svg>
```

CSS:
```css
.slide {
  width: 100%;
  aspect-ratio: 16 / 9;
  min-height: 742px;
  max-width: 1320px;
  display: block;
}
```

## 2. 그리드 마진

```
┌────────────────────────────────────────────────┐ y=0
│           30 px top margin                     │
│   ┌────────────────────────────────────────┐   │ y=30
│   │                                        │   │
│   │       유효 콘텐츠 영역 1260×682          │   │
│   │       (x: 30~1290, y: 30~712)          │   │
│   │                                        │   │
│   └────────────────────────────────────────┘   │ y=712
│           30 px bottom margin                  │
└────────────────────────────────────────────────┘ y=742
x=0      30                                  1290   1320
```

- **좌측 마진**: `x: 30` 부터 시작
- **우측 마진**: 콘텐츠 끝은 `x: 1290` (좌+우 60 px 마진)
- **상하 마진**: `y: 30 ~ 712`
- **유효폭**: 1260 px
- **유효높이**: 682 px

## 3. 자주 쓰는 분할 패턴 (유효폭 1260)

### N-column equal
```js
const gap = 14;       // 컬럼 사이 간격
const startX = 30;    // 좌측 마진
const totalGap = gap * (N - 1);
const colW = (1260 - totalGap) / N;
// i 번째 column 의 x = startX + i * (colW + gap)
```

| N | colW (gap=14) | 용도 |
|---|---|---|
| 2 | 623 | 좌/우 대비 |
| 3 | 410 | feature/metric 3 column |
| 4 | 301 | grid layout |
| 5 | 244 | timeline 5단 (cobot2 v6~v10) |
| 7 | 165 | 7 탭 가로 펼침 |
| 8 | 142 | 8 metric pills |

### 좌측 큰 + 우측 작은
```
┌───────────────────────┬─────────────┐
│                       │             │
│      좌측 (800)       │  우측 (430) │
│                       │             │
└───────────────────────┴─────────────┘
  30                 830  844    1290
```
- gap 14 px
- 좌 800 + gap 14 + 우 430 + 30 마진 양쪽 = 1304... 까진 OK
- 또는 좌 612 / 가운데 280 / 우 380 (3-column 비균등)

### 헤더 + 메인 + 푸터 (수직)
```
y=0
├─ Title block:   y=0~80   (h=80)
├─ Hero section:  y=90~210 (h=120)
├─ Main content:  y=220~600 (h=380)
└─ Footer/notes:  y=620~720 (h=100)
y=742
```

## 4. 타이포그래피 크기

| 용도 | font-size (px) | 비고 |
|---|---|---|
| Slide 제목 | 22 | weight 800 |
| Sub-title (영문 UPPERCASE) | 10.5 | letter-spacing 1.4 |
| 섹션 번호 (01, 02) | 56 | Georgia italic, opacity 0.18 |
| 섹션 라벨 (영문 UPPERCASE) | 12 | weight 700, letter-spacing 1.3 |
| 섹션 설명 | 10~11 | text-3 컬러 |
| 본문 텍스트 | 12~14 | weight 500~700 |
| 큰 수치 (KPI) | 24~32 | weight 800 |
| Bar / chip 안 라벨 | 11~13 | mono 권장 |
| 작은 메타 | 9~10 | text-3 |

**한글 보정**: 한글이 영문 대비 시각적으로 작아 보임. 한글 위주 라벨은 위 표에서 +1~2 px.

## 5. 좌표 계산 cheat sheet

- **가운데 정렬 (가로)**: `x = 30 + 1260 / 2 = 660` (centered)
- **카드 가운데 정렬**: `cardCenter = cardX + cardW / 2`
- **bar chart 우측 끝**: `x = barX + barW - 6` (안쪽 6 px 패딩, text-anchor end)
- **카드 간격 14 px** 권장, **카드 내부 패딩 16~20 px**

## 6. 슬라이드 디버그 그리드

개발 중 좌표 점검용 — 32×32 grid pattern (cobot2 와 동일):

```html
<defs>
  <pattern id="grid" x="0" y="0" width="32" height="32"
           patternUnits="userSpaceOnUse">
    <path d="M 32 0 L 0 0 0 32" fill="none"
          stroke="var(--line)" stroke-width="0.5" opacity="0.3"/>
  </pattern>
</defs>
<rect width="100%" height="100%" fill="url(#grid)"
      pointer-events="none"/>
```

배포 시에는 grid opacity 0 으로 또는 통째로 제거.
