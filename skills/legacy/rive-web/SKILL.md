---
name: rive-web
description: Comprehensive guide for using Rive interactive animations on the web — integrating Rive runtimes (`@rive-app/canvas`, `@rive-app/webgl2`, `@rive-app/react-canvas`, `rive-react`) into JS/TS/React/Next.js apps, interpreting `.riv` internals (artboards, state machines, inputs, data binding, events, embedded Luau scripts), and the editor-side workflows for editing or exporting `.riv` files. Use this skill whenever the user mentions Rive, `.riv` files, `useRive`, `useStateMachineInput`, `RiveCanvas`, rive-app packages, embedding Rive in a webpage, debugging a Rive state machine, hooking React state to Rive inputs/view-models, decoding what an existing `.riv` does, exporting from the Rive editor, or asks anything about real-time interactive vector animation that resembles Rive — even when they don't explicitly name "Rive".
---

# Rive on the Web — Skill

This skill is the entry point for any task that involves **using, interpreting, or editing Rive animations in a web context**. It bundles deep references aggregated from the official rive-app GitHub repos (`rive-docs`, `rive-wasm`, `rive-react`) and the rive.app docs site, organised so you can load only the slice of documentation you actually need.

Rive is a real-time interactive animation tool. A `.riv` file is a self-contained binary that can hold:
- one or more **artboards** (compositions),
- timeline animations,
- a **state machine** (the most powerful runtime mechanism — drives transitions via inputs and listeners),
- typed **inputs** (Boolean / Number / Trigger),
- **data bindings** with view-models (Rive's MVVM-ish layer for two-way reactive state),
- **Rive events** (arbitrary signals fired from the runtime to the host app),
- optional embedded **Luau scripts** (Rive Scripting),
- referenced or embedded assets (images, fonts, audio).

Web runtimes render this on `<canvas>` via either Canvas2D, WebGL2, or the new Rive Renderer (preferred for newer features). The two npm-level entry points are:

- **Vanilla JS / Wasm** — `@rive-app/canvas`, `@rive-app/webgl2`, `@rive-app/canvas-lite`, `@rive-app/webgl2-advanced` (the underlying engine lives in `rive-app/rive-wasm`).
- **React** — `@rive-app/react-canvas`, `@rive-app/react-webgl2` (hooks-based wrapper exposing `useRive`, `useStateMachineInput`, `useViewModel`, `useViewModelInstance*` etc.). The legacy package is `rive-react`.

## How to use this skill

The body of this file is intentionally short. **Most of the substantive material is in `references/`.** Read the relevant reference file when, and only when, it matches the user's task — that keeps your context lean.

| User intent | Read first |
|---|---|
| Integrate Rive into vanilla JS / Next.js / non-React | `references/web-runtime.md` |
| Integrate into React / Next.js with React Server/Client Components | `references/react.md` |
| Drive an animation from app state, debug a state machine, wire data binding | `references/state-and-data.md` |
| Understand or describe what an existing `.riv` does (interpretation) | `references/state-and-data.md` first, then `references/scripting.md` if scripts are embedded, then `references/editor-workflow.md` for editor-side concepts |
| Edit a `.riv` in the Rive editor, export for runtime, manage assets | `references/editor-workflow.md` |
| Inspect or write Luau scripts inside a `.riv` | `references/scripting.md` |

If multiple slices apply, prefer reading them sequentially as the task progresses rather than upfront.

For the canonical online docs, also consider querying context7 with library IDs `/rive-app/rive-docs` (broadest), `/websites/rive_app` (editor-leaning), `/rive-app/rive-react` (React API), `/rive-app/rive-wasm` (web runtime). The cloned repos under `/home/hoon/rive-research/repos/` are the local source of truth for this skill — re-aggregate references from there if the user updates them.

## Mental model — read this before answering

You will give better answers if you keep these distinctions straight:

1. **Editor-time vs runtime.** What the designer sets up in the Rive editor (artboards, state machines, view-model schemas, exported names) is what the runtime can see. If a name doesn't exist in the file, the runtime cannot reach it — no amount of code will fix that. When debugging, the first question is always "is this name actually exported?".

2. **State machine vs raw timeline.** Most production work uses a **state machine**, not raw timeline `.play()`. Inputs (Boolean / Number / Trigger) are the public API of the state machine; transitions and layers are internal. From the web side you interact almost exclusively with inputs, view-model properties, and Rive events.

3. **Data binding is the modern path.** Older Rive workflows hardcode logic in the state machine and expose it through a few inputs. Newer workflows put state on a **view-model** (typed properties: number, string, boolean, color, enum, image, list, nested view-model) and bind shapes/transitions to those properties. From web code you `bindViewModelInstance` and write to typed properties; the animation reacts. Use this when the project already commits to view-models.

4. **Rive Events are not state-machine inputs.** Inputs go *into* Rive; **Rive events** come *out* (open URL, play sound, custom payload). Wire them with `riveInstance.on(EventType.RiveEvent, …)` (vanilla) or `useRiveEvents` / event listener hooks (React).

5. **Renderer choice matters.** Default new code should target the Rive Renderer via `@rive-app/webgl2` (or `webgl2-advanced` for vector feathering, layout, advanced text). Canvas2D backend is fine for simple cases and small bundles. If `useRive` is silently empty, re-check the renderer and that the artboard name matches.

6. **Layout and resize are not free.** Without `useDevicePixelRatio: true` and a resize observer (or `Layout` config), Rive renders blurry on retina or stretched on resize. Both runtimes ship helpers — link to them rather than inventing your own.

7. **Asset loading.** Assets marked **Referenced** in the editor are *not* embedded in `.riv`; on export they ship as a zip alongside the `.riv` and the runtime needs an `assetLoader` to fetch them. Assets marked **Embedded** are inside the binary (larger file, simpler load). Get this wrong and images/fonts silently fail.

## Output expectations

When the user asks for code, prefer **complete, runnable snippets** with the relevant imports and a minimal HTML / React shell, not pseudo-code. Use TypeScript by default for React examples. Quote exact npm package names — there are several near-identical names (`rive-react` vs `@rive-app/react-canvas`) and copying the wrong one is the single most common Rive integration bug.

When the user asks you to interpret an existing `.riv` (e.g. they paste the editor's hierarchy or describe what they see), structure the answer as:

```
# What this file does
- Artboards: …
- State machines per artboard: …
- Inputs: …
- View-models / data bindings: …
- Rive events: …
- Embedded scripts: …
# How a host app would drive it
- Minimum integration code …
- What each input/property does at runtime …
# Likely gotchas given the structure
- …
```

When the user asks about editor workflow (e.g. "how do I export this for the web"), be explicit about which export menu, what the resulting bundle contains, and what the runtime side has to do to consume it — many bugs come from mismatched export options.

## Common quick-reference snippets

These are short enough to inline. Anything longer goes into `references/`.

### Vanilla JS — load + run a state machine

```ts
import { Rive, Layout, Fit, Alignment } from "@rive-app/webgl2";

const r = new Rive({
  src: "/animations/hero.riv",
  canvas: document.getElementById("hero") as HTMLCanvasElement,
  artboard: "Main",
  stateMachines: "State Machine 1",
  autoplay: true,
  layout: new Layout({ fit: Fit.Layout, alignment: Alignment.Center }),
  onLoad: () => r.resizeDrawingSurfaceToCanvas(),
});

window.addEventListener("resize", () => r.resizeDrawingSurfaceToCanvas());

// Control an input
const inputs = r.stateMachineInputs("State Machine 1");
const hover = inputs.find((i) => i.name === "Hover");
hover?.fire?.(); // Trigger
```

### React — `useRive` + input

```tsx
import { useRive, useStateMachineInput, Layout, Fit, Alignment } from "@rive-app/react-canvas";

export function Hero() {
  const { rive, RiveComponent } = useRive({
    src: "/animations/hero.riv",
    artboard: "Main",
    stateMachines: "State Machine 1",
    autoplay: true,
    layout: new Layout({ fit: Fit.Layout, alignment: Alignment.Center }),
  });

  const hover = useStateMachineInput(rive, "State Machine 1", "Hover");

  return (
    <div onMouseEnter={() => hover?.fire()}>
      <RiveComponent />
    </div>
  );
}
```

### React — view-model / data binding (newer API)

The React data-binding hooks live in `@rive-app/react-canvas` only. Each typed property has its **own dedicated hook** — do not invent hooks like `vm.string()` or `instance.number()`; those don't exist. The full set, all imported from `@rive-app/react-canvas`:

- `useViewModel(rive, { name?: string, useDefault?: boolean })` — get the view-model schema
- `useViewModelInstance(viewModel, { rive, name?, useDefault?, useNew? })` — get an instance bound to the rive instance
- `useViewModelInstanceString(path, { viewModelInstance })` → `{ value, setValue }`
- `useViewModelInstanceNumber(path, { viewModelInstance })` → `{ value, setValue }`
- `useViewModelInstanceBoolean(path, { viewModelInstance })` → `{ value, setValue }`
- `useViewModelInstanceColor(path, { viewModelInstance })` → `{ value, setValue, setRgb, setRgba, setAlpha, setOpacity }`
- `useViewModelInstanceEnum(path, { viewModelInstance })` → `{ value, values, setValue }`
- `useViewModelInstanceTrigger(path, { viewModelInstance, onTrigger })` → `{ trigger }`
- `useViewModelInstanceImage(path, { viewModelInstance })` → `{ setValue }` (value is *write-only*; pass a decoded `RenderImage`, not a URL or `ImageBitmap`)
- `useViewModelInstanceList(path, { viewModelInstance })` for list properties

```tsx
import {
  useRive, useViewModel, useViewModelInstance,
  useViewModelInstanceString, useViewModelInstanceNumber,
  useViewModelInstanceImage,
  decodeImage,
} from "@rive-app/react-canvas";

const { rive, RiveComponent } = useRive({ src: "/file.riv", autoBind: true });
const vm = useViewModel(rive, { name: "MainVM" });
const inst = useViewModelInstance(vm, { rive });

const username = useViewModelInstanceString("username", { viewModelInstance: inst });
const unread   = useViewModelInstanceNumber("unreadCount", { viewModelInstance: inst });
const avatar   = useViewModelInstanceImage("avatarUrl", { viewModelInstance: inst });

useEffect(() => { username.setValue("Hoon"); }, [username]);

useEffect(() => {
  fetch("/avatar.png")
    .then(r => r.arrayBuffer())
    .then(buf => decodeImage(new Uint8Array(buf)))
    .then(renderImage => {
      avatar.setValue(renderImage);
      renderImage.unref();   // Rive uses ref-counting. Always unref() after handing the image off, or memory leaks.
    });
}, [avatar]);
```

The image hook is the most error-prone Rive API. The four mistakes to avoid:

1. **Don't pass a string URL** — Rive cannot fetch on your behalf for view-model image properties.
2. **Don't pass `ImageBitmap` from `createImageBitmap`** — that's a browser type, not a Rive `RenderImage`. Use `decodeImage(Uint8Array)` (or `decodeFont` for fonts).
3. **Don't forget `.unref()`** — `decodeImage` / `decodeFont` return ref-counted handles; if you don't call `unref()` after `setValue()` / `setRenderImage()`, you leak GPU memory.
4. **Don't assume `RiveFile.cleanup` happens automatically** — when the component unmounts manually-cached files, call `.cleanup()` on them.

If the user is on the older `rive-react` package, port to `@rive-app/react-canvas`; data-binding hooks and the modern API only live in the new one.

### Vanilla JS — assetLoader for Referenced assets

When a `.riv` references external assets (image / font / audio), provide an `assetLoader`. The callback returns `true` if **you** handled the asset (so the runtime won't try anything else), or `false` to fall back to the runtime's default behavior (Embedded bytes or Hosted CDN UUID).

```ts
import { Rive, decodeImage, decodeFont, ImageAsset, FontAsset } from "@rive-app/webgl2";

new Rive({
  src: "/animations/splash.riv",
  canvas,
  assetLoader: (asset, bytes) => {
    if (bytes.length > 0) return false;          // Embedded — let runtime handle.
    if ((asset as any).cdnUuid?.length) return false; // Hosted — let runtime fetch from Rive CDN.

    if (asset.isImage) {
      fetch(`/animations/${asset.uniqueFilename}`)
        .then(r => r.arrayBuffer())
        .then(buf => decodeImage(new Uint8Array(buf)))
        .then(img => { (asset as ImageAsset).setRenderImage(img); img.unref(); });
      return true;
    }
    if (asset.isFont) {
      fetch(`/animations/${asset.uniqueFilename}`)
        .then(r => r.arrayBuffer())
        .then(buf => decodeFont(new Uint8Array(buf)))
        .then(font => { (asset as FontAsset).setFont(font); font.unref(); });
      return true;
    }
    return false;
  },
});
```

`asset.uniqueFilename` (or `asset.name + asset.fileExtension`) is what you match against the unzipped files — not just `asset.name`. Mismatched names fail silently (asset stays missing, no error thrown).

## Editor export options — exact terminology

The Rive editor's export menu has options that are easy to confuse:

- **For runtime** → produces a `.riv` (and an accompanying zip if any assets are Referenced). Optimized for size; editor metadata is stripped. This is what you ship to web/mobile/game runtimes.
- **For backup** → produces a `.rev` file (full editor state, fully re-importable). The runtime cannot load `.rev`. Use it only for archiving editable source. Often gated behind paid plans.
- **Referenced** assets → external. On "For runtime" export, all referenced assets ship in a zip alongside the `.riv`. The runtime needs an `assetLoader`.
- **Embedded** assets → bundled inside the `.riv`. Larger binary, simpler integration. The runtime resolves them automatically.
- **Hosted** assets → not in the file at all; only a CDN UUID is stored. The runtime fetches from Rive's CDN at load time. No host-side action needed (except CSP allowances).

Saying "export the file" without specifying which option will lead the user astray — always ask, or default to "For runtime".

## When to push back

Skill caveats — say something rather than producing wrong code:

- If the user is on **Rive 1.x** APIs (e.g. `play()` / `pause()` on raw animation names with no state machine), call out that they're on the legacy timeline API and ask whether the file actually has no state machine, or whether they want to migrate.
- If they ask to **edit a `.riv` programmatically** outside the editor — there is no public Rive file-editing SDK; programmatic changes happen through state-machine inputs / view-model properties at runtime, and structural edits go through the editor (or its MCP integration). Don't invent a binary editor.
- If a feature appears to require the **Rive Renderer** (advanced text, vector feathering, layout-based scaling) but the user is using `@rive-app/canvas` (Canvas2D), tell them to switch to `@rive-app/webgl2` or `webgl2-advanced` rather than trying to make Canvas2D do it.
- If they want to fire a state-machine **Trigger inside `onLoad`**, push back: the React runtime's `onLoad` fires before the state machine is fully initialized in some cases, so the trigger is silently missed. Use `useEffect(..., [rive, input])` watching for the input to become non-null and fire it then. (This is the single most common "my IntroPlayed never fires" bug.)
- If they pass `useDevicePixelRatio: false` (or omit the option) and complain about **blurry rendering on retina** — point out that `@rive-app/react-canvas` defaults `useDevicePixelRatio: true` *only since v4*; older versions need it explicitly, and the vanilla `@rive-app/canvas` runtime always needs `r.resizeDrawingSurfaceToCanvas()` on load + resize.
- If they assign a JS `ImageBitmap` or a URL string to a view-model image property, push back — it has to be a `RenderImage` from `decodeImage`, and `unref()` is required after handing it off.

## Files in this skill

```
rive-web/
├── SKILL.md                   ← you are here
└── references/
    ├── web-runtime.md         ← vanilla JS, Wasm, all common runtime concepts
    ├── react.md               ← React hooks API + examples + package README
    ├── state-and-data.md      ← state machines, inputs, data binding, events
    ├── editor-workflow.md     ← editor fundamentals, exporting, asset handling
    └── scripting.md           ← Rive Scripting (Luau) — for files that embed scripts
```

Each reference file is an aggregated dump of the relevant `.mdx` pages from `rive-app/rive-docs` plus the official READMEs. They are large (~60–160 KB). Read only the one(s) that match the current task.
