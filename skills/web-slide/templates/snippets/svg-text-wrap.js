/**
 * svg-text-wrap.js — SVG text 수동 wrap 헬퍼
 *
 * SVG <text> 는 자동 wrap 안 됨. 이 헬퍼로 max-chars 기준 split.
 *
 * 사용:
 *   import { wrapSvgText } from './snippets/svg-text-wrap.js';
 *   // 또는 inline (boilerplate 에 이미 포함)
 *
 *   wrapSvgText('긴 텍스트입니다 ...', 24).forEach((ln, i) => {
 *     $content.appendChild(svg('text', {
 *       x: 30, y: y0 + i * lineHeight,
 *       fill: 'var(--text)', 'font-size': 12,
 *       text: ln,
 *     }));
 *   });
 *
 * 한글 권장 maxChars: 18~24 (영문 36~50 대비 짧게)
 */

export function wrapSvgText(text, maxChars = 36) {
  if (!text) return [''];
  if (text.length <= maxChars) return [text];

  const lines = [];
  let remaining = text;
  while (remaining.length > maxChars) {
    // 공백에서 끊기 시도
    let cut = remaining.lastIndexOf(' ', maxChars);
    // 공백이 너무 앞에 있으면 (전체 1/2 미만) 강제 cut
    if (cut < maxChars * 0.5) cut = maxChars;
    lines.push(remaining.slice(0, cut));
    remaining = remaining.slice(cut).trim();
  }
  if (remaining) lines.push(remaining);
  return lines;
}

/**
 * wrapSvgTspan — <tspan> 으로 multiline 한 텍스트 요소 생성
 *
 * 한 <text> 요소 안에 <tspan> 여러 개. dy 로 줄간격 조정.
 *
 * 사용:
 *   const SVG_NS = 'http://www.w3.org/2000/svg';
 *   const t = document.createElementNS(SVG_NS, 'text');
 *   t.setAttribute('x', 30);
 *   t.setAttribute('y', 100);
 *   t.setAttribute('fill', 'var(--text)');
 *   t.setAttribute('font-size', 12);
 *   wrapSvgTspan(t, '긴 텍스트', 24, 1.3);
 *   $content.appendChild(t);
 */
export function wrapSvgTspan(textEl, text, maxChars = 36, lineHeightEm = 1.2) {
  const SVG_NS = 'http://www.w3.org/2000/svg';
  const lines = wrapSvgText(text, maxChars);
  const x = textEl.getAttribute('x');
  lines.forEach((ln, i) => {
    const span = document.createElementNS(SVG_NS, 'tspan');
    span.setAttribute('x', x);
    if (i > 0) span.setAttribute('dy', `${lineHeightEm}em`);
    span.textContent = ln;
    textEl.appendChild(span);
  });
  return textEl;
}
