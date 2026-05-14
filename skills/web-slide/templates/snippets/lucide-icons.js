/**
 * lucide-icons.js — Lucide icon path 데이터
 *
 * 자주 쓰는 30개 icon 을 SVG path 데이터로 제공. 이모지 대신 사용.
 * 사용자 선호: "유치한 이모지 대신 lucide 아이콘"
 *
 * Lucide license: ISC (https://lucide.dev)
 *
 * 사용:
 *   import { LUCIDE } from './snippets/lucide-icons.js';
 *   // 또는 inline 으로 직접 복사
 *
 *   $content.appendChild(svg('g', { transform: 'translate(30, 100)' },
 *     svg('svg', {
 *       viewBox: '0 0 24 24', width: 24, height: 24,
 *       fill: 'none', stroke: 'var(--accent)', 'stroke-width': 2,
 *       'stroke-linecap': 'round', 'stroke-linejoin': 'round',
 *     }, svg('path', { d: LUCIDE.cpu }))
 *   ));
 *
 * SVG 안에 inline icon 으로 그리려면 `<path d="${LUCIDE.cpu}"/>` 그대로.
 * 모든 icon 은 24×24 viewBox.
 */

export const LUCIDE = {
  // ─── Tech / hardware ────────────────────────────
  cpu:       'M4 4h16v16H4z M9 1v3 M15 1v3 M9 20v3 M15 20v3 M20 9h3 M20 14h3 M1 9h3 M1 14h3 M9 9h6v6H9z',
  server:    'M2 2h20v8H2z M2 14h20v8H2z M6 6h.01 M6 18h.01',
  database:  'M12 2 C7 2 3 4 3 6 v12 c0 2 4 4 9 4 s9-2 9-4 V6 c0-2-4-4-9-4z M3 6 c0 2 4 4 9 4 s9-2 9-4 M3 12 c0 2 4 4 9 4 s9-2 9-4',
  network:   'M16 16h-3a4 4 0 0 1 0-8h3 M8 16h3a4 4 0 0 0 0-8H8 M2 12h20',
  hard_drive: 'M22 12h-20 M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z M6 16h.01 M10 16h.01',

  // ─── Data / charts ──────────────────────────────
  bar_chart: 'M12 20V10 M18 20V4 M6 20v-6',
  line_chart: 'M3 3v18h18 M7 14l4-4 4 4 6-6',
  pie_chart: 'M21.21 15.89A10 10 0 1 1 8 2.83 M22 12A10 10 0 0 0 12 2v10z',
  activity:  'M22 12h-4l-3 9L9 3l-3 9H2',

  // ─── ML / AI ────────────────────────────────────
  brain:     'M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3 2.5 2.5 0 0 1 2.46-2.04z M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3 2.5 2.5 0 0 0-2.46-2.04z',
  bot:       'M12 8V4H8 M4 18 L4 8 a2 2 0 0 1 2-2 h12 a2 2 0 0 1 2 2 v10 M4 20 a2 2 0 0 0 2 2 h12 a2 2 0 0 0 2-2 M2 14h2 M20 14h2 M15 13v2 M9 13v2',
  zap:       'M13 2L3 14h9l-1 8 10-12h-9l1-8z',
  sparkles:  'M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.582a.5.5 0 0 1 0 .962L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z',

  // ─── Robotics / motion ──────────────────────────
  robot:     'M12 2v4 M5 10h14v9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-9z M10 14h4 M14 18h.01 M10 18h.01',
  rocket:    'M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0 M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5',
  move:      'M5 9L2 12l3 3 M9 5l3-3 3 3 M15 19l-3 3-3-3 M19 9l3 3-3 3 M2 12h20 M12 2v20',
  target:    'M12 22a10 10 0 1 1 0-20 10 10 0 0 1 0 20z M12 18a6 6 0 1 1 0-12 6 6 0 0 1 0 12z M12 14a2 2 0 1 1 0-4 2 2 0 0 1 0 4z',

  // ─── UI / common ────────────────────────────────
  check:     'M20 6L9 17l-5-5',
  check_circle: 'M22 11.08V12a10 10 0 1 1-5.93-9.14 M22 4L12 14.01l-3-3',
  x:         'M18 6L6 18 M6 6l12 12',
  x_circle:  'M12 22a10 10 0 1 1 0-20 10 10 0 0 1 0 20z M15 9l-6 6 M9 9l6 6',
  alert:     'M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z M12 9v4 M12 17h.01',
  info:      'M12 22a10 10 0 1 1 0-20 10 10 0 0 1 0 20z M12 16v-4 M12 8h.01',

  // ─── Flow / arrows ──────────────────────────────
  arrow_right: 'M5 12h14 M12 5l7 7-7 7',
  arrow_down:  'M12 5v14 M19 12l-7 7-7-7',
  git_branch:  'M6 3v12 M18 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M15 6a9 9 0 0 0-9 9',
  workflow:    'M3 3h6v6H3z M15 3h6v6h-6z M9 15h6v6H9z M9 6h12 M12 12v3',

  // ─── Time / state ───────────────────────────────
  clock:     'M12 22a10 10 0 1 1 0-20 10 10 0 0 1 0 20z M12 6v6l4 2',
  layers:    'M12 2 L2 7l10 5 10-5z M2 17l10 5 10-5 M2 12l10 5 10-5',

  // ─── File / package ─────────────────────────────
  package:   'M16.5 9.4 7.5 4.21 M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z M3.27 6.96 12 12.01l8.73-5.05 M12 22.08V12',
  code:      'M16 18l6-6-6-6 M8 6l-6 6 6 6',
};

/**
 * 사용 예시 — SVG icon 한 개 그리기:
 *
 *   const ICON = LUCIDE.cpu;
 *   $content.appendChild(svg('g', { transform: 'translate(30, 100)' },
 *     svg('rect', { x: 0, y: 0, width: 32, height: 32, rx: 6,
 *                   fill: 'var(--bg-3)', stroke: 'var(--line-2)' }),
 *     svg('svg', {
 *       x: 4, y: 4, viewBox: '0 0 24 24', width: 24, height: 24,
 *       fill: 'none', stroke: 'var(--accent)', 'stroke-width': 2,
 *       'stroke-linecap': 'round', 'stroke-linejoin': 'round',
 *     }, svg('path', { d: ICON }))
 *   ));
 *
 * Tip: icon 의 color 는 `stroke: 'var(--accent)'` 으로 테마 토큰 사용.
 */
