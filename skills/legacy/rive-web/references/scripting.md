# Rive Scripting (Luau-based) — Aggregated Reference

Source: rive-app/rive-docs/scripting

Rive Scripting lets you embed Luau scripts inside .riv files. From a *web* perspective
this matters when you must interpret what a .riv does or extend it programmatically.

## Core scripting docs

---
## scripting/getting-started.mdx

---
title: "Getting Started"
description: "Code, animation, and interaction all in one Editor."
---

import { Demos } from '/snippets/demos.jsx'
import { YouTube } from '/snippets/youtube.mdx'

Scripting lets you iterate on code, design, and animation in one collaborative editor.

## Quick Start

This video introduces the basics of writing and using scripts in Rive. You’ll learn how to create different types of scripts and how they connect to data bindings and artboards, and how you can create scripts with the [AI Agent](/editor/ai-agent).

<YouTube id="M6kGkR-7JTE" />

## Fundamentals

- [Why Luau](https://rive.app/blog/why-scripting-runs-on-luau?utm_source=docs&utm_medium=content) - Why Scripting runs on Luau
- [Creating Scripts](/scripting/creating-scripts) - Creating a new script
- [Protocols](/scripting/protocols) - The type of scripts you can create
- [Inputs](/scripting/script-inputs) - Connecting scripts to inputs and data
- [Debugging](/scripting/debugging/debug-panel) - Debugging your scripts
- [AI Agent](/editor/ai-agent) - Using AI to create and modify scripts

---
## scripting/configuration.mdx

---
title: "Configuration"
description: "Customize the Rive code editor with themes, typography, and execution settings."
---

You can customize the appearance and behavior of the Rive code editor by editing its configuration file. Your settings will be reflected in all code editor views for your user account. 

## Opening the Configuration

Press **⌘ + ,** on macOS or **Ctrl + ,** on Windows to open the editor configuration.

## Editing the Config

The configuration file returns a Lua table. Start with the default configuration and override any settings you want to change.

### Example Configuration

```lua
-- Import the default configuration
local config = require('config/default')

config.theme = require('theme/shades-of-purple-super-dark')
config.code.fontSize = 14
config.code.lineHeight = 20
config.code.selectionCornerRadius = 5
config.code.executionTimeoutMs = 2000

return config
```

## Available Options

| Option | Description |
|-------|-------------|
| `config.theme` | The editor theme. |
| `config.code.fontSize` | Font size used in the code editor. |
| `config.code.lineHeight` | Height of each line of code. |
| `config.code.selectionCornerRadius` | Corner radius of the selection highlight. |
| `config.code.executionTimeoutMs` | Maximum time a script can run before being stopped. |

<Tip>
  To browse available themes, type:

  `config.theme = require('theme/')`

  The editor will show the full list through autocomplete.

  ![autocomplete editor themes](/images/scripting/config-theme.png)
</Tip>

---
## scripting/creating-scripts.mdx

---
title: "Creating Scripts"
description: ""
---

There are two ways to create a new script, from the Assets Panel and with the Scripting tool.

### Creating a Script from the Assets Panel

1. In the Assets Panel, click the `+` button.
2. Choose **Script** and select the [Protocol](/scripting/protocols/overview) (type of script) you'd like to create.

![Create Script from Assets Panel](/images/scripting/assets-panel-create-script.png)

### Creating a Script with the Scripts Tool

1. Select the dropdown icon next to the Script button in the Toolbar
2. Select the [Protocol](/scripting/protocols/overview) (type of script) you'd like to create.

![Create Script from Assets Panel](/images/scripting/script-tool-create-script.png)

New scripts are saved as Assets and can be found in the Assets Panel.

<Tip>
Use **PascalCase** for script names and update the script’s type name accordingly.

Example: If the script is named `MyConverter`, the main type should also be named `MyConverter`.
</Tip>

## Adding Scripts to Your Scene

To run [Node](/scripting/protocols/node-scripts) and [Layout](/scripting/protocols/layout-scripts) scripts, they need to be added to the scene.

1. Right-click the artboard you'd like to add your script to and select your script from the menu
2. Position the script object, keeping in mind that the script's position will determine where it's rendered
3. Select the group to set inputs (See [Script Inputs](/scripting/script-inputs))

![Create Script from Assets Panel](/images/scripting/add-script-to-artboard.gif)

<Tip>
**Troubleshooting: If you don't see your script in the list:**

1. Make sure your script is in the Assets Panel.
2. Check the [Problems Panel](/scripting/debugging/debug-panel#problems) for issues.
3. Make sure your script returns a function that returns a table with at least an `init` and `draw` function.
</Tip>

---
## scripting/script-inputs.mdx

---
title: "Script Inputs"
sidebarTitle: "Script Inputs"
description: ""
---

import { Demos } from '/snippets/demos.jsx'

Scripted Inputs are the bridge between your scripts and the Rive editor, allowing you to customize and control script behavior through custom input fields.

By defining inputs in your scripts, you expose configurable properties — like numbers, colors, booleans, and artboard components — that appear directly in the Rive interface. This means you can write the logic once in a script, and then experiment freely with values, animate properties over time, bind data from external sources, and reuse the same script across multiple instances with different configurations. Inputs transform static scripts into flexible, designer-friendly tools that enable true collaboration and rapid iteration.

## Defining Inputs

To make new script inputs, add them to the type and set the defaults in the script's return function.

```lua
-- Define the script's data and inputs.
-- These properties will be available in `self`
type MyNode = {
  myNumber: Input<number>,
  myColor: Input<Color>,
  -- This input expects a View Model named Points
  myViewModel: Input<Data.Points>,
  -- This input expects an Artboard with a View Model named Points
  myArtboard: Input<Artboard<Data.Points>>,
  -- This will be accessible via self, but not in the inputs panel
  myString: string,
}

function init(self: MyNode): boolean
  print("myString", self.myString)
  print("myNumber", self.myNumber)
  print("myColor", self.myColor)
  print("myViewModel value", self.myViewModel.someString.value)
  print("myViewModel value", self.myArtboard.data.someEnum.value)

  return true
end

return function(): Node<MyNode>
  return {
    init = init,
    draw = draw,
    myString = "Rive for president!"
    -- Sets default value when creating a new instance of the script
    -- This will be overridden by a value set in the script's inputs
    myNumber = 0,
    myColor = Color.rgba(255, 255, 0, 255), -- 0xFFFFFF00

    -- Use late() to mark this input as assigned at runtime
    myViewModel = late(),
    myArtboard = late()
  }
end

```

<Tip>
  Using inputs, instances of Artboards can be added to your scene at runtime. See [Instantiating Components](/scripting/protocols/node-scripts#instanting-components).
</Tip>

## Setting Input Values

To access the input properties in the right sidebar of the editor, select your [Node](/scripting/protocols/node-scripts) or [Layout script](/scripting/protocols/layout-scripts) in the Hierarchy Panel or the [Converter](/scripting/protocols/converter-scripts) in the Data Panel.

![Node script input](/images/scripting/script-input.png)

<Demos
  examples={[
    "scriptingDrawingShapes"
  ]}
/>

## Data Binding Inputs

You can use [Data Binding](/editor/data-binding/overview) to control input values at runtime.

<Note>
  Inputs can control scripts, but scripts can't change the value of inputs.

  If you need to control a view model property from your script, access the [view models through context](/scripting/data-binding#context) or [View Model Inputs](#view-model-inputs).
</Note>

To data bind an input, right-click the input field in right sidebar, choose Data Bind, and select a
property.

![Data bind a converter input](/images/scripting/converter-script-input-data-binding.png)

## Listening for Changes to Inputs

The `update` function fires every time any input changes.

```lua
function update(self: MyNode)
  print('An update changed')
end
```

You can also listen for changes to specific properties:

```lua
function handleMyStringChanged()
  print('myString changed!')
end

function handleMyNumberChanged(myNumber: number)
  print('myNumber changed!', myNumber)
end

function init(self: MyNode): boolean
  -- handleMyStringChanged fires when self.myString changes
  local myString = self.myString
  myString:addListener(handleMyStringChanged)

  -- Pass a parameter to the handleMyStringChanged callback
  local myNumber = self.myNumber
  myNumber:addListener(myNumber.value, handleMyNumberChanged)

  return true
end
```


## View Model Inputs

View Model Inputs let your script read from and write to View Model properties. These properties can control any element in your Rive scene via (See [Data Binding](/editor/data-binding/overview)).

<Note>
  The easiest way to access view models in your scripts is [through context](/scripting/data-binding#context).
</Note>

### Setting Up Your View Model

**In this example:**

- The `Main` view model has a property named `character`.
- The `character` property is itself a `Character` view model.
- The `Character` view model contains two number properties (x and y) that you want to control from your script.

![Nested](/images/scripting/nested-view-model.png)

### Defining a View Model Input

Inside your script, declare a new input whose type matches the nested view model you want to reference (`Data.` + the name of your nested view model).

In this case, the Character view model type becomes `Data.Character`.

```lua
type MyNode = {
  -- This input expects a view model instance of type Character
  character: Input<Data.Character>
}

return function(): Node<MyNode>
  return {
    init = init,
    advance = advance,
    draw = draw,
    -- Initialize with `late()` so the value
    -- can be provided by the editor at runtime.
    character = late(),
  }
end
```

### Connecting the Input in the Editor

1. Select your script in the Scene panel (or the converter if you're using a [Converter](/scripting/protocols/converter-scripts) script)
2. In the right sidebar, look for the Property Group section
3. You’ll see a dropdown for your character input
4. Select your nested `character` property from the Main view model

![Nested](/images/scripting/select-vm-input.png)

### Reading and Writing View Model Properties

Once connected, you can access the nested view model directly from your script:

```lua
function moveCharacter(self: MyNode)
  print('Current x: ', self.character.x.value)
  self.character.x.value = 10
end
```

Because character is a view model instance, you can access all of its public properties:

```lua
self.character.<propertyName>.value
```



---
## scripting/data-binding.mdx

---
title: "Data Binding"
description: ""
---

Scripting allows you to read, modify, and subscribe to changes in View Model properties,
as well as create new View Model instances at runtime.

<Tip>
For a conceptual overview of View Models and how they drive your graphic,
see [View Models & Data Binding](/editor/data-binding/overview).
</Tip>

## View Models

There are three ways that a script can gain access to a View Model and its properties:
- Accessing View Models through [Context](#context)
- Data binding a [View Model as an input](#view-models-as-inputs)
- Data [binding view model properties to inputs](#binding-inputs)

### Context

The `init` lifecycle function includes a `context` parameter that gives you access
to your view models. This allows you to read values (strings, enums, lists, etc.), set values,
fire triggers, listen for triggers, and subscribe to value changes.

<Note>
  In addition to view models, [Context](/scripting/api-reference/interfaces/context) gives you access to named assets and update scheduling.
</Note>

```lua {5, 8, 11, 12}
type MyNode = {}

function init(self: MyNode, context: Context): boolean
  -- Get the view model from the node's immediate context.
  local vmi = context:viewModel()

  -- Get the root view model
  local rootVmi = context:rootViewModel()

  -- Get the view model from the parent node.
  local parentDC = dc:parent()
  local parentVmi = dc:viewModel()
end

return function(): Node<MyNode>
  return {
    init = init,
  }
end
```

### View Models as Inputs

You can create a [Script Input](/scripting/script-inputs) that can be bound to a view model. This allows you to read values (strings, enums, lists, etc.), set values, fire triggers, listen for triggers, and subscribe to value changes.

```lua {3,7,15}
type MyNode = {
  -- This input expects a view model instance of type Character
  character: Input<Data.Character>
}

function init(self: MyNode, context: Context): boolean
  local vmi = self.character
end

return function(): Node<MyNode>
  return {
    init = init,
    -- Initialize with `late()` so the value
    -- can be provided by the editor at runtime.
    character = late(),
  }
end
```

For a detailed explanation, see [View Models Inputs](/scripting/script-inputs#view-model-inputs).

### Binding Inputs

If you only need to read, not set view model properties, you can data bind view model property values to script inputs.
For more information see [Data Binding Inputs](/scripting/script-inputs#data-binding-inputs).

### Nested View Models

To reference a nested view model, use `getViewModel`.

```lua
local vmi = context:viewModel(),
local dateVmi = vmi:getViewModel('dateViewModel')
```

## Reading and Setting Properties

The following methods allow you to reference view model properties:

- [getNumber](/scripting/api-reference/interfaces/view-model#getnumber)
- [getTrigger](/scripting/api-reference/interfaces/view-model#gettrigger)
- [getString](/scripting/api-reference/interfaces/view-model#getstring)
- [getBoolean](/scripting/api-reference/interfaces/view-model#getboolean)
- [getColor](/scripting/api-reference/interfaces/view-model#getcolor)
- [getList](/scripting/api-reference/interfaces/view-model#getlist)
- [getViewModel](/scripting/api-reference/interfaces/view-model#getviewmodel)
- [getEnum](/scripting/api-reference/interfaces/view-model#getenum)


```lua {5,8,11,15,18}
local vmi = context:viewModel()

if vmi then
  -- Get a reference to the score property from the view model
  local score = vmi:getNumber('score')
  if score then
    -- Read the score
    print(score.value)

    -- Set the score
    score.value = 100
  end

  -- Get a reference to the myTrigger property from the view model
  local myTrigger = vmi:getTrigger('myTrigger')
  if myTrigger then
    -- Fire the trigger
    mytrigger:fire()
  end
end
```

## Listening for Property Changes

### Add a Listener

Use `addListener` to listen for triggers or changes to view model properties.

```lua {17,23}
type MyNode = {}

function handleHoursChanged()
  print('hours changed!')
end

function handleTriggerFired()
  print('Fire!')
end

function init(self: MyNode, context: Context): boolean
  local vmi = context:viewModel()

  local hours = vm:getNumber('hours')
  if hours then
    -- handleHoursChanged is called whenever the hours value changes
    hours:addListener(handleHoursChanged)
  end

  local trigger = vm:getTrigger('triggerProperty')
  if trigger then
    -- handleTriggerFired is called whenever the trigger is fired
    trigger:addListener(handleTriggerFired)
  end

  return true
end

return function(): Node<MyNode>
  return {
    init = init,
  }
end
```

### Remove a Listener

Always remove listeners when they are no longer needed to avoid memory leaks.

```lua highlight={17}
type MyNode = {}

function init(self: MyNode, context: Context): boolean
  local vmi = context:viewModel()

  if not vmi then
    print('No view model found')
    return false
  end

  local hours = vmi:getNumber('hours')
  if hours then
    local function handleHoursChanged()
      print('hours changed!')

      -- Remove the event listener
      hours:removeListener(handleHoursChanged)
    end

    -- handleHoursChanged is called whenever the hours value changes
    hours:addListener(handleHoursChanged)
  end

  return true
end

return function(): Node<MyNode>
  return {
    init = init,
    hours = late(),
    trigger = late(),
  }
end

```

## Creating a View Model Instance

Coming soon



---
## scripting/pointer-events.mdx

---
title: "Pointer Events"
description: ""
---

import { Demos } from '/snippets/demos.jsx'

You can listen for pointer events inside any script that implements `pointerDown`, `pointerMove`, `pointerUp`, or `pointerExit`. These functions can be defined in [Node Scripts](/scripting/protocols/node-scripts) and [Layout Scripts](/scripting/protocols/layout-scripts).

```lua
-- Pointer event callbacks have parameters of `self` and a `PointerEvent`.
function handlePointerDown(self: MyNode, event: PointerEvent)
  -- Pointer location in local coordinates relative to the script.
  print(event.position.x, event.position.y)

  -- the pointer identifier (useful for multi-touch)
  print(event.id)

  -- Marks the event as handled and prevents propagation.
  event:hit()
  -- event:hit(true) -- handled, but allowed to pass through translucent elements
end

-- Register your pointer handlers by assigning functions to pointerDown,
-- pointerUp, pointerMove, or pointerExit in the script’s returned table.
return function(): Node<MyScript>
  return {
    init = init,
    draw = draw,
    advance = advance,
    pointerDown = myPointerDownFunction,
  }
end

```

## Multi-touch

Using `event.id`, you can track multiple active pointers.

<Demos
  examples={[
    "scriptingMultiTouch"
  ]}
/>

```lua
type ActiveId = {
  position: Vec2D,
}

export type TrackPointers = {
  -- Keep track of the position for each of the pointers
  activePointers: { ActiveId },
}

function onPointerDown(self: TrackPointers, event: PointerEvent)
  -- Save an item in the table for each pointer down
  self.activePointers[event.id] = {
    position = event.position,
  }

  print('New pointer down: ' .. event.id)
  print('Position: ' .. event.position.x .. event.position.y)

  event:hit()
end

function onPointerMove(self: TrackPointers, event: PointerEvent)
  if self.activePointers[event.id] then
    self.activePointers[event.id].position = event.position

    -- Print all currently active pointer IDs
    print('Active pointer IDs:')
    for id, pointer in self.activePointers do
      print('  id: ', id)
      print('    x:', pointer.position.x)
      print('    y:', pointer.position.y)
    end
  end

  event:hit()
end

function onPointerUp(self: TrackPointers, event: PointerEvent)
  self.activePointers[event.id] = nil

  print('Pointer up: ' .. event.id)
  print('Position: ' .. event.position.x .. event.position.y)

  event:hit()
end

return function(): Node<TrackPointers>
  return {
    init = init,
    advance = advance,
    draw = draw,
    pointerDown = onPointerDown,
    pointerMove = onPointerMove,
    pointerUp = onPointerUp,
    activePointers = {},
  }
end

```

## Nested Pointer Events

Rive only listens for Pointer Events on the main artboard.
If you need to listen for Pointer Events in your [instantiated artboards](/scripting/protocols/node-scripts#instanting-components),
you must forward them manually.

<Demos
  examples={[
    "scriptingNestedPointers"
  ]}
/>


```lua
-- Handle pointer events in the main script
function handlePointerDown(self: MyScript, event: PointerEvent)
  -- self.enemy.pointerDown(self.enemy, event)
  for _, enemy in self.enemies do
    -- Convert the incoming pointer position into the enemy's local space.
    -- This example assumes enemy.position is in the same coordinate system.
    local localEvent = PointerEvent.new(
      event.id,
      Vec2D.xy(
        -- Normalize the pointer position based on the artboard's position
        event.position.x - enemy.position.x,
        event.position.y - enemy.position.y
      )
    )

    -- Forward the event into the instantiated artboard
    self.enemy:pointerDown(localEvent)
  end
end
```
---
## scripting/keyboard-shortcuts.mdx

---
title: "Keyboard Shortcuts"
description: "A comprehensive reference for all keyboard shortcuts in the Rive script editor."
---

## Basic Editing

| Command                 | macOS                                           | Windows/Linux                        |
| ----------------------- | ----------------------------------------------- | ------------------------------------ |
| **Undo**                | <kbd>⌘</kbd> + <kbd>Z</kbd>                     | <kbd>Ctrl</kbd> + <kbd>Z</kbd>       |
| **Redo**                | <kbd>⌘</kbd> + <kbd>⇧</kbd> + <kbd>Z</kbd>      | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Z</kbd> |
| **Copy**                | <kbd>⌘</kbd> + <kbd>C</kbd>                     | <kbd>Ctrl</kbd> + <kbd>C</kbd>       |
| **Cut**                 | <kbd>⌘</kbd> + <kbd>X</kbd>                     | <kbd>Ctrl</kbd> + <kbd>X</kbd>       |
| **Paste**               | <kbd>⌘</kbd> + <kbd>V</kbd>                     | <kbd>Ctrl</kbd> + <kbd>V</kbd>       |
| **Save**                | <kbd>⌘</kbd> + <kbd>S</kbd>                     | <kbd>Ctrl</kbd> + <kbd>S</kbd>       |
| **Select All**          | <kbd>⌘</kbd> + <kbd>A</kbd>                     | <kbd>Ctrl</kbd> + <kbd>A</kbd>       |
| **Indent**              | <kbd>Tab</kbd>                                  | <kbd>Tab</kbd>                       |
| **Outdent**             | <kbd>⇧</kbd> + <kbd>Tab</kbd>                   | <kbd>Shift</kbd> + <kbd>Tab</kbd>    |
| **Format File**         | <kbd>F4</kbd>                                   | <kbd>F4</kbd>                        |

## Application

| Command | macOS | Windows/Linux
| --- | --- | ---
| Open Settings / Configuration | `⌘` + `,` | `Ctrl` + `,`

## Cursor Movement

| Command                     | macOS                                              | Windows/Linux                              |
| --------------------------- | -------------------------------------------------- | ------------------------------------------ |
| **Move by Character**       | <kbd>←</kbd>/<kbd>→</kbd>                          | <kbd>←</kbd>/<kbd>→</kbd>                  |
| **Move by Line**            | <kbd>↑</kbd>/<kbd>↓</kbd>                          | <kbd>↑</kbd>/<kbd>↓</kbd>                  |
| **Move by Word**            | <kbd>⌥</kbd> + <kbd>←</kbd>/<kbd>→</kbd>           | <kbd>Alt</kbd> + <kbd>←</kbd>/<kbd>→</kbd> |
| **Move by Subword**         | <kbd>⌃</kbd> + <kbd>⌥</kbd> + <kbd>←</kbd>/<kbd>→</kbd> | —                                     |
| **Move to Line Start/End**  | <kbd>⌘</kbd> + <kbd>←</kbd>/<kbd>→</kbd>           | <kbd>Ctrl</kbd> + <kbd>←</kbd>/<kbd>→</kbd> |
| **Move to Document Start/End** | <kbd>⌘</kbd> + <kbd>↑</kbd>/<kbd>↓</kbd>        | <kbd>Ctrl</kbd> + <kbd>↑</kbd>/<kbd>↓</kbd> |

## Selection

All cursor movement commands can be combined with <kbd>⇧</kbd> (Shift) to extend the selection:

| Command                          | macOS                                                   | Windows/Linux                                       |
| -------------------------------- | ------------------------------------------------------- | --------------------------------------------------- |
| **Select by Character**          | <kbd>⇧</kbd> + <kbd>←</kbd>/<kbd>→</kbd>                | <kbd>Shift</kbd> + <kbd>←</kbd>/<kbd>→</kbd>        |
| **Select by Line**               | <kbd>⇧</kbd> + <kbd>↑</kbd>/<kbd>↓</kbd>                | <kbd>Shift</kbd> + <kbd>↑</kbd>/<kbd>↓</kbd>        |
| **Select by Word**               | <kbd>⇧</kbd> + <kbd>⌥</kbd> + <kbd>←</kbd>/<kbd>→</kbd> | <kbd>Shift</kbd> + <kbd>Alt</kbd> + <kbd>←</kbd>/<kbd>→</kbd> |
| **Select to Line Start/End**     | <kbd>⇧</kbd> + <kbd>⌘</kbd> + <kbd>←</kbd>/<kbd>→</kbd> | <kbd>Shift</kbd> + <kbd>Ctrl</kbd> + <kbd>←</kbd>/<kbd>→</kbd> |
| **Select to Document Start/End** | <kbd>⇧</kbd> + <kbd>⌘</kbd> + <kbd>↑</kbd>/<kbd>↓</kbd> | <kbd>Shift</kbd> + <kbd>Ctrl</kbd> + <kbd>↑</kbd>/<kbd>↓</kbd> |

## Line Operations

| Command                 | macOS                                           | Windows/Linux                                    |
| ----------------------- | ----------------------------------------------- | ------------------------------------------------ |
| **Toggle Comment**      | <kbd>⌘</kbd> + <kbd>/</kbd>                     | <kbd>Ctrl</kbd> + <kbd>/</kbd>                   |
| **Insert Line Below**   | <kbd>⌘</kbd> + <kbd>↩</kbd>                     | <kbd>Ctrl</kbd> + <kbd>Enter</kbd>               |
| **Insert Line Above**   | <kbd>⌘</kbd> + <kbd>⇧</kbd> + <kbd>↩</kbd>      | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Enter</kbd> |
| **Move Line(s) Up**     | <kbd>⌥</kbd> + <kbd>↑</kbd>                     | <kbd>Alt</kbd> + <kbd>↑</kbd>                    |
| **Move Line(s) Down**   | <kbd>⌥</kbd> + <kbd>↓</kbd>                     | <kbd>Alt</kbd> + <kbd>↓</kbd>                    |
| **Duplicate Line Up**   | <kbd>⇧</kbd> + <kbd>⌥</kbd> + <kbd>↑</kbd>      | <kbd>Shift</kbd> + <kbd>Alt</kbd> + <kbd>↑</kbd> |
| **Duplicate Line Down** | <kbd>⇧</kbd> + <kbd>⌥</kbd> + <kbd>↓</kbd>      | <kbd>Shift</kbd> + <kbd>Alt</kbd> + <kbd>↓</kbd> |

## Multi-Cursor Editing

| Command                      | macOS                                    | Windows/Linux                         |
| ---------------------------- | ---------------------------------------- | ------------------------------------- |
| **Add Cursor**               | <kbd>⌥</kbd> + Click                     | <kbd>Alt</kbd> + Click                |
| **Select Next Occurrence**   | <kbd>⌘</kbd> + <kbd>D</kbd>              | <kbd>Ctrl</kbd> + <kbd>D</kbd>        |
| **Collapse to Single Cursor**| <kbd>Esc</kbd>                           | <kbd>Esc</kbd>                        |

## Search and Replace

| Command                 | macOS                                           | Windows/Linux                                    |
| ----------------------- | ----------------------------------------------- | ------------------------------------------------ |
| **Find**                | <kbd>⌘</kbd> + <kbd>F</kbd>                     | <kbd>Ctrl</kbd> + <kbd>F</kbd>                   |
| **Find in Files**       | <kbd>⌘</kbd> + <kbd>⇧</kbd> + <kbd>F</kbd>      | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>F</kbd> |
| **Find Next**           | <kbd>⌘</kbd> + <kbd>G</kbd> or <kbd>↩</kbd>     | <kbd>Ctrl</kbd> + <kbd>G</kbd> or <kbd>Enter</kbd> |
| **Find Previous**       | <kbd>⌘</kbd> + <kbd>⇧</kbd> + <kbd>G</kbd>      | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd> |
| **Close Search**        | <kbd>Esc</kbd>                                  | <kbd>Esc</kbd>                                   |

The search panel includes toggle buttons for:
- **Match Case**: Toggle case-sensitive search
- **Whole Word**: Toggle whole word matching
- **Regex**: Toggle regular expression mode

## Code Navigation

| Command                 | macOS                                           | Windows/Linux                        |
| ----------------------- | ----------------------------------------------- | ------------------------------------ |
| **Go to Definition**    | <kbd>⌘</kbd> + Click                            | <kbd>Ctrl</kbd> + Click              |
| **File Palette**        | <kbd>⌘</kbd> + <kbd>P</kbd>                     | <kbd>Ctrl</kbd> + <kbd>P</kbd>       |
| **Command Palette**     | <kbd>⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd>      | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> |
| **Global Search**       | <kbd>⌘</kbd> + <kbd>K</kbd>                     | <kbd>Ctrl</kbd> + <kbd>K</kbd>       |

## File and Tab Management

| Command                     | macOS                                           | Windows/Linux                                    |
| --------------------------- | ----------------------------------------------- | ------------------------------------------------ |
| **Close Tab**               | <kbd>⌘</kbd> + <kbd>W</kbd>                     | <kbd>Ctrl</kbd> + <kbd>W</kbd>                   |
| **Previous Tab**            | <kbd>⌘</kbd> + <kbd>⇧</kbd> + <kbd>[</kbd>      | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>[</kbd> |
| **Next Tab**                | <kbd>⌘</kbd> + <kbd>⇧</kbd> + <kbd>]</kbd>      | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>]</kbd> |
| **Tab Palette Forward**     | <kbd>⌃</kbd> + <kbd>Tab</kbd>                   | <kbd>Ctrl</kbd> + <kbd>Tab</kbd>                 |
| **Tab Palette Backward**    | <kbd>⌃</kbd> + <kbd>⇧</kbd> + <kbd>Tab</kbd>    | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Tab</kbd> |

## Autocomplete

| Command                 | macOS                                           | Windows/Linux                        |
| ----------------------- | ----------------------------------------------- | ------------------------------------ |
| **Previous Suggestion** | <kbd>↑</kbd>                                    | <kbd>↑</kbd>                         |
| **Next Suggestion**     | <kbd>↓</kbd>                                    | <kbd>↓</kbd>                         |
| **Accept Suggestion**   | <kbd>↩</kbd> or <kbd>Tab</kbd>                  | <kbd>Enter</kbd> or <kbd>Tab</kbd>   |
| **Dismiss**             | <kbd>Esc</kbd>                                  | <kbd>Esc</kbd>                       |

## Mouse Actions

| Action                      | Description                                          |
| --------------------------- | ---------------------------------------------------- |
| Click                       | Place cursor at click position                       |
| Double-click                | Select the word at click position                    |
| Click in gutter             | Select entire line                                   |
| <kbd>⇧</kbd> + Click        | Extend selection to click position                   |
| <kbd>⌥</kbd> + Click        | Add additional cursor at click position              |
| <kbd>⌘</kbd> + Hover        | Show definition preview for symbol under cursor      |
| <kbd>⌘</kbd> + Click        | Go to definition of symbol under cursor              |
| Click and drag              | Select text by dragging                              |
| Click and drag in gutter    | Select multiple lines                                |

## Auto-Closing Pairs

The editor automatically inserts closing characters for:

| Opening | Closing | Notes                                |
| ------- | ------- | ------------------------------------ |
| `{`     | `}`     | Curly braces                         |
| `[`     | `]`     | Square brackets                      |
| `(`     | `)`     | Parentheses                          |
| `"`     | `"`     | Double quotes (not inside strings)   |
| `'`     | `'`     | Single quotes (not inside strings)   |
| `` ` `` | `` ` `` | Backticks (not inside strings)       |

## Surrounding Selection

When text is selected, typing an opening character wraps the selection:

| Type    | Selection becomes  |
| ------- | ------------------ |
| `{`     | `{selection}`      |
| `[`     | `[selection]`      |
| `(`     | `(selection)`      |
| `"`     | `"selection"`      |
| `'`     | `'selection'`      |
| `` ` `` | `` `selection` ``  |
| `<`     | `<selection>`      |

## Auto-Completion for Luau Blocks

When pressing <kbd>↩</kbd> (Enter) after certain keywords, the editor auto-completes the block structure:

| After typing... | Auto-inserts          |
| --------------- | --------------------- |
| `function`      | `end` on new line     |
| `do`            | `end` on new line     |
| `then`          | `end` on new line     |
| `else`          | `end` on new line     |
| `repeat`        | `until false` on new line |

## Smart Indentation

- Pressing <kbd>↩</kbd> (Enter) automatically maintains the current indentation level
- After opening keywords (`function`, `do`, `then`, `else`, `repeat`, `{`), the next line is indented
- <kbd>⌫</kbd> (Backspace) in the indent region removes a full tab (2 spaces) at a time
- <kbd>⌘</kbd> + <kbd>←</kbd> (Home) toggles between column 0 and the first non-whitespace character
- Indentation uses 2 spaces (soft tabs)
- Line comments use `--` (Luau style)

## Diff Mode

When viewing AI-generated changes:

| Action              | Description                               |
| ------------------- | ----------------------------------------- |
| Hover over chunk    | Shows accept/reject buttons               |
| Accept button       | Accept the changes in this chunk          |
| Reject button       | Reject the changes and restore original   |
| Accept All          | Accept all pending changes                |
| Reject All          | Reject all pending changes                |

---
## scripting/demos.mdx

---
title: "Scripting Demos"
sidebarTitle: "Demos"
description: ""
mode: 'wide'
---

import { Demos } from '/snippets/demos.jsx'

<Demos
  examples={[
    "scriptingLists",
    "scriptingPlinko",
    "scriptingSlotMachine",
    "scriptingSnakeGame",
    "scriptingBoilPathEffect",
    "scriptingTextPathEffect",
    "scriptingDrawingShapes",
    "scriptingTippingConverter",
    "scriptingMasonry",
    "scriptingDrawImages",
    "scriptingUnitTesting",
    "scriptingMultiTouch",
    "scriptingNestedPointers",
  ]}
  columns={3}
/>

## Scripting protocols

---
## scripting/protocols/converter-scripts.mdx

---
title: "Converter Scripts"
description: "Create custom converters using Rive scripting"
---

import { Demos } from '/snippets/demos.jsx'
import { YouTube } from '/snippets/youtube.mdx'

Rive includes several built-in converters like **Convert to String** and **Round**.
Scripting lets you create your own custom converters when you need behavior that isn’t covered by the built-ins.

For background on converters and data binding, see [Data Converters](/editor/data-binding/converters).

<YouTube id="rPIEATBt4Qo" />

## Examples

<Demos
  examples={[
    "scriptingTippingConverter",
  ]}
/>

## Creating a Converter

[Create a new script](/scripting/creating-scripts) and select **Converter** as the type.

## Anatomy of a Converter Script

```lua
type MyConverter = {}

-- Called once when the script initializes.
function init(self: MyConverter): boolean
  return true
end

-- Converts the property value.
function convert(self: MyConverter, input: DataInputs): DataOutput
  local dv: DataValueNumber = DataValue.number()

  if input:isNumber() then
    dv.value = (input :: DataValueNumber).value + 1
  else
    dv.value = 0 -- 0 if input is not a number
  end

  return dv
end

-- For 2-way data binding, converts the target value back to the source
function reverseConvert(self: MyConverter, input: DataOutput): DataInputs
  local dv: DataValueNumber = DataValue.number()

  if input:isNumber() then
    -- Example: Subtract 1 from the target number
    dv.value = (input :: DataValueNumber).value - 1
  else
    dv.value = 0 -- 0 if target is not a number
  end

  return dv
end

-- Return a factory function that builds the converter instance.
-- Rive calls this when the script is created, passing back a table
-- containing its lifecycle functions and any default values.
return function(): Converter<MyConverter, DataValueNumber, DataValueNumber>
  return {
    init = init,
    convert = convert,
    reverseConvert = reverseConvert,
  }
end
```


## Creating a Converter using your Script

Create a new converter using your new converter script:

1. In the Data panel, click the `+` button.
2. Choose **Converters → Script → MyConverter**.


![Create converter with a script](/images/scripting/create-converter-with-script.png)


## Adding Inputs

See [Script Inputs](/scripting/script-inputs).
---
## scripting/protocols/layout-scripts.mdx

---
title: "Layout Scripts"
description: ""
---

import { Demos } from '/snippets/demos.jsx'

Layout Scripts extend the behavior of [Node Scripts](/scripting/protocols/node-scripts), giving you programmatic control over Layout components. They let you measure, size, and react to changes in your Layout’s geometry. They are ideal for building custom layout behaviors such as masonry grids, carousels, spacing logic, and more.



## Examples

<Demos
  examples={[
    "scriptingMasonry",
    "scriptingPlinko"
  ]}
/>

## Adding a Layout Script to a Layout

1. Add a new [Layout](/editor/layouts/layouts-overview) to the scene.
2. [Create a new script](/scripting/creating-scripts) and select **Layout** as the type.
3. Add your script as a child of the Layout.

## Lifecycle

Layout Scripts add two additional lifecycle functions:

- `measure(self): Vec2D` — optional
- `resize(self, size: Vec2D)` — required

### Measure

Measure lets your script propose an ideal size for the layout.
Rive will use this value unless a Fit rule overrides it.

Measure only has an effect on layouts with a Fit type of Hug.

```lua
function measure(self: MyLayout): Vec2D
  -- Always declare that this layout would like to be 100×100
  return Vec2D.xy(100, 100)
end
```

### Resize

Resize runs whenever the Layout receives a new size from its parent or from your measure function.
This is where you position or update child nodes, recalculate flow, or react to container changes.

```lua
-- Called whenever the Layout is resized.
function resize(self: MyLayout, size: Vec2D)
  print("New size:")
  print("x:", size.x)
  print("y:", size.y)
end
```






---
## scripting/protocols/listener-action-scripts.mdx

---
title: "Listener Action Scripts"
description: "Run custom logic when a state machine listener fires"
---

[Listeners](/editor/state-machine/listeners) fire when a specific event occurs in a State Machine.
Listener Action Scripts let you run custom logic in response to those events.

Use Listener Action Scripts when you need to perform side effects—such as updating view model values, responding to pointer input, or triggering external behavior—without changing state.

## Creating a Listener Action Script

[Create a new script](/scripting/creating-scripts) and select **Listener Action Script** as the type.

## Anatomy of a Listener Action

```lua
type MyListenerAction = {
  context: Context,
}

-- Called once when the script initializes.
function init(self: MyListenerAction, context: Context): boolean
  -- Context gives you access to your main view model and other data.
  self.context = context
  return true
end

-- Called when the Listener fires.
-- Use this to perform side effects (no return value).
function perform(self: MyListenerAction, pointerEvent: PointerEvent)

end

-- Return a factory function that Rive uses to build the Listener Action instance.
return function(): ListenerAction<MyListenerAction>
  return {
    init = init,
    perform = perform,
    context = late(),
  }
end

```

## Adding your Listener Action

<Steps>
  <Step title="Select a Listener" />
  <Step title="Click + and select Scripted Action" />
  <Step title="From the Run dropdown, select your script" />
</Steps>

![Add a custom listener action](/images/scripting/add-listener-action.gif)

## Script Inputs

Inputs let you add parameters to a listener action without changing script logic—making the same script reusable across different listeners. For more information on adding inputs to your scripts, see [Script Inputs](/scripting/script-inputs).

<Note>
  Inputs can control scripts, but scripts can't change the value of inputs.

  If you need to control a view model property from your script, access the [Main View model through context](/scripting/data-binding#accessing-the-main-view-model) or [View Model Inputs](/scripting/script-inputs#view-model-inputs).
</Note>

### Setting an Input

To set the value of an input, select the Properties icon next to the listener script.

![listener action script inputs](/images/scripting/listener-action-script-input.png)

### Data Binding an Input

Right-click your property and select Data Bind to bind your input to a view model property.

![listener action script inputs](/images/scripting/listener-action-script-input-binding.png)

---
## scripting/protocols/node-scripts.mdx

---
title: "Node Scripts"
description: ""
---

import { Demos } from '/snippets/demos.jsx'

Node scripts can be used to render shapes, images, text, artboards, and more.

## Creating a Node Script

1. [Create a new script](/scripting/creating-scripts) and select **Node** as the type.
2. [Add it to the scene](/scripting/creating-scripts#adding-scripts-to-your-scene).

## Anatomy of a Node Script

```lua
-- Define the script's data and inputs.
type MyNode = {}

-- Called once when the script initializes.
function init(self: MyNode): boolean
  return true
end

-- Called every frame to advance the simulation.
-- 'seconds' is the elapsed time since the previous frame.
function advance(self: MyNode, seconds: number): boolean
  return false
end

-- Called when any input value changes.
function update(self: MyNode) end

-- Called every frame (after advance) to render the content.
function draw(self: MyNode, renderer: Renderer) end


-- Return a factory function that Rive uses to build the Node instance.
return function(): Node<MyNode>
  return {
    init = init,
    advance = advance,
    update = update,
    draw = draw,
  }
end
```


## Drawing

Node scripts allow you to draw shapes and render them in your scene.

<Demos
  examples={[
    "scriptingDrawingShapes"
  ]}
/>

```lua
function rectangle(self: Rectangle)
  -- Update the path with current width and height
  self.path:reset()

  local halfWidth = self.width / 2
  local halfHeight = self.height / 2

  -- Draw rectangle centered at origin
  self.path:moveTo(Vector.xy(-halfWidth, -halfHeight))
  self.path:lineTo(Vector.xy(halfWidth, -halfHeight))
  self.path:lineTo(Vector.xy(halfWidth, halfHeight))
  self.path:lineTo(Vector.xy(-halfWidth, halfHeight))
  self.path:close()

  -- Update paint color
  self.paint.color = self.color
end

function draw(self: Rectangle, renderer: Renderer)
  renderer:drawPath(self.path, self.paint)
end
```

See the [API Reference](/scripting/api-reference/path) for a complete list of drawing utilities.

## Common Patterns

### Instantiating Components

To be able to instantiate components at runtime, you will need to have a basic understanding of
[Data Binding](/editor/data-binding/overview), [Components](/editor/fundamentals/components), and [Script Inputs](/scripting/script-inputs).

See the following example showing how to set up your components, view models, and scripts:

<Demos
  examples={[
    "scriptingSnakeGame"
  ]}
/>


```lua
type Enemy = {
  artboard: Artboard<Data.Enemy>,
  position: Vector,
}

export type MyGame = {
  -- This is the component that we will dynamically add to our scene
  -- See: /scripting/script-inputs
  enemy: Input<Artboard<Data.Enemy>>,
  enemies: { Enemy },
}

function createEnemy(self: MyGame)
  -- Create an instance of the artboard
  local enemy = self.enemy:instance()

  -- Keep track of all enemies in self.enemies
  local entry: Enemy = {
    artboard = enemy,
    position = Vector.xy(0, 0),
  }
  table.insert(self.enemies, entry)
end

function init(self: MyGame)
  createEnemy(self)

  return true
end

function advance(self: MyGame, seconds: number)
  -- Advance the artboard of each enemy
  for _, enemy in self.enemies do
    enemy.artboard:advance(seconds)
  end

  return true
end

function draw(self: MyGame, renderer: Renderer)
  -- draw each enemy
  for _, enemy in self.enemies do
    renderer:save()
    enemy.artboard:draw(renderer)
    renderer:restore()
  end
end

return function(): Node<MyGame>
  return {
    init = init,
    advance = advance,
    draw = draw,
    enemy = late(),
    enemies = {},
  }
end
```

### Fixed-Step Advance

Frame rates can vary between devices and scenes. If your script moves or animates objects based directly on the frame time, faster devices will move them farther each second, while slower ones will appear to lag behind.

To keep movement and timing consistent, you can advance your simulation in fixed time steps instead of relying on the variable frame rate. This technique is called a fixed-step update or fixed timestep.

<Demos
  examples={[
    "scriptingSnakeGame"
  ]}
/>

```lua
--- Fixed Timestep Advance
--- Keeps movement consistent across different frame rates
--- by advancing the simulation in fixed time steps.
export type CarGame = {
  speed: Input<number>,
  accumulator: number,
  fixedStep: Input<number>,
  direction: number,
  currentX: number,
  currentY: number,
}

-- Prevent the script from running too many catch-up steps
-- after a long pause or frame drop.
local MAX_STEPS = 5

function advance(self: CarGame, seconds: number): boolean
  -- Add the time since the last frame to the accumulator.
  self.accumulator += seconds

  local dt = self.fixedStep
  local steps = 0

  -- Run the simulation in small, fixed steps.
  -- If the frame took longer than one step, multiple steps may run this frame.
  while self.accumulator >= dt and steps < MAX_STEPS do
    -- Move forward by speed * time.
    -- Using a fixed dt keeps movement stable even if the frame rate changes.
    self.currentX += self.speed * math.cos(self.direction) * dt
    self.currentY += self.speed * math.sin(self.direction) * dt

    -- Subtract one fixed step from the accumulator
    -- and repeat until we've caught up to real time.
    self.accumulator -= dt
    steps += 1
  end

  return true
end

-- Create a new instance of the CarGame script with default values.
-- The simulation runs 60 fixed steps per second.
return function(): Node<CarGame>
  return {
    speed = 100,
    accumulator = 0,
    direction = 0,
    fixedStep = 1 / 60,
    currentX = 0,
    currentY = 0,
  }
end

```


---
## scripting/protocols/overview.mdx

---
title: "Protocols"
sidebarTitle: "Overview"
description: ""
---

Protocols are the structured categories of scripts that tell the Editor what you’re trying to make.

Rive currently ships with the following protocols, with more to come:

- [Node](/scripting/protocols/node-scripts)
- [Layout](/scripting/protocols/layout-scripts)
- [Converter](/scripting/protocols/converter-scripts)
- [Path Effect](/scripting/protocols/path-effect-scripts) - Create custom path effects.
- [Transition Conditions](/scripting/protocols/transition-condition-scripts) - Create custom state machine transition conditions.
- [Listener Actions](/scripting/protocols/listener-action-scripts) - React to state machine listeners.
- [Test](/scripting/protocols/test-scripts) - Unit test your functions.

Each protocol represents a different kind of script the Editor can generate: a converter that shapes data, a custom drawing function, a layout helper, a testing harness, a path effect you can attach to strokes, and so on.

Selecting a protocol generates a typed scaffold that defines the surface area you’re allowed to operate on. From there, you work with Rive-native concepts — paths, shapes, view models, artboards, state machines, timelines — but always through the lens of the protocol you picked. It keeps scripts specific and prevents “do anything anywhere” chaos.

---
## scripting/protocols/path-effect-scripts.mdx

---
title: "Path Effect Scripts"
description: "Create custom path effects using Rive scripting"
---

import { Demos } from '/snippets/demos.jsx'

Path Effects are Rive scripts that modify and transform path geometry in real-time. They give you programmatic control over the shape and structure of paths in your animations, enabling effects like warping, distortion, animation, and procedural modifications.


## Creating a Path Effect

[Create a new script](/scripting/creating-scripts) and select **Path Effect** as the type.

## Examples

<Demos
  examples={[
    "scriptingBoilPathEffect",
    "scriptingTextPathEffect",
  ]}
/>

## Anatomy of a Path Effect Script

### Methods

- *init (optional)*
Called once when the path effect is created. Use this to set up initial state. Returns true if initialization succeeds.
- *update (required)*
The core method where path transformation happens. Receives the original `PathData` and returns a modified version. This is where you manipulate the path's geometry.
- *advance (optional)*
Called every frame with elapsed time in seconds. Returns true to continue receiving advance calls. Useful for animated effects that change over time.

## Working with `PathData`
`PathData` provides access to a path's drawing commands (`moveTo`, `lineTo`, `cubicTo`, `quadTo`, `close`). You can:

- Read existing commands using indexing
- Get the command count with `#pathData`
- Create new paths and add commands
- Use measurement tools like `contours()` and `measure()` for advanced operations

```lua
type MyPathEffect = {
  context: Context,
}

function init(self: MyPathEffect, context: Context): boolean
  self.context = context
  return true
end

function update(self: MyPathEffect, inPath: PathData): PathData
  local path = Path.new()
  return path
end

function advance(self: MyPathEffect, seconds: number): boolean
  return true
end

-- Return a factory function that Rive uses to build the Path Effect instance.
return function(): PathEffect<MyPathEffect>
  return {
    init = init,
    update = update,
    advance = advance,
    context = late(),
  }
end
```


## Add the Scripted Path Effect to a Stroke

Select or add a stroke to a shape:

1. Open the Options menu.
2. Select the Effects Tab and click the '+' to add an effect.
3. Find your effects under the Script Effects menu option.
4. Any inputs you have defined will apepar and can be edited here.

![Add Path Effect to a Stroke](/images/scripting/add-path-effect-to-stroke.png)

## Adding Inputs

See [Script Inputs](/scripting/script-inputs).
---
## scripting/protocols/test-scripts.mdx

---
title: "Test Scripts"
description: "Write tests for your scripts to ensure they are working correctly."
---

See [Unit Testing](/scripting/debugging/unit-testing).
---
## scripting/protocols/transition-condition-scripts.mdx

---
title: "Transition Condition Scripts"
description: "Create custom state machine transitions using scripts"
---

[Conditions](/editor/state-machine/transitions#conditions) are the rules that determine when the State Machine transitions from one state to another. Transition Condition Scripts let you define custom conditions when built-in comparisons aren’t enough—such as transitions that depend on complex logic or multiple view model properties evaluated together.

## Creating a Transition Condition Script

[Create a new script](/scripting/creating-scripts) and select **Transition Condition Script** as the type.

## Anatomy of a Transition Condition

```lua
type MyTransitionCondition = {
  context: Context,
}

-- Called once when the script initializes.
function init(self: MyTransitionCondition, context: Context): boolean
  -- Context gives you access to your main view model and other data.
  self.context = context

  return true
end

-- Add your transition logic here.
-- `evaluate` is fired every frame while the transition is active.
-- Returning false prevents a transition, true allows a transition.
function evaluate(self: MyTransitionCondition): boolean
  return false
end

-- Return a factory function that Rive uses to build the Transition Condition instance.
return function(): TransitionCondition<MyTransitionCondition>
  return {
    init = init,
    evaluate = evaluate,
    context = late(),
  }
end
```

<Note>
  `evaluate` runs every frame while the transition is active.

  It should be fast and side-effect free, and only return whether the transition is allowed.
</Note>

## Adding your Transition Condition

<Steps>
  <Step title="Select a Transition" />
  <Step title="Click + to add a new Condition" />
  <Step title="Select your Script" />
</Steps>

![Add a custom transition](/images/scripting/add-transition-condition.gif)

## Script Inputs

Inputs let you add parameters a transition without changing script logic—making the same condition reusable across different transitions or states. For more information on adding inputs to your scripts, see [Script Inputs](/scripting/script-inputs).

<Note>
  Inputs can control scripts, but scripts can't change the value of inputs.

  If you need to control a view model property from your script, access the [Main View model through context](/scripting/data-binding#accessing-the-main-view-model) or [View Model Inputs](/scripting/script-inputs#view-model-inputs).
</Note>

### Setting an Input

To set the value of an input, select the Properties icon next to the transition.

![transition script inputs](/images/scripting/transition-condition-input.png)

### Data Binding an Input

Right-click your property and select Data Bind to bind your input to a view model property.

![data binding transition script inputs](/images/scripting/transition-condition-input-binding.png)

---
## scripting/protocols/util-scripts.mdx

---
title: "Util Scripts"
description: "Create helper modules to organize shared logic across your scripts."
---

Util scripts let you organize your code into small, focused modules that can be reused across multiple scripts.
They’re ideal for math helpers, geometry utilities, color functions, or any logic that should be broken out into its own script.

## Creating a Util Script

[Create a new script](/scripting/creating-scripts) and select **Util** as the type.

```lua
--- Example helper function.
local function add(a: number, b: number): MyUtil
  return a + b,
end

-- Return the functions you'd like to use in another script
return {
  add = add,
}

```

**Usage:**

```lua
local MyUtil = require("MyUtil")

local result = MyUtil.add(2, 3)
print(result) -- 5

```

## Utils with Custom Types

Custom types defined in your Util scripts will automatically be accessible
in the parent script.

```lua
--- Defines the return type for this util.
--- The type is automatically available when you require the script.
export type AdditionResult = {
  exampleValue: number,
  someString: string
}

--- Example helper function.
local function add(a: number, b: number): AdditionResult
  return {
    exampleValue = a + b,
    someString = "4 out of 5 dentists recommend Rive"
  }
end

return {
  add = add,
}

```

**Usage:**

```lua
-- With type annotation
local result: AdditionResult = MyUtil.add(2, 3)
```

## Scripting debugging

---
## scripting/debugging/debug-panel.mdx

---
title: "Debug Panel"
description: ""
---

The Debug Panel lets you inspect script output and detect issues
in your code.

## Toolbar

Switch between [Console](#console) and [Problems](#problems) using the tabs to the left of the panel. Use the icons at the right end of the panel to open and close the panel and toggle fullscreen mode. Additional options to copy and clear the console show up when the Console tab is active.

![Debug panel toolbar](/images/scripting/debugging/debug-panel-toolbar.png)


## Console

The Console shows all log output from your scripts during playback. You can use the standard [Luau print()](https://create.roblox.com/docs/reference/engine/globals/LuaGlobals#print) function to log information, variable values, and messages.

```lua
print("Rive is so cool!")
print("Elapsed time:", seconds)
```

![Debug panel toolbar](/images/scripting/debugging/console-print.png)

## Problems

The Problems tab lists problems detected _before_ the script runs such as type mismatches, syntax errors, or missing data bindings.

The tab badge shows the number of issues found across your scripts.

Clicking a problem will jump directly to the affected line of code.
You can also hover any underlined code in the editor to see an explanation or suggested fix.

![Problems panel](/images/scripting/debugging/problems-panel.png)
---
## scripting/debugging/unit-testing.mdx

---
title: "Unit Testing"
description: "Write and run unit tests for your Util Scripts using Test scripts."
---
import { Demos } from '/snippets/demos.jsx'

Test scripts let you write unit tests for your [Util Scripts](/scripting/protocols/util-scripts) and run them directly in the Rive editor.
Use them to verify math helpers, string utilities, or any other pure logic your scripts depend on.

Beyond validating your code, tests also serve as precise instructions for the [AI Agent](/editor/ai-agent), helping it produce code that behaves exactly as you intend.

<Demos
  examples={[
    "scriptingUnitTesting"
  ]}
/>

## Creating a Test Script

[Create a new script](/scripting/creating-scripts) and select **Test** as the type.

### Anatomy of a Test Script

A Test script exposes a single `setup(test: Tester)` function. The `Tester` object gives you helpers to define and group tests:

- `test.case(name, fn)` – define a single test case.
- `test.group(name, fn)` – group related tests. Groups can be nested.
- `expect(value)` – create an expectation object to assert on a value.

Inside a case, the `expect` function is passed as an argument to your test callback.

### Example

```lua
-- Load the Util that you want to create tests for
local MyUtil = require('MyUtil')

function setup(test: Tester)
  local case = test.case
  local group = test.group

  -- Create a single case with multiple tests
  case('Addition', function(expect)
    local result = MyUtil.add(2, 3)
    expect(result).is(5)
    expect(result).greaterThanOrEqual(5)
  end)

  -- Organize your tests with groups
  group('Math', function()
    case('Subtraction', function(expect)
      local result = MyUtil.subtract(2, 3)
      expect(result).is(-1)
    end)

    case('Multiplication', function(expect)
      local result = MyUtil.multiply(2, 3)
      expect(result).greaterThanOrEqual(6)
    end)

    group('Trigonometry', function()

      case('Degrees to Radians', function(expect)
        local result = MyUtil.deg2rad(180)
        expect(result).is(math.pi)
      end)
    end)
  end)
end

```
<Tip>
  Tip: Use descriptive names for your groups and cases. They show up in the test results panel and make it easier to see what failed.
</Tip>

### Matchers (expectations)

The `expect` helper returns an object with matcher methods you can use in your tests, for example:

```lua
expect(value).is(expected)
expect(value).greaterThan(number)
expect(value).greaterThanOrEqual(number)
expect(value).lessThan(number)
expect(value).lessThanOrEqual(number)
```

For a complete list of matchers and test utilities, see Test API Reference (TODO: link).

### Inverting matchers with never

You can invert any matcher by chaining .never before it.
This means: the test passes only if the matcher would normally fail.

```lua
case('never examples', function(expect)
  -- This passes because 2 + 2 is NOT 3
  expect(2 + 2).never.is(3)

  -- This passes because 4 is NOT >= 6
  expect(4).never.greaterThanOrEqual(6)
end)
```

## Running Tests

1. In the Assets panel, right-click your Test script.
2. Select Run Tests.

Test results are shown:

- Passing and failing cases are listed under the script in the Assets Panel
- Passing and failing cases are highlighted in the script editor

![Problems panel](/images/scripting/debugging/test-results.png)

## API reference (top-level pages only — see repo for full per-class docs)
