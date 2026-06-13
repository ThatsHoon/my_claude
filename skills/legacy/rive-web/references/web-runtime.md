# Rive Web Runtime (Vanilla JS / Wasm) — Aggregated Reference

Source: rive-app/rive-docs · rive-app/rive-wasm (cloned)

## Common runtime concepts (apply to vanilla & React)

---
## runtimes/getting-started.mdx

---
title: 'Getting Started with the Rive Runtimes'
sidebarTitle: 'Getting Started'
description: 'Run Rive on your platform of choice.'
---

import NoteOnFeatureSupport from "/snippets/runtimes/rendering-feature-support.mdx"

The Rive runtimes are open-source libraries that allow you to load and control your animations in apps, games, and websites. Dive into each of the subpages to get started!

<NoteOnFeatureSupport/>

## How to use this guide

In this section you'll find runtime subpages that provide all the needed information and resources to get started on your platform of choice. See [Installation and getting started](#installation-and-getting-started) below.

You'll also find pages dedicated to controlling your Rive graphics at runtime. For example, updating data bound properties and loading in assets out-of-band. See [Graphic control and interaction](#graphic-control-and-interaction) below.

### Installation and getting started

<Info>
 Make sure to check out the additional documentation provided under each runtime section. These documents provide platform-specific considerations, migration guides, and advanced usage information.
</Info>

<CardGroup cols={2}>
  <Card title="Web (JS)" href="/runtimes/web"  icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>}>
    This guide documents how to get started using the Web runtime library.
  </Card>
  <Card title="React" href="/runtimes/react" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>}>
    This guide documents how to get started using the React runtime library.
  </Card>
  <Card title="React Native" href="/runtimes/react-native" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>}>
    This guide documents how to get started using the React Native runtime library.
  </Card>
  <Card title="Apple" href="/runtimes/apple" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>}>
    This guide documents how to get started using the Apple runtime library.
  </Card>
  <Card title="Android" href="/runtimes/android"icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>}>
    This guide documents how to get started using the Android runtime library.
  </Card>
  <Card title="Flutter" href="/runtimes/flutter" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>}>
    This guide documents how to get started using the Flutter runtime library.
  </Card>
  <Card title="Unity" href="/game-runtimes/unity" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>}>
    This guide documents how to get started using the Unity runtime library.
  </Card>
  <Card title="Unreal" href="/game-runtimes/unreal" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>}>
    This guide documents how to get started using the Unreal runtime library.
  </Card>
</CardGroup>

## Other sections

<CardGroup cols={2}>
  <Card title="Choose a Renderer" href="/runtimes/choose-a-renderer" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>}>
    Specify the desired renderer to use at runtime. Each runtime provides different options. We recommend using the Rive Renderer.
  </Card>
  <Card title="Format" href="/runtimes/advanced-topic/format" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>}>
    The Rive File format.
  </Card>
  <Card title="Feature Support" href="/feature-support" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>}>
    Runtime support for Rive features.
  </Card>
 </CardGroup>


## Versioning

As we publish updates to our Rive editor, we will occasionally push updated runtimes to support the new features. See [Feature Support](/feature-support) for the required minimum runtime version needed for specific features.

In most cases, the newest runtimes will also support previous versions of your Rive assets, so you will not need to re-export assets to update to the latest runtimes.

There are a number of ways to export your Rive files in cases where re-exporting is necessary to take advantage of the latest features. Check out our documentation on [Exporting](/editor/exporting) for more information.


## Official runtimes

Check out the runtime subpages for steps on how to get started!

<Accordion title="Web">
  All web runtimes are distributed via npm:

  - [GitHub](https://github.com/rive-app/rive-wasm)
  - [canvas](https://www.npmjs.com/package/@rive-app/canvas)
  - [webgl2](https://www.npmjs.com/package/@rive-app/webgl2)
  - [canvas-lite](https://www.npmjs.com/package/@rive-app/canvas-lite)

  **See [Canvas vs WebGL](/runtimes/web/canvas-vs-webgl) for package guidance and sizing tradeoffs.**
</Accordion>

<Accordion title="React">
  All React runtimes are distributed via npm:

  - [GitHub](https://github.com/rive-app/rive-react)
  - [canvas](https://www.npmjs.com/package/@rive-app/react-canvas)
  - [canvas-lite](https://www.npmjs.com/package/@rive-app/react-canvas-lite)
  - [webgl2](https://www.npmjs.com/package/@rive-app/react-webgl2)

</Accordion>

<Accordion title="Apple">
  The Apple runtime is distributed by:

  - [Swift Package Manager](https://swiftpackageregistry.com/rive-app/rive-ios)
  - Cocoapods

  [GitHub](https://github.com/rive-app/rive-ios)
</Accordion>

<Accordion title="Android">

  - [Maven](https://search.maven.org/artifact/app.rive/rive-android)
  - [GitHub](https://github.com/rive-app/rive-android)
</Accordion>

<Accordion title="Flutter">

  - [pub.dev](https://pub.dev/packages/rive)
  - [GitHub](https://github.com/rive-app/rive-flutter)
</Accordion>

<Accordion title="C++ (Mac/Linux/Windows)">

  - [GitHub](https://github.com/rive-app/rive-cpp)
</Accordion>

<Accordion title="C#">

  - [UWP (Recommended)](https://dev.azure.com/dotnet/CommunityToolkit/_artifacts/feed/CommunityToolkit-Labs/NuGet/CommunityToolkit.Labs.Uwp.RivePlayer/overview/0.0.1)
  - [WinUI](https://dev.azure.com/dotnet/CommunityToolkit/_artifacts/feed/CommunityToolkit-Labs/NuGet/CommunityToolkit.Labs.WinUI.RivePlayer/overview/0.0.1)
  - (High-level API) [RivePlayer Github](https://github.com/CommunityToolkit/Labs-Windows/blob/main/labs/RivePlayer/samples/RivePlayer.Samples/RivePlayer.md)
  - (Low-level API) [RiveSharp Github](https://github.com/rive-app/rive-sharp)

  **High-level APIs**:

  - [WinUI (High-level)](https://dev.azure.com/dotnet/CommunityToolkit/_artifacts/feed/CommunityToolkit-Labs/NuGet/CommunityToolkit.Labs.WinUI.RivePlayer/overview/0.0.1)
</Accordion>
<Accordion title="React Native">
  - [npm](https://www.npmjs.com/package/rive-react-native)
  - [GitHub](https://github.com/rive-app/rive-react-native)


</Accordion>

## Community runtimes

| **Runtime** | **Author** | **Link** |
| --- | --- | --- |
| QtQuick | [basysKom](https://github.com/basysKom) | [Github](https://github.com/basysKom/RiveQtQuickPlugin) |
| UWP (C#) | Windows Community Toolkit | [Github](https://github.com/CommunityToolkit/Labs-Windows/blob/main/components/RivePlayer/samples/RivePlayer.md) |
| RiveCMP | [muazkadan](https://github.com/muazkadan) | [Github](https://github.com/muazkadan/Rive-CMP/blob/main/README.md) |


## Handling .riv files

When checking in `.riv` files with Git, consider adding a `.gitattributes` file and marking `.riv` files as `binary` files to prevent Git from changing line endings when these files are checked in. Otherwise, some platforms may accidentally corrupt the `.riv` file where there are line returns (i.e. Windows CRLF line endings vs LF line endings) and cause issues at runtime when the file is read.

```riv
.gitattributes

*.riv binary
```

## Licensing

Our official runtimes are all open-source and licensed under the [MIT License](https://choosealicense.com/licenses/mit/). You're free to use them for personal and commercial applications.

## Contributing

Since all the runtimes are open-source, we encourage you to dive in and take a look around! If you see something missing or feel you can improve upon it, then fork it!
---
## runtimes/animation-playback.mdx

---
title: "Animation Playback"
description: "⚠️ DEPRECATED: Use State Machines instead of direct animation playback at runtime"
noindex: true
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'

Documentation for working with **Animation Playback** has moved to runtime-specific pages.

Select your runtime below to see the relevant guide.

<Runtimes
  runtimes={{
    web: '/runtimes/web/animation-playback',
    react: '/runtimes/react/animation-playback',
    reactNative: '/runtimes/react-native/animation-playback',
    flutter: '/runtimes/flutter/animation-playback',
    apple: '/runtimes/apple/animation-playback',
    android: '/runtimes/android/animation-playback'
  }}
/>
---
## runtimes/artboards.mdx

---
title: 'Artboards'
description: 'Selecting which artboard to render at runtime'
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'

A Rive file can contain multiple [Artboards](/editor/fundamentals/artboards), each representing a separate animation or interface. When rendering a `.riv` file in your application, you choose which artboard to display using your runtime’s API.

Select your runtime below to see the relevant guide.

<Runtimes
  runtimes={{
    web: '/runtimes/web/artboards',
    react: '/runtimes/react/artboards',
    reactNative: '/runtimes/react-native/artboards',
    flutter: '/runtimes/flutter/artboards',
    apple: '/runtimes/apple/artboards',
    android: '/runtimes/android/artboards',
    unity: '/game-runtimes/unity/fundamentals#artboards',
    unreal: '/game-runtimes/unreal/getting-started'
  }}
/>
---
## runtimes/caching-a-rive-file.mdx

---
title: "Caching a Rive File"
description: ""
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'
import { Demos } from "/snippets/demos.jsx";


Caching a Rive file lets your app reuse a loaded .riv file instead of loading and parsing it again. This can improve performance when the same file is rendered multiple times.

Each runtime provides its own APIs and patterns for loading, reusing, and caching Rive files.

<Runtimes
  runtimes={{
    web: '/runtimes/web/caching-a-rive-file',
    react: '/runtimes/react/caching-a-rive-file',
    reactNative: '/runtimes/react-native/caching-a-rive-file',
    flutter: '/runtimes/flutter/caching-a-rive-file',
    apple: '/runtimes/apple/caching-a-rive-file',
    android: '/runtimes/android/caching-a-rive-file'
  }}
/>

## Explore demos

<Demos examples={["cachingARiveFile"]} />
---
## runtimes/inputs.mdx

---
title: "Inputs"
description: "⚠️ DEPRECATED: Use Data Binding instead of Inputs for controlling Rive animations"
noindex: true
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'

Documentation for working with **Inputs** has moved to runtime-specific pages.

Select your runtime below to see the relevant guide.

<Runtimes
  runtimes={{
    web: '/runtimes/web/inputs',
    react: '/runtimes/react/inputs',
    reactNative: '/runtimes/react-native/inputs',
    flutter: '/runtimes/flutter/inputs',
    apple: '/runtimes/apple/inputs',
    android: '/runtimes/android/inputs',
    unity: '/game-runtimes/unity/inputs'
  }}
/>
---
## runtimes/layout.mdx

---
title: "Layout"
description: "Control how graphics are laid out within the canvas, view, widget, or texture."
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'
import { Demos } from "/snippets/demos.jsx";

Layouts control how elements in a Rive artboard respond to different container sizes.

Each runtime provides APIs for configuring layout behavior and controlling how the artboard fits its container.

<Runtimes
  runtimes={{
    web: '/runtimes/web/layouts',
    react: '/runtimes/react/layouts',
    reactNative: '/runtimes/react-native/layouts',
    flutter: '/runtimes/flutter/layouts',
    apple: '/runtimes/apple/layouts',
    android: '/runtimes/android/layouts',
    unity: '/game-runtimes/unity/layouts'
  }}
/>

## Explore demos

<Demos examples={["layouts"]} />


---
## runtimes/loading-assets.mdx

---
title: "Loading Assets"
description: "Loading and replacing assets dynamically at runtime"
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'

Loading assets allows your app to provide external resources used by a Rive file at runtime.
This can include images, fonts, and other assets referenced by the .riv file.

Each runtime provides APIs for loading and resolving these assets in your application.

<Runtimes
  runtimes={{
    web: '/runtimes/web/loading-assets',
    react: '/runtimes/react/loading-assets',
    reactNative: '/runtimes/react-native/loading-assets',
    flutter: '/runtimes/flutter/loading-assets',
    apple: '/runtimes/apple/loading-assets',
    android: '/runtimes/android/loading-assets',
    unity: '/game-runtimes/unity/loading-assets'
  }}
/>
---
## runtimes/playing-audio.mdx

---
title: "Playing Audio"
description: "Playing Rive audio events"
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'

Playing audio allows sounds embedded in a Rive file to play during animations or state machine interactions.

Each runtime provides APIs for enabling and controlling audio playback.

<Runtimes
  runtimes={{
    web: '/runtimes/web/playing-audio',
    react: '/runtimes/react/playing-audio',
    reactNative: '/runtimes/react-native/playing-audio',
    flutter: '/runtimes/flutter/playing-audio',
    apple: '/runtimes/apple/playing-audio',
    android: '/runtimes/android/playing-audio',
    unity: '/game-runtimes/unity/audio'
  }}
/>
---
## runtimes/runtime-sizes.mdx

---
title: "Runtime Sizes"
description: "Last updated: January 2026"
---

<Tabs>
  <Tab title="Web (JS)">
    <Note>The majority of the size is the WASM library, which the table below represents.</Note>

    Using: `brotli -9` for compression.

      | Runtime     | Uncompressed | Compressed |
      | ----------- | ------------ | ---------- |
      | canvas-lite | 707KB        | 222KB      |
      | canvas      | 1728KB       | 567KB      |
      | webgl2      | 2179KB       | 648KB      |

  </Tab>
  <Tab title="React">
      See `Web (JS)` for more details.
  </Tab>
  <Tab title="React Native">
      See `Android` and `Apple` for more details.
  </Tab>
  <Tab title="Apple">
        The following table shows the download and install size impact of adding RiveRuntime to your project,
        calculated by comparing the App Thinning report for an empty iOS app with and without RiveRuntime.

        | Platform  | Download Size Impact | Install Size Impact |
        | --------- | -------------------- | ------------------- |
        | Universal | ~1.67MB              | ~4.66mb             |
  </Tab>
  <Tab title="Android">
      | Target  | Download Size | Install Size |
      | ------- | ------------- | ------------ |
      | ARM-v8a | 2.40MB        | 7.03MB       |
      | ARM-v7a | 2.32MB        | 6.00MB       |

      ## Components
      Rive Android's binary size is comprised of a number of components:
      - Kotlin code compiled to a DEX file
      - Rive Android native shared library (`librive-android.so`)
          - Comprised of the Rive Android C++ bindings, the Rive C++ runtime, and the Rive Renderer.
          - Additionally has the [below third party static dependencies](#third-party-dependencies) (currently without Luau)
      - C++ standard library (shared .so file - 394KB download size, 1.2MB install size for ARM-v8a)
      - The following Android dependencies:
          | Dependency                                 | Reason                         |
          | ------------------------------------------ | ------------------------------ |
          | Compose: runtime, ui, ui-android           | Compose support                |
          | Lifecycle: runtime-ktx and runtime-compose | Lifecycle awareness in Compose |
          | Startup: startup-runtime                   | Automatic initialization       |
          | ReLinker                                   | Rive native library loading    |
          | Volley                                     | Network loading                |

      ## Amortization and R8
      The sizes listed above reflect adding Rive to an otherwise empty application. Some of the above dependencies may already be present in your application, and as a result do not contribute to the size increase when adding Rive. For example, if your app already uses Jetpack Compose, the Compose dependencies will likely already be included in your app's binary.

      The same is true for the C++ standard library, which will be shared across all dependencies with native code.

      Additionally, when compiling a release build, R8 will minify your application, removing unused code and resources. This can further reduce the size impact of adding Rive to your application. Ensure your Gradle file contains [`isMinifyEnabled = true`](https://developer.android.com/topic/performance/app-optimization/enable-app-optimization).

      ## Future Work
      There are options available to reduce the binary size of the library that can be considered for future work, including:
        - Replacing Miniaudio with Oboe for audio support
          - Currently Miniaudio can be removed by [compiling Rive Android yourself](https://github.com/rive-app/rive-android#no-audio-engine), using the `-PnoAudio` Gradle flag
        - Modularizing the runtime to allow including Compose support only when needed, and separating the Compose API from the Legacy API
        - Making Volley an opt-in dependency for network loading
        - Changing C++ compile flags to prefer size over speed (requires performance testing)

  </Tab>
</Tabs>

# Third Party Dependencies

The common Rive C++ runtime includes a number of open source third party dependencies which contribute to its binary weight. These are:

| Dependency                                            | Reason                     |
| ----------------------------------------------------- | -------------------------- |
| [HarfBuzz](https://github.com/harfbuzz/harfbuzz)      | Text rendering             |
| [Miniaudio](https://github.com/mackron/miniaudio)     | Audio support              |
| [SheenBidi](https://github.com/Tehreer/SheenBidi)     | Bidirectional text support |
| [Yoga](https://github.com/facebook/yoga)              | Layout                     |
| [Luau Interpreter](https://github.com/luau-lang/luau) | Scripting Support          |

---
## runtimes/text.mdx

---
title: "Text"
description: "⚠️ DEPRECATED: Use Data Binding instead of direct text run manipulation at runtime"
noindex: true
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'

Documentation for working with **Text** has moved to runtime-specific pages.

Select your runtime below to see the relevant guide.

<Runtimes
  runtimes={{
    web: '/runtimes/web/text',
    react: '/runtimes/react/text',
    reactNative: '/runtimes/react-native/text',
    flutter: '/runtimes/flutter/text',
    apple: '/runtimes/apple/text',
    android: '/runtimes/android/text',
    unity: '/game-runtimes/unity/text'
  }}
/>
---
## runtimes/fonts.mdx

---
title: 'Fonts'
description: 'Loading and replacing fonts dynamically at runtime.'
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'

Documentation for working with **Fonts** has moved to runtime-specific pages.

Select your runtime below to see the relevant guide.

<Runtimes
  runtimes={{
    web: '/runtimes/web/fonts',
    react: '/runtimes/react/fonts',
    reactNative: '/runtimes/react-native/fonts',
    flutter: '/runtimes/flutter/fonts',
    apple: '/runtimes/apple/fonts',
    android: '/runtimes/android/fonts'
  }}
/>
---
## runtimes/logging.mdx

---
title: 'Logging'
description: ''
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'

Some Rive runtimes include logging capabilities to help with debugging.

Select your runtime below to see the relevant guide.

<Runtimes
  runtimes={{
    apple: '/runtimes/apple/logging',
    android: '/runtimes/android/logging'
  }}
/>
---
## runtimes/demos.mdx

---
title: 'Rive Runtime Demos & Starters'
sidebarTitle: 'Demos'
description: 'Quick examples to get you up and running.'
mode: 'wide'
---

import { Demos } from '/snippets/demos.jsx'
import { RiveCard } from '/snippets/rive-card.jsx'
import { ExampleEyeFollow } from '/snippets/example-eye-follow.jsx'


<Demos
  examples={[
    "quickStart",
    "dataBindingQuickStart",
    "layouts",
    "fontsHostedCompressed",
    "dataBindingArtboards",
    "cachingARiveFile",
    "dataBindingImages",
    "dataBindingLists",
    "dataBindingSolos",
    "googleAppAds"
  ]}
  columns={3}
  childrenIndex={4}
>
  <RiveCard
    title="Follow the Cursor"
    description="Track the cursor, even if it's outside the bounds of the Rive instance."
    links={{
      web: "https://codesandbox.io/p/sandbox/rive-web-track-your-mouse-n38gdd"
    }}
    source={["https://rive.app/marketplace/24639-46040-cat-follow-cursor-demo?utm_source=docs&utm_medium=docs_card_demo"]}
  >
    <ExampleEyeFollow />
  </RiveCard>
</Demos>


---
## runtimes/rive-events.mdx

---
title: "Rive Events"
description: "⚠️ DEPRECATED: Use Data Binding instead of Events"
noindex: true
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'

Documentation for working with **Rive Events** has moved to runtime-specific pages.

Select your runtime below to see the relevant guide.

<Runtimes
  runtimes={{
    web: '/runtimes/web/rive-events',
    react: '/runtimes/react/rive-events',
    reactNative: '/runtimes/react-native/rive-events',
    flutter: '/runtimes/flutter/rive-events',
    apple: '/runtimes/apple/rive-events',
    android: '/runtimes/android/rive-events',
    unity: '/game-runtimes/unity/rive-events'
  }}
/>
## Web runtime (rive-js / @rive-app/canvas / @rive-app/webgl2)

---
## runtimes/web/animation-playback.mdx

---
title: "Animation Playback"
description: "⚠️ DEPRECATED: Use State Machines instead of direct animation playback at runtime"
noindex: true
---

import Overview from "/snippets/runtimes/animation-playback/overview.mdx"
import ChoosingStartingAnimations from "/snippets/runtimes/animation-playback/choosing-starting-animations.mdx"
import ControllingPlayback from "/snippets/runtimes/animation-playback/controlling-playback.mdx"

<Overview />

<ChoosingStartingAnimations />

```javascript
// Play the idle animation
new rive.Rive({
    src: 'https://cdn.rive.app/animations/vehicles.riv',
    canvas: document.getElementById('canvas'),
    animations: 'idle',
    autoplay: true
});
```

<ControllingPlayback />

#### Invoking Playback Controls

With the web runtime, you can provide callback functions to receive notification when certain animation events have occurred:

- `onLoad` when a rive file has been loaded and initialized; it's now ready for playback
- `onPlay` when one or more animations play; provides a list of animations
- `onPause` when one or more animations pause; provides a list of animations
- `onStop` when one or more animations are stopped; provides a list of animations
- `onLoop` when an animation loops; provides the animation name

See the following Codesandbox link to try out the below code: [https://codesandbox.io/p/sandbox/adoring-sea-n7m59f](https://codesandbox.io/p/sandbox/adoring-sea-n7m59f)

```javascript
const idleButton = document.getElementById("idle");
const wipersButton = document.getElementById("wipers");
const loopDiv = document.getElementById("loop");

const truck = new rive.Rive({
  src: "https://cdn.rive.app/animations/vehicles.riv",
  artboard: "Jeep",
  canvas: document.getElementById("canvas"),
  layout: new rive.Layout({ fit: "fill" }),
  // Listen for play events to update button text
  onPlay: (event) => {
    const names = event.data;
    names.forEach((name) => {
      if (name === "idle") {
        idleButton.innerHTML = "Stop Truck";
      } else if (name === "windshield_wipers") {
        wipersButton.innerHTML = "Stop Wipers";
      }
    });
  },
  // Listen for pause events to update button text
  onPause: (event) => {
    const names = event.data;
    names.forEach((name) => {
      if (name === "idle") {
        idleButton.innerHTML = "Start Truck";
      } else if (name === "windshield_wipers") {
        wipersButton.innerHTML = "Start Wipers";
      }
    });
  },
  onLoop: (event) => {
    loopDiv.innerHTML = `Looped Animation: ${event.data.animation}`;
  }
});

idleButton.onclick = (_) =>
  truck.playingAnimationNames.includes("idle")
    ? truck.pause("idle")
    : truck.play("idle");

wipersButton.onclick = (_) =>
  truck.playingAnimationNames.includes("windshield_wipers")
    ? truck.pause("windshield_wipers")
    : truck.play("windshield_wipers");
```
---
## runtimes/web/artboards.mdx

---
title: 'Artboards'
description: 'Selecting which artboard to render at runtime'
---

import Overview from "/snippets/runtimes/artboards/overview.mdx"
import ChoosingAnArtboard from "/snippets/runtimes/artboards/choosing-an-artboard.mdx"

<Overview />

<ChoosingAnArtboard />

```javascript
  new rive.Rive({
      src: 'https://cdn.rive.app/animations/vehicles.riv',
      canvas: document.getElementById('canvas'),
      artboard: 'Truck',
      autoplay: true
  });
```
---
## runtimes/web/caching-a-rive-file.mdx

---
title: "Caching a Rive File"
description: ""
---

import { Demos } from "/snippets/demos.jsx";
import Overview from "/snippets/runtimes/caching/overview.mdx"

<Overview />

## Example Usage

<Demos examples={["cachingARiveFile"]} runtime="web" />

The following is a basic example to illustrate how to preload a Rive file, and pass the data to multiple Rive instances.

```javascript
const rive = require("@rive-app/canvas");

let riveInstances = [];

function loadRiveFile(src, onSuccess, onError) {
const file = new rive.RiveFile({
    src: src,
    onLoad: () => onSuccess(file),
    onLoadError: onError,
});
// Remember to call init() to trigger the load;
file.init().catch(onError);
}

function setupRiveInstance(loadedRiveFile, canvasId) {
const canvas = document.getElementById(canvasId);
if (!canvas) return;

const riveInstance = new rive.Rive({
    riveFile: loadedRiveFile,
    // Be sure to specify the correct state machine (or animation) name
    stateMachines: "Motion", // Name of the State Machine to play
    canvas: canvas,
    layout: new rive.Layout({
    fit: rive.Fit.FitWidth,
    alignment: rive.Alignment.Center,
    }),
    autoplay: true,
    onLoad: () => {
    // Prevent a blurry canvas by using the device pixel ratio
    riveInstance.resizeDrawingSurfaceToCanvas();
    },
});

riveInstances.push(riveInstance);
}

// Loads the .riv file and initializes multiple Rive instances using the same loaded RiveFile in memory
loadRiveFile(
"clean_the_car.riv",
(file) => {
    setupRiveInstance(file, "rive-canvas-1");
    setupRiveInstance(file, "rive-canvas-2");
    // You could also store a reference to the loaded RiveFile here so you're able to initialize other Rive instances later.
},
(error) => {
    console.error("Failed to load Rive file:", error);
}
);

// Resize the drawing surface for all instances if the window resizes
window.addEventListener(
"resize",
() => {
    riveInstances.forEach((instance) => {
    if (instance) {
        instance.resizeDrawingSurfaceToCanvas();
    }
    });
},
false
);
```
---
## runtimes/web/canvas-vs-webgl.mdx

---
title: "Canvas vs WebGL2"
description: "Choose between `@rive-app/webgl2` and `@rive-app/canvas`, with guidance on performance, package size, and when to use canvas-lite."
---

### Choose a runtime

For web, start by choosing one of these two packages:

- [`@rive-app/webgl2`](https://www.npmjs.com/package/@rive-app/webgl2)
- [`@rive-app/canvas`](https://www.npmjs.com/package/@rive-app/canvas)

They share the same high-level API, so switching packages does not require changing how you create a `new Rive({...})` instance. The key differences are the renderer and package size; read the sections below to decide what is best for your use case, and compare package sizes on [Runtime Sizes](/runtimes/runtime-sizes/).

### `@rive-app/webgl2` (recommended)

Use `@rive-app/webgl2` if you want the best rendering quality and performance in most cases.

```bash
npm install @rive-app/webgl2
```

- Uses the [Rive Renderer](https://rive.app/renderer?utm_source=docs&utm_medium=content) for the best rendering performance
- Supports Rive Renderer-only features (for example, vector feathering)

<Note>
 WebGL has browser limits on concurrent contexts, which can limit how many `new Rive({...})` instances you can run at once. If you display many graphics on the same page, set `useOffscreenRenderer: true` for each Rive object.
 This moves rendering work to a shared offscreen WebGL context instead of creating as many separate contexts on visible canvases, which helps avoid context-limit issues and improves stability when many Rive instances are active.
</Note>

<Note>
  Enabling the draft
  [WEBGL_shader_pixel_local_storage](https://www.wikihow.tech/Enable-WebGL-Draft-Extensions-in-Google-Chrome)
  extension in Chrome improves rendering performance. Without it, Rive falls
  back to an MSAA-based WebGL2 path. We are actively working with browser
  vendors to make this enabled by default.
</Note>

### `@rive-app/canvas`

Use `@rive-app/canvas` when your graphics are less complex and you want a smaller runtime package.

```bash
npm install @rive-app/canvas
```

- Uses the browser's built-in [CanvasRenderingContext2D](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) renderer
- Smaller package size than the WebGL2 renderer option
- Good for simpler vector/raster graphics

### More options after your runtime choice

For the canvas-based runtime option, you can alternatively use these variants based on packaging needs.

#### `@rive-app/canvas-lite` variant

The canvas version of our runtime supports a `-lite` variant for smaller package size.

- Example: [`@rive-app/canvas-lite`](https://www.npmjs.com/package/@rive-app/canvas-lite)
- Use this package when you want the smallest runtime footprint
- This package variant removes some features (for example, text, layout, audio, and scripting engines)

#### `@rive-app/canvas-single` variant

The canvas version of our runtime supports a `-single` variant, which bundles `rive.wasm` directly into the JavaScript file.

- Example: [`@rive-app/canvas-single`](https://www.npmjs.com/package/@rive-app/canvas-single)
- Use this package if you want to avoid a separate WASM network request
- Expect a larger JS bundle compared to the standard package

### Deprecated package

`@rive-app/webgl` is deprecated and will no longer receive updates after `v2.37.0`. Prefer `@rive-app/webgl2`.

---
## runtimes/web/data-binding.mdx

---
title: "Data Binding"
description: "Connect your code to bound editor elements using View Models"
---

import Overview from "/snippets/runtimes/data-binding/overview.mdx"
import ViewModels from "/snippets/runtimes/data-binding/view-models.mdx"
import ViewModelInstances from "/snippets/runtimes/data-binding/view-model-instances.mdx"
import Binding from "/snippets/runtimes/data-binding/binding.mdx"
import AutoBinding from "/snippets/runtimes/data-binding/auto-binding.mdx"
import Properties from "/snippets/runtimes/data-binding/properties.mdx"
import ListingProperties from "/snippets/runtimes/data-binding/listing-properties.mdx"
import ReadingAndWritingProperties from "/snippets/runtimes/data-binding/reading-and-writing-properties.mdx"
import NestedPropertyPaths from "/snippets/runtimes/data-binding/nested-property-paths.mdx"
import Observability from "/snippets/runtimes/data-binding/observability.mdx"
import Images from "/snippets/runtimes/data-binding/images.mdx"
import Lists from "/snippets/runtimes/data-binding/lists.mdx"
import Artboards from "/snippets/runtimes/data-binding/artboards.mdx"
import Enums from "/snippets/runtimes/data-binding/enums.mdx"


import { YouTube } from "/snippets/youtube.mdx";
import { Demos } from "/snippets/demos.jsx";

<Overview />

<Demos examples={["quickStart"]} runtime="web" />

<ViewModels />

Access a View Model from the created Rive object in the `onLoad` callback:

```typescript
const r = new rive.Rive({
    onLoad: () => {
        // The Rive object is now loaded and ready to use.
    }
});
```

Once Rive is loaded, you can access the view models using the following methods:

```typescript
// Get reference by name
const namedVM = r.viewModelByName("My View Model");

// Get reference by index
for (let i = 0; i < r.viewModelCount; i++) {
    const indexedVM = r.viewModelByIndex(i);
}

// Get reference to the default view model
const defaultVM = r.defaultViewModel();
```

Alternatively, if you have access to the underlying `RiveFile` object you can access the above methods on the file.

```typescript
const file = new RiveFile(/** ... */);
await file.init();
const vmFromFile = file.viewModelByName("My View Model");

// Or grab the ViewModel via other means from the RiveFile underlying instance
const fileInstance = file.getInstance();
const namedVM = fileInstance.viewModelByName("My View Model");
const indexedVM = fileInstance.viewModelByIndex(0);
const defaultVM = fileInstance.defaultArtboardViewModel(artboard);
```

<ViewModelInstances />

```typescript
// Create a blank instance from a view model (ViewModel)
const vmiBlank = viewModel.instance();

// Create a default instance from a view model (ViewModel)
const vmiDefault = viewModel.defaultInstance();

// Create an instance by index from a view model (ViewModel)
for (let i = 0; i < viewModel.instanceCount; i++) {
    const vmiIndexed = viewModel.instanceByIndex(i);
}

// Create an instance by name from a view model (ViewModel)
const vmiNamed = viewModel.instanceByName("My Instance");
```

<Binding />

```typescript
const r = new rive.Rive({
    autoBind: false, // This should be set to false (default)
    onLoad: () => {
        const vm = r.viewModelByName("My View Model");
        const vmi = vm.instanceByName("My Instance");

        // Manually bind by applying the instance to the state machine and artboard
        r.bindViewModelInstance(vmi);
    }
});
```

<AutoBinding />

 ```typescript {4}
const r = new rive.Rive({
    src: "my_rive_file.riv",
    canvas: document.getElementById("canvas"),
    autoBind: true,
    onLoad: () => {
        // Access the current instance that was auto-bound
        let boundInstance = r.viewModelInstance;
    }
});
```

### Get View Model from Instance

When working with view model instances, you may want to get a reference to the view model the instance came from so you can dynamically create more instances of the same type (i.e. creating instances from lists).
To do so, first grab the name of the view model the instance came from via the `.viewModelName` property:
```ts
const vmi = r.viewModelInstance;
const vmName = vmi.viewModelName;
```

Then, once you have the name, you can get a reference to the view model itself and create instances as needed.
```ts
const vmi = r.viewModelInstance;
const mainListProp = vmi.list("todos") as ViewModelInstanceList;
const vmName = mainListProp.instanceAt(0)?.viewModelName;

const itemVmReference = r.viewModelByName(vmName);
const instanceCopies = [];
for (let i = 0; i < 10; i++) {
    instanceCopies.push(itemVmReference.defaultInstance());
}
```

<Properties />

<ListingProperties />

```typescript
    // A list of properties on a view model (ViewModel)
    const properties = viewModel.properties;
    console.log(properties);
```

<ReadingAndWritingProperties />

```typescript
const r = new rive.Rive({
    autoBind: true,
    onLoad: () => {
        // Access the current instance that was auto-bound
        let vmi = r.viewModelInstance;

        // Booleans
        const booleanProperty = vmi.boolean("My Boolean Property");
        const booleanValue = booleanProperty.value;
        booleanProperty.value = true;

        // Strings
        const stringProperty = vmi.string("My String Property");
        const stringValue = stringProperty.value;
        stringProperty.value = "Hello, Rive!";

        // Numbers
        const numberProperty = vmi.number("My Number Property");
        const numberValue = numberProperty.value;
        numberProperty.value = 10;

        // Colors
        const colorProperty = vmi.color("My Color Property");
        const colorValue = colorProperty.value;
        colorProperty.value = 0xFF000000; // Set color to black with 100% opacity

        // Other ways to set color
        colorProperty.rgb(255, 0, 0); // Set RGB to red
        colorProperty.rgba(255, 0, 0, 128); // Set RGBA to red with 50% opacity
        colorProperty.argb(128, 255, 0, 0); // Set ARGB to red with 50% opacity
        colorProperty.opacity(0.5); // Set opacity to 50%

        // Triggers
        const triggerProperty = vmi.trigger("My Trigger Property");
        triggerProperty.trigger();

        // Enumerations
        const enumProperty = vmi.enum("My Enum Property");
        const enumValue = enumProperty.value;
        enumProperty.value = "Option1";
    }
});
```

<NestedPropertyPaths />

```typescript
const r = new rive.Rive({
    autoBind: true,
    onLoad: () => {
        // Access the current instance that was auto-bound
        let vmi = r.viewModelInstance;

        const nestedNumberByChain = vmi
            .viewModel("My Nested View Model")
            .viewModel("My Second Nested VM")
            .number("My Nested Number");

        const nestedNumberByPath = vmi.number("My Nested View Model/My Second Nested VM/My Nested Number");
    }
});
```

<Observability />

Adding an observer to a property is done by calling the `on` method on the property.

    ```typescript
    public on(callback: EventCallback)
    ```

    The observer can be removed by calling the `off` method on the property and passing the callback function. Alternatively, you can call `off()` without any arguments to remove all observers.

    ```typescript
    public off(callback?: EventCallback)
    ```

    Example:

    ```typescript
    const r = new rive.Rive({
        autoBind: true,
        onLoad: () => {
            // Access the current instance that was auto-bound
            let vmi = r.viewModelInstance;
            const numberProperty = vmi.number("My Number Property");
            // Observe
            numberProperty.on((event) => {
                console.log(event.data);
            });
            // Remove all listener when done
            numberProperty.off();
        }
    });
    ```

<Images />

<Demos examples={['dataBindingImages']} runtime="web" />

```js
const randomImageAsset = (imageProperty) => {
    fetch("https://picsum.photos/300/500").then(async (res) => {
        // Decode the image from the response. This object is used to set the image property.
        const image = await rive.decodeImage(
            new Uint8Array(await res.arrayBuffer())
        );
        imageProperty.value = image;
        // Rive will automatically clean this up. But it's good practice to dispose this manually
        // after you have already set the decoded image. Don't call `unref` if you intend
        // to use the decoded asset again.
        image.unref();
    });
};

const r = new rive.Rive({
    autoBind: true,
    onLoad: () => {
        // Access the current instance that was auto-bound
        let vmi = r.viewModelInstance;

        // Get the image property by name
        var imageProperty = vmi.image("bound_image");

        // Load random image
        randomImageAsset(imageProperty);

        // Clear the image to render nothing
        imageProperty.value = null;
    }
});
```

<Lists />

<Demos examples={['dataBindingLists']} runtime="web" />

```javascript
const r = new rive.Rive({
    autoBind: true,
    onLoad: () => {
        // Access the current instance that was auto-bound
        let vmi = r.viewModelInstance;

        // Get the list property by name
        var list = vmi.list("todos");
        console.log("length: ", list.length);

        // Get the view model
        var todoItemVM = r.viewModelByName("TodoItem");

        // Create a blank instance from the view model.
        // Do this for each new item you want to add.
        var myTodo = todoItemVM.instance();
        myTodo.string("description").value = "Buy groceries";

        // Add the newly created instance to the list
        list.addInstance(myTodo);

        // Remove a specific instance from the list
        list.removeInstance(myTodo);

        // Swap two instances in the list at index 0 and 1
        list.swap(0, 1);

        // Remove instance at index 0
        list.removeInstanceAt(0);
    }
});
```

<Artboards />

<Demos examples={["dataBindingArtboards"]}  runtime="web" />

```typescript
let artboardProperty = null;
let characterArtboard = null;

function attachCharacter() {
    // If the artboard property and the character artboard, both exist, set the artboard
    if (characterArtboard && artboardProperty) {
        artboardProperty.value = characterArtboard;
    }
}

const r = new Rive({
    src: "swap_character_main.riv",
    autoplay: true,
    canvas: el,
    autoBind: true,
    layout: new Layout({
        fit: Fit.Layout,
        layoutScaleFactor: 0.5,
    }),
    stateMachines: "State Machine 1",
    onLoad: () => {
        r.resizeDrawingSurfaceToCanvas();

        const vmi = r.viewModelInstance;
        artboardProperty = vmi.artboard("Artboard property");

        attachCharacter();
    },
    onLoadError: () => {
        console.log("error");
    },
});

// Load an external artboard
const assetsFile = new RiveFile({
    src: "swap_character_assets.riv",
    onLoad: () => {
        characterArtboard = assetsFile.getBindableArtboard("Character 1");
        attachCharacter();
    },
    onLoadError: () => {
        console.log("error");
    },
});
assetsFile.init();
```

In the example above, we load from a separate `swap_character_assets.riv` file to get the `Character 1` bindable artboard. We can then use this value in the main `swap_character_main.riv` file by setting the value of the `artboardProperty` to the loaded `characterArtboard`. This allows us to swap out the artboard being used in the main file at runtime.
Additionally, you can set an external `ViewModelInstance` to that bindable artboard via the `.viewModel` setter.

<Enums />

```typescript
const r = new rive.Rive({
    onLoad: () => {
        const enums = r.enums();

        console.log(enums);
    }
});
```

# Examples

<YouTube id="y7glxOIFEjg" />
<YouTube id="1WFtGX2coXM" />

---
## runtimes/web/faq.mdx

---
title: 'FAQ'
description: 'Common issues for the web runtime.'
---




## Concerns

We've compiled a list of common concerns when using web-based runtimes. See each section below for more on how to address these in your applications.

### Why am I getting CORS errors fetching Rive files?

In some cases, you may decide to host your `.riv` files over a CDN, and store them in AWS S3 for example. At runtime, some users face CORS issues where you may not be able to load in the `.riv` file in the web runtime. When this happens, make sure to set CORS headers on the host platform such that when the Rive file content is accessed in the web apps/sites, browsers won't block pulling data down.

Read more on [what CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) is. [See here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ManageCorsUsing.html#cors-example-1) for more docs on how to configure CORS in AWS S3, as an example.

### Is there a smaller dependency I can use? My Rive graphic doesn't require all of Rive's feature-set capabilities.

Yes! You may notice that starting in `v2.0.0` of the web runtimes, the size of the `rive.wasm` file requested on the browser increased. This was due to including a new dependency in the WASM build for a text engine that supports the powerful and flexible [Rive Text](/editor/text/) feature.

However, if you don't have a need to use the native Rive Text feature (or prefer to use imported SVG text), you can use the [@rive-app/canvas-lite](/runtimes/web/web-js#canvas-vs-webgl) which provides the same API and similar rendering capabilities as `@rive-app/canvas`, with a smaller package.

### Why did the canvas width/height attribute values change?

You may have noticed that the `<canvas>` width/height attributes in the DOM may be larger than you originally set by some factor. Internally, the high-level API tries to adjust the original set (or default) canvas width/height attributes by accounting for the `window.devicePixelRatio`. By doing this internal calculation, we're able to account for high-dpi screens so that Rive animations don't have a "blurry" output. We do not however try to size the actual size of the canvas element with respect to the DOM. This is ultimately up to you to configure.

### Why is my animation blurry at runtime?

It may be because there are no width/height attributes on the `<canvas>` element to determine the drawing size of the canvas, or the default values are not large enough to meet the artboard bounds of the animation. We recommend setting at least some CSS style width/height properties on the canvas to determine the size of the canvas box on the page, as the runtime will then use those values to try and set a best-fit estimate of the drawing size to the canvas element.

Additionally, you could take advantage of a public function `resizeDrawingSurfaceToCanvas` on the `Rive` object when instantiated that helps adjust the width/height attributes of the canvas in the DOM based on the user's `devicePixelRatio`. (**note**: this applies to the drawing surface of the canvas, not the size of the bounding box of the canvas element).

```html
<canvas
    id="some-canvas-element-id"
    style="width: 400px; height: 400px;"
></canvas>
```

```javascript
const canvasElement = document.getElementById('some-canvas-element-id');

const r = new Rive({
  src: 'some-file.riv',
  canvas: canvasElement,
  autoplay: true,
  onLoad: () => {
    r.resizeDrawingSurfaceToCanvas();
  },
});
```

<Note>
 If you use the `resizeDrawingSurfaceToCanvas` function, make sure you bound your canvas actual style size to desired values, otherwise the canvas could double in size.
</Note>

### What's the difference in width/height attributes on the canvas and the CSS width/height?

Great question! With the `<canvas>` element, there are 2 types of space sizes to think about.

There's the size of the canvas element itself on the page, which is usually what most people think of when setting width/height styles on an element. This involves setting the CSS width/height properties on an element.

```html
<canvas style="width: 400px; height: 400px;"></canvas>
```

![Image](/images/runtimes/web/166b48f5-9893-4371-8655-b69d987a2235.webp)

Then there are the width/height attributes on a `<canvas>` element that determines the drawing surface size of the canvas. In some cases, these values may influence the actual canvas size as well if there are no CSS styles set on the width/height of the element. But mainly, these width/height attributes help determine how much space is available to draw within the canvas element itself. Unlike the CSS width/height properties, these values are unitless.

```html
<canvas width="800" height="800"></canvas>
```

![Image](/images/runtimes/web/4fd1465b-97e3-4542-9e47-7babfb27c400.webp)

Ideally, you want to ensure that the width/height attributes on the canvas are at least the size of or greater than the width/height CSS properties on the canvas, otherwise, you may have blurry output (see above for how to address blurry animations).

### How come my state machine isn't playing?

Make sure you've specified the `stateMachines` property when instantiating Rive with the name of your state machine. To autoplay the state machine, don't forget to set `autoplay: true` when instantiating the Rive object.

### How do I get other web-frameworks to support Rive?

Currently, we support the React runtime officially, beyond the plain JS/TS runtime here. There have been community-driven wrappers created to support other web-based libraries/frameworks. We recommend checking out the [rive-react](https://github.com/rive-app/rive-react) source project to understand how it wraps this JS runtime into React-friendly components and hooks to make using Rive better in React-based applications. We encourage you to explore doing the same for any other web-based framework/library you may be interested in building Rive with!

### I have Content-Security-Policy set to block unsafe-eval, and now Rive fails to load. What do I do?

Our Web (JS) runtime is built on top of a cpp runtime layer that provides a rendering abstraction. The web runtime uses web assembly (WASM) to bind the cpp layer to JS API's. We use a tool called [Emscripten](https://emscripten.org/) to do this compilation. As part of that tool's source code and binding techniques, it may use some techniques to generate the JS API's that the `unsafe-eval` policy would block. Because of this, the runtime may fail to load in the web assembly successfully, and thus Rive would fail to load since the web-assembly is crucial to running Rive in the web. See more on that issue [here](https://github.com/WebAssembly/content-security-policy/issues/7).

To get around this, there is a new CSP setting you can set that would still allow you to block `unsafe-eval` but also give some freedom with regards to WASM being executed; `wasm-unsafe-eval`. While not the perfect solution, it is a better solution than allowing any unsafe evaluation of JS, while allowing web applications to still take WASM builds.
---
## runtimes/web/fonts.mdx

---
title: 'Fonts'
description: 'Loading and replacing fonts dynamically at runtime.'
---

import SwappingFonts from "/snippets/runtimes/fonts/swapping-fonts.mdx"
import fallbackFonts from "/snippets/runtimes/fonts/fallback-fonts.mdx"

<SwappingFonts />

For more information, see [Loading Assets](/runtimes/web/loading-assets).
`
<fallbackFonts />

<Note>
  For security reasons, browsers do not allow direct access to a user's system fonts. As a result, fallback fonts must be explicitly provided for this runtime.
</Note>

As of `v2.37.1`, the JS runtime provides an API for supplying fallback fonts. When a glyph cannot be rendered with the default font, Rive will invoke a callback you provide to retrieve a list of decoded fonts to try instead. Importantly, this callback must be registered before Rive begins rendering. 

To start, import the `RiveFont` named export from the JS package and call its static method `setFallbackFontCallback()`, passing in your callback. The callback receives the glyph that failed to render (as a Unicode code point) and the font weight, and should return a list of fallback fonts. It may be called multiple times if successive fallback fonts also lack support for the glyph.

```javascript
import { RiveFont, decodeFont, Rive } from "@rive-app/webgl2";

const THAI_FALLBACK_FONT_URL =
  "https://raw.githubusercontent.com/google/fonts/main/ofl/notoserifthai/NotoSerifThai%5Bwdth%2Cwght%5D.ttf";

const setFallbackFonts = async () => {
  const notoSerifThai = await fetch(THAI_FALLBACK_FONT_URL).then((res) => res.arrayBuffer());
  const riveThaiDecodedFont = await decodeFont(new Uint8Array(notoSerifThai));

  RiveFont.setFallbackFontCallback((codePoint: number, weight: number) => {
    console.log("fallback font missing glyph: ", codePoint, " + weight: ", weight);
    // For Thai, use Noto Serif Thai font
    if (codePoint >= 0x0E00 && codePoint <= 0x0E7F) {
      return [riveThaiDecodedFont];
    }
    return null;
  });
};

const main = async () => {
  await setFallbackFonts();
  const r = new Rive({ 
    src: "my.riv",
    autoplay: true,
    stateMachines: "State Machine 1",
    // ...
  });
};
main();
```



---
## runtimes/web/inputs.mdx

---
title: "Inputs"
description: "⚠️ DEPRECATED: Use Data Binding instead of Inputs for controlling Rive animations"
noindex: true
---

import Overview from "/snippets/runtimes/inputs/overview.mdx"
import ControllingInputs from "/snippets/runtimes/inputs/controlling-inputs.mdx"
import NestedInputs from "/snippets/runtimes/inputs/nested-inputs.mdx"

<Overview />

<ControllingInputs />

### Examples

- [Setting state machine inputs](https://codesandbox.io/p/sandbox/rive-state-machine-inputs-js-forked-s6gfjg)

### Inputs

The web runtime provides an `onLoad` callback that's run when the Rive file is loaded and ready for use. We use this callback to ensure that the state machine is instantiated before we query for inputs.

```javascript
<div id="button">
    <canvas id="canvas" width="1000" height="500"></canvas>
</div>
<script src="https://unpkg.com/@rive-app/canvas@2.10.3"></script>
<script>
    const button = document.getElementById('button');

    const r = new rive.Rive({
        src: 'https://cdn.rive.app/animations/vehicles.riv',
        canvas: document.getElementById('canvas'),
        autoplay: true,
        stateMachines: 'bumpy',
        onLoad: (_) => {
            // Get the inputs via the name of the state machine
            const inputs = r.stateMachineInputs('bumpy');
            // Find the input you want to set a value for, or trigger
            const bumpTrigger = inputs.find(i => i.name === 'bump');
            button.onclick = () => bumpTrigger.fire();
        },
    });
</script>
```
We use the `stateMachineInputs` function on the Rive object to retrieve the inputs. Each input will have a name and type. There are three types:

- `StateMachineInputType.Trigger` which has a `fire()` function
- `StateMachineInputType.Number` which has a `value` number property where you can `get`/`set` the value
- `StateMachineInputType.Boolean` which has a `value` boolean property where you can `get`/`set` the value

```javascript
const inputs = r.stateMachineInputs("bumpy");
inputs.forEach((i) => {
  const inputName = i.name;
  const inputType = i.type;
  switch (inputType) {
    case rive.StateMachineInputType.Trigger:
      i.fire();
      break;
    case rive.StateMachineInputType.Number:
      i.value = 42;
      break;
    case rive.StateMachineInputType.Boolean:
      i.value = true;
      break;
  }
});
```

<NestedInputs />

To set the **Volume** input for the above example:

```javascript
const rive = new Rive({...});
...
rive?.setNumberStateAtPath("volume", 80.0, "Volume Molecule/Volume Component");
```

**All options:**
- `setNumberStateAtPath(inputName: string, value: number, path: string)`
- `setBooleanStateAtPath(inputName: string, value: boolean, path: string)`
- `fireStateAtPath(inputName: string, path: string)`

---
## runtimes/web/layouts.mdx

---
title: "Layout"
description: "Control how graphics are laid out within the canvas."
---

import { Demos } from "/snippets/demos.jsx";

import FitMode from '/snippets/runtimes/layouts/fit-mode.mdx'
import Alignment from "/snippets/runtimes/layouts/alignment.mdx"
import Bounds from "/snippets/runtimes/layouts/bounds.mdx"
import ApplyingFitMode from "/snippets/runtimes/layouts/applying-fit-mode.mdx"
import ResponsiveLayouts from "/snippets/runtimes/layouts/responsive-layouts.mdx"

<Demos examples={["layouts"]} runtime="web"/>

<FitMode />

<Alignment />

<Bounds />

<ApplyingFitMode />

Use the `Layout` object to configure `Fit` and `Alignment`. See [Fit](#the-fit-mode) and [Alignment](#alignment) for all enum options.

  ```javascript

// Fill the canvas, cropping Rive if necessary
let layout = new rive.Layout({
    fit: rive.Fit.Cover,
});

// Fit to the width and align to the top of the canvas
layout = new rive.Layout({
    fit: rive.Fit.FitWidth,
    alignment: rive.Alignment.TopCenter,
});

// Constrain the Rive content to (minX, minY), (maxX, maxY) in the canvas
layout = new rive.Layout({
    fit: rive.Fit.Contain,
    minX: 50,
    minY: 50,
    maxX: 100,
    maxY: 100,
});

const riveInstance = new rive.Rive({
    src: 'https://cdn.rive.app/animations/vehicles.riv',
    canvas: document.getElementById('canvas'),
    layout: layout,
    autoplay: true
});

// Update the layout
riveInstance.layout = new rive.Layout({ fit: rive.Fit.Fill });
```

<ResponsiveLayouts />

**Steps**

    1. Set `fit` to `Fit.Layout` - this will automatically scale and resize the artboard to match the canvas size when calling `resizeDrawingSurfaceToCanvas()`.
    2. Optionally set `layoutScaleFactor` for manual control of the artboard size (scale factor).
    3. Subscribe to `window.onresize` and call `resizeDrawingSurfaceToCanvas()` to adjust the artboard size as the canvas and window changes.
    4. Subscribe to **device pixel ratio** changes and call `resizeDrawingSurfaceToCanvas()` to ensure the artboard updates correctly on various screen densities. For example, when dragging the window between multiple monitors with different device pixel ratios.

```javascript
  const rive = new Rive({
    src: "your-rive-file.riv",
    autoplay: true,
    canvas: riveCanvas,
    layout: new Layout({
      fit: Fit.Layout,
      // layoutScaleFactor: 2, // 2x scale of the layout, when using `Fit.Layout`. This allows you to resize the layout as needed.
    }),
    stateMachines: ["State Machine 1"],
    onLoad: () => {
      computeSize();
    },
  });

  function computeSize() {
    rive.resizeDrawingSurfaceToCanvas();
  }

  // Subscribe to window size changes and update call `resizeDrawingSurfaceToCanvas`
  window.onresize = computeSize;

  // Subscribe to devicePixelRatio changes and call `resizeDrawingSurfaceToCanvas`
  window
    .matchMedia(`(resolution: ${window.devicePixelRatio}dppx)`)
    .addEventListener("change", computeSize);
```

## TypeScript API surface

These types are exported from `@rive-app/canvas` (or your bundled `rive` global):

```typescript
export interface LayoutParameters {
  fit?: Fit;
  alignment?: Alignment;
  layoutScaleFactor?: number;
  minX?: number;
  minY?: number;
  maxX?: number;
  maxY?: number;
}

export class Layout {
  constructor(params?: LayoutParameters);
  readonly fit: Fit;
  readonly alignment: Alignment;
  readonly layoutScaleFactor: number;
  readonly minX: number;
  readonly minY: number;
  readonly maxX: number;
  readonly maxY: number;
  copyWith(partial: LayoutParameters): Layout;
}
```

---
## runtimes/web/loading-assets.mdx

---
title: "Loading Assets"
description: "Loading and replacing assets dynamically at runtime"
---

import { YouTube } from "/snippets/youtube.mdx";

import Overview from '/snippets/runtimes/loading-assets/overview.mdx'
import MethodsForLoadingAssets from '/snippets/runtimes/loading-assets/methods-for-loading.mdx'
import EmbeddedAssets from '/snippets/runtimes/loading-assets/embedded-assets.mdx'
import LoadingViaCDN from '/snippets/runtimes/loading-assets/loading-via-cdn.mdx'
import ImageCDNs from '/snippets/runtimes/loading-assets/image-cdns.mdx'
import ReferenceAssets from '/snippets/runtimes/loading-assets/referenced-assets.mdx'
import HandlingAssets from '/snippets/runtimes/loading-assets/handling-assets.mdx'
import Resources from '/snippets/runtimes/loading-assets/resources.mdx'

<Overview />
<MethodsForLoadingAssets />
<EmbeddedAssets />
<LoadingViaCDN />
<ImageCDNs />
<ReferenceAssets />
<HandlingAssets />

### Examples

{/* TODO Demo cards */}

- [Specify a font asset to load](https://codesandbox.io/p/devbox/rive-out-of-band-fonts-js-forked-kml2wd?file=%2Fsrc%2Findex.ts)
- [Specify an image asset to load](https://codesandbox.io/p/sandbox/rive-out-of-band-images-js-forked-23jx8m?file=%2Fsrc%2Findex.ts)

### Using the Asset Handler API

When instantiating a new Rive instance, add an `assetLoader` callback property to the list of parameters. This callback will be called for every asset the runtime detects from the `.riv` file on load, and will be responsible for either handling the load of an asset at runtime or passing on the responsibility and giving the runtime a chance to load it otherwise.

An instance where you may want to handle loading an asset is if an asset in the file is marked as **Referenced**, and you need to provide an actual asset to render for the graphic, as Rive does not embed it in the `.riv` and thus cannot load it.

An instance where you may want to give the runtime a chance to load the asset is if the asset in the file is marked as **Hosted**, and want to pass the responsibility of loading it to the runtime (which will call into a Rive CDN to do so).

```javascript
assetLoader: (asset: rc.FileAsset, bytes: Uint8Array) => boolean;
```

Your provided callback will be passed an `asset` and `bytes`.

- `asset` - Reference to a `FileAsset` object from WASM. You can grab a number of properties from this object, such as the name, asset type, and more. You'll also use this to set a new Rive-specific asset for the dynamically loaded in asset you want to set (i.e. `RenderImage` for an image, `Font` for a font, or `Audio` for audio).
- `bytes` - Array of bytes for the asset (if possible, such as if it's an embedded asset)

**Important**: Note that the return value is a `boolean`, which is where you need to return `true` if you intend on handling and loading in an asset yourself, or `false` if you do not want to handle asset loading for that given asset yourself, and attempt to have the runtime try to load the asset.

When decoding an asset be sure to call `unref` once it is no longer needed - to avoid memory leaks. This allows the engine to clean it up when it is not used by any more animations.\
Example Usage

```javascript
import {
    Rive,
    Fit,
    Alignment,
    Layout,
    decodeFont,
    ImageAsset, // Optionally include for type checking
    FontAsset, // Optionally include for type checking
    FileAsset, // Optionally include for type checking
} from "@rive-app/canvas";

// Load a random asset by using a decodeFont API to feed to a
// setFont API on the asset provided in assetLoader
const randomFontAsset = (asset) => {
const urls = [
    "https://cdn.rive.app/runtime/flutter/IndieFlower-Regular.ttf",
    "https://cdn.rive.app/runtime/flutter/comic-neue.ttf",
    "https://cdn.rive.app/runtime/flutter/inter.ttf",
    "https://cdn.rive.app/runtime/flutter/inter-tight.ttf",
    "https://cdn.rive.app/runtime/flutter/josefin-sans.ttf",
    "https://cdn.rive.app/runtime/flutter/send-flowers.ttf",
];
let randomIndex = Math.floor(Math.random() * urls.length);
fetch(urls[randomIndex]).then(
    async (res) => {
    // decodeFont creates a Rive-specific Font object that `setFont()` takes
    // on the asset from assetLoader
    const font = await decodeFont(new Uint8Array(await res.arrayBuffer()));
    asset.setFont(font);

    // Be sure to call unref on the font once it is no longer needed. This
    // allows the engine to clean it up when it is not used by any more animations.
    font.unref();
    }
);
};


const riveInstance = new Rive({
src: "acqua_text.riv",
stateMachines: "State Machine 1", // Name of the State Machine to play
canvas: document.getElementById("rive-canvas"),
layout: new Layout({
    fit: Fit.Cover,
    alignment: Alignment.Center,
}),
autoplay: true,
// Callback handler to pass in that dictates what to do with an asset found in
// the Rive file that's being loaded in
assetLoader: (asset, bytes) => {
    console.log("Asset properties to query", {
        name: asset.name,
        fileExtension: asset.fileExtension,
        cdnUuid: asset.cdnUuid,
        isFont: asset.isFont,
        isImage: asset.isImage,
        isAudio: asset.isAudio,
        bytes,
    });

    // If the asset has a `cdnUuid`, return false to let the runtime handle
    // loading it in from a CDN. Or if there are bytes found for the asset
    // (aka, it was embedded), return false as there's no work needed here
    if (asset.cdnUuid.length > 0 || bytes.length > 0) {
        return false;
    }

    // Here, we load a font asset with a random font on load of the Rive file
    // and return true, because this callback handler is responsible for loading
    // the asset, as opposed to the runtime
    if (asset.isFont) {
        randomFontAsset(asset);
        return true;
    }
},
onLoad: () => {
    // Prevent a blurry canvas by using the device pixel ratio
    riveInstance.resizeDrawingSurfaceToCanvas();
}
});
```

<Resources />

---
## runtimes/web/low-level-api-usage.mdx

---
title: 'Low-level API Usage'
description: 'Using low-level JS APIs to construct Rive scenes.'
---

## Background

While the JS runtime offers a high-level API that allows for integrating Rives into web applications quickly, the runtime also allows for a smaller advanced low-level API that allows for constructing and controlling Rive(s) in your own render loop. There are several reasons and benefits to using this lower-level API:

- Construct a scene of multiple Rive files, artboards, linear animations, and state machines, all in one `<canvas>` element. This is useful if you're building a game!
- Control the render loop, which involves how you advance each artboard, animation, and state machine over time (including speed)
- Ability to tap into several transform property values on nodes/bones in the draw hierarchy
- Smaller dependency size
- ...and more!

## Premise

Here's the basic render workflow using the low-level API to render Rives:

<Steps>
  <Step title="Load the Rive Web Assembly (WASM) file, which contains the module with lower-level APIs" />
  <Step title="Load the Rive file in" />
  <Step title="Create instances for Artboards, LinearAnimations, and StateMachines" />
  <Step title="Build the render loop function to manipulate the instances created above">
    <Steps>
      <Step title="Advance any animation instances and apply it" />
      <Step title="Advance any state machine instances" />
      <Step title="Advance the artboard" />
      <Step title="Render the updated artboard on the canvas" />
      <Step title="Request the next animation frame" />
    </Steps>
  </Step>
  <Step title="Clean-up created instances when finished" />
</Steps>

## Getting Started

If you’ve decided that the low-level JS APIs are what you need for your app, read below for a guide on how to set everything up, or you can skip to the end to see some examples in action.

### Loading in WASM

The first step to setting up the low-level Rive APIs is to load in the Rive WASM file from either the `@rive-app/canvas-advanced` or `@rive-app/webgl2-advanced` libraries (by default, we recommend `@rive-app/canvas-advanced` for a smaller dependency, unless you need to use WebGL2). When the WASM file is loaded into your app, you'll gain access to necessary APIs such as the renderer for canvas/WebGL, along with relevant JS classes generated from underlying CPP bindings via [rive-cpp](https://github.com/rive-app/rive-cpp), the core c++ runtime used as the base for several other Rive runtimes. You'll use these classes to construct your rendering scene in the canvas below.

You can load the Rive WASM file via [unpkg](https://unpkg.com/) (hosts our NPM modules for the JS runtimes), which will make a network call to the CDN, or you can choose to host the WASM file on your own servers. With `unpkg`, the URL will look something like this:

https://unpkg.com/@rive-app/canvas-advanced@2.26.1/rive.wasm

<Note>
 You'll want to ensure that the version at the end of @rive-app/canvas-advanced@ or @rive-app/webgl2-advanced@ matches the version of the dependency you installed in your app. For example, if you installed @rive-app/canvas-advanced@2.26.1 in package.json, the Rive WASM file you request from unpkg would be https://unpkg.com/@rive-app/canvas-advanced@2.26.1/rive.wasm.
<br/>
 See [Preloading WASM](/runtimes/web/preloading-wasm) to preload WASM.
</Note>

To start, import the default module from the library and then call it with an object where you only need to set a single parameter, `locateFile`, which is a function that returns the URI of the WASM file. This can be either the `unpkg` URL or the URI to your self-hosted version of it. Simply `await` for the call to resolve, and then you'll get a reference to the low-level Rive runtime APIs.

```javascript
import RiveCanvas from '@rive-app/canvas-advanced';

async function main() {
  const rive = await RiveCanvas({
    locateFile: (_) => '<https://unpkg.com/@rive-app/canvas-advanced@2.26.1/rive.wasm>'
  });
}
main();
```

### Creating the Renderer

Once the WASM is loaded in, the next step is to create the renderer with the `makeRenderer()` API and pass in the canvas element on which Rive should render. The renderer draws Rive onto the `<canvas>` element with a rendering context. If you're using `@rive-app/canvas-advanced`, it will create a Canvas2D rendering context. If you're using `@rive-app/webgl2-advanced`, it will create a WebGL rendering context.

```javascript
const canvas = document.getElementById('your-canvas-element');
const renderer = rive.makeRenderer(canvas);
```

### Loading in Rive Files

After the renderer is created, you can also start to load in the Rive file(s) as an ArrayBuffer, which you'll feed into the runtime's `load()` API. You can fetch this at a URL or from somewhere within your project.

```typescript
const bytes = await (
  await fetch(new Request('basketball.riv'))
).arrayBuffer();

// import File as a named import from the Rive dependency
const file = (await rive.load(new Uint8Array(bytes))) as File;
```

<Note>
 Make sure to await the `.load()` call, as it synchronously tries to load assets from the `File`. Additionally, pass in the `ArrayBuffer` to a `Uint8Array` view before sending it as a param to `.load()`
</Note>
### Setting up the Instances

Once you have a reference to the loaded `File` object, you can begin instancing all the artboards, state machines, and linear animations from the Rive file. Instancing creates an underlying CPP reference and allows you to control how each entity advances over time. More on that further down this guide.

The main components you will most likely want to instance are:

- `Artboard` - Instance 1 or more artboards from the Rive file you want to draw
- `StateMachineInstance` - Instance a state machine from a given artboard
- `LinearAnimationInstance` - Instance a single timeline animation from a given artboard

Start by instancing an artboard, and then you can create a state machine and linear animation instances from the artboard reference like below.

```javascript
const artboard = file.artboardByName('New Artboard');
const animation = new rive.LinearAnimationInstnace(
  artboard.animationByName('idle'),
  artboard
);
const stateMachine = new rive.StateMachineInstance(
  artboard.stateMachineByName('your-state-machine-name'),
  artboard
);
```

The great thing here is if you want to display multiple artboards or even copies of the same one on the canvas, you can easily do so (as opposed to the high-level API, which only displays one at a time).

Beyond instancing the relevant pieces for the render loop, you can also extract references to nodes, targets, and bones within the drawing hierarchy. This is useful if you need to track any transform property values on a given node for any calculations or even to get world-space or parent transforms (i.e., tracking the x, y-coordinate, or rotation value of a node over the lifetime of an animation). See some of the examples at the bottom of the guide to see this in action.

### Constructing the Render Loop

You may be familiar with constructing a render loop using `requestAnimationFrame` (rAF) to build animations frame-by-frame in between the browser's repaint cycle. If not, check out [this guide](https://developer.mozilla.org/en-US/docs/Games/Anatomy#building_a_main_loop_in_javascript) as a starting point for building a render loop.

In the case of a Rive render loop, you'll be using a custom Rive API that wraps rAF, so you'll need to use `rive.requestAnimationFrame()` as well as `rive.cancelAnimationFrame()`. The structure should be similar to any other rAF loop you build for other animations, but you'll be advancing the instances you created above and aligning the artboard to the canvas as you see fit.

Start by creating your callback loop for the rAF cycle and tracking the last time since the previous rAF callback to get an elapsed time in seconds. Then, clear the canvas by using the renderer's `.clear()` API.

```javascript
let lastTime = 0;
function renderLoop(time) {
  if (!lastTime) {
    lastTime = time;
  }
  const elapsedTimeMs = time - lastTime;
  const elapsedTimeSec = elapsedTimeMs / 1000;
  lastTime = time;

  renderer.clear();

  ...

  rive.requestAnimationFrame(renderLoop);
}
rive.requestAnimationFrame(renderLoop);
```

#### Advancing Animations

A `LinearAnimationInstance` has a set of keyframes to apply to objects in an artboard. In the render loop, you'll want to call `.advance()` on the created animation instances to get those keyframes and, like the API is named, advance the animation by a certain amount of time (in seconds).

<Note>
 Normally, you would want to advance the animation by the elapsed time calculated above to playback at “normal” speed (or rather, whatever speed is set for that timeline animation). With the low-level APIs, by controlling the render loop, you can advance the instance by a custom time value, such as half the elapsed time (to playback the animation at 0.5x speed) or even twice the elapsed time (to playback the animation at 2x speed). You could even multiply the elapsed time by -1 to run the animation direction backward.
</Note>

In addition to advancing a linear animation, you need to apply the keyframe values to the properties of relevant objects in the artboard for that animation and specify the animation's mix value using the `.apply()` call. When the animation applies the interpolated values from the keyframes, it blends these values with the current values on the artboard objects. This allows you to "blend" into an animation, which is helpful if you have two animation instances applying a keyframe value on the same property of an object. The default mix value to replace the old property values with the new keyframe values should be `1`.

After applying an animation’s values to the artboard, advance the artboard (more on that below) to update the artboard's objects and resolve the property value changes.

To summarize all of this, the order of operations in advancing a linear animation is as follows:

```css
advance animation -> apply animation values -> advance artboard
```

See the below snippet for an example:

```typescript
function renderLoop(time) {
  if (!lastTime) {
    lastTime = time;
  }
  const elapsedTimeMs = time - lastTime;
  const elapsedTimeSec = elapsedTimeMs / 1000;
  lastTime = time;

  renderer.clear();
  animation.advance(elapsedTimeSec);
  animation.apply(1);
  artboard.advance(elapsedTimeSec);
}
```

#### Advancing State Machines

A `StateMachineInstance` is similar to the `LinearAnimationInstance` flow above, with a few differences. With state machines, you don't need to apply a mix value since you should only have one state machine instance correlated to an artboard, and mix values are determined by the transitions set between timeline animations. Additionally, the `.advance()` method updates the properties of objects on the artboard. Therefore, the order of operations for advancing a state machine is simplified to:\\\`

```css
advance state machine -> advance artboard
```

See the below snippet for an example:

```javascript
function renderLoop(time) {
  if (!lastTime) {
    lastTime = time;
  }
  const elapsedTimeMs = time - lastTime;
  const elapsedTimeSec = elapsedTimeMs / 1000;
  lastTime = time;

  renderer.clear();
  stateMachine.advance(elapsedTimeSec);
  artboard.advance(elapsedTimeSec);
}
```

#### Advancing the Artboard

As you've seen above, advancing the artboard will do the work of updating the relevant objects in the hierarchy after the values have been applied through animations and/or state machines. If you're controlling multiple animations at once, you only need to advance the artboard once in the render loop. If you're controlling multiple artboards for your scene in the canvas, advance each artboard as needed in the render loop.

#### Align and Render

The last bit to consider in the render loop is to set the alignment of the artboard(s), set the bounds for the drawing area and artboard, and then finally pass the rendering context to the artboard so that the artboard gets drawn in the canvas.

After advancing the artboard, call the `save()` API on the rendering context to save the state of the canvas. Then call the `align()` API on the context to provide:

1. `Fit` and `Alignment` values
2. The bounds of the canvas space to draw to
3. The bounds of the Rive content to draw within that space

[See here](/runtimes/web/layouts) for options for `Fit` and `Alignment`. For the latter two parameters, provide an axis-aligned bounding box (AABB). See the snippet below for an example of the `align()` API.

Finally, after calling the `align()` API, pass the renderer to the artboard via the `draw()` method to draw the artboard on the canvas, then end with a call to the `restore()` API on the renderer to restore the saved state of the canvas.

<Note>
 If you're using `@rive-app/webgl2-advanced`, you will need to call `renderer.flush()` to empty different buffer commands.
</Note>
The last thing to do is to call on Rive's `requestAnimationFrame` with this callback to queue up the next callback for the next frame.

Altogether, this looks like the following:

```javascript
function renderLoop(time) {
  if (!lastTime) {
    lastTime = time;
  }
  const elapsedTimeMs = time - lastTime;
  const elapsedTimeSec = elapsedTimeMs / 1000;
  lastTime = time;

  ...

  renderer.clear();
  stateMachine.advance(elapsedTimeSec);
  artboard.advance(elapsedTimeSec);
  renderer.save();
  renderer.align(
    rive.Fit.contain,
    rive.Alignment.center,
    {
      minX: 0,
      minY: 0,
      maxX: canvas.width,
      maxY: canvas.height
    },
    artboard.bounds,
  );
  artboard.draw(renderer);
  renderer.restore();
  // Optionally make the below call if using WebGL
  // renderer.flush()
  rive.requestAnimationFrame(renderLoop);
}
rive.requestAnimationFrame(renderLoop);
```

At this point, you should be able to render Rive on the canvas!

### Cleaning Up Instances

For each of the created CPP instances, you’ll want to delete them when you are finished so that you don’t have any memory leaks in your application. Unfortunately, this is a manual operation as we cannot yet rely on the new finalizer API in browsers to be called for garbage collection. Call the `.delete()` API on any instances created from the Rive runtime when they are no longer needed. An example is shown below:

```javascript
// Created instances
const renderer = rive.makeRenderer(canvas);
const bytes = await (
  await fetch(new Request('basketball.riv'))
).arrayBuffer();
const file = (await rive.load(new Uint8Array(bytes))) as File;
const artboard = file.artboardByName('New Artboard');
const animation = new rive.LinearAnimationInstnace(
  artboard.animationByName('idle'),
  artboard
);
const stateMachine = new rive.StateMachineInstance(
  artboard.stateMachineByName('your-state-machine-name'),
  artboard
);

...

renderer.delete();
file.delete();
artboard.delete();
animation.delete();
stateMachine.delete();
```

## Examples

See below for links to examples demonstrating the use of low-level JS APIs:

- [Simple use of @rive-app/canvas-advanced](https://codesandbox.io/p/sandbox/canvas-advance-api-example-s6dz3m?file=%2Fsrc%2Findex.ts)
- [Simple use of @rive-app/webgl2-advanced](https://codesandbox.io/p/sandbox/rive-webgl-advanced-57lczl?file=%2Fsrc%2Findex.ts)
- [Out of band assets (fonts) @rive-app/canvas-advanced](https://codesandbox.io/p/sandbox/rive-canvas-advanced-out-of-band-assets-fonts-3q4zzy?file=%2Fsrc%2Findex.ts)

## API References

See our [types file](https://github.com/rive-app/rive-wasm/blob/master/js/src/rive_advanced.mjs.d.ts) for the advanced API to understand the API signatures and return types.

## Caveats

The high-level JS runtime APIs are built with the low-level APIs specified above. Along with this, the high-level JS runtime has additional affordances that make it easy for users to do some of the following things:

- Ease of playback control with APIs such as `.play()`, `.pause()`, `.stop()`, etc.
- Callbacks such as `onStateChange`, `onLoad`, etc. that would allow you to hook into specific Rive lifecycle events
- Hooking up gesture events to [Rive Listeners](/editor/state-machine/listeners)

When using Rive’s advanced JS APIs to customize how you use Rive, you will have to set up some of these affordances yourself. Take a look at how the [high-level Rive API is built here](https://github.com/rive-app/rive-wasm/blob/master/js/src/rive.ts) to get a sense of how to replicate some of these high-level affordances should you need these.

## Integrating Rive into Existing rAF Loop

If you're looking to add Rive to your existing render loop (the JS API `requestAniationFrame()`) and do not want to use the Rive-wrapped `requestAnimationFrame()` API, you can do so with an extra API call at the end of your render loop. Call the `rive.resolveAnimationFrame()` API at the end of the render loop before calling `requestAnimationFrame()` again.
---
## runtimes/web/migration-guides.mdx

---
title: 'Migration Guides'
description: 'Migrating between major versions of the Apple runtime'
---

<AccordionGroup>
    <Accordion title={`Migrating from @rive-app/webgl to @rive-app/webgl2`}>
        We highly recommend migrating to `@rive-app/webgl2` for the best rendering quality and performance in most cases. The `@rive-app/webgl` package is deprecated and no longer receives updates after `v2.37.0`.

        The migration process involves updating your package installation and import statements to use `@rive-app/webgl2` instead of `@rive-app/webgl`. There are no breaking API changes, so your existing code should work with the new package without modification.

        For example, if you were previously using:

        ```bash
        npm install @rive-app/webgl
        ```

        ```typescript
        import { Rive } from '@rive-app/webgl';
        ```

        You can update this to:

        ```bash
        npm install @rive-app/webgl2
        ```

        ```typescript
        import { Rive } from '@rive-app/webgl2';
        ```

        This change will allow you to take advantage of the improved rendering capabilities of the [Rive renderer](https://rive.app/renderer) while maintaining compatibility with your existing codebase.
    </Accordion>
    <Accordion title="Migrating from v1 to v2">
        Starting in v2 of our Web (JS) runtimes, Rive will support Rive Text at runtime, which includes the following packages:

        - Web (JS) / WASM
        - `@rive-app/canvas`
        - `@rive-app/canvas-advanced`
        - `@rive-app/canvas-single`
        - `@rive-app/webgl2`

        ## Major Changes
        <Note>
        No breaking API changes!
        </Note>

        While a new major version has been released for the runtimes without breaking API changes, v2 was released due to a **bundle** **size increase** in the package. The reason for this is new internal dependencies added to the Web Assembly (WASM) build that powers Rive, specifically for supporting the powerful Rive Text feature. You may find that the request for the WASM file when loading Rive is *\~261kb* brotli-compressed as of `v2.0.0`.

        If you're looking for a lite version without the Rive Text/Layouts/Audio/Scripting features, you can look to `@rive-app/canvas-lite`.
    </Accordion>
    <Accordion title="Migrating from rive.js">
       Previously, the web runtime would deploy to the [rive-js](https://www.npmjs.com/package/rive-js) package on npm. We have since moved away from this one-package model and into a place where you can import from several different packages based on your API/rendering-level needs.

        - @rive-app/webgl2
        - @rive-app/canvas
        - @rive-app/canvas-advanced

        In addition to these new packages, there is a `@rive-app/canvas-single` package that has the WASM encoded in the JS. See [canvas vs webgl2](/runtimes/web/canvas-vs-webgl) for more details.

        We changed the package model to choose which renderer to use (i.e., [CanvasRenderingContext2D](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) vs. [WebGL2](https://developer.mozilla.org/en-US/docs/Web/API/WebGL2RenderingContext)), impacting bundle size and performance. In addition, all of the new web runtime packages will support the latest Rive features, such as raster assets.

        In any case, there should be no changes in high-level API usage required as far as using the `rive` instance. You only need to change the package you install in your project and the associated places you import it.

        For instance, instead of the following integration:

        ```bash
        npm i rive-js
        ```

        ```typescript
        import rive from 'rive-js';

        const foo = new rive.Rive({
        src: "https://cdn.rive.app/animations/vehicles.riv",
        });
        ```

        You could replace this with:

        ```bash
        npm i @rive-app/webgl2
        ```

        ```typescript
        import {Rive} from '@rive-app/webgl2';

        const foo = new Rive({
        src: "https://cdn.rive.app/animations/vehicles.riv",
        });
        ```

        Or, you can replace `@rive-app/webgl2` with any of the new package outputs for web runtime that suit your need.
    </Accordion>
</AccordionGroup>
---
## runtimes/web/playing-audio.mdx

---
title: "Playing Audio"
description: "Playing Rive audio events"
---

import Overview from "/snippets/runtimes/playing-audio/overview.mdx"
import WebWarning from "/snippets/runtimes/playing-audio/web-warning.mdx"
import EmbeddedAssets from "/snippets/runtimes/playing-audio/embedded-assets.mdx"
import ReferencedAssets from "/snippets/runtimes/playing-audio/referenced-assets.mdx"

<Overview />

<WebWarning />

<EmbeddedAssets />

<ReferencedAssets />

For more information, see [Loading Assets](/runtimes/web/loading-assets).

## Volume control

To control volume on the artboard, set the `.volume` property on the Rive instance. The value is a multiplier applied to the default volume level of each audio event on the artboard, allowing you to adjust the overall audio level up or down as needed. The default value is `1.0`, which means the audio plays at its default level.
To mute the audio, set `.volume` to `0`.

The example below adjusts the volume to be 50% softer than the default level.
```javascript
const r = new Rive ({ ... });
r.volume = 0.5;
```

---
## runtimes/web/preloading-wasm.mdx

---
title: 'Preloading WASM'
description: ''
---

import Overview from '/snippets/runtimes/preloading-wasm/overview.mdx'
import Thanks from '/snippets/runtimes/preloading-wasm/thanks.mdx'

<Overview />

If you're using the base `@rive-app/canvas` or `@rive-app/webgl2` (or any plain JS-variant runtime), import the WASM resource into your app, as well as the `RuntimeLoader` API:

```javascript
import riveWASMResource from '@rive-app/canvas/rive.wasm';
import { Rive, RuntimeLoader } from '@rive-app/canvas';

RuntimeLoader.setWasmUrl(riveWASMResource);
...
const riveInstance = new Rive({
  src: 'foo.riv',
  ...
});
```

The `RuntimeLoader` is a singleton that manages loading in the WASM file behind the scenes when loading in the `Rive` instance. By calling the `setWasmUrl` API, you can load in WASM for the Rive runtime with the data URI from the direct import of the WASM file. Run this API on any page that has a Rive animation to load.

<Note>
 You may need to add configuration into your build tool to import WASM files and inline it as a data URI. See the [original blog post](https://dev.to/alex_barashkov/optimization-techniques-for-rive-animations-in-react-apps-1a8p) that inspired us to add these to docs for some guidance here
</Note>

<Thanks />


---
## runtimes/web/rive-events.mdx

---
title: "Rive Events"
description: "⚠️ DEPRECATED: Use Data Binding instead of Events"
noindex: true
---

import { YouTube } from "/snippets/youtube.mdx";

import Overview from "/snippets/runtimes/events/overview.mdx"
import AdditionalResources from "/snippets/runtimes/events/additional-resources.mdx"

<Overview />

### Examples

- [Star rating example](https://codesandbox.io/p/sandbox/rive-events-js-forked-gkwjqr)
- [Neostream example (Chrome only)](https://codesandbox.io/p/sandbox/neostream-rive-events-js-forked-g7t3xl) (This example does not make use of the new [Audio Events ](/editor/events/audio-events)feature)

### High-level API usage

#### Adding an Event Listener

Similar to the `addEventListener()` / `removeEventListener()` API for DOM elements, you'll use the Rive instance's `on()` / `off()` API to subscribe to Rive events. Simply supply the RiveEvent enum and a callback for the runtime to call at the appropriate moment any Rive event gets detected.

#### Example Usage

```javascript
import { Rive, EventType, RiveEventType } from '@rive-app/canvas'

const r = new Rive({
src: "/static-assets/star-rating.riv",
artboard: "my-artboard-name",
autoplay: true,
stateMachines: "State Machine 1",
// automaticallyHandleEvents: true, // Automatically handle OpenUrl events
onLoad: () => {
    r.resizeDrawingSurfaceToCanvas();
},
});

function onRiveEventReceived(riveEvent) {
const eventData = riveEvent.data;
const eventProperties = eventData.properties;
if (eventData.type === RiveEventType.General) {
    console.log("Event name", eventData.name);
    // Added relevant metadata from the event
    console.log("Rating", eventProperties.rating);
    console.log("Message", eventProperties.message);
} else if (eventData.type === RiveEventType.OpenUrl) {
    console.log("Event name", eventData.name);
    window.open(eventData.url);
}
}

// Add event listener and provide callback to handle Rive Event
r.on(EventType.RiveEvent, onRiveEventReceived);
// Can unsubscribe to Rive Events at any time via the off() API like below
// r.off(EventType.RiveEvent, onRiveEventReceived);
```

### Low-level API usage

When using the low-level APIs (i.e. `@rive-app/canvas-advanced`), you'll need to catch Rive events reported during the render loop yourself via your created state machine instance (see docs on [Low-level API Usage](/runtimes/web/low-level-api-usage)). To achieve this, before advancing the state machine:

- Determine the number of Rive events reported since the last frame via the state machine's `reportedEventCount()` API
- Iterate over the events and grab a reference to an Event via the state machine's `reportedEventAt(idx)` API

```javascript
import RiveCanvas, {RiveEventType} from '@rive-app/canvas-advanced';

...
// render loop
function myCustomRenderLoop(timestamp) {
    ...
    const elapsedTimeSec = (timestamp - prevTimestamp) / 1000;
    if (stateMachine) {
    const numFiredEvents = stateMachine.reportedEventCount();
    for (let i = 0; i < numFiredEvents; i++) {
        const event = stateMachine.reportedEventAt(i);
        // Run any Event-based logic now
        if (event.type === RiveEventType.OpenUrl) {
        const a = document.createElement("a");
        a.setAttribute("href", event.url);
        a.setAttribute("target", event.target);
        a.click();
        }
    }
    }
    // Now advance
    stateMachine.advance(elapsedTimeSec);
    ...
    rive.requestAnimationFrame(myCustomRenderLoop);
}
rive.requestAnimationFrame(myCustomRenderLoop);
```

<AdditionalResources />

---
## runtimes/web/rive-parameters.mdx

---
title: 'Rive Parameters'
description: 'API docs for the Rive instance.'
---

This page is a **reference** for constructor options, types, and instance methods on the high-level **`Rive`** class, as well as a number of other exported classes. For walkthroughs and samples, use the guides below and link back here when you need exact signatures.

**Related guides**

- [Getting started](/runtimes/web/web-js) — start here for a walkthrough of loading Rive into your web applications
- [Artboards](/runtimes/web/artboards) — choosing artboards to load from the `.riv` file
- [Layout](/runtimes/web/layouts) — see how to layout your Rive graphic within the canvas and make it responsive to size changes
- [State machine playback](/runtimes/web/state-machines) — handle playback controls for the Rive state machine
- [Loading assets](/runtimes/web/loading-assets) — handle asset loading for your Rive file
- [Caching a Rive file](/runtimes/web/caching-a-rive-file) — **`RiveFile`** + **`riveFile`** for multiple instances
- [Data binding](/runtimes/web/data-binding) — **`autoBind`**, view models, `bindViewModelInstance`
- [Playing audio](/runtimes/web/playing-audio) — handling audio assets and controlling volume levels

## `Rive` constructor parameters

You can set any of the following parameters on the Rive object when instantiating:

```typescript
export interface RiveParameters {
  canvas: HTMLCanvasElement | OffscreenCanvas; // required
  src?: string; // one of src, buffer, or riveFile is required
  buffer?: ArrayBuffer; // one of src, buffer, or riveFile is required
  riveFile?: RiveFile; // one of src, buffer, or riveFile is required
  artboard?: string;
  stateMachines?: string | string[]; // strongly recommended setting this property
  layout?: Layout;
  autoplay?: boolean;
  autoBind?: boolean;
  useOffscreenRenderer?: boolean;
  enableRiveAssetCDN?: boolean;
  shouldDisableRiveListeners?: boolean;
  isTouchScrollEnabled?: boolean;
  automaticallyHandleEvents?: boolean;
  dispatchPointerExit?: boolean;
  enableMultiTouch?: boolean;
  drawingOptions?: DrawOptimizationOptions;
  onLoad?: EventCallback;
  onLoadError?: EventCallback;
  onPlay?: EventCallback;
  onPause?: EventCallback;
  onStop?: EventCallback;
  onLoop?: EventCallback;
  onStateChange?: EventCallback;
  onAdvance?: EventCallback;
  assetLoader?: AssetLoadCallback;
  enablePerfMarks?: boolean;

  // Deprecated parameters
  animations?: string | string[]; // deprecated in favor of stateMachines
}
```

- `canvas` - *(required)* Provide a `<canvas>` element to draw Rive animations onto.
- To load a `.riv` file, one of the following is required:
  - `src` - *(optional)* Hosted URL or app-relative public path to the `.riv` file. See a minimal example on the [Getting started](/runtimes/web/web-js#loading-rive-files) guide.
  - `buffer` - *(optional)* `ArrayBuffer` of `.riv` bytes.
  - `riveFile` - *(optional)* Provide a loaded **`RiveFile`** across instances. See [Caching a Rive file](/runtimes/web/caching-a-rive-file) for more details.
- `artboard` - *(optional)* Name of the artboard to use. If not provided, it will pull the default artboard from the exported `.riv` file.
- `stateMachines` - *(strongly recommended)* Name of a state machine to load (i.e. `"State Machine 1"`) from the `.riv` file. If not provided, currently Rive will pull the first linear animation it finds (deprecated behavior). In the next major version of the runtime, Rive will default to pulling the default state machine on the artboard.

<Note>
 Note: You should only provide a single state machine string for `stateMachines`. Running multiple state machines of the same artboard at the same time may cause unintended consequences.
</Note>

- `layout` - *(optional)* Provide a [`new Layout()`](/runtimes/web/layouts) instance. See that guide for fit modes, alignment, bounds, and responsive layout.
- `autoplay` - *(optional)* If true, the animation will automatically start playing when loaded. Defaults to false.
- `autoBind` - *(optional)* When set to `true`, Rive will automatically look for a default view model and view model instance to bind to the artboard. Defaults to false.
- `useOffscreenRenderer` - *(optional)* Boolean flag to determine whether to use a shared offscreen WebGL2 context rather than create its own WebGL2 context for this instance of Rive. This is only relevant for WebGL-based runtimes such as `@rive-app/webgl2`. If you are displaying multiple Rive instances on a page, it is highly encouraged to set this flag to `true`. Defaults to `false`.
- `enableRiveAssetCDN` - *(optional)* Allow the runtime to automatically load assets (i.e. fonts) hosted in Rive's CDN. Defaults to true.
- `shouldDisableRiveListeners` - *(optional)* Boolean flag to disable setting up Rive Listeners on the `<canvas>` element, thus preventing any event listeners from being set up on the element.
  - **Note:** Rive Listeners by default are not set up on a `<canvas>` element if there is no playing state machine, or a state machine without any Rive Listeners set up on the state machine
- `isTouchScrollEnabled` - *(optional)* For Rive Listeners, allows scrolling behavior to still occur on canvas elements when a touch/drag action is performed on touch-enabled devices. Otherwise, scroll behavior may be prevented on touch/drag actions on the canvas by default.
- `automaticallyHandleEvents` - *(optional)* Enable Rive Events to be handled by the runtime. This means any special Rive Event may have a side effect that takes place implicitly. For example, if during the render loop an `OpenUrlEvent` is detected, the browser may try to open the specified URL in the payload. This flag is `false` by default to prevent any unwanted behaviors from taking place. This means any special Rive Event will have to be handled manually by subscribing to `EventType.RiveEvent`
- `dispatchPointerExit` - *(optional)* For Rive Listeners, dispatches a pointer exit event when the pointer exits the canvas. This can be useful for ensuring hover states are properly reset when the user's cursor leaves the canvas area. Defaults to true.
- `enableMultiTouch` - *(optional)* Enables multi-touch support for Rive Listeners. When enabled, the runtime will track and respond to multiple simultaneous touch points on touch-enabled devices. Defaults to false.
- `drawingOptions` - *(optional)* An enum (`DrawOptimizationOptions`) that provides drawing optimization options. This can be used to configure rendering performance optimizations. The default is `DrawOptimizationOptions.DrawOnChanged`, which will only submit a draw command if the artboard has visually updated.
  - `DrawOptimizationOptions.DrawOnChanged` - Only submit a draw command if the artboard has visually updated
  - `DrawOptimizationOptions.AlwaysDraw` - Always submit a draw command, even if the artboard has not visually updated.
- `onLoad` - *(optional)* Callback that gets fired when the .riv file loads.
- `onLoadError` - *(optional)* Callback that gets fired when an error occurs loading the .riv file.
- `onPlay` - *(optional)* Callback that gets fired when the animation starts playing.
- `onPause` - *(optional)* Callback that gets fired when the animation pauses.
- `onStop` - *(optional)* Callback that gets fired when the animation stops playing.
- `onLoop` - *(optional)* Callback that gets fired when the animation completes a loop.
- `onStateChange` - *(optional)* Callback that gets fired when a state change occurs.
- `onAdvance` - *(optional)* Callback that gets fired every frame when the Artboard has advanced.
- `assetLoader` - *(optional)* Callback to load assets. Full patterns and examples in the [loading assets](/runtimes/web/loading-assets) guide.
- `enablePerfMarks` - *(optional)* Emits `performance.mark` / `performance.measure` entries for key Rive startup and render events for performance profiling purposes. False by default. Also available on `RuntimeLoader` and `RiveFile`.

### Deprecated parameters
- `animations` - *(optional)* Deprecated in favor of `stateMachines`. Name of a singular timeline animation to load from the `.riv` file. If not provided, Rive will pull the first linear animation it finds. In the next major version of the runtime, Rive will default to pulling the default state machine on the artboard.


## APIs

The following APIs are available on a `Rive` instance after construction.

---

### Data binding (View Models)

View model APIs on `Rive` are documented in depth on the [data binding](/runtimes/web/data-binding) guide. For a quick reference on available APIs on the `Rive` instance, see below:

- `viewModelInstance` (getter) — currently bound instance, if any. This is available if `autoBind` is `true` and there is a default View Model instance to reference. From an instance, you can get a reference to view model properties based on type:
  - `.number(path: string): ViewModelInstanceNumber`
  - `.boolean(path: string): ViewModelInstanceBoolean`
  - `.string(path: string): ViewModelInstanceString`
  - `.color(path: string): ViewModelInstanceColor`
  - `.trigger(path: string): ViewModelInstanceTrigger`
  - `.enum(path: string): ViewModelInstanceEnum`
  - `.list(path: string): ViewModelInstanceList`
  - `.image(path: string): ViewModelInstanceAssetImage`
  - `.artboard(path: string): ViewModelInstanceArtboard`
  - `.viewModel(path: string): ViewModelInstance`
  - `.viewModelName` - Getter property to return the name of the `ViewModel` the instance is created from
  - `.properties` - Getter property to return the list of properties available on this `ViewModel`
- `viewModelCount` (getter)
- `viewModelByIndex(index: number): ViewModel | null` - returns a `ViewModel` specified by index from the `.riv` file, or null if it doesn't exist or the file isn't loaded yet
- `viewModelByName(name: string): ViewModel | null` - returns a `ViewModel` specified by name, or null if it doesn't exist or the file isn't loaded yet
- `defaultViewModel(): ViewModel | null` - returns the default `ViewModel` for the file, or null if it doesn't exist or the file isn't loaded yet
- `bindViewModelInstance(instance: ViewModelInstance | null): void` - Binds a `ViewModelInstance` to the state machine. Note that this is taken care of automatically if `autoBind` is `true`.
- `enums(): DataEnum[]` - List of enums defined in the file
- `getBindableArtboard(name: string): BindableArtboard | null` - Returns a named artboard as a `BindableArtboard`, which exposes data-binding APIs. Once you have a bindable artboard, you can set the `.viewModel` property on that artboard to bind a `ViewModelInstance`. Bindable artboards can be set as a value to an artboard property on a different ViewModel. Returns `null` if the artboard doesn't exist or the file isn't loaded.
- `getDefaultBindableArtboard(): BindableArtboard | null` - Returns the file's default artboard as a `BindableArtboard`, or `null` if not available.

---

### Playback

Examples and UX-oriented discussion: [State machine playback](/runtimes/web/state-machines).

#### play()

`play(names?: string | string[], autoplay?: true): void`

Plays a specified state machine via the passed-in name. Useful if you have either programmatically called `pause()` or `stop()` or set `autoplay: false` when instantiating Rive. If no name is passed in, it plays all instantiated state machines (or the default linear animation if a state machine is not instantiated).

#### pause()

`pause(names?: string | string[]): void`

Pauses a specified state machine via the passed-in name. If no name is passed in, it pauses all instantiated timeline animations or state machines.

#### stop()

`stop(names?: string | string[]): void`

Stops a specified state machine via the passed-in name. If no name is passed in, it stops all instantiated timeline animations or state machines.

#### reset()

```typescript
interface RiveResetParameters {
  artboard?: string;
  animations?: string | string[];
  stateMachines?: string | string[];
  autoplay?: boolean;
  autoBind?: boolean;
}

reset(params?: RiveResetParameters): void
```

Resets the artboard, timeline animations, and/or state machines from the start (or entry state). Cleans up existing artboard/animation/state machine instances first. Playback after reset follows `autoplay` and `autoBind` (same meaning as constructor parameters). Example: [State machine playback](/runtimes/web/state-machines).

---

### Canvas size and layout

Use these APIs to respond to canvas or window resize changes to ensure Rive content scales and renders clearly.

#### resizeDrawingSurfaceToCanvas()

`resizeDrawingSurfaceToCanvas(customDevicePixelRatio?: number): void`

Sets the canvas element’s `width` and `height` from its CSS layout size and device pixel ratio (or your optional `customDevicePixelRatio`). Reduces blur on high-DPI displays. Calls `resizeToCanvas()` and updates **`devicePixelRatioUsed`**. If `layout.fit` is set to `Fit.Layout`, artboard width/height are adjusted from the layout.

<Note>
In a future major version of this runtime, this API may be called internally on initialization by default, with an option to opt-out if you have specific `width` and `height` properties you want to set on the canvas.
</Note>

See the [layout](/runtimes/web/layouts) guide for examples on usage.

#### resizeToCanvas()

`resizeToCanvas(): void`

Sets layout bounds (`minX`, `minY`, `maxX`, `maxY`) from the current canvas pixel width and height. Call when the canvas backing store size changes.

#### resetArtboardSize()

`resetArtboardSize(): void`

Restores artboard dimensions to the file's original values.

#### devicePixelRatioUsed

Getter/setter for the device pixel ratio (DPR) value applied when sizing the drawing surface (updated by `resizeDrawingSurfaceToCanvas()`).

#### bounds

Artboard axis-aligned bounds, or `undefined` if the artboard is not ready.

#### layout (get/set)

Get this property to return the current `Layout` instance (treat as immutable; use `new Layout({...})` or `copyWith` to change). Set this property to replace the layout. Examples: [Layout](/runtimes/web/layouts).

#### artboardWidth / artboardHeight

Getters/setters for logical artboard dimensions. If the artboard is not loaded and you have not set a value, you may see `0`.

Avoid setting these manually when using [`resizeDrawingSurfaceToCanvas()`](#resizedrawingsurfacetocanvas) with `Fit.Layout`, because the runtime sets width/height from the canvas.

---

### Audio

#### volume

Getter/setter for artboard audio volume. The default value is `1.0`, which means the volume is set by the default level for that artboard.

See the [playing audio](/runtimes/web/playing-audio) guide for more details on controlling volume levels.

---

### Events

In addition to the event callbacks you can set in the `Rive` constructor (i.e. `onLoad`), you can also subscribe to events using the `on` and `off` methods for more controlled Rive event subscription.

#### on()

`on(type: EventType, callback: EventCallback): void`

Subscribe to runtime events (similar to `addEventListener`).

#### off()

`off(type: EventType, callback: EventCallback): void`

Unsubscribe using the same `EventType` and callback reference passed to `on()`.

#### removeAllRiveEventListeners()

`removeAllRiveEventListeners(type?: EventType): void`

Removes all listeners for a given `EventType`, or all types if `type` is omitted.

#### Event types and payload

```typescript
export enum EventType {
  Load = "load",
  LoadError = "loaderror",
  Play = "play",
  Pause = "pause",
  Stop = "stop",
  Loop = "loop", // Only applicable for timeline animations, not state machines
  Advance = "advance", // Called each frame after state machine advance
  StateChange = "statechange",
  RiveEvent = "riveevent",
}
```

The `Event` type is `{ type: EventType; data?: ... }`. The shape of `data` depends on `type`:

- **Load** — `RiveFile`  (the loaded file handle) or the string "buffer" indicating a load from an ArrayBuffer
- **LoadError** — `string` (error message)
- **Play**, **Pause**, **Stop** — `string[]` (names of the animations or state machines affected)
- **Loop** — `LoopEvent` (`{ animation: string; type: LoopType }`). `LoopType` is `OneShot`, `Loop`, or `PingPong`.
- **Advance** — `number` (elapsed seconds for that frame)
- **StateChange** — `string[]` (state names that changed)
- **RiveEvent** — custom or built-in Rive event payload (for example open-URL events)

For **`EventType.RiveEvent`** listener examples, see [Rive Events](/runtimes/web/rive-events). Prefer [Data binding](/runtimes/web/data-binding) for new work where it applies.

---

### File and lifecycle

When using Rive to load different Rive content, or to cleanup resources when Rive is no longer needed, the following APIs may be useful.

#### load()

```typescript
interface RiveLoadParameters {
  src?: string;
  buffer?: ArrayBuffer;
  riveFile?: RiveFile;
  autoplay?: boolean;
  autoBind?: boolean;
  artboard?: string;
  animations?: string | string[];
  stateMachines?: string | string[];
  useOffscreenRenderer?: boolean;
  shouldDisableRiveListeners?: boolean;
}

load(params: RiveLoadParameters): void
```

Replaces the current `.riv` source and reinitializes the instance. This also stops current playback and clears the previous file reference. One of `src`, `buffer`, or `riveFile` must be provided (same rule as the constructor) when resetting. WASM is typically already loaded, so you usually only pay network cost if you point at a new `.riv` hosted location.

#### cleanup()

`cleanup(): void`

Stops the render loop and disposes artboard, animations, state machines, renderer, file handle, listeners, and view model instance references. Call when the Rive instance is no longer needed to avoid memory leaks.

#### cleanupInstances()

`cleanupInstances(): void`

Disposes only artboard, timeline animation, and state machine instances. The file and renderer remain valid so you can switch artboards or re-init via `reset()` / `load()`.

#### deleteRiveRenderer()

`deleteRiveRenderer(): void`

Deletes the underlying renderer object, releasing GPU/WebGL resources. Call this only after `cleanup()` when you need a full teardown — for example, when removing a WebGL canvas from the DOM entirely. In most cases `cleanup()` alone is sufficient.

---

### Rendering loop

#### stopRendering()

`stopRendering(): void`

Stops scheduling frames. Does not change play/pause/stop state of animations. Resume with `startRendering()`. This is useful for situations when the `<canvas>` is not visible.

#### startRendering()

`startRendering(): void`

Starts the render loop if it was stopped with `stopRendering()`. No-op if already running.

#### drawFrame()

`drawFrame(): void`

Advances and draws one frame. Use this when you need an explicit draw after certain updates, but typically you do not need to manually call this API.

#### `resolveAnimationFrame()`

Not a method on the high-level **`Rive`** class, but available for using the low-level APIs when constructing a render loop from scratch. On the loaded **`RiveCanvas`** (`@rive-app/canvas-advanced` / `@rive-app/webgl2-advanced`), call **`rive.resolveAnimationFrame()`** after drawing when using the browser’s **`requestAnimationFrame`** yourself. The high-level **`Rive`** instance uses **`drawFrame()`** and its internal loop instead. Full loop example: [Low-level API — Integrating Rive into Existing rAF Loop](/runtimes/web/low-level-api-usage#integrating-rive-into-existing-raf-loop).

---

### Rive Listeners

In most cases, listeners are automatically set up and handled during instantiation. See the guide on Rive [listeners](/editor/state-machine/listeners) for more details.
The following APIs are available if you need specific control over Rive intercepting input events on the canvas.

#### setupRiveListeners()

`setupRiveListeners(options?: { isTouchScrollEnabled?: boolean }): void`

(Re)attaches pointer/touch listeners on the canvas for active state machines that use Rive Listeners. Called automatically when appropriate; use after dynamic changes if listeners must be refreshed. Optional `isTouchScrollEnabled` overrides the instance default for this setup only.

#### removeRiveListeners()

`removeRiveListeners(): void`

Removes listener callbacks installed for Rive Listeners on the canvas.

---

### Deprecated

The following APIs on the `Rive` instance are deprecated. They may still work but for future-proofing your Rive grpahics, we recommend migrating away from these patterns.

Setting state machine inputs and text runs directly are deprecated. Use [Data binding](/runtimes/web/data-binding) for new work where possible.

#### stateMachineInputs()

`stateMachineInputs(stateMachineName: string): StateMachineInput[] | undefined`

Returns inputs for an **instantiated** state machine with the given name, or `undefined` if the file is not loaded yet. See the below interface on getting/setting values and firing trigger inputs.

```typescript
export enum StateMachineInputType {
  Number = 56,
  Trigger = 58,
  Boolean = 59,
}

class StateMachineInput {
  public readonly type: StateMachineInputType;
  public get name(): string;
  public get value(): number | boolean;
  public set value(value: number | boolean);
  public fire(): void; // trigger inputs only
  public delete(): void; // clears the wrapper’s reference to the native input
}
```

---

#### Nested artboard paths (deprecated)

For inputs and text runs on **nested artboards**, use a path string (for example `"parentArtboard"` or `"group/nested"`) to set input and text run values.

- `setBooleanStateAtPath(inputName: string, value: boolean, path: string): void`
- `setNumberStateAtPath(inputName: string, value: number, path: string): void`
- `fireStateAtPath(inputName: string, path: string): void`
- `getTextRunValueAtPath(textName: string, path: string): string | undefined`
- `setTextRunValueAtPath(textName: string, value: string, path: string): void`

Prefer data binding with [Nested Property Paths](/runtimes/web/data-binding#nested-property-paths) for nested artboard properties.

---

#### getTextRunValue() / setTextRunValue()

`getTextRunValue(textRunName: string): string | undefined`

`setTextRunValue(textRunName: string, textValue: string): void`

These target named text runs on the **currently active** artboard. Console warnings are emitted when the run cannot be resolved.

Prefer data binding with [Text data binding](/runtimes/web/data-binding#reading-and-writing-properties) for new work where possible.

---

## Debugging and inspection

Once Rive is instantiated, you can inspect various properties of the playing instance by reading some of the following properties/getters on the `Rive` instance.

### `contents`

`get contents(): RiveFileContents | undefined`

When the file has finished loading, `contents` describes artboards, animations, state machines, and each state machine’s inputs. If not loaded, `undefined`.

```typescript
// Documented shape; types may not be exported from the package
interface RiveFileContents {
  artboards: {
    name: string;
    animations: string[];
    stateMachines: {
      name: string;
      inputs: { name: string; type: StateMachineInputType; initialValue?: boolean | number }[];
    }[];
  }[];
}
```

### `enableFPSCounter()` / `disableFPSCounter()`

Enable FPS readouts for the current instance.

```typescript
type FPSCallback = (fps: number) => void;

enableFPSCounter(fpsCallback?: FPSCallback): void;
disableFPSCounter(): void;
```

Without a callback, a fixed-position FPS readout may be injected in the corner of the viewport.

### Performance profiling marks

When instantiating `Rive`, set `enablePerfMarks: true` to emit `performance.mark` and `performance.measure` entries for key events like WASM initialization and file loading. This should give you
insight into where time is being spent during Rive startup and can be used in conjunction with browser profiling tools. Marks emitted may include:
- Time fetching WASM
- Time instantiating Rive and the renderer
- Time parsing and loading `.riv` file setup
- Time rendering the first few frames on the canvas

Check the [Performance panel](https://developer.chrome.com/docs/devtools/performance/overview#capture_and_analyze_a_performance_report) in Chrome DevTools to see these marks on the flame chart.
See the [Preloading WASM](/runtimes/web/preloading-wasm) guide and the [Caching a Rive File](/runtimes/web/caching-a-rive-file) guide for more information on ways to optimize Rive load times.

### `source`

Getter — current `src` string (if any).

### `activeArtboard`

Name of the active artboard, or `""` if none.

### `animationNames` / `stateMachineNames`

All animation and state machine names on the **active** artboard.

### `playingAnimationNames` / `playingStateMachineNames`

Currently playing animations or state machines on the active artboard.

### `pausedAnimationNames` / `pausedStateMachineNames`

Currently paused animations or state machines on the active artboard.

### `isPlaying` / `isPaused` / `isStopped`

Aggregate playback flags for instantiated animations and state machines.

---

## Related exports (module)

The following below are named exports from the same package.

### `RiveFile`

`RiveFile` lets you parse a `.riv` file once and share the result across multiple `Rive` instances — avoiding redundant network fetches and parse overhead. See the full usage guide at [Caching a Rive file](/runtimes/web/caching-a-rive-file).
In many cases, you may want to load a `RiveFile` before actually rendering the graphic on a canvas. This is useful if you want to preload Rive WASM and the `.riv` file ahead of rendering, or to get certain `.riv` file data.

#### `RiveFile` constructor parameters

```typescript
interface RiveFileParameters {
  src?: string;           // URL or public path to the .riv file
  buffer?: ArrayBuffer;   // raw .riv bytes
  assetLoader?: AssetLoadCallback;
  enableRiveAssetCDN?: boolean;
  enablePerfMarks?: boolean;
  onLoad?: EventCallback;
  onLoadError?: EventCallback;
}
```

One of `src` or `buffer` is required.

```typescript
const riveFile = new RiveFile({ src: ‘/my-animation.riv’ });
await riveFile.init(); // resolves when the file is parsed and ready
```

Calling `.init()` starts loading and parsing of the `.riv` file. Resolves when the file is ready to be passed to `new Rive({ riveFile })`. If you provide `onLoad` / `onLoadError` callbacks in the `RiveFile` parameters, those fire at the same point.

#### `on()` / `off()`

`on(type: EventType, callback: EventCallback): void`
`off(type: EventType, callback: EventCallback): void`

Subscribe or unsubscribe from `EventType.Load` and `EventType.LoadError` events on the file itself. Mirrors the same API on the `Rive` instance.

#### `getBindableArtboard()`

`getBindableArtboard(name: string): BindableArtboard | null`

Returns a `BindableArtboard` by name. Returns `null` if the artboard doesn’t exist.

Once you have a bindable artboard, you can set the `.viewModel` property on that artboard to bind a `ViewModelInstance`. Bindable artboards can be set as a value to an artboard property on a different ViewModel.

#### `getDefaultBindableArtboard()`

`getDefaultBindableArtboard(): BindableArtboard | null`

Returns the default artboard as a `BindableArtboard`, or `null` if not available.

#### `viewModelByName()`

`viewModelByName(name: string): ViewModel | null`

Returns a `ViewModel` from the file by name, or `null` if it doesn’t exist or the file isn’t loaded yet. Equivalent to the `Rive` class's `.viewModelByName()` API, but accessible directly on the file handle before a `Rive` instance is created.

#### `cleanup()`

`cleanup(): void`

Unconditionally releases the underlying WASM file handle and all associated listeners. Call when the `RiveFile` is no longer needed and you want to free memory.

---

### `RuntimeLoader`

`RuntimeLoader` is a singleton that manages loading and caching the Rive WASM binary for all Rive instances on the page. Control where the Rive WASM is loaded from and when with this class.

#### `enablePerfMarks`

`static enablePerfMarks: boolean`

When `true`, emits `performance.mark` / `performance.measure` entries for WASM initialization timing. Set before the first `getInstance()` / `awaitInstance()` call. Also available on `RiveFile` and the `Rive` constructor parameter `enablePerfMarks`.

#### `getInstance()`

`static getInstance(callback: (rive: RiveCanvas) => void): void`

Provides the loaded WASM runtime via callback, initiating load if it hasn’t started yet. The callback fires immediately if the runtime is already loaded.

```typescript
RuntimeLoader.getInstance((runtime) => {
  // runtime is a RiveCanvas — the low-level WASM module
});
```

#### `awaitInstance()`

`static awaitInstance(): Promise<RiveCanvas>`

Promise-based alternative to `getInstance()`. Resolves with the runtime when loading is complete.

```typescript
const runtime = await RuntimeLoader.awaitInstance();
```

#### `setWasmUrl()` / `getWasmUrl()`

`static setWasmUrl(url: string): void`
`static getWasmUrl(): string`

Override the default/primary URL from which the WASM binary is fetched. Call `setWasmUrl()` **before** any `Rive` or `RiveFile` is constructed, as WASM is fetched on first use. By default, Rive pulls from the [UNPKG CDN](https://unpkg.com/) for the version of the package you have installed.

```typescript
RuntimeLoader.setWasmUrl(‘/static/rive.wasm’);
```

#### `setWasmFallbackUrl()` / `getWasmFallbackUrl()`

`static setWasmFallbackUrl(url: string | null): void`
`static getWasmFallbackUrl(): string | null`

Configures a fallback WASM URL to try if the primary URL fails to load. Defaults to pulling from [jsdelivr](https://www.jsdelivr.com/). Pass `null` to disable fallback behavior.

#### `setWasmBinary()` / `getWasmBinary()`

`static setWasmBinary(value: ArrayBuffer | null): void`
`static getWasmBinary(): ArrayBuffer | null`

Supply the WASM binary as an in-memory `ArrayBuffer` instead of fetching it from a URL — useful for environments without network access or for bundling WASM inline. When supplied, this is used instead of fetching from the primary URL. Pass `null` to clear.

---

### `RiveFont`

`RiveFont` is a static-only utility class (never instantiated) for configuring **fallback fonts** — fonts Rive tries when the primary font is missing a glyph. This is useful for multilingual content where a single font doesn't cover all required Unicode ranges.

#### `setFallbackFontCallback()`

`static setFallbackFontCallback(fontCallback: FallbackFontsCallback | null): void`


```typescript
type FallbackFontsCallback = (
  missingGlyph: number,
  weight: number
) => FontWrapper | FontWrapper[] | null | undefined;
```

`FallbackFontsCallback` is invoked by the runtime when a glyph cannot be found in the active font. Set this callback to handle the missing glyph codepoint and the current font weight. Return a single `FontWrapper`, an array of `FontWrapper`s, or `null`/`undefined` to indicate no fallback is available. `FontWrapper` is the type returned by `decodeFont`.

This API registers a callback that is invoked whenever the runtime encounters a missing glyph. When an array of fonts is returned from this callback, Rive works through them in order until a match is found. Call  `RiveFont.setFallbackFontCallback(null)` to clear any previously registered callback.

See [fallback fonts](/runtimes/web/fonts#fallback-fonts) for more details.

---

### Utility decoders

`decodeAudio`, `decodeImage`, and `decodeFont` decode raw bytes into asset wrapper classes you can pass to `assetLoader`. See [Loading assets](/runtimes/web/loading-assets) for more details.

#### decodeImage() / decodeFont() / decodeAudio()
`async decodeImage(bytes: Uint8Array): Promise<ImageWrapper>`

`async decodeFont(bytes: Uint8Array): Promise<FontWrapper>`

`async decodeAudio(bytes: Uint8Array): Promise<AudioWrapper>`

---
## runtimes/web/state-machines.mdx

---
title: "State Machine Playback"
description: "Playing a state machine"
---

import Overview from "/snippets/runtimes/state-machines/overview.mdx"
import ControllingPlayback from "/snippets/runtimes/state-machines/controlling-playback.mdx"
import PlayingStateMachines from "/snippets/runtimes/state-machines/playing-state-machines.mdx"

<Overview />

<ControllingPlayback />

<PlayingStateMachines />

### Autoplay the State Machine

To autoplay a state machine immediately after it loads, simply set `autoplay` to `true`.

```js
const r = new rive.Rive({
    src: 'https://cdn.rive.app/animations/vehicles.riv',
    canvas: document.getElementById('canvas'),
    autoplay: true,
    stateMachines: 'bumpy',
    onLoad: () => {}
});
```

### Controlling State Machine Playback

You can manually play and pause the State Machine using the `play`, `pause`, and `stop` methods.

```js
const r = new rive.Rive({
    src: 'https://cdn.rive.app/animations/vehicles.riv',
    canvas: document.getElementById('canvas'),
    stateMachines: 'bumpy',
    onLoad: () => {}
});

const handlePlay = () => {
  r.play()
}

const handlePause = () => {
  r.pause()
}

const handleStop = () => {
  r.stop()
}
```

### reset()

To dispose the current artboard / animation / state machine instances and create fresh ones (optionally changing artboard or `stateMachines`), use **`reset()`**. Pass the same kinds of options you use on the constructor. See [Rive Parameters](/runtimes/web/rive-parameters) for the full **`RiveResetParameters`** fields (`artboard`, `stateMachines`, `autoplay`, `autoBind`).

```js
r.reset({
  stateMachines: 'bumpy',
  autoplay: true,
});
```
---
## runtimes/web/text.mdx

---
title: "Text"
description: "⚠️ DEPRECATED: Use Data Binding instead of direct text run manipulation at runtime"
noindex: true
---

import Overview from "/snippets/runtimes/text/overview.mdx"
import NestedArtboard from "/snippets/runtimes/text/nested-artboard.mdx"
import SemanticsForAccessibility from "/snippets/runtimes/text/semantics-for-accessibility.mdx"
import Resources from "/snippets/runtimes/text/resources.mdx"

<Overview />

## Examples

- [Updating Text at Runtime - Localization example](https://codesandbox.io/p/sandbox/rive-text-js-x9jn5w)

## High-level API usage

**Reading Text**

To read a given text run text value at any given time, reference the `.getTextRunValue()` API on the Rive instance:

```javascript
public getTextRunValue(textRunName: string): string | undefined
```

Supply the text run name, and you'll have the Rive text run value returned, or `undefined` if the text run could not be queried.

**Setting Text**

To set a given text run value at any given time, reference the `.setTextRunValue()` API on the Rive instance:

```javascript
public setTextRunValue(textRunName: string, textRunValue: string): void
```

Supply the text run name and a second parameter, `textValue`, with a String value that you want to set the new text value for if the text run can be successfully queried on the active artboard.

### Example Usage

```javascript
import {Rive} from '@rive-app/canvas'

const r = new Rive({
src: "my-rive-file.riv"
artboard: "my-artboard-name",
autoplay: true,
stateMachines: "State Machine 1",
onLoad: () => {
    console.log("My design-time text is, ", r.getTextRunValue("MyRun"));
    r.setTextRunValue("MyRun", "New text value");
},
})
```

## Low-level API usage

Get a reference to the Rive `Artboard`, find a text run by a given **name**, and get/update the text value property.

```javascript
import RiveCanvas from '@rive-app/canvas-advanced';


const bytes = await (
await fetch(new Request('./my-rive-file.riv'))
).arrayBuffer();
const myRiveFile = await rive.load(new Uint8Array(bytes));

const artboard = myRiveFile.defaultArtboard();
const textRun = artboard.textRun("MyRun"); // Query by the text run name
console.log(`My design-time text is ${textRun.text}`);
textRun.text = "Hello JS Runtime!";

...
```

<NestedArtboard />

## Examples

- [Updating Nested Text at Runtime - Localization example](https://codesandbox.io/p/sandbox/rive-text-nested-js-pzs9lf)

### High-level API usage

**Reading Text**

To read a given text run text value at a specific path, reference the `.getTextRunValueAtPath()` API on the Rive instance:

```javascript
public getTextRunValueAtPath(textRunName: string, path: string): string | undefined
```

Supply the text run name and the path where it is located, and you'll have the Rive text run value returned, or `undefined` if the text run could not be queried.

**Setting Text**

To set a given text run value at a specific path, reference the `.setTextRunValueAtPath()` API on the Rive instance:

```javascript
public setTextRunValueAtPath(textRunName: string, textRunValue: string, path: string): void
```

Supply the `textRunName`, the new `textValue`, and the `path` where the run is located at a component instance level.

### Example Usage

```javascript
import {Rive} from '@rive-app/canvas'

const r = new Rive({
src: "my-rive-file.riv"
artboard: "my-artboard-name",
autoplay: true,
stateMachines: "State Machine 1",
onLoad: () => {
    console.log("My design-time text is, ", r.getTextRunValueAtPath("MyRun", "path/to/run"));
    r.setTextRunValueAtPath("MyRun", "New text value", "path/to/run");
},
})
```

<SemanticsForAccessibility />

The following code snippets provide guidance on how to add semantic labels to your Rive animations.

#### Adding ARIA Label

At a minimum - if it is important to convey the text value displayed in the Rive animation to all users, add an `aria-label` to the `<canvas>` element with the text value from the animation. Screen readers may read this label out immediately as it parses out the DOM contents. You'll also want to add `role="img"` to the `<canvas>` element as well.

```javascript
<canvas
    id="rive-canvas"
    width={500}
    height={500}
    role="img"
    aria-label="Hello friend, welcome to my page"
></canvas>
```

#### Adding ARIA Live Region

While ARIA labels are a direct method to manage a textual label for screen readers to read out as it parses web content, using an ARIA live region allows you a way to control when screen readers read out dynamic text content.

Live regions are useful in cases where the text content in your Rive graphic becomes visible or changes on a particular state in a state machine, and you want screen readers to pick up on text changes. Another use case is when you only want screen readers to read your Rive text content when the `<canvas>` is scrolled into view.

Read more on ARIA live regions [here](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Live_Regions).

#### Example: Rating Graphic

<Note>
    To try this example out, visit this [CodeSandbox link](https://codesandbox.io/p/sandbox/rive-rating-ally-example-ptydr8)
</Note>
Imagine you're displaying an interactive Rive graphic that allows users to choose a rating from 1-5 stars. Users clicking on the different stars can visually see the state machine in action with animations to see what star they click, but screen readers may need a way to announce what selection was chosen as other users navigate the canvas with keyboard controls, for example.

The HTML for this might look like the following:

```javascript
<canvas
role="img"
tabindex="0"
aria-describedby="rating-animation-live"
id="canvas"
></canvas>
<p id="rating-animation-live" class="sr-only" aria-live="assertive">
An interactive rating simulation. Use the left and right arrow keys to
select a rating
</p>
```

Note that the `<canvas>` element has an `aria-describedby` attribute whose value matches the `id` of the `<p>` below it, `#rating-animation-live`. This allows the `<p>` block content to describe the `<canvas>` element. And similar to using `aria-label`, we have to add the `role="img"` attribute to the canvas as well. The `aria-live="assertive"` attribute describes how to interrupt the screen reader's flow of reading content based on when the content within this `<p>` changes.

Let's take a look at what the JS might look like using the Rive Web (JS) runtime:

```javascript
const rive = require("@rive-app/canvas");
const dynamicTextEl = document.getElementById("rating-animation-live");

const r = new rive.Rive({
src: "rating.riv",
canvas: document.getElementById("canvas"),
stateMachines: "State Machine 1",
autoplay: true,
onLoad: () => {
    r.setTextRunValue("RatingRun", "0");
    r.resizeDrawingSurfaceToCanvas();
    // See CodeSandbox link above for further functionality
},
onStateChange: (e) => {
    const name = e.data[0];
    const ratingStr = name.charAt(0);
    const ratingNum = parseInt(ratingStr);
    if (!isNaN(ratingNum)) {
    const ratingString = name
        .split("_")
        .reduce((acc, temp) => {
        return (acc += ` ${temp}`);
        }, "")
        .trim();
    r.setTextRunValue("RatingRun", ratingStr);

    dynamicTextEl.innerHTML = `Rating: ${ratingString}`;
    }
}
});
```

In the above snippet, we've created an instance of Rive, and as the state changes in the state machine, we're dynamically updating the contents of the live region (represented by `dynamicTextEl`) with the string rating. Due to the live region having the property of `aria-live="assertive"`, screen readers should read off the new dynamic text content.

<Resources />

---
## runtimes/web/web-js.mdx

---
title: "Getting Started"
description: "JavaScript/WASM runtime for Rive."
---

import NoteOnFeatureSupport from "/snippets/runtimes/rendering-feature-support.mdx"
import { Demos } from '/snippets/demos.jsx'

<NoteOnFeatureSupport />

<Demos examples={['quickStart']} runtime="web" />

## Overview

This guide documents how to get started using the Rive web runtime library. The runtime is open source and available in this [GitHub repository](https://github.com/rive-app/rive-wasm). This library has a high-level JavaScript API (with TypeScript support) and a low-level API to load in Web Assembly (WASM) and control the rendering loop yourself. This runtime allows you to:

- Quickly integrate Rive into all web applications (Webflow, WordPress, etc.)
- Provides a base API to build other web-based Rive runtime wrappers (React, Svelte, etc.)
- Support advanced use cases by controlling the render loop (web-based game engines)

## Getting started

Follow the steps below to integrate Rive into your web app.

<Note>
  The following instructions describe using the `@rive-app/webgl2` package. Rive provides web-based packages like WebGL2, Canvas, and Lite versions.

  See [Canvas vs WebGL2](/runtimes/web/canvas-vs-webgl) for guidance on which package is the correct choice for your use case.
</Note>

<Steps>
  <Step title="Install the dependency">
    <Warning>
      We recommend always using the [latest version](https://www.npmjs.com/package/@rive-app/webgl2). The versions listed below and in the examples may differ from the latest.
    </Warning>
    <Tabs>
      <Tab title="Script Tag">
        ```html
        // Add the following script tag to your web page to get the latest version:


        <script src="https://unpkg.com/@rive-app/webgl2"></script>

        // You can also pin to a specific version (See [here](https://www.npmjs.com/package/@rive-app/webgl2) for the latest):


        <script src="https://unpkg.com/@rive-app/webgl2@2.36.0"></script>

        // This will make a global `rive` object available, allowing you to access the Rive API via the `rive` entry point:

        new rive.Rive({});
        ```
      </Tab>
      <Tab title="Package Manager">
        ```bash npm
        npm install @rive-app/webgl2
        ```

        ```bash pnpm
        pnpm add @rive-app/webgl2
        ```

        ```bash yarn
        yarn add @rive-app/webgl2
        ```

        ```bash bun
        bun add @rive-app/webgl2
        ```

        ```javascript Importing
        // Import the entire module under the global identifier `rive`
        import * as rive from "@rive-app/webgl2";

        // Alternatively, import only the specific parts you need
        import { Rive } from "@rive-app/webgl2";

        ```
      </Tab>
    </Tabs>
    <Note>
      Not using [Rive Text](/editor/text/), [Rive Layouts](/editor/layouts/), [Rive Scripting](/scripting/), or [Rive Audio](/editor/events/audio-events)? Consider using [@rive-app/canvas-lite](/runtimes/web/canvas-vs-webgl#rive-app-webgl2-lite) which is a smaller package variant of our canvas runtime.
    </Note>
  </Step>
  <Step title="Create a Canvas">
    Add a canvas element to your HTML where you want the Rive graphic to be displayed:

    ```html
    <canvas id="canvas" width="500" height="500"></canvas>
    ```
  </Step>
  <Step title="Create a Rive instance">
    To create a new instance of a Rive object, provide the following properties:

    - `src`: A string representing the URL of the hosted `.riv` file (as shown in the example below) or the path to the public asset `.riv` file. For more details, refer to [Rive Parameters](/runtimes/web/rive-parameters) on how to properly use this property.
    - `artboard` - (Optional) A string representing the artboard you want to display. If not supplied, the default artboard from the `.riv` file is selected.
    - `stateMachines` - A string representing the name of the state machine you wish to play. This must be supplied, or the Rive instance may only play the first linear animation it finds. In the next major version, the default behavior will be to play the default state machine of the artboard.
    - `canvas` - The canvas element where the animation will be rendered.
    - `autoplay` - A boolean indicating whether the animation should play automatically.
    - `autoBind` - A boolean indicating whether to automatically data-bind the default `ViewModelInstance` if one is found.

    ```javascript
    <script>
        const r = new rive.Rive({
            src: "https://cdn.rive.app/animations/vehicles.riv",
            // OR the path to a discoverable and public Rive asset
            // src: '/public/example.riv',
            canvas: document.getElementById("canvas"),
            autoplay: true,
            autoBind: true,
            // artboard: "Artboard", // Optional. If not supplied the default is selected
            stateMachines: "bumpy",
            onLoad: () => {
              r.resizeDrawingSurfaceToCanvas();
            },
        });
    </script>
    ```

    <Note>
      The `resizeDrawingSurfaceToCanvas` method ensures that the Rive animation is correctly scaled to fit the dimensions of the specified canvas element. By default, the canvas rendering surface might not match the exact size of the `<canvas>` element defined in your HTML, which can lead to blurry or incorrectly scaled graphics, especially on high-DPI or retina displays.

      Calling this method adjusts the internal drawing surface so that the animation is rendered with crisp detail, matching the pixel density of the canvas. This is particularly important when:

      - The size of the canvas changes dynamically (e.g., if it is resized due to responsive layouts).
      - You want to ensure the animation remains sharp, regardless of device or screen resolution.

      **Best practices:**

      - **Call after load**: It's recommended to call `resizeDrawingSurfaceToCanvas` inside the `onLoad` callback to ensure that the Rive asset has been fully loaded before adjusting the drawing surface. This prevents any rendering issues.
      - **Handling window resize**: If your canvas size changes during the user's interaction (such as when resizing the browser window), you should also listen for window resize events and call `resizeDrawingSurfaceToCanvas` to re-adjust the rendering surface:

      ```javascript
      window.addEventListener("resize", () => {
          r.resizeDrawingSurfaceToCanvas();
      });
      ```

      This way, the Rive animation will continue to look sharp and correctly scaled as the canvas size changes.
    </Note>
  </Step>
</Steps>

### Complete example

Bringing it all together, here's how to load a Rive graphic in a single HTML file.

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Rive Hello World</title>
  </head>
  <body>
    <canvas id="canvas" width="500" height="500"></canvas>

    <script src="https://unpkg.com/@rive-app/webgl2"></script>
    <script>
      const r = new rive.Rive({
        src: "https://cdn.rive.app/animations/vehicles.riv",
        canvas: document.getElementById("canvas"),
        autoplay: true,
        // artboard: "Arboard", // Optional. If not supplied the default is selected
        stateMachines: "bumpy",
        onLoad: () => {
          // Ensure the drawing surface matches the canvas size and device pixel ratio
          r.resizeDrawingSurfaceToCanvas();
        },
      });
    </script>
  </body>
</html>
```

### Loading Rive files

[See this example](https://codesandbox.io/p/sandbox/rive-quick-start-js-xmwcm6?file=%2Fsrc%2Findex.ts) for the different ways to load in a .riv file, the options are:

1. **Hosted URL**: Use a string representing the URL where the `.riv` file is hosted. Set this as the `src` attribute when creating a new Rive instance.
2. **Static Assets in the bundle**: Provide a string with the path to a publicly accessible `.riv` file within your web project. Handle `.riv` files just like any other static asset (e.g., images or fonts) in your project.
3. **Fetching a file**: Instead of using the `src` attribute, use the `buffer` attribute to load an `ArrayBuffer` when fetching a file. This is useful when reusing the same `.riv` file across multiple Rive instances, allowing you to load it only once.
4. **Reusing a Loaded File**: Use the `rivFile` parameter to reuse a previously loaded Rive runtime file object, avoiding the need to fetch it again via the `src` URL or reload it from the `buffer`. This can significantly improve performance by eliminating redundant network requests and loading times, especially when creating multiple Rive instances from the same source. Unlike the `src` and `buffer` parameters, which require parsing under the hood to create a runtime file object, the `riveFile` parameter uses an already parsed object, including any loaded assets. See [Caching a Rive File](/runtimes/web/caching-a-rive-file).

For more details, refer to the [Rive Parameters](/runtimes/web/rive-parameters) section on the `src` property.

## Clean up Rive

When working with a Rive instance, it's important to properly clean it up when it's no longer needed. This is especially necessary in scenarios where:

- The UI containing Rive animations is no longer needed (e.g., when a modal with Rive graphics is closed).
- The animation or state machine has completed and will not be shown or run again.

Under the hood, Rive creates various low-level objects (such as artboard instances, animation instances, and state machine instances) in C\+\+, which need to be manually deleted to prevent memory leaks. If not cleaned up, these objects can consume unnecessary resources, potentially impacting your application's performance.

Fortunately, the high-level JavaScript API simplifies this process. You don't need to track every object created during the Rive instance lifecycle. Instead, you can clean up all associated objects with a single method call.

To clean up a Rive instance and free up resources, simply call the following method on your Rive instance:

```javascript
const riveInstance = new Rive({...));
...
// When ready to cleanup
riveInstance.cleanup();
```

# Additional Rive web resources

More in-depth Rive web documentation and advanced use cases.

<CardGroup cols={2}>
  <Card title="Rive Parameters" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>} href="/runtimes/web/rive-parameters">
    API docs for the Rive instance.
  </Card>
  <Card title="Canvas vs WebGL2" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>} href="/runtimes/web/canvas-vs-webgl">
    A guide to the different Rive web packages
  </Card>
  <Card title="FAQ" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>} href="/runtimes/web/faq">
    Frequently asked questions
  </Card>
  <Card title="Preloading WASM" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>} href="/runtimes/web/preloading-wasm">
    Instructions on how to preload and self-host the rive WASM library.
  </Card>
  <Card title="Low-level API Usage" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>} href="/runtimes/web/low-level-api-usage">
    Control the Rive render loop and layout, and draw multiple artboards to the same canvas.
  </Card>
</CardGroup>

# Examples

- [Basic gallery app](https://github.com/rive-app/rive-wasm/tree/master/js/examples/_frameworks/parcel_example_canvas)
- [Tracking mouse cursor](https://codesandbox.io/p/sandbox/tracking-mouse-cursor-n38gdd?file=%2Fsrc%2Findex.ts)
- [Connecting to page scroll](https://codesandbox.io/p/sandbox/rive-page-scroll-h4msqw?file=%2Fsrc%2Findex.ts%3A27%2C45)
- [Playing state machine only when scrolled into the user's viewport](https://codesandbox.io/p/sandbox/rive-wait-for-scroll-into-view-y9wg8d?file=%2Fsrc%2Findex.ts)
## rive-wasm package README

![Build Status](https://github.com/rive-app/rive-wasm/actions/workflows/build.yml/badge.svg)
![Discord badge](https://img.shields.io/discord/532365473602600965)
![Twitter handle](https://img.shields.io/twitter/follow/rive_app.svg?style=social&label=Follow)

# Rive Web

![Rive hero image](https://cdn.rive.app/rive_logo_dark_bg.png)

A JavaScript/TypeScript and Web Assembly ([WASM](https://developer.mozilla.org/en-US/docs/WebAssembly)) runtime library for [Rive](https://rive.app).

This library allows full control over Rive files with a high-level API for hooking up many simple interactions and animations, as well as a low-level API that allows you to drive your own render loop to create multiple artboards, animations, and state machines all in one canvas.

## Table of contents

- :star: [Rive Overview](#rive-overview)
- 🚀 [Getting Started & API docs](#getting-started)
- :mag: [Supported Browsers](#supported-browsers)
- :books: [Examples](#examples)
- :runner: [Migration Guides](#migration-guides)
- 👨‍💻 [Contributing](#contributing)
- :question: [Issues](#issues)

## Rive overview

[Rive](https://rive.app) is a real-time interactive design and animation tool that helps teams create and run interactive animations anywhere. Designers and developers use our collaborative editor to create motion graphics that respond to different states and user inputs. Our lightweight open-source runtime libraries allow them to load their animations into apps, games, and websites.

:house_with_garden: [Homepage](https://rive.app/)

:blue_book: [Rive docs](https://rive.app/docs/getting-started/introduction)

## Getting started

Follow along with the link below for a quick start in getting Rive JS integrated into your web applications.

- [Getting Started with Rive in Web](https://rive.app/docs/runtimes/web/web-js)
- [API documentation](https://rive.app/docs/runtimes/web/rive-parameters)

For more information, see the Runtime sections of the Rive help documentation:

- [Layout](https://rive.app/docs/runtimes/layout)
- [State Machines](https://rive.app/docs/runtimes/state-machines)
- [Data Binding](https://rive.app/docs/runtimes/data-binding)
- [Rive Events](https://rive.app/docs/runtimes/rive-events)
- [Loading Assets](https://rive.app/docs/runtimes/web/loading-assets)

## Supported browsers

Rive can be used in all major browsers. We're constantly working to improve performance with our renderer so that animations playback smoothly for all.

## Examples

Check out some of the demos using this JS/WASM runtime in the [Rive documentation](https://rive.app/docs/runtimes/demos).

### Awesome Rive

For even more examples and resources on using Rive at runtime or in other tools, checkout the [awesome-rive](https://github.com/rive-app/awesome-rive) repo.

## Migration guides

Using an older version of the runtime and need to learn how to upgrade to the latest version? Check out the migration guides below in our help center that help guide you through major version bumps; breaking changes and all!

[Migration guides](https://rive.app/docs/runtimes/web/migration-guides)

## Contributing

We love contributions! Check out our [contributing docs](./CONTRIBUTING.md) to get more details into how to run this project, the examples, and more all locally.

## Issues

Have an issue with using the runtime, or want to suggest a feature/API to help make your development life better? Log an issue in our [issues](https://github.com/rive-app/rive-wasm/issues) tab! You can also browse older issues and discussion threads there to see solutions that may have worked for common problems.
