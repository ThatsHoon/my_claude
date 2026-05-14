# Export — slide HTML → PNG / PDF / PPTX

> deck 작성 후 발표/공유용으로 정적 이미지/문서로 export 하는 방법.

## 1. PDF (가장 간단)

브라우저 인쇄 → "Save as PDF":

1. 브라우저로 deck 열기 (`open deck.html` 또는 `xdg-open`)
2. `Cmd+P` / `Ctrl+P`
3. **Destination**: "Save as PDF"
4. **Layout**: Landscape (가로)
5. **Paper size**: A4 또는 Custom (1320×742 비율 ≈ 11.7×6.5 in)
6. **Margins**: None
7. **Background graphics**: ✓ (없으면 색 안 나옴 — boilerplate 에 `print-color-adjust: exact` 포함됨)
8. Save

`@media print` 가 `header` / `.tabs` 자동 숨김. 모든 슬라이드가 page-break 으로 분리되어 N 페이지 PDF.

## 2. PNG (탭별)

### A. chrome-devtools-mcp 사용 (가장 통합)

```
1. new_page({ url: 'file:///path/to/deck.html' })
2. resize_page({ width: 1320, height: 742 })
3. 각 탭별:
   - run script: switchView('<tab-name>')
   - take_screenshot({ filePath: '/tmp/deck-<tab>.png', fullPage: false })
```

MCP tool 호출은 Claude Code 안에서 직접 가능.

### B. Chrome headless CLI

```bash
# 각 탭별 PNG (URL fragment 사용 시 boilerplate 측에 hashchange 핸들러 필요)
for tab in overview system metrics; do
  google-chrome --headless --disable-gpu \
    --screenshot=/tmp/deck-$tab.png \
    --window-size=1320,742 \
    "file://$PWD/deck.html#$tab"
done
```

### C. Puppeteer 스크립트 (Node)

```js
import puppeteer from 'puppeteer';

const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.setViewport({ width: 1320, height: 742 });
await page.goto(`file://${process.cwd()}/deck.html`);

const tabs = await page.$$eval('.tab', els => els.map(e => e.dataset.view));
for (const tab of tabs) {
  await page.evaluate(t => window.switchView(t), tab);
  await new Promise(r => setTimeout(r, 200));  // render wait
  await page.screenshot({ path: `/tmp/deck-${tab}.png`, fullPage: false });
}
await browser.close();
```

`npm i puppeteer` 필요. 가장 강력하지만 의존성 무거움.

## 3. PPTX (.pptx 파일)

web-slide 는 HTML 출력. PPTX 가 필요하면 두 경로:

**A. PNG 으로 export 후 PPTX 에 삽입** (가장 빠름):
1. 위 §2 로 탭별 PNG 생성
2. `document-skills:pptx` 또는 PowerPoint 에서 PNG 를 슬라이드 배경으로 삽입

**B. HTML → PPTX 변환** (`document-skills:pptx` 의 html2pptx):
- 단, html2pptx 는 일반적 HTML 구조 지원. SVG 가 메인 컨텐츠인 web-slide 는 SVG 가 그대로 들어가지 않을 수 있음 — 결국 PNG 캡처 방식이 더 안정적.

권장: **PNG 캡처 → PPTX 삽입**.

## 4. 정적 사이트 / 공유

deck 은 **단일 HTML 파일** — 의존성 없음 (web font CDN 만 외부). 다음 방식으로 공유 가능:

- 파일 자체 이메일 첨부
- GitHub Pages / Netlify drop
- Notion / Confluence 등에 iframe embed
- USB / 로컬 zip

## 5. 인쇄 (실제 종이)

브라우저 `Cmd+P` → "Print":
- 16:9 PDF 가 A4 종이에 맞춰 축소됨 (가로 인쇄 권장)
- N 페이지 출력 (각 탭 1 페이지)
- Background graphics 켜기 (없으면 흰 배경)
