# Rive Editor Workflow — Aggregated Reference

Source: rive-app/rive-docs/editor + getting-started

## Getting started

---
## getting-started/best-practices.mdx

---
title: "Best Practices"
description: "Editor & runtime performance and usage considerations."
---

Rive is built to efficiently play interactive graphics in the editor and at runtime in applications and games. However, poorly optimized animations can consume significant resources and cause poor performance, particularly on low-end devices. In the following sections, we will outline important considerations and tips for maintaining optimal performance and minimal resource utilization both during design/animate time in the Rive editor, as well as during runtime in applications.

<Info>
  We recommend continuous testing of your animations on your target devices/platforms.
</Info>

## Design-time Considerations

See below for some techniques to employ in the Rive editor to keep Rive performant:

### Asset Optimizations

Image, audio, and font assets are often the biggest source of bloat in .riv files. Unoptimized assets increase download size and must be loaded into memory, which can lead to slowdowns—especially on lower-end devices.

<Info>
  Only assets used in artboards will be compiled for runtime. Items in the Assets panel that aren't used in an artboard will not increase the size of your .riv file.
</Info>

#### Fonts

Font files often include thousands of glyphs you may not need, such as Greek letters, mathematical operators, and icons. To reduce the size of the exported font or .riv file, [select which glyphs to include](/editor/text/fonts#glyph-%2F-script-selection).

#### Raster Image Sizes & Dimensions

It is crucial to ensure that the size of an image asset is appropriate for its usage. For instance, avoid using an image with large dimensions (e.g., 8192 x 7022) when it will be displayed in a small section of your artboard (e.g., sized 100 x 100).

Using large images can quickly consume device memory. This is particularly true on mobile devices where applications are more memory-constrained. Even if these images are compressed, their dimensions will still impact the amount of application memory used.

If you have a very large image and only part of it will be visible at any given time (ie; a scrolling background), consider breaking the image into smaller chunks or mixing raster and recreating part of it as a vector.

![Image](/images/getting-started/best-practices/breaking-up-raster-images.webp)

#### Raster Image Compression

Compression involves reducing the file size by employing various algorithms to discard some image data. You can compress images directly from the Rive editor, which means you maintain the original image but compress the images for runtime use. If the asset is embedded in the animation, this will reduce the file size of the exported riv.

For the smallest image file size and best performance, we recommend exporting assets using the WebP Format.

#### Vector Images

Be efficient with the number of vertices in your vector image. While a few extra vertices won’t have much of an impact, thousands might. Be especially careful when importing vectors that were generated with AI, converted from raster images, or were created in drawing apps.

### Importing Lottie Files

While Rive provides a Lottie converter for easy .riv file export, recreating graphics and animations directly in Rive often results in significantly smaller file sizes. If you're importing a Lottie file, you can further reduce the .riv file size by converting images from PNG to WebP and choosing to export only the necessary glyphs for font files. Additionally, you can [load assets out of band](#out-of-band-assets) to reuse fonts and images across multiple .riv files, optimizing storage.

Working directly in Rive is generally preferable as it allows for file optimization based on your animation requirements. For instance, using bones and constraints to create rigs will result in fewer keys in the animation compared to converting directly from Lottie.

### Layer Blend Modes for Web

Blend modes are particularly expensive on the web because WebGL doesn’t expose mechanisms for accessing the framebuffer. To apply a blend mode, Rive must copy rendered pixels into a separate texture before compositing, which introduces significant performance and memory overhead.

While there are efforts underway to improve this through new WebGL capabilities, these solutions are still pending broader support. Until then, it’s best to use blend modes sparingly in web projects to ensure optimal performance.

### Artboard Considerations

#### Clipped Artboards

Clipping artboards is generally fine, but if you're experiencing performance issues, it's worth minimizing their use. Clipping can be computationally expensive, as the renderer must evaluate every object—including component instances—to determine pixel visibility. Instead, consider applying clips to specific objects or groups within the artboard.

In most cases you can safely remove the clip from the main artboard itself, since nothing outside the Rive instance will be rendered at runtime.

#### Unused Artboards

Unused artboards are still included in the compiled .riv file and are parsed when the file is first loaded. This can lead to unnecessary memory usage and performance overhead, especially if the unused artboards contain complex animations or large assets. To keep your file lean and efficient, it's best practice to remove any artboards that aren't actively being used.

### Idle Animations

If you have idle animation states where the graphic remains static at a given state in a state machine, consider using a "one-shot" animation and ensuring that the timeline animation is not unnecessarily long. At runtime in a state machine, if no looping animations or active blend states are playing, the runtime will preemptively “pause” itself until a state machine input or Rive Listener triggers the next transition in the state machine. This is useful because resource consumption (i.e., CPU usage) may decrease to the point of making Rive impact on resources negligent on applications.

Scenarios: Icons, buttons, graphics that only animate based on user interaction, etc.

### Using Solos

A [Solo](/editor/manipulating-shapes/solos) is similar to a group but with the added ability to toggle the rendering of nested objects. It functions like a radio button, deactivating other objects on the same level.

When you're looking to show or hide a specific object, using a Solo can be a more efficient since it stops the rendering of any non active objects.

Solos can also be an effective way to build skins for a character, but it's important to note that this should only be used if your skins require binding and weighting.

**Data Binding Artboards**\
When looking to build more complex skins (that don't require binding and weighting), or wanting to swap out widgets, icons, ect... data binding an artboard node is the most performant way to do this.\
\
In addition to only rendering the things you need, you also save yourself both memory and CPU usage by providing only the graphics you need.

### Blend States

Similar to the guidance in “Idle Animations”, ensure blend states transition out to other states, or move to an exit state when finished if possible. When blend states are activated at runtime, Rive will continually play the state machine, even if it is not necessary anymore. Providing some transition away from the blend state when complete ensures Rive has one less “active” animation to track when considering whether to self-pause at any point while playing the state machine.

## Runtime Considerations

See below for some techniques to employ when using Rive runtimes in application to keep Rive performant:

### Out-of-band Assets

See our documentation on [Loading Assets](/runtimes/loading-assets). This feature allows you to dynamically load and replace assets (such as fonts, images, and audio) at runtime through code and provide the resources to your Rive graphic. This has the following benefits:

- Reduces the exported `.riv` binary size.
- Assets can be reused across multiple Rive files or other areas of your application.
- Assets can be preloaded and cached to be more readily available before displaying a Rive graphic.
- Assets can be swapped based on the users’ screen size and resolution, like in this [web JS example](https://codesandbox.io/p/sandbox/cool-dewdney-hlk5xl?file=%2Fsrc%2Findex.ts).

### Caching your .riv

If you're using the same Rive file in multiple places across your page or app, you can [cache the .riv](/runtimes/caching-a-rive-file) file to improve performance. The key benefit of caching is that the file only needs to be parsed and decoded once. Creating new artboard instances from a cached, already-decoded file is significantly faster than decoding the file each time before instantiating an artboard.

### Pausing Programmatically

There are several cases where you may want to pause a state machine configured with Rive programmatically. By pausing the Rive graphic at runtime, you may notice that Rive’s impact on the application has negligible resource consumption (i.e., CPU).

1. Rive graphic is offscreen
   a. If a Rive graphic is scrolled offscreen and does not need to continue playing, call the `pause` API on the respective runtime you’re using to prevent Rive from continuing to animate and consume resources when not needed.
   b. Call the `play` API to continue playing Rive when the graphic needs to continue animating if back onscreen.
2. Accessibility
   - If a user has set in device settings that they prefer reduced motion, you may want to read this property at runtime and programmatically either call `pause` or set `autoplay: false` with the Rive runtime to ensure these users have reduced motion when navigating the application. Alternatively, different artboards or state machines can be created and loaded at runtime that function differently.
3. State machine is idle with static graphics
   a. `Pause` when the Rive graphic is idling while it waits for a transition in the state machine from user interaction, data resolving, etc.

### Low-end devices

Rive will try to run performantly across all browsers/devices, but if you can, test how your application performs on resource-constrained devices with your specific Rive graphics running. You may find that for a given screen, Rive files that include heavily-animated graphics might be overkill for what is truly needed and decide to display static Rive graphics (i.e., autoplay: false) or reduce the amount of Rive entities animating at any given point.

A strategy for lower-end devices could be to create an alternative artboard or state machine with reduced usage/motion, that can dynamically be loaded in at runtime when running on older devices.
---
## getting-started/introduction.mdx

---
title: "Introduction"
description: "Welcome to the Rive docs. Browse the sections below to get started. Need help or can’t find something? Reach out on [Twitter](https://twitter.com/rive_app), join our [Discord](https://discord.com/invite/FGjmaTr), or ask the [Rive Community](https://community.rive.app/c/support/)."
---

import { YouTube } from '/snippets/youtube.mdx'

## Getting Started

New to Rive? Here are some tips to get started:

- [Create an account](https://rive.app/login/?redirect=https%3A%2F%2Feditor.rive.app) today and try out the Rive Editor
- Ready to design and animate? Peruse the Rive docs here, or watch our series of short tutorial videos in [Rive 101](https://youtube.com/playlist?list=PLujDTZWVDSsFGonP9kzAnvryowW098-p3)
- Want to jump straight into adding Rive into your apps and games? See the [app runtimes docs](/runtimes/getting-started) and [game runtime docs](/game-runtimes/unreal/unreal) for quickstart guides, examples, and code snippets
- Curious about what use cases to consider when building with Rive? We've got examples, blogs, tutorials, and more on our [use cases page](https://rive.app/use-cases)

## Explore Rive

<CardGroup cols={1}>
  <Card title="Interface Overview" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>} href="/editor/interface-overview/overview">
    Ready to start designing and animating in Rive? The editor is where you create and animate designs and utilize the powerful State Machine to build your logic of how different animations mix together. From there, you can export your work ready to drop into your app or game via one of our runtimes.
  </Card>

  <Card title="App Runtimes" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>} href="/runtimes/getting-started">
    App runtimes are open-source libraries that enable real-time rendering and updating of your Rive files across various platforms and frameworks, including Web, iOS, Android, Flutter, React Native, and more.
  </Card>

  <Card title="Game Runtimes" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>} href="/game-runtimes/unreal/unreal">
    Game runtimes are open-source libraries that allow real-time rendering and updating of your Rive files in Unity, Unreal, and Defold and is easy to integrate with custom engines.
  </Card>
</CardGroup>

<CardGroup cols={2}>
  <Card title="Marketplace Overview" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>} href="/community/marketplace-overview">
    Share and remix creations with the Rive Marketplace.
  </Card>

  <Card title="Admin" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>} href="/account-admin/account-overview/creating-an-account">
    All the information you need to manage accounts, teams, and plans.
  </Card>

  <Card title="Terms of Service" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>} href="/legal/terms-of-service">
    All our legal stuff, like our Terms of Service, Acceptable Use Policy, and Privacy Policy.
  </Card>
</CardGroup>
## Editor — get/install

---
## editor/get-rive.mdx

---
title: "Using the Rive Editor"
sidebarTitle: "Get Rive"
description: "Choose how you want to use the Rive editor: in your browser or as a desktop app."
---

You can use the Rive editor as a **desktop application** or directly in your **browser**. Both editors provide the same features and workflows.

<CardGroup cols={2}>
  <Card
    title="Downloads"
    href="https://rive.app/downloads?utm_source=docs&utm_medium=content"
  >
    Download the Rive editor for macOS or Windows.
  </Card>

  <Card
    title="Web Editor"
    href="https://editor.rive.app?utm_source=docs&utm_medium=content"
  >
    Use Rive instantly in your browser.
  </Card>
</CardGroup>

<Note>
  Voyager user can try upcoming features in the **[Early Access Editor](https://rive.app/downloads)** before they are released publicly.
</Note>

---
## editor/keyboard-shortcuts.mdx

---
title: 'Keyboard Shortcuts'
description: ''
---

Navigate quickly with keyboard shortcuts

## Tools

| Tools                       | Shortcut      |
|-----------------------------|---------------|
| Select Tool                                           | <kbd>V</kbd> |
| Translate Tool                                        | <kbd>Q</kbd> |
| Rotate Tool                                           | <kbd>W</kbd> |
| Scale Tool                                            | <kbd>E</kbd> |
| Rectangle Tool                                        | <kbd>R</kbd> |
| Ellipse Tool                                          | <kbd>O</kbd> |
| [Pen Tool Overview](/editor/fundamentals/pen-tool-overview) | <kbd>P</kbd> |
| [Artboards](/editor/fundamentals/artboards)                 | <kbd>A</kbd> |
| [Bones](/editor/manipulating-shapes/bones)                  | <kbd>B</kbd> |
| [Groups](/editor/fundamentals/groups)                       | <kbd>G</kbd> |
| [Freeze and Origin](/editor/fundamentals/freeze-and-origin) | <kbd>Y</kbd> |


## Editor
| Purpose                         | Shortcut                                                                                     |
|---------------------------------|---------------------------------------------------------------------------------------------|
| Switch Mode                     | <kbd>Tab</kbd>                                                                              |
| Constrain Shape/Angle           | <kbd>Shift</kbd>                                                                            |
| Deep Select                     | macOS: <kbd>⌘</kbd> + click Windows: <kbd>Ctrl</kbd> + click                                |
| Select Behind                   | <kbd>Alt</kbd>                                                                              |
| Nudge Object                    | Arrow Keys                                                                                  |
| Edit Vertices                   | <kbd>Enter</kbd> w/ path selected                                                           |
| Group Selection                 | macOS: <kbd>⌘</kbd> + <kbd>G</kbd> Windows: <kbd>Ctrl</kbd> + <kbd>G</kbd>                  |
| Ungroup Selection               | macOS: <kbd>⌘</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd> Windows: <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd> |
| Convert to Solo                 | macOS: <kbd>⌘</kbd> + <kbd>L</kbd> Windows: <kbd>Ctrl</kbd> + <kbd>L</kbd>                 |
| Duplicate                       | macOS: <kbd>⌘</kbd> + <kbd>D</kbd> Windows: <kbd>Ctrl</kbd> + <kbd>D</kbd>                 |
| Layer Forward                   | macOS: <kbd>⌘</kbd> + <kbd>]</kbd> Windows: <kbd>Ctrl</kbd> + <kbd>]</kbd>                  |
| Layer Backward                  | macOS: <kbd>⌘</kbd> + <kbd>[</kbd> Windows: <kbd>Ctrl</kbd> + <kbd>[</kbd>                  |
| Layer to Top                    | macOS: <kbd>⌘</kbd> + <kbd>Opt</kbd> + <kbd>]</kbd> Windows: <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>]</kbd> |
| Layer to Bottom                 | macOS: <kbd>⌘</kbd> + <kbd>Opt</kbd> + <kbd>[</kbd> Windows: <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>[</kbd> |
| Move Timeline Playhead          | <kbd>,</kbd> or <kbd>.</kbd> Hold <kbd>Shift</kbd> to move 10 frames                        |
| Move                            |                                                                                             |
| Move Selected Keys              | <kbd>Alt</kbd> + <kbd>,</kbd> or <kbd>.</kbd> Hold <kbd>Shift</kbd> to move 10 frames       |
| Skip to Keys (Selected Row, Otherwise All) | macOS: <kbd>⌘</kbd> + <kbd>,</kbd> or <kbd>.</kbd> Windows: <kbd>Ctrl</kbd> + <kbd>,</kbd> or <kbd>.</kbd> |
| Toggle Snapping                 | macOS: hold <kbd>⌘</kbd> Windows: hold <kbd>Ctrl</kbd>                                      |
| Color Picker                    | macOS: <kbd>Ctrl</kbd> + <kbd>C</kbd> or <kbd>I</kbd> Windows: <kbd>I</kbd>                 |
| Search                          | macOS: <kbd>⌘</kbd> + <kbd>K</kbd> Windows: <kbd>Ctrl</kbd> + <kbd>K</kbd>                  |
| Reveal Keys for Selection       | <kbd>U</kbd>                                                                                |
| Play Default State Machine      | <kbd>Shift</kbd> + <kbd>Space</kbd>                                                         |



## View
| Purpose                         | Shortcut                                                                                     |
|---------------------------------|---------------------------------------------------------------------------------------------|
| Fit selection to screen         | <kbd>F</kbd>                                                                                 |
| Zoom (mouse)                    | macOS: <kbd>⌘</kbd> + Mouse Wheel Windows: <kbd>Ctrl</kbd> + Mouse Wheel                     |
| Zoom (keyboard)                 | <kbd>+</kbd> and <kbd>-</kbd>                                                                 |
| Zoom (marquee)                  | <kbd>Z</kbd> (hold)                                                                           |
| Pan                             | <kbd>Right-click</kbd> + drag <kbd>Space</kbd> + drag                                        |


## Hierarchy

| Purpose                        | Shortcut                                                                                  |
|--------------------------------|------------------------------------------------------------------------------------------|
| Select parent                  | <kbd>Esc</kbd>                                                                              |
| Select 1st child               | <kbd>Enter</kbd>                                                                             |
| Rename                         | macOS: <kbd>⌘</kbd> + <kbd>R</kbd> Windows: <kbd>Ctrl</kbd> + <kbd>R</kbd>                  |
| Expand/Collapse all children   | macOS: <kbd>Opt</kbd> + click expand icon Windows: <kbd>Alt</kbd> + click expand icon       |
| Show/hide self only            | macOS: <kbd>⌘</kbd> + click eye icon Windows: <kbd>Ctrl</kbd> + click eye icon             |
| Show/hide parents only         | macOS: <kbd>Opt</kbd> + click eye icon Windows: <kbd>Alt</kbd> + click eye icon            |

---
## editor/libraries.mdx

---
title: "Libraries"
sidebarTitle: "Libraries"
description: "Publish your components with dynamic data once, and reuse them everywhere in your project."
---

import { YouTube } from '/snippets/youtube.mdx'

<Note>Libraries are available on Voyager and Enterprise plans. [Learn more about our plans and pricing](https://rive.app/pricing?utm_source=docs&utm_medium=content).</Note>

<YouTube id="g6AXyqp4Ow0" />

## Introduction
Libraries facilitate the sharing of [components](editor/fundamentals/components) and their view models across Rive files. In the past, you may have relied on nested artboards and copy-paste workflows to share elements. This works for individuals, but breaks down at scale: exports bloat, versions drift, and teams lose track of changes.

With Libraries:

- Components can be published and reused across project files.
- Updates flow downstream with version history and change notifications.
- Teams can collaborate without worrying about mismatched assets.

<Note>Libraries are available on Voyager and Enterprise plans. [Learn more about our plans and pricing](https://rive.app/pricing?utm_source=docs&utm_medium=content).</Note>

## Creating a Library
Any file can be made into a library. First, you'll need to create a [component](editor/fundamentals/components) and/or a view model before you can publish the file as a library. Select an artboard on the stage and use the component icon in the inspector or `Shift` + `N` to toggle its status as a component.

![Image](/images/editor/libraries/01-component.webp)

With a component or view model present in the file, select the **Publish Library** option via the export action on the toolbar, or via the file menu. The publishing panel provides an opportunity to select which of the components, view models, and enums you'd like to be published as part of the library.

![Image](/images/editor/libraries/15-publish-alt.webp)

<Tip>You can identify a library file by the icon in the tab bar and in the file browser.</Tip>

## Importing from a Library
To start using components and view models from a published library, select the library icon present in both the asset and data panels. The library panel displays alongside the hierarchy/asset/data column, and displays a list of the available libraries for the active file.

![Image](/images/editor/libraries/05-browse.webp)

<Note>Currently, a Rive file can only access libraries contained within the same project. Cross-project — or workspace — libraries are coming soon. Public libraries are planned soon after that.</Note>

Selecting a library listed in the panel will present its available components, view models, and enums. Choose the elements you'd like to add to your file, and use the **Add to File** action in the inspector to import them.

![Image](/images/editor/libraries/06-add-component.webp)

<Tip>You can use the version dropdown to browse and import previous iterations of libraries and their components.</Tip>

![Image](/images/editor/libraries/07-version-dropdown.webp)

With the chosen elements added to your file, you can access and reuse components and view models via the asset and data panels. Elements sourced from a library can be identified by the library icon appended to the bottom-right corner of the regular icon.

![Image](/images/editor/libraries/08-assets.webp)

## Updating a Library
After publishing, you can continue to make changes, add, or remove components, view models, and enums. Republish the library via the same option in the export or file menus. Upon publishing an updated version of the library, any files that have imported elements from it will display a small badge indicating an available update.

![Image](/images/editor/libraries/09-update-badge.webp)

To update a component, right-click it in asset panel and select **Library Options** -> **Update Component** from the context menu. Choose the library elements you'd like to update and select **Update Selected**.

![Image](/images/editor/libraries/10-update.webp)

## Detaching

<YouTube id="TtOOPSAm6pI" />

After importing a component from a library and creating an instance of it on the stage, you may choose to detach it. Detaching a component will decouple it from the source and copy over its contents into your active file. Any references to it will be redirected to the new local copy. You may want to detach a component to make changes to it, without changing the source.

<Note>It's not possible to re-attach a component after it has been detached.</Note>

![Image](/images/editor/libraries/13-detach.webp)

## Export Options
By using libraries, you create a series of dependencies between files. For example, an instance of an imported component depends on the library file it came from, which in turn may depend on an image asset used within the component, or perhaps another component from a different library entirely.

The export options control what and how components and any assets they depend on get exported to a riv file. These options are available across assets and components, with an additional layer of separation for libraries specifically.

To access the export options for a given component, asset, or library, select it in the asset panel and set the desired options in the inspector.

![Image](/images/editor/libraries/12-component-level-options.webp)

- **Automatic:** Include this asset/component in the export if it's being used somewhere on the stage. For assets contained within a library, this option is inherited from the source file.
- **Force Export:** Export this asset/component, regardless of whether or not it's referenced within the file.
- **Prevent Export:** Don't include this asset/component in the export, regardless of whether or not it's referenced within the file.

You may want to adjust these options to suit your needs at runtime as opposed to design-time. For example, images used within a design are to be supplied from an external source at runtime, and therefore aren't required in the riv file. Or, you intend to use a library component across multiple Rive files at once via data binding. Exporting the library component separately and excluding from the host files prevents it from being duplicated.

<Note>Currently, the export behavior for assets within a library component can only be set at the library level, not per component. To do so, set the panel display mode to Source/Type, and select the library item in the asset panel.</Note>

![Image](/images/editor/libraries/11-library-wide-options.webp)

## Unpublishing a Library
Use the **Unpublish Library** action in the file menu to prevent additional files from accessing the library and its components. Unpublishing does not remove library components from host files that had already imported them. Host files that have imported library components will retain access to previously published versions of the library. You may republish a library at any time.

![Image](/images/editor/libraries/14-unpublish.webp)

---
## editor/tagging.mdx

---
title: 'Tagging'
description: ''
---

Tagging is a way to organize your hierarchy further. Create tags, then apply them to objects in the Hierarchy like Bones or Groups, then filter the view to see exactly what you need, when you need it. 

## Creating Tags

There are two ways to create a Tag: either through the Hierarchy or by using the Inspector. Remember that any Tag created can be used on any artboard in the file.

### In the Inspector

To create a new tag, ensure that you have nothing selected on the artboard, then use the plus button next to the Tags option.

![Create Tag through Inspector](https://ucarecdn.com/9b8a9f8d-7755-4341-a2e2-e765277c078b/)

Once the Tag has been added, you can change the name and color to your liking.

### In the Hierarchy 

There are two ways to create tags through the Hierarchy. The first is by using the tag menu at the top of the Hierarchy. From here you can create new Tags, edit Tags, collapse Tags, filter, lock, or select assigned Tags.

![Create Tag through Tag menu](https://ucarecdn.com/efcce09c-e7dc-46d4-9d29-7f8e57d63248/)

The second way is to select one or more objects to create a tag directly in the hierarchy, then right-click and use the add tag option. From there, you can either create a new tag or assign a tag that you’ve already created.

![Create Tag on object](https://ucarecdn.com/7e3b90b7-97de-4337-9c5b-77e8038f11b3/)

To edit the Tag's properties, use the steps above.

## The Tags Menu 

The Tags Menu is where you will find most of the Tag Options. Some of these options are self-explanatory, such as creating or editing a tag. Let’s explore some of the other available options.

![Tag menu](/images/editor/b4ba7047-3927-467f-9528-32c9b066f0d2.webp)

### Collapse Tag

When you add a tag to an object, you’ll notice that the Tag's name and the color pip are displayed to the right.

![Image](https://ucarecdn.com/eb9e515c-04e3-4f56-bee5-196e72e65ad9/)

We can use the Collapse Tag option to hide the name. Conversely, we can use the Reveal Tag option to display the names again.

### Filter Tags 

When you mouse over a tag in the menu, you’re given the option to Filter. This option will filter your Hierarchy and only show you the objects with the filtered tag. The current filtered tabs are shown next to the Tag Menu.

![Image](https://ucarecdn.com/e808968b-1ee4-4e25-a3f6-09f615ba2229/)

Note that you can add as many tags to the filter as you want. This is a great way to show only the controls you need to create an animation.

### Locked 

The Locked option will allow you to lock the objects with the selected Tag. When locked, you can no longer select that object on the stage.

![Image](https://ucarecdn.com/f2b63a89-cbea-42ed-bd3b-c35969ef62ee/)

This is a great tool to use when you want to hand off a file to another animator so that they don’t inadvertently use a control that shouldn’t be.

This option is also available via the Inspector via the lock icon.

### Select 

The Select option will select every object with the assigned tag.

Note that this option is also available in the Inspector via the target icon.
## Editor — fundamentals

---
## editor/fundamentals/artboards.mdx

---
title: "Artboards"
description: "Artboards are the foundation of a file."
---

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="xdqqPAlB4n8" />


Artboards are the foundation of your composition across both design and animate mode. They act as the root of every hierarchy and let you define a scene's dimensions and background color. You can create infinite artboards on the [Stage](/editor/interface-overview/stage), but each Rive file has at least one artboard.

![Artboard](/images/artboard.png)


## ​Active artboard


The active artboard is represented with an Active tag next to its name on the stage. You can activate an artboard by clicking on it or any of its children within the stage. Note that sections of the editor will only surface content associated with the active artboard. For instance, only the active artboard's hierarchy is displayed in the tree. Similarly, only animations referenced to the active artboard will surface within the timeline.


<img
  src="/images/active.gif"
  alt="Active Gi"
  title="Active Gi"
  style={{ width:"100%" }}
/>

The active artboard is represented with a dot next to its name on the stage. You can activate an artboard by clicking on it or any of its children within the stage. Note that sections of the editor will only surface content associated with the active artboard. For instance, only the active artboard's hierarchy is displayed in the tree. Similarly, only animations referenced to the active artboard will surface within the timeline.

## Default State Machine

The default state machine is the state machine that will be played when using the play button in the Toolbar. In addition to setting the default state machine, this also sets the default artboard that a developer will see when using this file outside of Rive.

![Default SM](/images/defaultSM.gif)

To change the default state machine, use the dropdown to select the one you want to use.

You can quickly play the selected state machine from Design Mode by holding shift and hitting the space bar.

![Play Default](/images/playDefault.gif)

## ​Creating an artboard

Before creating any graphics, you'll first need to create an artboard. There are two ways to create an artboard.

In a new file, you'll find options on the stage to define an artboards dimensions or to select from a few defined presets. Once you've decided on the properties, you can then hit the Create Artboard button.

![Create AB](/images/create_AB.gif)


Alternatively, you can use the​ Artboard tool which is found in the Artboard menu, or by using the shortcut A. With the tool active, click and drag to define the bounds. You can always adjust the size and position by selecting the artboard in the [Hierarchy](/editor/interface-overview/hierarchy) to surface its properties in the [Inspector](/editor/interface-overview/inspector).

## Artboard properties

Every artboard has various properties that can be changed in the [Inspector](/editor/interface-overview/inspector). Some of the attributes that can be changed include an artboard's position on the [Stage](/editor/interface-overview/stage), its size, layout properties, fill color, origin point, and render presets.

![Artboard Prop](/images/artboard_prop.png)

## **Position**

The position of the artboard on the stage is controlled by the position properties of the artboard.

## Size and Size Type

By default, artboards are set to a fixed size with that size being determined by the Width and Height properties.

![With and height](/images/WandH.png)

**Link Icon**

Like other properties where the link icon is found, it can be used to lock the current ratio of the size properties.

![Link](/images/link.png)

**Size Type**

There are two sizing modes an artboard can have; Fixed, and Hug. These can be changed by using the dropdown under both the Width and Height properties.

![Size Type](/images/size_type.png)

As the name suggests, the Fixed type allows you to define and animate the artboards size properties.

The Hug type will let the artboard automatically size its height, width, or both to fit its children. Note that this option is only available if the artboard has at least one child layout object.

## Origin

The origin of an artboard determines the point from which all objects associated with the artboard will be measured. By default, the origin of an artboard is X:0%, Y:0%. These values place the origin at the top left of the artboard.

![Origin](/images/origin.png)

As you increase the value of either the X or Y, that shifts the origin point to the right (on the X), and down (on the Y).

You won't typically be changing the origin of an artboard, but if you plan on changing the origin, it's best done before any animation work is done. Changing the origin after animation keys are added can cause objects to appear out of position due to the origin shifting to a new position.

**Component Origin**

It's important to remember that a Component shares the origin of its source artboard. If you plan to do things like scale or rotate the Component, changing the origin will help make that process easier.

If you forget to change the origin after adding animations, you can always add the Component to a group, which will give you the same level of control.

## Layout Settings

Since an Artboard is the root object that all other objects are added to, Artboards allow you to add and adjust their layout properties. Read more about layouts [here](/editor/layouts/layouts-overview).

![Layout](/images/layout.png)

Note that these properties only take effect when one or more layouts have been added to the artboard.

## Fill and Stroke

Like other objects in Rive, Artboards can have one or more fills or strokes added to them. The process of adding and customizing fills and strokes is the same for both artboards and objects in the hierarchy.

![Fill and stroke](/images/fillandstroke.png)

Read more about fills and strokes [here](/editor/fundamentals/fill-and-stroke).

## Render Presets

Selecting an artboard allows you to create Render Presets that can be used to render out static graphics such as PNGs and SVGs, as well as video and motion files like PNG sequences and MP4s.

![Render](/images/render.png)

Read more about creating render presets [here](/editor/exporting/exporting-for-video-and-static-design).

## Selected Colors

When an artboard is selected, you can see, target, and adjust all colors associated with every object on the artboard.

![Select Color](/images/selectColor.png)

---
## editor/fundamentals/components.mdx

---
title: "Components (formerly Nested Artboards)"
sidebarTitle: "Components"
description: "Components streamline your workflow with reusable artboards and animations. Changes made to the source component are reflected across all of its instances."
---

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="HRUr9mnh41A" />

## Creating a Component

Any artboard can be converted to a component. To do so, select an artboard on the stage and use the component icon in the inspector to toggle its status.

Alternatively, you can use the `Shift` + `N` shortcut with an artboard selected. If you're coming from Figma, then the `Cmd/Ctrl` + `Alt/Option` + `K`, shortcut will also work.

Select the component toggle in the inspector again to revert your selection back to a regular artboard, or use the `Shift` + `Alt/Option` + `N` shortcut.

Currently, only artboards that have been flagged as components will be exported to your `.riv` file. If you think you may want to programmatically access an artboard at runtime, you should mark it as a component. More options on specific export behaviors are coming soon.

## Using Components

Use the Component Tool — formerly known as the Nested Artboard Tool — to select and place instances of a component on the stage. Select the tool from the toolbar or use the `N` shortcut to enable it.

Click anywhere on the stage to place the component in the desired location. A menu will display available components to instance. If none show up, you may have no artboards marked as components in your file.

![Image](/images/editor/fundamentals/components-add.gif)

Alternatively, select the dropdown menu to the right of the toolbar icon to select the component ahead of time. The menu is informed by the sort mode of the assets tab — the 'Custom' mode will present components as they’re organized in the asset panel, while the 'Source/Type' mode will present components from their source. The latter will become useful with our Libraries feature.

## Configuring a Component Instance

Once you’ve added an instance of a component, select a timeline or state machine for playback.

### State Machines

After assigning an instance, the default state machine is displayed in the inspector.

![Image](/images/editor/fundamentals/components-statemachine.gif)

If you’ve exposed any inputs, you can access them using the options menu (when an animation is selected) or via the inputs panel when a state machine is selected.

![Image](/images/editor/fundamentals/components-nested_inputs.gif)

### Adding an Animation

You can playback any animation associated with a component. You’ll need to add the desired animation to the instance using the plus button in the Inspector.

![Image](/images/editor/fundamentals/components-animations.gif)

These animations can be used by themselves, mixed with the state machine, or layered with other animations.

Note that before adding the animation, you must select whether it's a simple or remapped animation.

#### Simple

Simple animations are an easy way to playback a component's timeline.

![Image](/images/editor/fundamentals/components-animation-simple.gif)

A simple animation lets you key its start point on a timeline. You also have the option to change the animation's playback speed.

#### Remap

Remap animations allow you to key time values of an animation on the timeline. This lets you stretch, shrink, or even play an animation in reverse.

![Image](/images/editor/fundamentals/components-animation-remap.gif)

Note that the time value is in percent, with 0% representing the start of the timeline and 100% representing the end.

### Mix Value

As you add additional animations to a Component, animations begin to mix together. This mixing is important, especially when multiple animations share keyed properties. Without adjusting this value, your Component may not playback your animations in the way you want.

By default, any animation added to a component starts with a mix value of 100%. You can adjust this value in design mode or in a specific animation by setting keys. **Note that an animation that has a non-zero mix value will always be mixing with other animations, regardless if it has a play key set or not.**

To ensure the correct animation is playing, ensure that you key the mix value for the desired animation to 100%, and all other animations have a mix of 0%.

## Instance Modes

Component instances can be set to use one of 3 modes which will behave differently based on their contents and the context in which they are used. The Leaf and Layout modes are typically used when the parent artboard needs to layout its contents responsively.

### Node

This is the default mode and is used in non-responsive scenarios. Its contents will always appear scaled (via the Scale property).

### Leaf

![Image](/images/editor/fundamentals/components-leaf.png)

Leaf mode will result in the Component always being positioned and resized relative to its containing Layout or Artboard. This can be useful if the Component contains elements that need to resize to its container, but don't contain Layouts themselves.

#### Leaf Fit

The Fit type determines how the Component Leaf will scale within its allotted area.

- **Fill (Default)**: Content will fill the available view. If the aspect ratios differ, then the Rive content will be stretched.
- **Contain**: Content will be contained within the view, preserving the aspect ratio. If the ratios differ, then a portion of the view will be unused.
- **Cover**: Rive will cover the view, preserving the aspect ratio. If the content has a different ratio to the view, then the content will be clipped.
- **Fit Width**: Content will fill to the width of the view. This may result in clipping or unfilled view space.
- **Fit Height**: Content will fill to the height of the view. This may result in clipping or unfilled view space.
- **None**: Content will render to the original size of its artboard, which may result in clipping or unfilled view space.
- **Scale Down**: Content is scaled down to the size of the view, preserving the aspect ratio. This is equivalent to **Contain** when the content is larger than the canvas. If the canvas is larger, then **ScaleDown** will not scale up.

#### Leaf Alignment

The Alignment type determines how the contents are aligned within the allotted area. Alignment is set in a 3x3 grid fashion: **Center (Default)**, **Bottom Left**, **Bottom Center**, **Bottom Right**, **Left Center**, **Right Center**, **Top Left**, **Top Center**, **Top Right**.

#### Leaf Alignment Position X/Y

Leaf Alignment Position is a numerical representation of Alignment and can be used in cases where the 9 Alignment options are not desirable. Values can be represented in the following ways: X = -1 (Left), 0 (Center), 1 (Right) and Y = -1 (Top), 0 (Center), 1 (Bottom). Non-integer values can also be used in order to align in various ways, for example, X = 0.5 will position the content half way between Center and Right.

### Layout

![Image](/images/editor/fundamentals/components-layout.png)

Layout mode is used when your Component contains Layouts that need to remain responsive as the size of its parent changes. This is the only mode where the Component contents are not scaled, rather the artboard size changes in order to reflow the Components's contents.

#### Layout Scale Type

- **Fixed** - A fixed width or height for the layout. The defined value can be either a point or percentage value. Use the unit toggle within the fields to toggle between value types.
- **Hug** - The width and/or height of the layout shrinks to fit its children. This is useful if your Component contains text or other objects that need to determine its size.
- **Fill** - The width and/or height of the layout expands to fill the available space within the parent layout or artboard.

#### Layout Size

When set to Fixed, the width and height of the Component can be set to either pixel or percent values. This is different than the scale property, which changes the Components's scale. Typically scale should not be used when Layout mode is selected.

## Exposing Inputs and Events

Expose the Inputs and/or Events of a Component to control them from a parent/host Artboard. This allows you to control one Component with another via a State Machine.

### How to Expose an Input

Exposing an Input allows the parent artboard to access and manipulate it. To do this, select the desired input, then check the expose to main artboard option in the inspector.

![Image](https://ucarecdn.com/251b0247-ae05-4f58-8858-8e7a21abd816/)

After creating a Component, you’ll see any exposed inputs in the Inspector via the options panel and in the Inputs panel.

### Using Inputs on a Parent Artboard

Exposed inputs can be found in the Inputs panel or in the inspector. You can use them through listeners, an event, or by keying them on a timeline.

![Image](https://ucarecdn.com/ee1dd959-9fba-45c9-a74b-1173cd71e894/)

#### Via a Listener

When you create a listener, you’ll find all exposed Inputs as a set input property of a Listener. This option lets you, for example, change the boolean input of multiple artboards simultaneously.

![Image](https://ucarecdn.com/2349fdd6-5a5a-434e-a1dc-3974e6f1e01c/)

#### Using Events

Additionally, we can use Listeners to listen for Events firing from our Component, and change inputs accordingly.

![Image](https://ucarecdn.com/2b1ddae6-31c9-41be-969c-86a59b2206cd/)

To see an Event associated with an Artboard, you’ll need to set the Artboard as a target of the Listener. The Event will now be listed as a listener action.

#### Keying on the State Machine

You can key exposed inputs on the parent artboard via the options panel in the inspector.

This is a handy trick when you, for example, want to set the text value within an Instance.
---
## editor/fundamentals/design-vs-animate-mode.mdx

---
title: "Design vs Animate Mode"
description: "The Rive Editor has two distinct modes, Design and Animate. Switching between modes changes the interface to show the appropriate tools and options."
---

## Design Mode

Use Design Mode to prepare your graphics for animation. This is where you can design your own graphics with Rive's [tools](/editor/interface-overview/toolbar), [import graphics from other software](/editor/fundamentals/importing-assets), or rig your graphics with [bones](/editor/manipulating-shapes/bones), [transform spaces](/editor/fundamentals/transform-spaces), [layouts](/editor/layouts/layouts-overview), [joysticks](/editor/manipulating-shapes/joysticks), and [constraints](/editor/constraints/constraints-overview).

![Image](/images/editor/fundamentals/Design_Mode.png)

Design Mode is the default mode for any file that doesn't have any animations created. The mode exists because Rive allows you to attach multiple animations to a single artboard, so you need a place to set up and create those graphics.

## Animate Mode

Use [Animate Mode](/editor/animate-mode/animate-mode-overview) to create all of the [States](/editor/state-machine/states) and [State Machine](/editor/state-machine/state-machine) for your artboard.

When you switch to Animate Mode, the UI updates to display a list of Timelines and State Machine associated with the [active artboard](/editor/fundamentals/artboards#active-artboard). The [Inspector](/editor/interface-overview/inspector) also updates to show key buttons next to any property that can be animated.

![Animate Mode](/images/editor/fundamentals/Animate_Mode.png)

Selecting any Animation from the Animations list will bring up a timeline view, while selecting a state machine will replace the timeline with the graph view.

![State Machine](/images/editor/fundamentals/State_Machine.png)

## Creating Assets in Animate Mode

While there are separate modes, graphics can be created and changed in both modes, but it's important to keep a few things in mind.

1. If a Timeline is selected, graphics, both procedural and custom paths, can be created. While graphics can be created, any changes to the path, shape, or its properties will automatically be keyed on the timeline. Because of this, we recommend not making any assets when a timeline is selected.
2. Animate Mode works like Design Mode if a State Machine is selected. Asset creation, rigging, and other design changes will not be automatically keyed. This lets you make any design changes you want without switching between the different modes, though you do lose some screen real estate due to the graph. We recommend making vast changes in Design mode while using Animate mode only to add quick adjustments like hit boxes or layouts.
---
## editor/fundamentals/edit-vertices.mdx

---
title: "Edit Vertices"
description: "No matter the type of vector you create, you can edit the vertices by changing their position or handles in both design and animate mode."
---

import { YouTube } from '/snippets/youtube.mdx'

## Edit Vertices mode

To enter Edit Vertices mode, either select the shape and hit enter twice or select a path and hit enter once.


![EVM](/images/EVM.gif)


After activating Edit Vertices mode, you can select any vertex, reposition it, and edit the bezier handles.

### Deep Selection

You may want to select and edit a specific path when dealing with a group of shapes. You can either find that path in the Hierarchy or you can use Deep Selection to select it directly on the Stage.

To select a path within a group on the stage, hold `⌘` (Mac) or `ctrl` (Windows) and click the target path. Alternatively, you can double-click on the path you want to select.

### Path Options

Each path in Edit Vertices mode has a set of path options at the top of the Inspector.


**Done Editing Button**


The Done Editing button can be used to exit Edit Vertices Mode.

![Done Edit](/images/DoneEdit.png)

**Open Path**

The Open Path button will disconnect the last vertex from the first vertex.

![Open Path](/images/OpenPath.png)

**Reverse Direction**

<YouTube id="zp2NNsSTfO8" />

The Reverse Direction button can be used to reverse the direction of the path. Depending on the Fill-Rule, this can eliminate holes in our shape by changing the mathematical value of the selected path.

**Convert Radial Corners**

Straight vertices with a corner radius will deform when the scale transform is applied to the shape or path layer. You can convert radial corners from a procedural property to a defined set of vertices. This process will eliminate deformation of the corner.


![Convert](/images/convert.gif)


## Bezier Handles


**‌Straight**

‌The default handles are set to straight, which creates straight edges between vertices.

![Straight](/images/Straight.png)

**Corner Radius**

The Corner Radius property allows you to round straight corners. This property only appears on vertices that are set to straight.

**‌Mirrored**


‌Mirrored is the default handle when you create a vertex by clicking and dragging. These handles always keep the same rotation and length.

![Mirrored](/images/mirriored.gif)


**‌Detached‌**

Detached handles allow each handle to have its own rotation and length.

![Detached](/images/detached.gif)

**‌Asymmetric**


‌Asymmetric handles share the same rotation but can have lengths independently of each other.


![‌Asymmetric](/images/asem.gif)



---
## editor/fundamentals/fill-and-stroke.mdx

---
title: "Fill and Stroke"
description: "The Fill and Stroke section of the Inspector allows you to add and modify the Fill and Stroke properties of the currently selected object. You can create as many fills or strokes as you'd like."
---

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="4ZRzKScvJbQ" />

# Fill

### **Create a new Fill**

To create a fill, select a shape, then use the plus button under the Fill and Stroke section of the Inspector. Be sure to select Fill from the new menu. You'll be able to tell that a layer is a fill by looking at the color box on the left side.

![New Fill](/images/newFill.gif)

### **Changing Fill color**

To change the color of a Fill, select the color box on the left side of the Fill layer. This will open the Color Picker. From there, you can use the various sliders to choose which color you'd like for the Fill.

![Change color](/images/changecolor.gif)

### **Changing Fill Type**

When a new shape is created, by default the shape will have a solid fill. When a new fill is added, by default the fill type is set to linear. We often need to change the fill type between the different types. This can be done by selecting the color box.

![Change fill type](/images/changefilltype.gif)

Once the Fill has been opened, you'll find the Fill Selector dropdown in the top of the option box.

The different fills that can be selected are:

- **Solid**
- **Linear Gradient**
- **Radial Gradient**

### **Changing Fill color (Gradient)**

To change the color of a Fill, select the color box on the left side of the Fill layer. This will open the Color Picker.

![Change stopper](/images/changestopper.gif)

When a gradient is selected, you'll notice a new bar appear above the color picker. This represents the color of the gradient at different points.

By default, a gradient has two points.

### **Changing the color of a stopper**

To change the color of a particular color stopper, start by selecting the stopper you'd like to change.

Next, use the various sliders to choose which color that stopper should be.

### **Adding and removing stoppers**

To add a new color stopper, click any space along the long that isn't currently occupied by another stopper. This will generate an additional color stopper.

![Add Remove](/images/add_remove.gif)

To delete a color stopper, select the stopper you'd like to delete, then hit the Delete or Backspace key.

### **Change Fill Order**

The order of fills determines their render order, with fills on top rendered in front and fills at the bottom rendered in back.

![Fill Order](/images/fillOrder.gif)

This order can be changed at any time by clicking and dragging on an empty area within the layer.

### **Fill Properties**

Each Fill has its own properties which can be edited and keyed on the timeline. Some of these properties can be found by using the fill option button.

![Fill Prop](/images/fillProp.png)

**Fill Name -** You can edit the name of a fill using this property.

**Blend -** This option can be used to change the Blend Mode of an individual Fill. By default, this mode will be set to inherit, which inherits the blend mode from the shape layer.

**Fill Rule -**  This option can be used to change the fill rule for the Fill. This must be set to clock-wise if you want the fill to be feathered.

\*\*Feather - \*\*This option can be toggled to feather the chosen Fill. Read more about Feathering below.

### **Deleting and hiding a Fill**

Often times we'll need to delete or hide a particular Fill. This can be done by selecting the shape, then using the eye icon to hide the Fill, or the minus icon to delete the fill.

![Delete](/images/delete.gif)

### Fill Rule

The Fill Rule determines how overlapping paths in a shape will be filled:

- **Non-Zero** assigns a \+1 value to clockwise paths and a -1 value to counter clock wise paths. Areas that equal a value other than 0 will be filled.
- **Even-Odd** assigns a \+1 value to clockwise paths and a -1 value to counter clock wise paths. Areas that equal an even value will be filled while odd values wont be.
- **Clockwise** a Fill Rule exclusive to Rive. This fill rule enables manual subtraction of paths which can be found in edit vertices mode. This fill rule is also required for shapes where you'd like to enable vector feathering.

# Stroke

### Create a new Stroke

To create a Stroke, select a shape, then use the plus button under the Fill and Stroke section of the Inspector. Be sure to select Stroke from the new menu. You'll be able to tell that a layer is a Stroke by looking at the color box on the left side. Strokes are represented by an outlined box.

![New Stroke](/images/NewStroke.gif)

### **Changing stroke color (solid)**

To change the color of a Stroke, select the color box on the left side of the Stroke layer. This will open the Color Picker. From there, you can use the various sliders to choose which color you'd like for the Stroke.

![Stroke Color](/images/StrokeColor.gif)

### **Changing Stroke type**

By default, strokes are set to a solid color, but various stroke types are available from the Color Picker menu.

![Change Stroke Type](/images/ChangeStrokeType.gif)

The different strokes that can be selected are:

- **Solid**
- **Linear Gradient**
- **Radial Gradient**

### **Changing Stroke color (Gradient)**

To change the color of a Stroke, select the color box on the left side of the Stroke layer. This will open the Color Picker.

When a gradient is selected, you'll notice a new bar appear above the color picker. This represents the color of the gradient at different points.

By default, a gradient has two points.

### **Changing the color of a stopper**

To change the color of a particular color stopper, start by selecting the stopper you'd like to change.

![Change Gradient Color](/images/ChangeGradientColor.gif)

Next, use the various sliders to choose which color that stopper should be.

### **Adding and removing stoppers**

To add a new color stopper, click any space along the long that isn't currently occupied by another stopper. This will generate an additional color stopper.

![Add Remove Stroke Stopper](/images/add_removeStroke_Stopper.gif)

To delete a color stopper, select the stopper you'd like to delete, then hit the Delete or Backspace key.

### **Deleting and hiding a Stroke**

Often times we'll need to delete or hide a particular Stroke. This can be done by selecting the shape, then using the eye icon to hide the Stroke, or the minus icon to delete the Stroke.

# Stroke Properties

Each Stroke has its own properties which can be edited and keyed on the timeline. Some of these properties can be found by using the Stroke option button.

**Stroke Name -** You can edit the name of a Stroke using this property.

**Blend -** This option can be used to change the Blend Mode of an individual Stroke. By default, this mode will be set to inherit, which inherits the blend mode from the shape layer.

**Cap -** This option changes the end cap of a Stroke. Read more about the different Caps below.

- **Butt** The end of the stroke is a straight line and does not extend beyond the end vertices. On a zero-length path, the stroke will not be rendered at all.
- **Round** The ends of a stroke are rounded. On a zero-length path, the stroke is a full circle.
- **Square** The ends of a stroke are squared off and extend beyond the end vertices. On a zero-length path, the stroke is a square.

**Join -** This option changes how the corners of a Stroke are rendered. Read more about the different Join options below.

- **Round** creates a rounded corner.
- **Bevel** creates a beveled corner.
- **Miter** creates a mitered corner.

**Apply Transformations -** The Apply Transformations toggle determines whether the shape layers scale will affect the thickness of the stroke. When this is toggled off, the thickness of the stroke will stay the same regardless of scale.

**Feather -** This option can be toggled to feather the chosen stroke. Read more about Feathering below.

**Stroke Type** - At the bottom of the Stroke Options Panel, you'll find options to change your stroke between a solid, trim, dashed stroke.

- **Solid -** Renders the stroke as a solid stroke. This is the default stroke type for each new stroke created.
- **Trim -**  Lets you animate the start, end, and offset of a line segment. Read more [here](/editor/manipulating-shapes/trim-path).
- **Dashed -** Lets you create dashed strokes with animatable property like the length of the dashed segment and offset.  Read more [here.](/editor/manipulating-shapes/trim-path)

# Vector Feathering

Vector feathering is a new way to feather both Fills and Strokes. Vector Feathering is a technique we invented at Rive that can soften the edge of vector paths without the typical performance impact of traditional blur effects.

### **Enabling Vector Feathering**

There are two main ways to enable vector feathering on any Stroke of Fill.

![Enable Feather](/images/EnableFeather.gif)

- **Feather Icon -** The feathering icon can be used on any Fill or Stroke layer to enable vector feathering.
- **Feather Toggle -** The feather toggle can be found in the Fill / Stroke options panel.

### Feathering Options

Feathers can be customized in a number of ways. The Feathering options can be found in the options panel once Feathering has been enabled on a Fill or Stroke.

**Direction** - This option lets you choose which direction the path will feather as you increase the feather amount.

![Direction](/images/Direction.gif)

- Outer - This option creates a feather that will feather outward from the path.
- Inner - This option creates a feather that will feather inward from the path.

**Amount** - This option lets you increase or decrease the amount of feather applied.

![Amount](/images/amount.gif)

**Space -** Determines how the feathered fill or stroke will apply transforms from the parent if any offset is present on the feather.

![Space](/images/space.gif)

- World - Transforms will be applied from the world transform. Feather will now act as a drop shadow.
- Local - Transforms will be applied from the local transform. This mode will have the feather work with transforms as you'd expect.

**Offset** - The Offset properties let you move the feather away from the path by increasing or decreasing the X and Y numbers.

![Amount](/images/amount.gif)

# Effect Groups

Effect groups let you apply a single path effect — or a stack of effects — to multiple strokes and fills at once, without having to configure each one individually. This is useful any time you have multiple shapes that need to share the same trim, dash, or scripted effect behavior, and you want to control them from one place.

<YouTube id="18LrObHLRFQ" />
---
## editor/fundamentals/freeze-and-origin.mdx

---
title: "Freeze and Origin"
---

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="nA15ZXkMb_c" />

When you transform objects, their children inherit the same transformations. The location where these transformations happen (sometimes called the origin, anchor point, or pivot) affects how your objects animate.

For example, manipulating the scale of a group creates different results if the scale originates in the center or the bottom.

You need to reposition the parent group to change the point of origin for these transformations. However, moving a parent causes all the children to move with it. The Freeze feature makes it possible to achieve this without having to rework the hierarchy structure.

# Origin of a Procedural Path

Procedural objects (like artboards and procedural paths) have an origin property. The origin of a procedural path determines where its properties originate from. For example, changing the width of a rectangle with its origin in the middle (50% X and 50% Y) causes it to grow from its center.

![Origin in the center](/images/editor/fundamentals/freeze-origin-center.gif)

Changing the width on a rectangle with its origin on the left side (0% X) causes it to grow from its left.

![Origin on the left](/images/editor/fundamentals/freeze-origin-left.gif)

This is particularly useful when animating paths that have other procedural properties enabled, such as rounded corners.

You can use the Freeze feature to change the Origin position on the Stage. Alternatively, set the exact value in the Inspector.

# Origin of a Custom Path and Group

### Freeze Mode

The Freeze feature allows you to move any parent object (groups, shapes, bones) without affecting the position of its children. Activate Freeze in the [Transform Tools menu](/editor/interface-overview/toolbar) or use the `Y` shortcut.

When Freeze Mode is active, you'll notice that your Stage is wrapped in a blue outline. You're now free to move the Origin without affecting the children.

Be sure to turn off Freeze by pressing `Y` again.

# Changing Origin with Align Tools

You can quickly change the location of an origin with the align tools.

Start by selecting the shape, then holding Option on Mac, or Alt on Windows. \
\
This now allows the align tool to reposition the Origin various positions.
---
## editor/fundamentals/groups.mdx

---
title: "Groups"
description: "Use groups to organize your graphics or to add extra transform spaces."
---

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="FnnZV57Dp3c" />

Activate the Group tool with the `G` shortcut. Click anywhere in an artboard to add a new group. Now drag and drop objects into the group in the Hierarchy.

You can also wrap a selection of shapes into a group with `⌘`\+`G` in macOS or `Ctrl`\+`G` in Windows.

Unwrap a group with `⌘`\+`Shift`\+`G` in macOS or `Ctrl`\+`Shift` +`G` in Windows.

## Group Style

The Style property of a group can be set to Group or Target.

### Group

Group is the default behavior, which behaves as described in the [Selecting and Navigating Groups](/editor/fundamentals/selecting-and-navigating-groups).

### Target

The Target option draws a different icon on the Stage that is always visible, regardless of whether the group has children (usually a group only displays an icon if it is empty). When a group displays as a Target, it also disables the functionality described in [Selecting and Navigating Groups](/editor/fundamentals/selecting-and-navigating-groups) section. This means you can immediately click through to any child of the group (no need to double-click, enter/esc, or Deep Select).

![Groups change Target](/images/editor/fundamentals/groups-targets.gif)

The Target option is particularly useful when working with Constraints.

<Card title="Constraints" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>} iconType="solid" href="/editor/constraints/">
  Constraints are a way to control the properties of an object through another target object. Some constraints can set limits on these properties (and their hierarchical relationships), while others can copy properties from one object to another.
</Card>
---
## editor/fundamentals/importing-assets.mdx

---
title: 'Importing Assets'
description: 'Import your assets by dragging and dropping them onto the Rive Editor. You can import SVG, JSON, PNG, PSD, and JPG formats.'
---

import { YouTube } from '/snippets/youtube.mdx'

## Assets Panel

<YouTube id="B9uD-Gh8zjg" />
<YouTube id="vH9UHmdVwx4" />

<YouTube id="hPbgPGJNE78" />

After dragging in your graphics, they now appear in the Assets Panel, located in the left side of the editor UI. Drag and drop them onto an artboard to begin using them.

## Importing Custom Font

For Pro customers, you can add custom fonts to be used with our Text tool. Drag and drop your `.OTF` or `.TTF` file into the editor, or use the plus button next to the Font section.

## Updating image assets


You can make updates to your images after they've been imported.

Do this by selecting the image in the Assets Panel; the asset's properties appear in the Inspector, and a "Replace" button will be available for raster assets (PNG, JPG, PSD).

Hit the replace button, and when prompted, select the updated image. You'll notice that this updates all instances of the graphic used in the file.

## Supported formats

Rive supports importing SVG (see limitations below), JSON, PNG, PSD, and JPG formats.

#### Copy and paste directly from Figma

You can use "copy as SVG" and paste it directly into the Rive editor.

![Image](https://ucarecdn.com/ec7e980c-ea0a-4147-96df-f29b7dc2be2c/)

#### Import Lottie file

<Note>
  Importing Lottie files is available on the Enterprise plan. [Learn more about our plans and pricing](https://rive.app/pricing?utm_source=docs&utm_medium=content).

  This workflow can introduce risks that vary across customer setups, and implementing them without our guidance can lead to issues in performance, security, or reliability. Helping customers assess and mitigate these risks takes significant time and effort, which is why this level of support is only available on Enterprise.
</Note>

You can import your Lottie animations into Rive. To get started, drag and drop your Lottie JSON file into the Rive editor. This adds it to your Assets panel.

![Image](/images/editor/fundamentals/12a13a71-d5d0-4ed2-a1b1-2fe49bbbb9df.webp)

From there, you can drag it into an existing Artboard or drag it into an empty space to create a new Artboard.

![Image](/images/editor/fundamentals/49c02a1d-18d9-4937-8ea1-bad52ba9ce4e.webp)

<Note>If you run into issues at runtime, you may need to convert any `Plus`, `Add`, or `Hard Mix` layer blend modes to a blend mode supported by the Rive runtimes.</Note>

## SVG Tips

SVG is a very flexible and feature-rich format. We aim to support SVG as best we can; however, there are some features that we do not support at this stage.

Exporting files as SVG with inline style instead of CSS will work best for our importer.

When exporting from other design tools, look for the option to retain the IDs and names of your shapes when you export. This will ensure that your imported file retains the same structure and layer names. Most tools have this option, as in the Figma example below.

![Image](/images/editor/fundamentals/9a2b2c37-c330-4323-a4c6-9928fbac8d94.webp)

### Photoshop

<YouTube id="Mlo9mQBUaTE" />

When exporting from Photoshop, make sure you're only using vector layers. Don't convert or flatten anything to raster.

### Illustrator

When using "Save As" to export an SVG from Illustrator, set the CSS Properties in the SVG Options to "Presentation Attributes" instead of the default setting. Similarly, when using "Export As" to export an SVG from Illustrator, set Styling to "Presentation Attributes" in the SVG Options. Note that Illustrator uses the "Export As" SVG Options when copying directly from Illustrator, so if you are copy-pasting from Illustrator to the Rive editor, be sure to set Styling to "Presentation Attributes" in the SVG Options.

Additionally, disable the "Preserve Illustrator Editing Capabilities" option, as this will make your file much larger and add data that our importer does not recognize.

### Known Issues

- Embedded images are ignored. We plan to implement this.
- Gradient transforms are ignored.
  - We currently cannot provide equal support for this across our runtimes, so this is not supported.
  - However, we support linear and radial gradients, which can cover some use cases.
- Rive does not have a concept of point (pt) or millimeter (mm) sizing. An SVG that uses dimensions provided in pt or mm will have its values converted to pixels (px). Points are converted to 1.33 px, and millimeters are converted to 3.78 px.
- SVG provides `inherit` to let strokes and fills use the color of their ancestors. Rive does not support this, and any inherited color defaults to white.
- Other unsupported SVG features:
  - `stroke-dasharray` - you may see a solid stroke line instead
  - `mask` - we treat this like clipping
  - `filter`
  - `skew`
---
## editor/fundamentals/overview.mdx

---
title: "Fundamentals Overview"
sidebarTitle: "Overview"
description: "In this section, we'll step through a typical workflow from creating an artboard all the way to exporting your first Rive file. Before we get started, check out our brief overview of the interface to familiarise yourself with the various sections and modes."
---

<Info>Prefer to watch a series of short videos to follow visually? Check out our [Rive 101](https://www.youtube.com/playlist?list=PLujDTZWVDSsFGonP9kzAnvryowW098-p3) playlist!</Info>

## Explore

<CardGroup cols={1}>
  <Card
    title="Interface Overview"
    icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>}
    iconType="solid"
    href="/editor/interface-overview/"
  >
    Take a tour of the Rive editor to familiarize yourself with the various sections and modes.
  </Card>
</CardGroup>

<CardGroup cols={2}>
  <Card
    title="Artboards"
    icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>}
    iconType="solid"
    href="/editor/fundamentals/artboards"
  >
    Artboards are the foundation of your composition across both design and animate mode. Learn how to create and manage artboards within a file.
  </Card>
  <Card
    title="Shapes and Paths"
    icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>}
    iconType="solid"
    href="/editor/fundamentals/shapes-and-paths-overview"
  >
    Start creating assets to work with, and learn about the nuances between shapes and paths.
  </Card>
</CardGroup>

<CardGroup cols={2}>
  <Card
    title="Importing Assets"
    icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>}
    iconType="solid"
    href="/editor/fundamentals/importing-assets"
  >
    Import your assets by dragging and dropping them onto the Rive Editor. You can import SVG, JSON, PNG, PSD, and JPG formats.
  </Card>
  <Card
    title="Exporting"
    icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M8.036 1v4.178c0 1.034.839 1.873 1.873 1.873h4.003v6.178a1.77 1.77 0 0 1-1.77 1.77H3.858a1.77 1.77 0 0 1-1.771-1.77V2.771A1.77 1.77 0 0 1 3.857 1zm1.25.145v4.033c0 .345.279.624.623.624h3.889a1.8 1.8 0 0 0-.377-.597L11.618 3.32 9.842 1.525a1.8 1.8 0 0 0-.557-.38" clip-rule="evenodd"></path></svg>}
    iconType="solid"
    href="/editor/exporting/"
  >
    Instructions on exporting your Rive files.
  </Card>
</CardGroup>
---
## editor/fundamentals/pen-tool-overview.mdx

---
title: "Pen Tool Overview"
description: "The Pen tool allows you to create custom vector paths as well as add additional vertices to your procedural paths. Learn more about the Pen tool by either watching the video or reading more below."
---

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="dE1OEaaX5dw" />

## Creating custom shapes

The Pen tool allows you to create custom vector shapes. Activate the Pen tool by finding it under the Create Tools menu or by using the `P` shortcut.

Click on the stage to place vertices.

![Image](/images/editor/fundamentals/pen-tool-create.gif)

Click and drag to create a vertex with bezier handles. When you are finished, hit `esc` on your keyboard.

![Image](/images/editor/fundamentals/pen-tool-create-handless.gif)

## Path & vertex shortcuts

- Hold Alt (Opt) to detach the Pen tool while drawing a path.
- Ctrl+click (Cmd+click) on the vertex to toggle between mirrored and straight handles.
- With Select or Pen tool, Ctrl+click (Cmd+click) on the vertex handle to remove that handle.
- With Select or Pen tool, Alt+click (Opt+click) on a vertex handle to detach the handle.
- With Pen tool, Alt+click (Opt+click) on a vertex to delete the vertex.
- Alt+drag (Option+drag) to duplicate vertices.
---
## editor/fundamentals/procedural-shapes.mdx

---
title: "Procedural Shapes"
---

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="vU5SrgymGD8" />

## Creating a procedural shape

![Procedural Shapes Menu](/images/editor/fundamentals/procedural-shapes-menu.png)

Under the Create Tools menu, you will find shape tools that are defined by procedural properties like width, height, corner radius, number of points, and more.

![Create Shape](/images/editor/fundamentals/procedural-shapes-create.gif)

Select the tool then click and drag anywhere inside an artboard. Hold `shift` to constrain the proportions of the shape.

### Convert a procedural path to a custom path

![Convert a procedural path to a custom path](/images/editor/fundamentals/procedural-shapes-convert.gif)

To edit the vertices of a procedural path, press `Enter` on your keyboard. This will convert the path into a custom path and allow you to modify the position of each vertex. Procedural properties (e.g. width, height, number of points) will no longer be available. Keep in mind that any animations applied to these properties will also be removed once the procedural path is converted to a custom path.

### Origin of a procedural path

The [origin](/editor/fundamentals/freeze-and-origin) of a procedural path determines where its properties originate from. For example, changing the width on a rectangle with its origin in the middle (50% X and 50% Y) causes it to grow from its center.

![Change size of procedural shape](/images/editor/fundamentals/procedural-shapes-size.gif)

Changing the width of a rectangle with its origin on the left side (0% X) causes it to grow from its left.

![Origin in procedural shapes](/images/editor/fundamentals/procedural-shapes-origin.gif)

This is particularly useful when animating paths that have other procedural properties enabled, such as rounded corners.
---
## editor/fundamentals/revision-history.mdx

---
title: "Revision History"
description: "Rive saves your files automatically as you work. Even if multiple people are working on the same file at the same time, Rive tracks all changes and stores them in the Revision History."
---

## View a file's history

The Revision History can be accessed from the [Editor Menu](/editor/interface-overview/toolbar).

![Menu Revision History](/images/editor/fundamentals/revision-history-menu.gif)

## Restore a revision

Select a revision to preview it and press the Edit Current Revision button. This copies the selected revision and creates a new entry at the top of the list. This guarantees that even restoring revisions is non-destructive, and you can always go back to the previous version of the file.

![Restore a revision](/images/editor/fundamentals/revision-history-restore.gif)

## Save a Revision

From the Editor Menu, select the Create a Revision button. You'll then be prompted to name the revision.

Once the revision is created, you can restore that revision using the steps above.

![Save a new revision](/images/editor/fundamentals/revision-history-save.gif)
---
## editor/fundamentals/selecting-and-navigating-groups.mdx

---
title: "Selecting and Navigating Groups"
---

## Double-click

Click on a group on the [Stage](/editor/interface-overview/stage) to select it. To select an object in a group, double-click on the object you want to select. This takes you down one level in the hierarchy and allows you to select any object on that level.

![Double Click1](/images/editor/fundamentals/DoubleClick1.gif)

You can continue to double-click on other nested groups and shapes to navigate down the [Hierarchy](/editor/interface-overview/hierarchy).

![Double Click2](/images/editor/fundamentals/DoubleClick2.gif)

## Enter and Esc shortcuts

Use the `Enter` key to navigate down a level in the Hierarchy to the selected object's child.

![Enter And Escape](/images/editor/fundamentals/EnterAndEscape.gif)

Use the `Esc` key to quickly navigate up the Hierarchy to select the object's parent.

## Deep Select

Hold `⌘` in macOS or `Ctrl` in Windows, click directly on a shape to select it, no matter where you are in the Hierarchy. This allows you to click through all groups and directly select a shape.

![Deep Select](/images/editor/fundamentals/DeepSelect.gif)
---
## editor/fundamentals/shapes-and-paths-overview.mdx

---
title: "Shapes and Paths Overview"
description: "Rive allows you to create, edit, and animate vector graphics using either procedural or custom shapes. These graphics combine shape and path layers to define them, which Rive exposes to give you greater flexibility and control with your designs and animations."
---

import { YouTube } from '/snippets/youtube.mdx'

To learn more about Shape and Path layers, watch our video on Shapes and Paths, or read more below.

<YouTube id="KunkCnbkTsg" />

## Shape layer

![Shape Layer](/images/editor/fundamentals/shape-and-path-shapelayer.png)

Vectors in Rive are rendered on shape layers. Shape layers define the style of the shape by allowing you to customize the fill and stroke.\`

![Fill and Stroke](/images/editor/fundamentals/shape-and-path-fill.png)

## Path layer

![Path Layer](/images/editor/fundamentals/shape-and-path-pathlayer.gif)

The actual shape of a vector is defined by a path (or multiple paths). Expanding a shape layer in Rive will reveal the paths it's using.

![Move Path](/images/editor/fundamentals/shape-and-path-move.gif)

‌You can add new paths to any shape by dragging and dropping an existing path onto the desired shape layer.

### Path layer properties

Path layers display properties that to the type of path. Learn more about [Procedural Shapes](/editor/fundamentals/procedural-shapes).

![Path layer Properties](/images/editor/fundamentals/shape-and-path-properties.png)

## Enter and Esc shortcuts

Use the `Enter` key to quickly navigate down the Hierarchy. If you have a shape selected, this allows you to select the child path layer quickly.

Use the `Esc` key to quickly navigate up the Hierarchy. If you have a path selected, this allows you to select the parent shape layer quickly.
---
## editor/fundamentals/transform-spaces.mdx

---
title: "Transform Spaces"
---

import { YouTube } from '/snippets/youtube.mdx'

Container Objects, like Groups, Bones, and Layouts, allow you to create new transform spaces for your graphics, opening up the ability to animate graphics from multiple areas of interest. For example, you might want a planet to rotate on its own axis while also rotating around another planet. Multiple transform spaces (achieved by nesting groups, bones, and other container objects) allow you to achieve this.

This technique is a fundamental concept for all motion graphics. To learn more about transform spaces, be sure to watch our video on hierarchical relationships.

<YouTube id="IcSXchdnzHM" />

## Transform space example

![Image](https://ucarecdn.com/8d60bc32-96ce-4b77-ade8-836f7c92b51d/)

Nest multiple groups to transform your shapes from different locations. In the example above, a group is rotating the Earth, another is rotating the Moon around the Earth, and another is rotating the moon on its axis.

![Image](https://ucarecdn.com/ab64bd82-90f1-46eb-b50a-506ec16e36ff/)
## Editor — exporting

---
## editor/exporting/exporting-for-backup.mdx

---
title: 'Exporting for Backup'
description: ''
---

<Note>Exporting for backup is available on paid plans. [Learn more about our plans and pricing](https://rive.app/pricing?utm_source=docs&utm_medium=content).</Note>

Exporting a file for backup is useful when you want a hard copy of your file saved to your device, if you are looking to transfer a file from one user to another, or you're trying to send in a file for a support ticket. Unlike files exported for runtime (.riv), files exported for backup (.rev) contain all of the information that is typically stripped from the file.\
\
 To export a file for backup, you can either do this from the file browser, or from the file menu when the file is open.

## Exporting from the file browser

To export a backup file from the file browser, first, find the file that you want to download.

![Image](https://ucarecdn.com/4a80265b-e521-476a-8bbd-476e34027443/)

\
Next, right click on the file and choose whether you want to download the file backup, or you can choose to download a specific revision of the file.

## Exporting from the file menu

To export a backup file, when the file is open, first, click on the file menu. Next, find the export option and select "for backup".

![Image](https://ucarecdn.com/4af741f7-8925-4ab1-88de-472ea00a47e1/)
---
## editor/exporting/exporting-for-runtime.mdx

---
title: 'Exporting for Runtime'
description: ''
---

import { YouTube } from '/snippets/youtube.mdx'

<Note>Exporting for runtime is available on paid plans. [Learn more about our plans and pricing](https://rive.app/pricing?utm_source=docs&utm_medium=content).</Note>

<YouTube id="H_px35jTqhg" />


To export a file for runtime, select the blue export action on the right-hand side of the toolbar or navigate to `Export` &gt; `For runtime` via the left-hand toolbar menu. You can load the exported `.riv` file into your app, game, or website via any of our [open source runtimes](/runtimes/).

![Image](/images/editor/exporting/94fc0d7c-cc7e-4b17-a6f7-0a00c98db70e.webp)

## Changes to exporting object names

You may need to access certain objects at runtime, such as a text run to swap a string, or a component to access its inputs. In order to make these objects discoverable at runtime, you'll need to explicitly set its name to be exported.

Previously, names would be exported if renamed from their default value in the editor. The issue with this approach was it assumed any renamed object was being sought at runtime, when in many cases you may simply want to rename objects to better organise your file — you didn't necessarily need them to be exported into your `.riv` export. Subsequently, we've changed this approach to provide more finite control over what object names get exported.

To export a name, right-click on it in the hierarchy or on the stage and toggle the 'Export name' option.

<Note>Objects with names set to be exported can be identified by the brackets wrapping their name.</Note>

![Image](/images/editor/exporting/8a147f5b-4e93-4d45-8984-64746ae1417d.webp)

<Note>Animations, State Machines, Events, and Input names do not require manual export.</Note>

### Benefits of optimizing your names

Exporting an object's name into your `.riv` adds a small amount of data. For large, complex files, the name data can start to add up. For that reason, it's desirable to only export the names you need to reference at runtime.

### Files created before the introduction of explicit export

For files created before this toggle was implemented, we assume any renamed object needs to be discoverable at runtime. That means you may notice a lot of items in your hierarchy being displayed inside brackets when opening an existing file. If, however, you'd prefer to not export the names and make your export size smaller, you can take these steps:

1. From the toolbar menu, select `Export options` &gt; `Remove name exports`.
2. Individually re-enable name exports for objects you need to access at runtime by right-clicking them in the hierarchy or on the stage and selecting `Export name`.

![Image](/images/editor/exporting/33b3efc7-3a2d-4c19-9ebd-c2dd1a0636c1.webp)
---
## editor/exporting/exporting-for-video-and-static-design.mdx

---
title: 'Exporting for Video or Static Design'
description: ''
---

<Note>Exporting video and images is available on paid plans. [Learn more about our plans and pricing](https://rive.app/pricing?utm_source=docs&utm_medium=content).</Note>

Rive is all about interactive animation, but sometimes you need  traditional formats such as MP4, GIF, or PNG sequence. Our Cloud Renderer turns any device into a supercomputer, allowing you to continue working while we generate your video or design file.

# Supported Formats

- H.264
- GIF
- PNG Sequence
- SVG Sequence
- WebM
- PNG
- SVG

# How to render

All rendering is done by creating Rendering Presets, then adding those Render Presets to the Render Que.

## Creating a preset

With the Artboard selected, you'll find the Render Presets option. Hitting the plus button will create a new Render Preset. This can be done from either Design or Animate mode.

![Image](/images/editor/exporting/36d52cd8-b10b-444f-8231-a1dc74e7511c.webp)

By creating a Render Preset in Design Mode you'll have the option to render either an SVG or PNG. This option can be changed using the dropdown menu with the preset selected.

![Image](/images/editor/exporting/d002a7fd-0c64-4adf-8ed9-bdd886c4ef6a.webp)

By creating a Render Preset in Animate Mode you'll have the option to render a number of video formats including  H.264, GIF, PNG/SVG sequence, and WebM. This option can be changed using the dropdown menu with the preset selected.

![Image](https://ucarecdn.com/e826d407-8977-4ed7-9c02-f35a8a30441b/)

To the left of the Render Preset name, you'll find additional options which allow you to change a number of options.

- Animation
- Format
- FPS
- Duration
- Bit rate
- Size

## Adding a Preset to the Render Queue

When you're finished creating a preset, you'll need to add it to the Render Queue.

Do this by either using the Queue All button below the Render Presets, or by finding the Add to Render Queue option within a Render Preset.

![Image](/images/editor/exporting/af23a14f-9a85-4bf6-af36-10a867fd8ca8.webp)

Once you've added an item to the Render, you'll see that a new window appears. This window is the Render Queue. From here, you can change rendering options, as well as begin the rendering process.

You can always find the Renderer via the File Menu.\
\
To begin rendering an animation, use the play button next to the preset name, or hit the double play button at the top of the Render Queue.

![Image](/images/editor/exporting/137a5d20-809e-4344-9d92-8e41519c7b45.webp)

Once you're file  is finished rendering, you'll be able to download it from the Completed tab within the Cloud Renderer.

![Image](/images/editor/exporting/67a9f6ab-7738-4f6e-bce4-21518e01ca2a.webp)
## Editor — embed-urls (sharing & embedding)

---
## editor/embed-urls/framer-and-rive.mdx

---
title: 'Framer And Rive'
description: 'Learn more about the Rive integration into Framer. '
---

You can now use the official [Rive Framer Plugin](https://www.framer.com/marketplace/plugins/rive/) to more easily integrate Rive graphics into Framer.

---
## editor/embed-urls/overview.mdx

---
title: 'Embed URLs Overview'
sidebarTitle: 'Overview'
description: 'Embed URLs are a fast, no-code way to share or embed your Rive files on the web.'
---

<Note>Generating embed URLs is available on Voyager and Enterprise plans. [Learn more about our plans and pricing](https://rive.app/pricing?utm_source=docs&utm_medium=content).</Note>

Embed URLs let you quickly generate a public version of your file for embedding or sharing.

Unlike [inviting someone to collaborate](/account-admin/workspaces/inviting-workspace-members), an embed URL is a **snapshot** of your file at the moment it’s generated. If you make changes later, you’ll need to generate a new link to reflect those updates.

## Creating an embed URL

<Steps>
  <Step title="Open the Embed Link dialog">
    In the Rive editor, click the **hamburger menu** in the top-left corner and select **Generate Embed URL**.

    ![Generate embed URL](/images/integrations/html-embed/generate-share-link-1.png)
  </Step>
  <Step title="Generate your link">
    In the dialog that appears, click **Generate Embed URL**.

    ![Generate embed URL](/images/integrations/html-embed/generate-share-link-2.png)
  </Step>
  <Step title="Choose an embed URL type">
    Once the link is generated, select the option that best fits how you plan to use your file.

    <Note>
      For more information on using embed URLs with tools like Framer, Webflow, and Notion, see [Integrations](/integrations/overview).
    </Note>

    ![Generate embed URL](/images/integrations/html-embed/generate-share-link-3.png)
  </Step>
</Steps>

### Embed URL types

- **Hosted link** — Opens your file on a dedicated Rive page with a framed viewer. Ideal for sharing with clients or stakeholders.
- **Embed link** — Displays your file without the surrounding Rive UI. Useful for platforms that automatically preview links (e.g. Notion, Telegram).
- **Embed code** — An iframe snippet for embedding your file into sites where you can edit HTML (e.g. WordPress).
- **Framer code (Deprecated)** — See the new official [Rive Framer Plugin](https://www.framer.com/marketplace/plugins/rive/).

### Embed URL options

- **Enable** — Turn the link on or off to control access.
- **Rive Renderer** — Use the Rive Renderer (recommended) or Canvas renderer.
- **Multi-touch** — Enable support for multi-touch interactions.

<Note>Certain features, such as [Vector Feathering](https://rive.app/blog/introducing-vector-feathering?utm_source=docs&utm_medium=content), are only available using the Rive Renderer. See our [Feature Support](/feature-support) page for more information.</Note>


## Sharing on Social Media

1. Copy the **Hosted Link**
2. Paste it into your favorite platform
3. See your Rive creation unfurl when you post

## Managing embed URLs

Visit the [Embed URLs](https://rive.app/account/links?utm_source=docs&utm_medium=content) section of your settings to manage the links you've generated. You can disable an embed URL by setting its Active toggle to off.