# Rive React Integration — Aggregated Reference

Source: rive-app/rive-docs/runtimes/react · rive-app/rive-react (cloned)


---
## runtimes/react/animation-playback.mdx

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
export const Simple = () => (
  <Rive src="https://cdn.rive.app/animations/vehicles.riv" animations="idle" />
);

// With `useRive` Hook:
export default function Simple() {
  const { RiveComponent } = useRive({
    src: 'https://cdn.rive.app/animations/vehicles.riv',
    animations: ['idle'],
    autoplay: true,
  });

  return <RiveComponent />;
}
```

<ControllingPlayback />

#### Invoking Playback Controls

Very similarly to Web, you can pass in Rive params and callbacks for certain animation events. See the Web tab for some examples of callbacks you can set. Additionally, you can use the `rive` object returned from the `useRive` hook to invoke playback controls.

See the example below here: [https://codesandbox.io/p/sandbox/adoring-sea-n7m59f](https://codesandbox.io/p/sandbox/adoring-sea-n7m59f)

```javascript
import { useState } from "react";
import { useRive, Layout, Fit } from "@rive-app/react-canvas";

export default function App() {
  const [truckButtonText, setTruckButtonText] = useState("Start Truck");
  const [wiperButtonText, setWiperButtonText] = useState("Start Wipers");

  // animation will show the first frame but not start playing
  const { rive, RiveComponent } = useRive({
    src: "https://cdn.rive.app/animations/vehicles.riv",
    artboard: "Jeep",
    layout: new Layout({ fit: Fit.Cover }),
    // Listen for play events to update button text
    onPlay: (event) => {
      const names = event.data;
      names.forEach((name) => {
        if (name === "idle") {
          setTruckButtonText("Stop Truck");
        } else if (name === "windshield_wipers") {
          setWiperButtonText("Stop Wipers");
        }
      });
    },
    // Listen for pause events to update button text
    onPause: (event) => {
      const names = event.data;
      names.forEach((name) => {
        if (name === "idle") {
          setTruckButtonText("Start Truck");
        } else if (name === "windshield_wipers") {
          setWiperButtonText("Start Wipers");
        }
      });
    },
  });

  function onStartTruckClick() {
    if (rive) {
      if (rive.playingAnimationNames.includes("idle")) {
        rive.pause("idle");
      } else {
        rive.play("idle");
      }
    }
  }

  function onStartWiperClick() {
    if (rive) {
      if (rive.playingAnimationNames.includes("windshield_wipers")) {
        rive.pause("windshield_wipers");
      } else {
        rive.play("windshield_wipers");
      }
    }
  }

  return (
    <>
      <div>
        <RiveComponent style={{ height: "1000px" }} />
      </div>
      <div>
        <button id="idle" onClick={onStartTruckClick}>
          {truckButtonText}
        </button>
        <button id="wipers" onClick={onStartWiperClick}>
          {wiperButtonText}
        </button>
      </div>
    </>
  );
}
```
---
## runtimes/react/artboards.mdx

---
title: 'Artboards'
description: 'Selecting which artboard to render at runtime'
---

import Header from "/snippets/runtimes/artboards/overview.mdx"
import ChoosingAnArtboard from "/snippets/runtimes/artboards/choosing-an-artboard.mdx"

<Header />

<ChoosingAnArtboard />

```javascript
export const Simple = () => (
  <Rive src="https://cdn.rive.app/animations/vehicles.riv" artboard="Truck" />
);

// With `useRive` Hook:
export default function Simple() {
  const { RiveComponent } = useRive({
      src: 'https://cdn.rive.app/animations/vehicles.riv',
      artboard: 'Truck',
      autoplay: true,
  });

  return <RiveComponent />;
}
```
---
## runtimes/react/caching-a-rive-file.mdx

---
title: "Caching a Rive File"
description: ""
---

import { Demos } from "/snippets/demos.jsx";
import Overview from "/snippets/runtimes/caching/overview.mdx"

<Overview />

## Example Usage

<Demos examples={["cachingARiveFile"]} runtime="react"/>

Here’s a simplified example showing how to integrate the `useRiveFile` hook to reuse a `RiveFile` across components:

```javascript
import React, { useState } from 'react';
import { useRiveFile } from '@rive-app/react-canvas';

// Custom Wrapper component to display the Rive animation
const RiveAnimation = ({ riveFile }) => {
    const { RiveComponent } = useRive({
        riveFile: riveFile,
        autoplay: true
    });

    return <RiveComponent/>;
};

function App() {
const { riveFile, status } = useRiveFile({
    src: 'https://cdn.rive.app/animations/myrivefile.riv',
});

const [instanceCount] = useState(5); // Number of RiveAnimation components to render

if (status === 'idle') {
    return <div>Idle...</div>;
}

if (status === 'loading') {
    return <div>Loading...</div>;
}

if (status === 'failed') {
    return <div>Failed to load Rive file.</div>;
}

// Each RiveAnimation component uses the RiveFile we loaded earlier, so it is only fetched and initialized once
return (
    <div className="App">
        <header className="App-header">Rive Instances</header>
        <div className="rive-list">
        {Array.from({ length: instanceCount }, (_, index) => (
            <RiveAnimation key={`rive-instance-${index}`} riveFile={riveFile} />
        ))}
        </div>
    </div>
    );

}

export default App;
```
---
## runtimes/react/data-binding.mdx

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

<Demos examples={["quickStartReact"]} />

<ViewModels />

Use the `useViewModel` hook to get a reference to a view model. You need to pass the `rive` object obtained from `useRive`.

```typescript
import { useRive, useViewModel } from '@rive-app/react-webgl2';

const { rive, RiveComponent } = useRive({
    src: 'your_file.riv',
    // ... other options
});

// Option 1: Get the default ViewModel for the artboard
const defaultViewModel = useViewModel(rive);

// Option 2: Get the default ViewModel explicitly
const defaultViewModelExplicit = useViewModel(rive, { useDefault: true });

// Option 3: Get a ViewModel by its name
const namedViewModel = useViewModel(rive, { name: 'MyViewModelName' });
```

<ViewModelInstances />

Use the `useViewModelInstance` hook to create a view model instance from a view model returned by the `useViewModel` hook.

```typescript
import { useRive, useViewModel, useViewModelInstance } from '@rive-app/react-webgl2';

const { rive, RiveComponent } = useRive({
    src: 'your_file.riv',
    artboard: 'MyArtboard',
    stateMachine: 'MyStateMachine',
    // ... other options
});

const viewModel = useViewModel(rive, { name: 'MyViewModelName' });
// Or: const viewModel = useViewModel(rive); // Default VM

// Get default instance without binding
const defaultUnbound = useViewModelInstance(viewModel, { useDefault: true });

// Get named instance without binding
const namedUnbound = useViewModelInstance(viewModel, { name: 'MyInstanceName' });

// Create new blank instance without binding
const newUnbound = useViewModelInstance(viewModel, { useNew: true });
```

You can also bind the view model instance directly to the Rive instance by passing the `rive` object to the `useViewModelInstance` hook.

```typescript
import { useRive, useViewModel, useViewModelInstance } from '@rive-app/react-webgl2';

const { rive, RiveComponent } = useRive({
    src: 'your_file.riv',
    artboard: 'MyArtboard',
    stateMachine: 'MyStateMachine',
    autoBind: false, // Disable auto binding so we can manually bind later
    // ... other options
});

const viewModel = useViewModel(rive, { name: 'MyViewModelName' });

// Get default instance (implicit) and bind it
const defaultBound = useViewModelInstance(viewModel, { rive });

// Get named instance and bind it
const namedBound = useViewModelInstance(viewModel, { name: 'MyInstanceName', rive });

// Create a new blank instance and bind it
const newBound = useViewModelInstance(viewModel, { useNew: true, rive });
```

If you set `autoBind: true` in `useRive`, you can access the automatically bound default instance directly via `rive.viewModelInstance` once Rive is loaded, without needing `useViewModel` or `useViewModelInstance`.

```typescript
const { rive, RiveComponent } = useRive({
    src: 'your_file.riv',
    artboard: 'MyArtboard',
    stateMachine: 'MyStateMachine',
    autoBind: true,
});

// Once loaded, the instance is available:
const boundInstance = rive?.viewModelInstance;
```

<Binding />

For React, no additional steps are needed to bind the view model instance to the Rive component. Passing the `rive` object to `useViewModelInstance` handles this automatically.

<AutoBinding />

```typescript
const { rive, RiveComponent } = useRive({
    src: 'your_file.riv',
    artboard: 'MyArtboard',
    stateMachine: 'MyStateMachine',
    autoBind: true, // Enable auto-binding
    // ... other options
});

// Once loaded, the instance is available:
const boundInstance = rive?.viewModelInstance;
```

<Properties />

<ListingProperties />

```typescript
// Access properties from the view model returned by useViewModel
const viewModel = useViewModel(rive);
console.log(viewModel?.properties);
```

<ReadingAndWritingProperties />

Use the specific hook for a given property type to get and set property values.

- `useViewModelInstanceBoolean`: Read/write boolean properties
- `useViewModelInstanceString`: Read/write string properties
- `useViewModelInstanceNumber`: Read/write number properties
- `useViewModelInstanceColor`: Read/write color properties with additional RGB/alpha methods
- `useViewModelInstanceEnum`: Read/write enum properties with available values
- `useViewModelInstanceTrigger`: Fire trigger events with optional callbacks

These hooks return the current `value` and a function to update it (`setValue`, `setRgb`, `trigger`). The `value` will be null if the property is not found or if the hook is provided with an invalid viewModelInstance.

```typescript
import {
    useViewModelInstanceBoolean,
    useViewModelInstanceString,
    useViewModelInstanceNumber,
    useViewModelInstanceEnum,
    useViewModelInstanceColor,
    useViewModelInstanceTrigger
} from '@rive-app/react-webgl2';

// Assuming viewModelInstance is obtained via useViewModelInstance or rive.viewModelInstance

// Boolean
const { value: isActive, setValue: setIsActive } = useViewModelInstanceBoolean(
    'isToggleOn', // Property path
    viewModelInstance
);
// Set: setIsActive(true);

// String
const { value: userName, setValue: setUserName } = useViewModelInstanceString(
    'user/name', // Property path
    viewModelInstance
);
// Set: setUserName('Rive');

// Number
const { value: score, setValue: setScore } = useViewModelInstanceNumber(
    'levelScore', // Property path
    viewModelInstance
);
// Set: setScore(100);

// Enum
const { value: status, setValue: setStatus, values: statusOptions } = useViewModelInstanceEnum(
    'appStatus', // Property path
    viewModelInstance
);
// Set: setStatus('loading');
// Get available options: statusOptions is an array like ['idle', 'loading', 'error']

// Color
const {
    value: themeColor, // Raw number value like -3267805
    setRgb: setThemeColorRgb, // Set RGB components (0-255 values)
    setAlpha: setThemeColorAlpha, // Set alpha component (0-255)
    setOpacity: setThemeColorOpacity, // Set opacity (0.0-1.0)
    setRgba: setThemeColorRgba, // Set all components at once
    setValue: setThemeColorValue // Set raw color value
} = useViewModelInstanceColor(
    'ui/themeColor', // Property path
    viewModelInstance
);
// Set RGB: setThemeColorRgb(0, 128, 255); // Set to a blue color
// Set Alpha: setThemeColorAlpha(128); // Set to 50% opacity
// Set Opacity: setThemeColorOpacity(0.5); // Set to 50% opacity
// Set RGBA: setThemeColorRgba(0, 128, 255, 255); // Blue with full opacity
// Set Value: setThemeColorValue(-3267805); // Set using raw color value

// Trigger (No value, just a trigger function)
const { trigger: playEffect } = useViewModelInstanceTrigger(
    'playButtonEffect', // Property path
    viewModelInstance,
    {
        // Optional callback to be called when the trigger is fired
        onTrigger: () => {
            console.log('Trigger Fired!');
        }
    }
);
// Trigger: playEffect();
```

The `value` returned by each hook will update automatically when the property changes in the Rive graphic.

<NestedPropertyPaths />

Access nested properties by providing the full path (separated by `/`) as the first argument to the property hooks.

```typescript
import { useViewModelInstanceString, useViewModelInstanceNumber } from '@rive-app/react-webgl2';

// Accessing 'settings/theme/name' (String)
const { value: themeName, setValue: setThemeName } = useViewModelInstanceString(
    'settings/theme/name',
    viewModelInstance
);

// Accessing 'settings/volume' (Number)
const { value: volume, setValue: setVolume } = useViewModelInstanceNumber(
    'settings/volume',
    viewModelInstance
);

console.log('Current theme:', themeName);
// setThemeName('Dark Mode');
// setVolume(80);
```

<Observability />

The React hooks handle observability automatically. When a property's value changes within the Rive instance (either because you set it via a hook or due to an internal binding), the `value` returned by the corresponding hook (e.g., `useViewModelInstanceString`) updates. This state change triggers a re-render of your React component, allowing you to react to the new value.

For Triggers, you can provide an `onTrigger` callback directly to the `useViewModelInstanceTrigger` hook, which fires when the trigger is activated in the Rive instance.

```typescript
import { useViewModelInstanceTrigger } from '@rive-app/react-webgl2';

// Assuming viewModelInstance is available
const { trigger } = useViewModelInstanceTrigger(
    'showPopup',
    viewModelInstance,
    {
        onTrigger: () => {
            console.log('Show Popup Trigger Fired!');
            // Show your popup UI
        }
    }
);
```

<Images />

Use the `useViewModelInstanceImage` hook to set image properties on view model instances.

    ```typescript
    import { useRive, useViewModel, useViewModelInstance, useViewModelInstanceImage } from '@rive-app/react-webgl2';

    const { rive, RiveComponent } = useRive({
        src: 'your_file.riv',
        artboard: 'MyArtboard',
        stateMachine: 'MyStateMachine',
        autoBind: false,
        // ... other options
    });

    const viewModel = useViewModel(rive, { name: 'MyViewModel' });
    const viewModelInstance = useViewModelInstance(viewModel, { rive });

    // Get the image property setter
    const { setValue: setImage } = useViewModelInstanceImage(
        'profileImage', // Property path
        viewModelInstance
    );

    // Load and set a random image
    const loadRandomImage = async () => {
        if (!setImage) return;

        try {
            const imageUrl = 'https://picsum.photos/300/500';
            const response = await fetch(imageUrl);
            const imageBuffer = await response.arrayBuffer();

            // Decode the image from the response
            const decodedImage = await decodeImage(new Uint8Array(imageBuffer));
            setImage(decodedImage);

            // Clean up the decoded image
            decodedImage.unref();
        } catch (error) {
            console.error('Failed to load image:', error);
        }
    };

    // Clear the image
    const clearImage = () => {
        if (setImage) {
            setImage(null);
        }
    };
    ```

<Lists />

<Demos examples={['dataBindingLists']} runtime="react" />

Use the `useViewModelInstanceList` hook to manage list properties on view model instances.

```typescript
import { useRive, useViewModel, useViewModelInstance, useViewModelInstanceList } from '@rive-app/react-webgl2';

const { rive, RiveComponent } = useRive({
    src: 'your_file.riv',
    artboard: 'MyArtboard',
    stateMachine: 'MyStateMachine',
    autoBind: false,
    // ... other options
});

const viewModel = useViewModel(rive, { name: 'MyViewModel' });
const viewModelInstance = useViewModelInstance(viewModel, { rive });

// Get the list property with manipulation functions
const {
    length,
    addInstance,
    addInstanceAt,
    removeInstance,
    removeInstanceAt,
    getInstanceAt,
    swap
} = useViewModelInstanceList('todos', viewModelInstance);

// Add a new todo item
const handleAddItem = () => {
    const todoItemViewModel = rive?.viewModelByName?.('TodoItem');
    if (todoItemViewModel) {
        const newTodoItem = todoItemViewModel.instance?.();
        if (newTodoItem) {
            // Set some initial values
            newTodoItem.string('description').value = 'Buy groceries';
            addInstance(newTodoItem);
        }
    }
};

// Insert item at specific index
const handleInsertItem = () => {
    const todoItemViewModel = rive?.viewModelByName?.('TodoItem');
    if (todoItemViewModel) {
        const newTodoItem = todoItemViewModel.instance?.();
        if (newTodoItem) {
            addInstanceAt(newTodoItem, 0); // Insert at beginning
        }
    }
};

// Remove first item by instance
const handleRemoveFirst = () => {
    const firstInstance = getInstanceAt(0);
    if (firstInstance) {
        removeInstance(firstInstance);
    }
};

// Remove item by index
const handleRemoveAt = () => {
    if (length > 0) {
        removeInstanceAt(0);
    }
};

// Swap two items
const handleSwap = () => {
    if (length >= 2) {
        swap(0, 1);
    }
};

console.log(`List has ${length} items`);
```

<Artboards />

<Demos examples={["dataBindingArtboards"]}  runtime="react" />

Use the `useViewModelInstanceArtboard` hook to set artboard properties on view model instances.

```typescript
import { useRive, useViewModel, useViewModelInstance, useViewModelInstanceArtboard } from '@rive-app/react-webgl2';

const { rive, RiveComponent } = useRive({
    src: 'your_file.riv',
    artboard: 'MyArtboard',
    stateMachine: 'MyStateMachine',
    autoBind: true,
    // ... other options
});

// Get artboard property setters
const { setValue: setArtboard1 } = useViewModelInstanceArtboard(
    'artboard_1', // Property path
    rive?.viewModelInstance
);

const { setValue: setArtboard2 } = useViewModelInstanceArtboard(
    'artboard_2', // Property path
    rive?.viewModelInstance
);

// Assign different artboards from the same file
const handleSetBlueArtboard = () => {
    if (rive) {
        const blueArtboard = rive.getBindableArtboard('ArtboardBlue');
        setArtboard1(blueArtboard);
    }
};

const handleSetRedArtboard = () => {
    if (rive) {
        const redArtboard = rive.getBindableArtboard('ArtboardRed');
        setArtboard2(redArtboard);
    }
};

const handleSetGreenArtboard = () => {
    if (rive) {
        const greenArtboard = rive.getBindableArtboard('ArtboardGreen');
        setArtboard1(greenArtboard);
    }
};

```

<Enums />

```typescript
const { rive } = useRive({
    src: 'your_file.riv',
    artboard: 'MyArtboard',
    stateMachine: 'MyStateMachine',
    autoBind: true
    // ... other options
});
const enums = rive?.enums();
console.log(enums);
```

# Examples

See the `DataBinding` story in the [Rive React repo](https://github.com/rive-app/rive-react) for a demo.

---
## runtimes/react/fonts.mdx

---
title: 'Fonts'
description: 'Loading and replacing fonts dynamically at runtime.'
---

import SwappingFonts from "/snippets/runtimes/fonts/swapping-fonts.mdx"
import fallbackFonts from "/snippets/runtimes/fonts/fallback-fonts.mdx"

<SwappingFonts />

For more information, see [Loading Assets](/runtimes/react/loading-assets).

<fallbackFonts />

<Note>
  For security reasons, browsers do not allow direct access to a user's system fonts. As a result, fallback fonts must be explicitly provided for this runtime.
</Note>

As of `v4.28.0`, the React runtime provides an API for supplying fallback fonts. When a glyph cannot be rendered with the default font, Rive will invoke a callback you provide to retrieve a list of decoded fonts to try instead. **Importantly**, this callback must be registered before Rive begins rendering.

To start, import `RiveFont` and `decodeFont` from the React package and call `RiveFont.setFallbackFontCallback()`, passing in the callback before the Rive component begins rendering. The callback receives the glyph that failed to render (as a Unicode code point) and the font weight, and should return a list of fallback fonts. It may be called multiple times if successive fallback fonts also lack support for the glyph.

```tsx
import { useEffect } from "react";
import { useRive, RiveFont, decodeFont } from "@rive-app/react-webgl2";

const THAI_FONT_URL =
  "https://raw.githubusercontent.com/google/fonts/main/ofl/notoserifthai/NotoSerifThai%5Bwdth%2Cwght%5D.ttf";

export default function MyRiveComponent() {
  useEffect(() => {
    const loadFonts = async () => {
      const notoSerifThai = await fetch(THAI_FONT_URL).then((res) => res.arrayBuffer());
      const riveThaiDecodedFont = await decodeFont(new Uint8Array(notoSerifThai));

      RiveFont.setFallbackFontCallback((codePoint: number, weight: number) => {
        // For Thai, use Noto Serif Thai font
        if (codePoint >= 0x0E00 && codePoint <= 0x0E7F) {
          return [riveThaiDecodedFont];
        }
        return null;
      });
    };
    loadFonts();
  }, []);

  const { RiveComponent } = useRive({
    src: "my.riv",
    autoplay: true,
    stateMachines: "State Machine 1",
  });

  return <RiveComponent />;
}
```

---
## runtimes/react/inputs.mdx

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

### Example

- [Setting state machine inputs (React)](https://codesandbox.io/p/sandbox/rive-state-machine-inputs-react-forked-k6gglh)

### Inputs

The react runtime provides a `useStateMachineInput` hook to make the process of retrieving a state machine input much simpler than that of the basic web runtime.

```javascript
import { useRive, useStateMachineInput } from "@rive-app/react-canvas";

export default function Simple() {
    const { rive, RiveComponent } = useRive({
        src: "https://cdn.rive.app/animations/vehicles.riv",
        stateMachines: "bumpy",
        autoplay: true,
    });

    const bumpInput = useStateMachineInput(rive, "bumpy", "bump");

    return (
        <RiveComponent
            style={{ height: "1000px" }}
            onClick={() => bumpInput && bumpInput.fire()}
        />
    );
}
```

<NestedInputs />

To set the **Volume** input for the above example:

```tsx
const {rive, RiveComponent} = useRive({...});

useEffect(() => {
  if (rive) {
    rive?.setNumberStateAtPath("volume", 80.0, "Volume Molecule/Volume Component");
  }
}, [rive]);
```

**All options:**
- `setNumberStateAtPath(inputName: string, value: number, path: string)`
- `setBooleanStateAtPath(inputName: string, value: boolean, path: string)`
- `fireStateAtPath(inputName: string, path: string)`
---
## runtimes/react/layouts.mdx

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

<Demos examples={["layouts"]} runtime="react"/>

<FitMode />

<Alignment />

<Bounds />

<ApplyingFitMode />

Use the `Layout` object to configure `Fit` and `Alignment`. See [Fit](#the-fit-mode) and [Alignment](#alignment) for all enum options.

```javascript
import Rive, { Layout, Fit, Alignment } from '@rive-app/react-canvas';

export const Simple = () => (
  <Rive
    src="https://cdn.rive.app/animations/vehicles.riv"
    layout={new Layout({ fit: Fit.Contain, alignment: Alignment.TopCenter })}
  />
);
```

With the `useRive` hook:

```javascript
import { useRive, Layout, Fit, Alignment } from '@rive-app/react-canvas';

export default function Example() {
  const { RiveComponent } = useRive({
    src: 'my-file.riv',
    artboard: 'my-artboard',
    animations: 'my-animation',
    layout: new Layout({
      fit: Fit.Cover,
      alignment: Alignment.TopCenter,
    }),
    autoplay: true,
  });

  return <RiveComponent />;
}
```

<ResponsiveLayouts />

**Steps**

1. Set `fit` to `Fit.Layout` in the `Layout` object - this will automatically scale and resize the artboard to match the canvas size.
2. Pass the `Layout` object to the `layout` prop in `useRive`.
3. Optionally set `layoutScaleFactor` in the `Layout` object for manual control of the artboard's scale factor.
4. The React runtime automatically handles window resizing and device pixel ratio changes.

```jsx
import { useRive, Layout, Fit } from "@rive-app/react-canvas";

export const RiveComponent = () => {
  const { RiveComponent } = useRive({
    src: "your-rive-file.riv",
    stateMachines: "State Machine 1",
    layout: new Layout({
      fit: Fit.Layout,
      // layoutScaleFactor: 2, // Optional: 2x scale of the layout
    }),
    autoplay: true,
  });

  return <RiveComponent />;
};
```
---
## runtimes/react/loading-assets.mdx

---
title: "Loading Assets"
description: "Loading and replacing assets dynamically at runtime"
---

import { YouTube } from "/snippets/youtube.mdx";

import { Demos } from "/snippets/demos.jsx";
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

<Demos examples={["fontsHostedCompressed"]} runtime="react" />


### Examples

- [Specify a font asset to load](https://codesandbox.io/p/sandbox/peaceful-water-2chg77?file=%2Fsrc%2FApp.tsx%3A20%2C38)
- [Localization - Swap a font based on language (TypeScript & i18n)](https://codesandbox.io/p/sandbox/rive-react-i18n-localization-and-font-swapping-kfsqsl?file=%2Fsrc%2FRiveDemo.tsx)
- [Specify an image asset to load](https://codesandbox.io/p/sandbox/rive-out-of-band-images-react-forked-gstq2w?file=%2Fsrc%2FApp.tsx%3A14%2C30)

### Using the Asset Handler API

When instantiating a new Rive instance with the `useRive` hook, add an `assetLoader` callback property to the list of parameters. This callback will be called for every asset the runtime detects from the `.riv` file on load, and will be responsible for either handling the load of an asset at runtime or passing on the responsibility and giving the runtime a chance to load it otherwise.

<Note>
Note that you can only use the `assetLoader` callback with the `useRive` hook, and not the default-exported `<Rive />` component from the React runtime
</Note>

```javascript
assetLoader: (asset: rc.FileAsset, bytes: Uint8Array) => boolean;
```

See the [Web (JS) example](/runtimes/web/loading-assets#using-the-asset-handler-api) for more API details.

<Resources />

---
## runtimes/react/migration-guides.mdx

---
title: 'Migration Guides'
description: 'Migrating between major versions of the Apple runtime'
---

<AccordionGroup>
    <Accordion title={`Migrating from @rive-app/react-webgl to @rive-app/react-webgl2`}>
        We highly recommend migrating to `@rive-app/react-webgl2` for the best rendering quality and performance in most cases. The `@rive-app/react-webgl` package is deprecated and no longer receives updates after `v4.27.3`.

        No changes to the API are necessary, simply update your package installation and import statements to use `@rive-app/react-webgl2`. This change will allow you to take advantage of the improved rendering capabilities of the [Rive renderer](https://rive.app/renderer) while maintaining compatibility with your existing codebase.
    </Accordion>
    <Accordion title="Migrating from 3.x.x to 4.x.x">
        Starting in v4 of our React runtimes, Rive will support Rive Text at runtime, which includes the following packages:

        - React
        - `@rive-app/react-canvas`
        - `@rive-app/react-webgl2`

        ## Major Changes

        <Note>
        No breaking API changes!
        </Note>

        While a new major version has been released for the runtimes without breaking API changes, v4 was released due to a **bundle** **size increase** in the package from the core Web (JS) runtime dependency. See that migration guide [here](/runtimes/react/migration-guides#migrating-from-1-x-x-to-3-x-x).

        In the future, we may introduce a "lite" package without these larger dependencies if you don't need the text feature, but for now, it will remain the default on the main web runtime packages.
    </Accordion>
    <Accordion title="Migrating from 1.x.x to 3.x.x">

        For the most part, if you're using v1.x.x of `rive-react`, you should be able to upgrade to the new dependencies in v3.x.x without many changes.

        <Note>
        **Note**: Migrating from v2.x.x to 3.x.x can be done safely without any changes on your end.
        </Note>

        ## Dependency Change

        Previous to v2.x.x, you could use Rive in React via the `rive-react` package. This package was a wrapper around the `@rive-app/webgl` dependency. In version 2.x.x+, we enable the React runtime to wrap around both the `@rive-app/webgl` and `@rive-app/canvas` dependencies through 2 main new React packages:

        - **(Recommended)** `@rive-app/react-canvas`
        - `@rive-app/react-webgl`

        The `rive-react` package will still be published to regularly along with the above packages, but it has both of the web runtime dependencies set as `dependencies` and may result in a larger bundle. Because of this, we recommend switching from `rive-react` to `@rive-app/react-canvas` or the WebGL variant if you need to use a WebGL backing context.

        **Before:**

        ```bash
        npm i rive-react
        ```

        **After:**

        ```bash
        npm i @rive-app/react-canvas
        ```

        <Note>
        There are no changes regarding the way you import from the React runtime between `rive-react` and `@rive-app/react-canvas `
        </Note>

        ## Prop Spreading

        The React runtime provides a `RiveComponent` whether you use the default export or the `useRive` hook provided. This component should be passed into the JSX to render the canvas out. The DOM encompasses a wrapping div around the canvas that helps to handle the styling and sizing of the canvas. Most props spread on the `RiveComponent` would be spread onto that wrapping `<div>` element. Starting in v2.x.x, certain props will be spread onto the wrapping `<div>` that concern styling (i.e `className` and `style`), but any other props will now be spread onto the `<canvas>` element, so that you can set `role`, `aria-*` attributes, etc.

        **Before:**

        ```javascript
        <RiveComponent className="foo" aria-label="Label" />
        ```

        Would render the (simplified) DOM such as:

        ```javascript
        <div className="foo" aria-label="Label">
        <canvas></canvas>
        </div>
        ```

        **After:**

        ```javascript
        <RiveComponent className="foo" aria-label="Label" />
        ```

        Now yields the following (simplified) DOM:

        ```javascript
        <div className="foo">
        <canvas aria-label="Label"></canvas>
        </div>
        ```
    </Accordion>
    <Accordion title="Migrating from 0.x.x to 1.x.x">
        Before v1.0.0 of `rive-react`, the React runtime wrapped the `@rive-app/canvas` runtime dependency, using the backing `CanvasRenderingContext2D`. In order for the React runtime to support some upcoming advanced drawing features like Mesh Deformations, it needed to use the `@rive-app/webgl` runtime.

        The major version bump to v1.0.0 involves no breaking API changes, but rather internally uses a different backing context with WebGL. If you have issues, please log them to the issues tab of the `rive-react` runtime [here](https://github.com/rive-app/rive-react/issues).
    </Accordion>
</AccordionGroup>
---
## runtimes/react/parameters-and-return-values.mdx

---
title: 'Parameters and Return Values'
description: 'Rive React API.'
---

## Hooks

### useRive

The `useRive` hook is the recommended way to hook into the Rive runtime for full control, especially when using the Rive State Machine. See below for parameters to pass in and the return values.

`useRive(riveParams: UseRiveParameters, opts: UseRiveOptions): RiveState`

- `riveParams` - See below for a set of parameters passed to the `Rive` object at instantiation from the Web runtime. `null` and `undefined` can be passed to conditionally display the .riv file
- `opts` - *(Optional)* See below for a set of options specific to `rive-react`

#### Parameters

**UseRiveParameters**

Most of these parameters come from the underlying web runtime configuration items for the Rive object, with the exception of supplying a `canvas` element. See [Rive Parameters](/runtimes/web/rive-parameters) for all the parameters you can supply in this object.

<Note>
 If you supply an `onLoad` callback in the parameters, you may not have access to the `rive` instance yet. The React runtime uses `onLoad` internally to setState with the `rive` instance, and therefore may not be populated by the time it reaches a consumer-supplied callback. We recommend using a `useEffect` in place of `onLoad` to reliably use the `rive` instance if you are looking for a similar method. In a future version of the web runtime, we may supply the `rive` instance in the parameters of your callback so you can supply an `onLoad` here.
</Note>

**UseRiveOptions**

- `useDevicePixelRatio` - *(optional)* If `true`, the hook will scale the resolution of the animation based on the [devicePixelRatio](https://developer.mozilla.org/en-US/docs/Web/API/Window/devicePixelRatio). Defaults to `true`. NOTE: Requires the `setContainerRef` ref callback to be passed to an element wrapping a canvas element. If you use the `RiveComponent`, then this will happen automatically
- `fitCanvasToArtboardHeight` - *(optional)* If `true`, then the canvas will resize based on the height of the artboard. Defaults to `false`
- `useOffscreenRenderer` - *(optional)* If `true`, the Rive instance will share (or create if one does not exist) an offscreen `WebGL` context. This allows you to display multiple Rive animations on one screen to work around some browser limitations regarding multiple concurrent WebGL contexts. If `false`, each Rive instance will have its own dedicated `WebGL` context and you may need to be cautious of the browser limitations just mentioned. We recommend **not** changing this default prop, so you don't have to manage WebGL contexts. Destroying a React component does not guarantee the browser cleans up the WebGL context that was created when the canvas was mounted. Only relevant when using `@rive-app/react-webgl2`. Defaults to `true`

#### Return Values

**RiveState**

- `canvas` - Canvas element the Rive instance is rendered onto
- `container` - Container element of the canvas that Rive instance is rendered onto
- `setCanvasRef` - Ref callback to be passed to the canvas element
- `setContainerRef` - Ref callback to be passed to the container element of the canvas. This is optional, however, if not used then the hook will not take care of automatically resizing the canvas to its outer container if the window resizes
- `rive` - Newly created Rive instance from the Web runtime
- `RiveComponent` - JSX element to render the Rive instance in the DOM

<Note>
 In most cases, you will just need to grab the `RiveComponent` and `rive` return values from the `useRive` hook. Setting the canvas ref and container ref is only needed if you need to control the canvas/containing element yourself.
</Note>
### useStateMachineInput

The `useStateMachineInput` hook is the recommended way to grab references to Rive State Machine inputs, both for reading input values, and setting (or triggering) them. See below for parameters to pass in and the return value.

`useStateMachineInput(rive: Rive | null, stateMachineName?: string, inputName?: string, initialValue?: number | boolean): StateMachineInput | null`

<Note>
 The return value which is the state machine input may not be immediately available due to the need for the `rive` instance to resolve first. You may want to use a `useEffect` to watch for when the `rive` instance and the return value of the `useStateMachineInput` hook has value
</Note>

#### parameters

- `rive` - The 1st parameter is the Rive object instantiated - this can be retrieved via the `useRive` hook
- `stateMachineName?` - *(optional)* Name of the state machine to grab the input from
- `inputName?` - *(optional)* Name of a single state machine input to grab a reference to
- `initialValue?` - *(optional)* Initial value to set on the input

#### Return Values

This hook returns a default instance of a `StateMachineInput`.

**StateMachineInput**

- `name` (get) - Access the name of the input
- `value` (get and set) - Access the value of the input, and set the value of the input via this property
- `fire()` - Fires off a trigger input

See the [Inputs page](/runtimes/react/inputs) to see more usage of this hook.

### useResizeCanvas

The `useResizeCanvas` hook is an optional utility hook to resize the `<canvas>` element to its parent container element's size, while also resetting the appropriate surface area size of the canvas as well. This is useful when you don't want to use the `useRive` hook to render your Rive, and are perhaps using the web JS runtime in your React apps, but still want the ability to scale the `<canvas>` to its parent appropriately.

<Note>
 This hook is already internally used in the Rive React runtime, so if you use the `useRive` hook or the default exported `<RiveComponent />` to render your Rive, you don't need to consume this hook yourself.
</Note>

`useResizeCanvas(resizeProps: UseResizeCanvasProps): void`

- `resizeProps` - See below for a set of properties to set onto this object parameter

#### Parameters

**UseResizeCanvasProps**

- `riveLoaded: boolean` - If `true`, the Rive instance has been created and the Rive file have been parsed. This ensures the hook does not prematurely scale the `<canvas>` element. Defaults to `false`
- `canvasRef: MutableRefObject<HTMLCanvasElement | null>` - React `Ref` for the `<canvas>` element where Rive will be rendering onto
- `containerRef: MutableRefObject<HTMLElement | null>` - React `Ref` for the canvas's parent container element
- `onCanvasHasResized?: () => void` (Optional) Callback to be invoked after the canvas has been resized due to a resize of its parent container. This is where you would want to reset the layout dimensions for the Rive renderer to dictate the new min/max bounds of the canvas.
  - Using the high-level JS runtime, this might be a simple call to `rive.resizeToCanvas()`
  - Using the low-level JS runtime, this might be invoking the renderer's `.align()` method, with the Layout and min/max X/Y values of the canvas.
- `options?: Partial` - (Optional) Options passed to the useRive hook (see `UseRiveOptions` further up the document)
- `artboardBounds?: Bounds` - (Optional) AABB bounds of the Artboard; you only need to supply this if `options.fitCanvasToArtboardHeight` is set to `true`.

### useRiveFile

The `useRiveFile` hook is designed for initializing and managing a `RiveFile` instance within a component. It sets up a `RiveFile` based on provided source parameters (URL or ArrayBuffer) and ensures proper cleanup to avoid memory leaks when the component unmounts or inputs change.

The main benefit of this hook is that it allows you to create a `RiveFile` instance that you can reuse across components without needing to fetch it again from the `src` URL or reload it from the `buffer`. This improves performance by eliminating redundant network requests and loading times, especially when creating multiple Rive instances from the same source. Unlike passing the `buffer` and `src` parameters to the `useRive` hook directly—which still requires parsing under the hood to create the `RiveFile` object—this hook returns an already parsed `RiveFile` object, including any loaded assets.

`useRiveFile(params: UseRiveFileParameters): RiveFileState`

#### Parameters

**UseRiveFileParameters**

- `src?` - *(optional)* There are two optional ways to use `src`: either via URL to the `.riv` file, or a path to the public `.riv` asset to use. One of `src` or `buffer` must be provided.
  - URL - If you are hosting your `.riv` on some publicly accessible bucket/CDN (i.e. AWS, GCS, etc.), you can pass in the URL here.
    - Alternatively, with ES6, you may import the `.riv` file as a data URI. Depending on your bundle loader, you may need to use a plugin (i.e `url-loader` for Webpack) to properly parse and load in `.riv` files as a data URI string. See [this project](https://github.com/zplata/rive-nextjs/blob/main/next.config.js#L8) as a basic example on how to set this up
  - Path to public asset - This is a string path to the`.riv` public asset if bundled in your application. Note that this is **not** a relative path to the asset from wherever the current JS file is in. Treat the `.riv` as any other asset bundled in your application, such as an image or font. If your JS is compiled and run at the root of your web application, you must specify the path from the root to the location of the asset. For example, if your asset is in `/public/foo.riv`, and your JS is run from the root at `/`, you would specify: `src: '/public/foo.riv'` in this property.
- `buffer?` - *(optional)* ArrayBuffer containing the raw bytes from a .riv file. One of `src` or `buffer` must be provided.
- `enableRiveAssetCDN?` - *(optional)* Allow the runtime to automatically load assets hosted in Rive's CDN. Enabled by default.

**Return Values**

**RiveFileState**

- `riveFile` - The `RiveFile` instance. This is `null` until the file is loaded.
- `status` - The status of the file loading process, can be `idle`, `loading`, `failed`, or `success`.

## Components

### `<RiveComponent />`

The `RiveComponent` default export and the `RiveComponent` returned from the `useRive` hook are both to be rendered in the JSX of a component. As noted previously, all attributes and event handlers that can be passed to a `canvas` element can also be passed to the `Rive` component and used in the same manner.

One thing to note is that `style`/`className` props set on the component will be passed onto the containing `<div>` element, rather than the underlying `<canvas>` itself. The reason for this is that the containing `<div>` element handles resizing and layout for you, and thus, all styles should be passed onto this element.

The `<canvas>` element will still receive any other props passed into the component, such as `aria-*` attributes, `role`'s, etc. You can also set children content inside the component for fallback scenarios where the `<canvas>` element cannot be shown.
---
## runtimes/react/playing-audio.mdx

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

For more information, see [Loading Assets](/runtimes/react/loading-assets).

---
## runtimes/react/preloading-wasm.mdx

---
title: 'Preloading WASM'
description: ''
---

import Overview from '/snippets/runtimes/preloading-wasm/overview.mdx'
import Thanks from '/snippets/runtimes/preloading-wasm/thanks.mdx'

<Overview />

If you're using `@rive-app/react-canvas` or `@rive-app/react-webgl2`, import the WASM resource into your app, as well as the `RuntimeLoader` API:

```javascript
import riveWASMResource from '@rive-app/canvas/rive.wasm';
import { useRive, RuntimeLoader } from '@rive-app/react-canvas';

RuntimeLoader.setWasmUrl(riveWASMResource);

const MyComponent = () => {
  const { rive, RiveComponent } = useRive({
    src: 'foo.riv',
    ...
  });
};
```

The `RuntimeLoader` is a singleton that manages loading in the WASM file behind the scenes when loading in the `Rive` instance. By calling the `setWasmUrl` API, you can load in WASM for the Rive runtime with the data URI from the direct import of the WASM file. Run this API on any page that has a Rive animation to load.

<Note>
 You may need to add configuration into your build tool to import WASM files. See the [original blog post](https://dev.to/alex_barashkov/optimization-techniques-for-rive-animations-in-react-apps-1a8p) that inspired us to add these to docs for some guidance here
</Note>

You can additionally preload the WASM module if you set up your build tools to load Web Assembly for your application in relevant pages where you create Rive instances to instance your Rive animations quickly.

For example, with Next.js, you may attach the following to your main page layout:

```javascript
import { Html, Head } from "next/document";
import riveWASMResource from '@rive-app/canvas/rive.wasm';

export default function Document() {
  return (
    <Html>
      <Head>
        <link rel="preload" href={riveWASMResource} as="fetch" crossOrigin="anonymous" />
      </Head>
    </Html>
  );
}
```

You may need to install `@rive-app/canvas` at the version tied down with the correlated React version on `@rive-app/react-canvas` or you may notice issues at runtime. For example, `@rive-app/react-canvas@3.0.33` ties down the JS dependency at `@rive-app/canvas@1.0.95`; therefore you may want to install that specific version of the JS runtime to ensure compatibility.

<Thanks />

---
## runtimes/react/react.mdx

---
title: 'React'
description: 'React runtime for Rive.'
---

import NoteOnFeatureSupport from "/snippets/runtimes/rendering-feature-support.mdx"
import { Demos } from '/snippets/demos.jsx'

<NoteOnFeatureSupport/>

<Demos examples={['quickStartReact']} />

## Overview

This guide documents how to get started using the React runtime library. Rive runtime libraries are open-source. The source is available in its [GitHub repository](https://github.com/rive-app/rive-react).

This library contains a React component, as well as custom hooks to help integrate Rive into your web application (types included). Under the hood, this runtime is a React-friendly wrapper around the `@rive-app/webgl2` runtime, exposing types, and Rive instance functionality.

## Getting Started

Follow the steps below for a quick start on integrating Rive into your React app.

<Steps>
  <Step title="Install the dependency">
    The Rive React runtime allows for two main options based on which backing renderer you need.

    - **(Recommended)** `@rive-app/react-webgl2` - Wraps the `@rive-app/webgl2` dependency, which uses the Rive Renderer.
    - `@rive-app/react-canvas` - Wraps the `@rive-app/canvas` dependency. This does not utilize the Rive Renderer and doesn't support advanced features, like Vector Feathering.
    - `@rive-app/react-canvas-lite` - Similar to `@rive-app/react-canvas`, but [smaller](/runtimes/web/canvas-vs-webgl). This is not recommended if the Rive file uses [Rive Text](/editor/text/) or other advanced features.

    <Note>
    To take advantage of the full performance benefits of the Rive Renderer with `react-webgl2`, [enable the draft](https://www.wikihow.tech/Enable-WebGL-Draft-Extensions-in-Google-Chrome) `WEBGL_shader_pixel_local_storage` Chrome Extension (by adding WebGL Draft Extensions).

    If the draft extension is disabled on a user's device, Rive will fall back to an MSAA solution (also with WebGL2) on browsers without the extension support.

    Current work is underway with major browsers to support this extension by default in consumer's browsers.
    </Note>

    ```bash
    npm i --save @rive-app/react-webgl2
    ```
  </Step>
  <Step title="Render the Rive component">
    Rive React provides a basic component as its default import for displaying simple animations with a few props you can set such as artboard and layout. Include the code below in your React project to test out an example Rive animation.

    ```javascript
    import Rive from '@rive-app/react-webgl2';

    export const Simple = () => (
      <Rive
        src="https://cdn.rive.app/animations/vehicles.riv"
        stateMachines="bumpy"
      />
    );
    ```

    See [Parameters and Return Values](/runtimes/react/parameters-and-return-values) for more on the parameters and return values of the `<Rive />` component.
  </Step>
  <Step title="Using the useRive hook">
    In many cases, you may not only need the React component to render your animation but also the `rive` object instance that controls it as well. The Rive object instance allows you to tap into APIs for:

    - Setting Rive Text values dynamically
    - Subscribing to Rive Events with your own callbacks
    - Controlling animation playback (i.e. pause and play)
    - ... and [much more](https://github.com/rive-app/rive-wasm)

    The `useRive` hook returns both this `rive` instance, as well as the React component that mounts the underlying `<canvas>` element that Rive will draw onto.

    ```javascript
    import { useRive } from '@rive-app/react-webgl2';

    export default function Simple() {
      const { rive, RiveComponent } = useRive({
        src: 'https://cdn.rive.app/animations/vehicles.riv',
        stateMachines: "bumpy",
        autoplay: false,
      });

      return (
        <RiveComponent
          onMouseEnter={() => rive && rive.play()}
          onMouseLeave={() => rive && rive.pause()}
        />
      );
    }
    ```

    <Note>
    **Note:** Rive will not instantiate until the `<RiveCopmonent />` is rendered out, as the underlying `<canvas>` element needs to be present in the DOM.
    </Note>

    Also, keep in mind that the canvas size depends on the container it's placed within. Initially, this is 0x0. Either pass a `className` to `RiveComponent` or wrap `RiveComponent` with an appropriately sized container.

    See [here](/runtimes/react/parameters-and-return-values) for more on the parameters and return values of `useRive`.

    Additionally, explore subsequent runtime pages to learn how to control animation playback, state machines, and more.
  </Step>
</Steps>

## Rendering Considerations with useRive

At this time, we highly recommend isolating your usage of `useRive` to its own wrapper component if you plan on conditionally rendering the `<RiveComponent />` returned from the `useRive` hook. This is due to Rive being instanced when the component is mounted and the rendering context associated with a specific underlying `<canvas>` element. When React tries to unmount/re-render, you may end up with the animation restarting or not displaying when a new `<canvas>` is mounted.

By isolating `useRive` to its own wrapper component, Rive will have a chance to properly clean up, and restart the animation with a new canvas. In a parent component, you can then conditionally render the wrapper component based on any state or prop-based logic.

Check out [this example CodeSandbox](https://codesandbox.io/p/sandbox/rive-react-swapping-skins-with-solos-ctcnlx?file=%2Fsrc%2FApp.tsx) to see this pattern in use.

## Resources

**GitHub**: [https://github.com/rive-app/rive-react](https://github.com/rive-app/rive-react)

**Types**: [https://github.com/rive-app/rive-react/blob/main/src/types.ts](https://github.com/rive-app/rive-react/blob/main/src/types.ts)

**Examples**
- Simple skinning example: [https://codesandbox.io/p/sandbox/rive-react-swapping-skins-with-solos-ctcnlx](https://codesandbox.io/p/sandbox/rive-react-swapping-skins-with-solos-ctcnlx?file=%2Fsrc%2FApp.tsx)
- Storybook demo: [https://rive-app.github.io/rive-react/](https://rive-app.github.io/rive-react/)
- Animated Login Form:
  - Demo: [https://rive-app.github.io/rive-use-cases/?path=/story/example-loginformcomponent--primary](https://rive-app.github.io/rive-use-cases/?path=/story/example-loginformcomponent--primary)

---
## runtimes/react/rendering-to-a-bitmap.mdx

---
title: 'Rendering to a Bitmap'
description: 'Render screenshots and video at runtime.'
---

import Overview from "/snippets/runtimes/rendering-to-bitmap/overview.mdx"

<Overview />

<Note>
  For rendering to a bitmap from the Rive Editor, see [Exporting for Video or Static Design](/editor/exporting/exporting-for-video-and-static-design).
</Note>

Rendering to a bitmap is not supported directly in the React runtime. For offline or server-side rendering, you can use external tools like [Revideo](https://github.com/redotvideo/examples/tree/main/rive-explanation-video) and [Remotion](https://www.remotion.dev/docs/rive/), both of which support Rive.
---
## runtimes/react/rive-events.mdx

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

- [Star rating example](https://codesandbox.io/p/sandbox/rive-events-react-forked-ct9k2z?file=%2Fsrc%2FApp.js%3A6%2C44)

### Adding an Event Listener

Similar to the `addEventListener()` / `removeEventListener()` API for DOM elements, you'll use the Rive instance's `on()` / `off()` API to subscribe to Rive events from the `rive` object returned from the `useRive` hook. Simply supply the RiveEvent enum and a callback for the runtime to call at the appropriate moment any Rive event gets detected.

<Note>
    **Note:** You must use the `useRive()` hook to subscribe to Rive events
</Note>
#### Example Usage

```javascript
import { useRive, EventType, RiveEventType } from '@rive-app/canvas';
import { useCallback, useEffect } from 'react';

const MyTextComponent = () => {
const {rive, RiveComponent} = useRive({
    src: "/static-assets/star-rating.riv",
    artboard: "my-artboard-name",
    autoplay: true,
    // automaticallyHandleEvents: true, // Automatically handle OpenUrl events
    stateMachines: "State Machine 1",
});

const onRiveEventReceived = (riveEvent) => {
    const eventData = riveEvent.data;
    const eventProperties = eventData.properties;
    if (eventData.type === RiveEventType.General) {
    console.log("Event name", eventData.name);
    // Added relevant metadata from the event
    console.log("Rating", eventProperties.rating);
    console.log("Message", eventProperties.message);
    } else if (eventData.type === RiveEventType.OpenUrl) {
    console.log("Event name", eventData.name);
    // Handle OpenUrl event manually
    window.location.href = eventData.url;
    }
};

// Wait until the rive object is instantiated before adding the Rive
// event listener
useEffect(() => {
    if (rive) {
    rive.on(EventType.RiveEvent, onRiveEventReceived);
    }
}, [rive]);

return (
    <RiveComponent />
);
};
```

<AdditionalResources />

---
## runtimes/react/state-machines.mdx

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

#### Autoplay the State Machine

To auto-play a state machine by default, simply set `autoplay` to `true`.
```js
export default function Simple() {
  const { RiveComponent } = useRive({
    src: 'https://cdn.rive.app/animations/vehicles.riv',
    stateMachines: "bumpy",
    autoplay: true,
  });

  return <RiveComponent />;
}
```

#### Controlling State Machine Playback

You can manually play and pause the state machine using the `play`, `pause`, and `stop` methods.

  ```js
  export default function Simple() {
    const { rive, RiveComponent } = useRive({
      src: "https://cdn.rive.app/animations/vehicles.riv",
      stateMachines: "bumpy",
      autoplay: true,
    });

    const handlePlay = useCallback(() => {
      rive?.play();
    }, [rive]);

    const handlePause = useCallback(() => {
      rive?.pause();
    }, [rive]);

    const handleStop = useCallback(() => {
      rive?.stop();
    }, [rive]);

    return (
      <div>
        <RiveComponent />
        <div style={{ marginTop: 12 }}>
          <button onClick={handlePlay}>Play</button>
          <button onClick={handlePause}>Pause</button>
          <button onClick={handleStop}>Stop</button>
        </div>
      </div>
    );
  }

```
---
## runtimes/react/text.mdx

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

- [Updating Text at Runtime - Localization example](https://codesandbox.io/p/sandbox/rive-text-react-38lt4k)

#### Reading Text

To read a given text run text value at any given time, reference the `.getTextRunValue()` API on the `rive` instance returned from `useRive`:

```javascript
public getTextRunValue(textRunName: string): string | undefined
```

Supply the text run name, and you'll have the Rive text run value returned, or `undefined` if the text run could not be queried.

#### Setting Text

To set a given text run value at any given time, reference the `.setTextRunValue()` API on the `rive` instance returned from `useRive`:

```javascript
public setTextRunValue(textRunName: string, textRunValue: string): void
```

Supply the text run name and a second parameter, `textValue`, with a String value that you want to set the new text value for if the text run can be successfully queried on the active artboard.

#### Example Usage

```javascript
import { useRive } from '@rive-app/canvas';

const MyTextComponent = () => {
const {rive, RiveComponent} = useRive({
    src: "my-rive-file.riv",
    artboard: "New Artboard",
    stateMachines: "State Machine 1",
    autoplay: true,
});

// Cannot query for the text run immediately, you have to wait until `rive`
// has value and has instantiated before querying or setting text run values
useEffect(() => {
    if (rive) {
    console.log("Rive text was initially: ", rive.getTextRunValue("MyRun"));
    rive.setTextRunValue("MyRun", "New Text!!");
    console.log("Rive text is now: ", rive.getTextRunValue("MyRun"));
    }
}, [rive]);

return (
    <RiveComponent />
);
};
```

<NestedArtboard />

## Examples

- [Updating Text at Runtime - Localization example](https://codesandbox.io/p/sandbox/rive-text-react-38lt4k)

#### Reading Text

To read a given text run text value at any given time, reference the `.getTextRunValue()` API on the `rive` instance returned from `useRive`:

```javascript
public getTextRunValue(textRunName: string): string | undefined
```

Supply the text run name, and you'll have the Rive text run value returned, or `undefined` if the text run could not be queried.

#### Setting Text

To set a given text run value at any given time, reference the `.setTextRunValue()` API on the `rive` instance returned from `useRive`:

```javascript
public setTextRunValue(textRunName: string, textRunValue: string): void
```

Supply the text run name and a second parameter, `textValue`, with a String value that you want to set the new text value for if the text run can be successfully queried on the active artboard.

#### Example Usage

```javascript
import { useRive } from '@rive-app/canvas';

const MyTextComponent = () => {
const {rive, RiveComponent} = useRive({
    src: "my-rive-file.riv",
    artboard: "New Artboard",
    stateMachines: "State Machine 1",
    autoplay: true,
});

// Cannot query for the text run immediately, you have to wait until `rive`
// has value and has instantiated before querying or setting text run values
useEffect(() => {
    if (rive) {
    console.log("Rive text was initially: ", rive.getTextRunValue("MyRun"));
    rive.setTextRunValue("MyRun", "New Text!!");
    console.log("Rive text is now: ", rive.getTextRunValue("MyRun"));
    }
}, [rive]);

return (
    <RiveComponent />
);
};
```

<SemanticsForAccessibility />

<Resources />

## rive-react package README

![Build Status](https://github.com/rive-app/rive-react/actions/workflows/tests.yml/badge.svg)
![Discord badge](https://img.shields.io/discord/532365473602600965)
![Twitter handle](https://img.shields.io/twitter/follow/rive_app.svg?style=social&label=Follow)

# Rive React

![Rive hero image](https://cdn.rive.app/rive_logo_dark_bg.png)

[Rive](https://rive.app) combines an interactive design tool, a new stateful graphics format, a lightweight multi-platform runtime, and a blazing-fast vector renderer. This end-to-end pipeline guarantees that what you build in the Rive Editor is exactly what ships in your apps, games, and websites.

This library is a wrapper around the [JS/Wasm runtime](https://github.com/rive-app/rive-wasm), giving full control over the JS/Wasm runtime while providing components and hooks for React applications.

For more information, check out the following resources:

- [Homepage](https://rive.app/)
- [General Docs](https://rive.app/docs/)
- [React Docs](https://rive.app/docs/runtimes/react/react)
- [Rive Community / Support](https://community.rive.app/c/support/)

## Table of contents

- :star: [Rive Overview](#rive-overview)
- 🚀 [Getting Started & API docs](#getting-started)
- :mag: [Supported Versions](#supported-versions)
- :books: [Examples](#examples)
- :runner: [Migration Guides](#migration-guides)
- 👨‍💻 [Contributing](#contributing)
- :question: [Issues](#issues)

## Rive overview

[Rive](https://rive.app) is a real-time interactive design and animation tool that helps teams create and run interactive animations anywhere. Designers and developers use our collaborative editor to create motion graphics that respond to different states and user inputs. Our lightweight open-source runtime libraries allow them to load their animations into apps, games, and websites.

:house_with_garden: [Homepage](https://rive.app/)

:blue_book: [General help docs](https://rive.app/community/doc/)

🛠 [Rive Forums](https://rive.app/community/forums/home)

## Getting started

Follow along with the link below for a quick start in getting Rive React integrated into your React apps.

- [Getting Started with Rive in React](https://rive.app/community/doc/react/docRfaSQ0eaE)
- [API documentation](https://rive.app/community/doc/parameters-and-return-values/docJlDMNulDh)

For more information, see the Runtime sections of the Rive help documentation:

- [Animation Playback](https://rive.app/community/doc/animation-playback/docDKKxsr7ko)
- [Layout](https://rive.app/community/doc/layout/docBl81zd1GB)
- [State Machines](https://rive.app/community/doc/state-machines/docxeznG7iiK)
- [Rive Text](https://rive.app/community/doc/text/docn2E6y1lXo)
- [Rive Events](https://rive.app/community/doc/rive-events/docbOnaeffgr)
- [Loading Assets](https://rive.app/community/doc/loading-assets/doct4wVHGPgC)

## Supported versions

This library supports React versions `^16.8.0` through `^19.0.0`.

## Examples

Check out our Storybook instance that shows how to use the library in small examples, along with code snippets! This includes examples using the basic component, as well as the convenient hooks exported to take advantage of state machines.

- [Mouse tracking](https://codesandbox.io/s/rive-mouse-track-test-t0y965?file=/src/App.js)
- [Accessibility concerns](https://rive.app/blog/accesible-web-animations-aria-live-regions)

### Awesome Rive

For even more examples and resources on using Rive at runtime or in other tools, checkout the [awesome-rive](https://github.com/rive-app/awesome-rive) repo.

## Migration guides

Using an older version of the runtime and need to learn how to upgrade to the latest version? Check out the migration guides below in our help center that help guide you through version bumps; breaking changes and all!

[Migration guides](https://rive.app/community/doc/migrating-from-v3-to-v4/dociIPXVHKFF)

## Contributing

We love contributions! Check out our [contributing docs](./CONTRIBUTING.md) to get more details into how to run this project, the examples, and more all locally.

## Issues

Have an issue with using the runtime, or want to suggest a feature/API to help make your development life better? Log an issue in our [issues](https://github.com/rive-app/rive-react/issues) tab! You can also browse older issues and discussion threads there to see solutions that may have worked for common problems.

## rive-react examples (file listing)

/home/hoon/rive-research/repos/rive-react/examples/package.json
/home/hoon/rive-research/repos/rive-react/examples/.storybook/main.ts
/home/hoon/rive-research/repos/rive-react/examples/.storybook/preview.ts
/home/hoon/rive-research/repos/rive-react/examples/src/components/Simple.tsx
/home/hoon/rive-research/repos/rive-react/examples/src/components/FallbackFonts.stories.ts
/home/hoon/rive-research/repos/rive-react/examples/src/components/DataBinding.tsx
/home/hoon/rive-research/repos/rive-react/examples/src/components/Simple.stories.ts
/home/hoon/rive-research/repos/rive-react/examples/src/components/Scripting.stories.ts
/home/hoon/rive-research/repos/rive-react/examples/src/components/ResponsiveLayout.stories.ts
/home/hoon/rive-research/repos/rive-react/examples/src/components/DataBindingTests.stories.tsx
/home/hoon/rive-research/repos/rive-react/examples/src/components/DataBinding.stories.ts
/home/hoon/rive-research/repos/rive-react/examples/src/components/Events.stories.ts
/home/hoon/rive-research/repos/rive-react/examples/src/components/Scripting.tsx
/home/hoon/rive-research/repos/rive-react/examples/src/components/Http.stories.ts
/home/hoon/rive-research/repos/rive-react/examples/src/components/DataBindingTests.tsx
/home/hoon/rive-research/repos/rive-react/examples/src/components/Events.tsx
/home/hoon/rive-research/repos/rive-react/examples/src/components/Http.tsx
/home/hoon/rive-research/repos/rive-react/examples/src/components/FallbackFonts.tsx
/home/hoon/rive-research/repos/rive-react/examples/src/components/ResponsiveLayout.tsx
