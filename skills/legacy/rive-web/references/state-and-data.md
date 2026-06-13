# State Machine, Inputs, Data Binding & Events — Aggregated Reference

These are the core mechanics for *interpreting and driving* Rive animations from web code.

## Runtime perspective (how to read/write from web app)

---
## runtimes/state-machines.mdx

---
title: "State Machine Playback"
description: "Playing a state machine"
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'

[State machines](/editor/state-machine/state-machine) define the logic that controls interactive animations in a Rive file.
They transition between animation states in response to inputs such as triggers, booleans, and numbers.

Each runtime provides APIs for reading and updating these inputs at runtime.

<Runtimes
  runtimes={{
    web: '/runtimes/web/state-machines',
    react: '/runtimes/react/state-machines',
    reactNative: '/runtimes/react-native/state-machines',
    flutter: '/runtimes/flutter/state-machines',
    apple: '/runtimes/apple/state-machines',
    android: '/runtimes/android/state-machines',
    unity: '/game-runtimes/unity/state-machines'
  }}
/>
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
## runtimes/data-binding.mdx

---
title: "Data Binding"
description: "Connect your code to bound editor elements using View Models"
---

import { Runtimes } from '/snippets/runtimes/landing-pages/runtimes.jsx'
import { Demos } from "/snippets/demos.jsx";


[Data Binding](/editor/data-binding/overview) lets your app read and update values in a Rive file at runtime.
Values exposed in the Editor can be connected to properties such as text, numbers, and booleans.

Each runtime provides APIs for reading and updating these values from your application.

<Runtimes
  runtimes={{
    web: '/runtimes/web/data-binding',
    react: '/runtimes/react/data-binding',
    reactNative: '/runtimes/react-native/data-binding',
    flutter: '/runtimes/flutter/data-binding',
    apple: '/runtimes/apple/data-binding',
    android: '/runtimes/android/data-binding',
    unity: '/game-runtimes/unity/data-binding'
  }}
/>

## Explore demos

<Demos examples={["quickStart", "dataBindingQuickStart", "dataBindingImages", "dataBindingLists", "dataBindingArtboards"]} />

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
## Editor perspective — State Machine

---
## editor/state-machine/inputs.mdx

---
title: "Inputs"
description: "⚠️ DEPRECATED: Use Data Binding instead of Inputs for controlling Rive graphics"
noindex: true
---

import { YouTube } from "/snippets/youtube.mdx";

<Warning>
  **DEPRECATION NOTICE:** This entire page documents the legacy Inputs system.
  **For new projects:** Use [Data Binding](/editor/data-binding) instead. **For
  existing projects:** Plan to migrate from Inputs to Data Binding as soon as
  possible. **This content is provided for legacy support only.**
</Warning>

Inputs are a legacy tool to control transitions in our state machine. While Inputs can still be used to control transitions, Data Binding is considered best practice since View Models are both more powerful and easier to control at runtime.

The best use for Inputs is quick, prototype interactions that you don't plan to migrate to runtime.

<YouTube id="rJVfBs6VA0I" />

### Creating a new Input

To create a new Input, use the plus button in the input panel. After hitting the plus button, you’ll be prompted to select the type of input you want to create. There are three types of inputs; booleans, triggers, and numbers.

![Image](https://ucarecdn.com/11d24273-9c87-4adb-963a-fd45f8e667b6/)

## Input Types

We can use three types of inputs depending on the situation and type of interactive content: booleans, triggers, and numbers. We'll discuss each of these inputs below.

### Boolean

A boolean can hold either a true or false value.

![Boolean for a switch](https://ucarecdn.com/4886ec99-ad57-4ae7-9709-5f028c6cbaab/)

### Trigger

Triggers are similar to booleans, but can only become true for a short time.

![Trigger for attack animation](https://ucarecdn.com/29401ecd-875b-4925-bb1e-b48518786c42/)

### Number

A number input give you a number box that can be any integer.

![Number input for rating animation](https://ucarecdn.com/dbd19760-02e4-4d37-a3a8-627ce8e0b65c/)

---
## editor/state-machine/layers.mdx

---
title: "Layers"
description: "Layers let you build more complex logic and animation with the state machine. "
---

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="7Vb1LosMzwk" />

A layer on the state machine allows you to play a single animation at a time. For this reason, you can create multiple layers if you wish to mix multiple animations or add additional interactions to a state machine.

This example uses layers to mix different background animations, and add multiple interactions onto a single artboard.

![Using multiple Layers](https://ucarecdn.com/aeedde5a-598f-42b3-a5df-81212757395e/)

### Creating a new layer

To create a new layer, use the plus button on the Layers Tab.

![Add a new Layer](/images/editor/state-machine/state-machine-layer-create.gif)

Notice that each new tab that you create comes with the Default States.

### Layer Order

It may not be obvious, but the order of your Layers matter, with Layers to the right taking priority over the Layers to the left. In most cases, this won’t matter, but if your Layers have States that control the same object properties, the animations in the right most layer will take priority over the layers to the left as they mix.

<YouTube id="Fc9MutscvAo" />

**Changing layer order**

You can change the layer order by dragging and dropping your layers around on the Layers tab.

<img
  src="/images/editor/state-machine/state-machine-layer-order.gif"
  alt="Move layers"
  title=""
  style={{ width:"100%" }}
/>

**Delete layer**

You can delete a layer with right click over the name and selecting the option "Delete Layer".

![Delete layer](/images/editor/state-machine/state-machine-layer-delete.gif)

**Duplicate layer**

You can delete a layer with right click over the name and selecting the option "Delete Layer".

![Duplicate layer](/images/editor/state-machine/state-machine-layer-duplicate.gif)

**Disable and Enable layer**

You can delete a layer with right click over the name and selecting the option "Delete Layer".

![Disable and Enable layer](/images/editor/state-machine/state-machine-layer-disable.gif)
---
## editor/state-machine/listeners.mdx

---
title: "Listeners"
description: "Listeners let designers create interactive behavior without the use of code."
---

import { YouTube } from '/snippets/youtube.mdx'

Listeners let designers create interactive behaviors—like clicks, hovers, and drags—directly within Rive, without needing code. For example, you can attach Pointer Enter, Pointer Exit, and Click listeners to a button. When triggered, these listeners can update data bindings, set inputs, fire events, and more—enabling dynamic, interactive experiences at runtime.

<YouTube id="25uQiqdmT9c" />

#### Creating a new Listener

1. In the Animations tab, select your State Machine.
2. In the Listeners tab, click the plus icon.

<Info>
  If you have an object selected when creating a listener, it will automatically be designated as the target.
</Info>

![New listener](/images/CleanShot2025-06-12at14.46.58.gif)

With the new listener selected, you’ll see its options displayed in a new panel at the bottom of the State Machine Graph and to the right of the Graph.

# Elements of a Listener

A listener consists of three parts: a Target, a Listener Condition, and a Listener Action.

### Target

The Target determines where to listen for the Listener Condition.

**Hit Areas**

In most cases the Target defines the interactive area that responds to user interactions—similar to a hitbox in game development. When a user interacts with this area (e.g., by clicking or hovering), the associated listener is triggered.

It's usually best to use shapes as targets—for example, an ellipse or rectangle with 0% opacity. If you use a Group as a target, the shapes within the group will serve as the interactive area.

To select a target, click the Target icon and choose an object from the artboard or the Hierarchy panel.

![Choose target](/images/CleanShot2025-06-12at14.52.27.gif)

Note that having an object selected when you create a listener will automatically assign the selected object as the target of the listener.

**Listening to Events on Components**

<Info>
  We strongly recommend using data binding to communicate between artboards, rather than relying on nested Events.
</Info>

Setting an Artboard or Component as the target allows you to listen for Events fired from that Artboard.

**Opaque Target**

The Opaque Target option determines whether or not pointer events will pass through the hit area, potentially triggering multiple Listeners at once.

![Opaque target](/images/CleanShot2025-06-12at15.11.08.gif)

# Listener Condition

The Listener Condition defines what the listener is listening for. This includes pointer-based interactions as well as data-driven triggers such as View Model property changes. The drop-down menu below the Target button allows you to change which Listener Condition the listener checks for.

![User action](/images/CleanShot2025-06-12at15.14.19.gif)

Available actions include:

**Pointer Down** – Mouse down or finger press.

**Pointer Up** – Releasing a mouse click or finger press.

**Pointer Enter** – A mouse or finger entering the target area.

**Pointer Exit** – A mouse or finger exiting the target area.

**Pointer Move** – Any mouse or finger movement within the target area.

**Click** – A combination of pointer down and pointer up within the same target area.

**Listen for Event** – Only visible if the target is an Artboard or Component. If multiple events exist, use the dropdown to select the specific one.

**View Model Property Change** – Triggers when a selected View Model property changes. Only available when the Artboard is set as the Target. Use the dropdown to select the specific property to listen to.

Note that it is not possible to specify an expected value—the listener fires whenever the property changes, regardless of the direction of the change. For example, a Boolean listener will fire whether the value changes from `true` to `false` or from `false` to `true`.

![Listener configured to listen for a boolean View Model property change, with the Artboard set as the Target](/images/editor/state-machine/listener-view-model-property-change-boolean.png)

<Info>
  Since General Events are deprecated, **View Model Property Change** is the recommended way to react to changes happening inside a State Machine. In particular, Triggers are a direct replacement for Events: a Trigger can be fired from within the State Machine (e.g. on a state transition), and a listener set to **View Model Property Change** on that Trigger property will fire in response—giving you the same notification pattern without relying on Events.
</Info>

# Listener Action

A Listener Action defines what happens when the user interaction occurs.

To add a Listener Action, click the plus icon in the panel below the State Machine Graph. You can add multiple actions to a single listener.

![Listener action](/images/CleanShot2025-06-12at15.16.20.gif)

## **View Model Change**

Updates values within your View Model Instance. This is the preferred way to communicate from your Rive file to your runtime code. By default, listeners are set to View Model Change, unless an artboard or component instance is the target of the Listener.

### **View Model Dropdown**

The View Model Dropdown lets you select which View Model Property you want the Listener to change.

![View model dropdown](/images/CleanShot2025-06-12at15.18.21.gif)

Note that listeners can change the properties of any View Model in the file, even if it isn't assigned to the Artboard.

### **Value vs Property**

Once you've selected which property you'd like the Listener to modify, you can set it to a specific Value or to equal a different view model property.

**Value**

If you select Value, you can use the input field to change the specific value you'd like the property set to. The value type changes depending on the property.

![Value](/images/CleanShot2025-06-12at15.24.51.gif)

**View Model Property**

Selecting a property will set the View Model Property in the listener equal to another.

![View model property](/images/CleanShot2025-06-12at15.31.06.gif)

Note that we can set the View Model Property to be equal to itself.

**Adding a Converter**

If we choose to set a View Model Property equal to another View Model Property, the converter icon appears to the right of the View Model Property. This lets us apply a converter to a property.

![Adding a converter](/images/CleanShot2025-06-12at15.37.13.gif)

\
For example, we can set Number to Number, but attach an add one converter. Every time this listener fires, we can increase our Number property by one.

### **Report Event**

Fires an event each time the Listener Condition is met. This is the default option when an artboard or component instance is the target of a listener.

### **Align Target**

The Align Target action positions a target object to follow the pointer when the Listener Condition is met within the listener area.

Use the Target Picker to select the object you want to align.

Enable Preserve Offset to maintain the original distance between the object and the pointer when the action was triggered. When unchecked, the object will align directly to the pointer’s center.

<YouTube id="Zfvb9jy6VRY" />

### **Input Change**

Allows the listener to change a defined input—such as toggling a boolean, firing a trigger, or setting a number input to a specific value.

\
This is useful for creating interactive behaviors like hover states or click effects directly on the Artboard.
---
## editor/state-machine/state-machine.mdx

---
title: "State Machine Overview"
sidebarTitle: "Overview"
description: "Add intelligence to your animations."
---

## Overview

State Machines are a visual way to connect animations together and define the logic that drives the transitions. They allow you to build interactive motion graphics that are ready to be implemented in your product, app, game, or website.

State machines create a new level of collaboration between designers and developers, allowing both teams to iterate deep in the development process without the need for a complicated handoff.

<YouTube id="0Hb7SlEW6MI" />

Using the State Machine requires designers and animators to think more like a developer but in a straightforward, visual way.

Every artboard has at least one State Machine by default, but you can create as many as you’d like. To create a new state machine, hit the plus button in the Animations List and select the State Machine option.

### Anatomy of a State Machine

A basic state machine will consist of a Graph, [States](/editor/state-machine/states), [Transitions](/editor/state-machine/transitions), [Inputs](/editor/state-machine/inputs) and [Layers](/editor/state-machine/layers). We’ll explore each of these pieces and more throughout this section.

The Graph is the space in which you’ll be adding States and connecting Transitions. It appears in place of the Timeline when a state machine is selected in the animations list.

![State Machine Graph](/images/editor/state-machine/307461c0-2006-4fdf-bdc3-61875d40f422.webp)

States are simply timeline animations that can play in your state machine. Typically, these will represent some state that your animated content is in. For example, a button will typically have an Idle state (the button is stationary), a Hovered state (what the button looks like when it is hovered), and a Clicked state (what the button looks like when it’s been clicked).

![Preview of States](https://ucarecdn.com/ca93f148-a38c-4eac-a166-8399065315c2/)

Once we have defined the States of our content, we can tie them together with transitions to create a logical path that our State Machine can take through these different timelines. We’re creating a map that our State Machine can use to get from one animation to the next.

![Creating Transitions](https://ucarecdn.com/cf0f53e3-abc9-43a9-b43a-e18483fe2613/)

<Warning>
  **DEPRECATION NOTICE:** This section is about the legacy Inputs system. \
  **For new projects:** Use [Data Binding](/editor/data-binding) instead. \
  **For existing projects:** Plan to migrate from Inputs to Data Binding as soon as possible. \
  **This content is provided for legacy support only.**
</Warning>

Inputs are a legacy tool to control transitions in our state machine. While Inputs can still be used to control transitions, Data Binding is considered best practice since View Models are both more powerful and easier to control at runtime.

import { YouTube } from '/snippets/youtube.mdx'

The best use for Inputs is quick, prototype interactions that you don't plan to migrate to runtime.

Inputs are the contract between designers and developers. As designers, we use them as rules for our transitions to occur. For example, we could have a boolean called isHovered. That boolean controls the transition between our idle and hovered state. When the boolean is true, the state machine is in the hovered state, and when it is false, the state machine is in the Idle state. Developers tie into these inputs at runtime and define actions that control the state machines inputs I.E. defining hit areas that can change the isHovered boolean.

![Adding Inputs and Conditions](/images/editor/state-machine/state-machine-overview-inputs.gif)

Lastly, all state machines will have at least one Layer. Because only a single animation can play on a given layer, we have the ability to add multiple layers if we want to mix different animations, or add additional interactions. For example, this state machine has multiple layers, each one with the logic to control one of the buttons in this menu.

![Image](https://ucarecdn.com/9b454ffc-1e08-495c-a4b7-b6ba71a7cbd2/)
---
## editor/state-machine/states.mdx

---
title: 'States'
description: ''
---

import { YouTube } from '/snippets/youtube.mdx'

States are simply timeline animations that can play at any point in your state machine. A state could be as simple as changing the color and position of an object, or as complex as blending multiple timelines together.

There are a few types of states that you’ll end up using as you work with the State Machine, including Default States, Single animations, and Blend States. We’ll explore each of these below.

## Default States

The Default States are the states that, by default, are added to every State Machine.

![Default States](/images/editor/state-machine/42815967-dd47-4da1-ba8a-4fc12f64d972.webp)

### Entry State

The Entry State is the state that your State Machine will start from. You’ll notice that by default, your state machine will already have an animation attached to the Entry State, but you can change this animation at any time. Note that you can connect multiple animations to the Entry State if you need I.E. you want to build a switch that can start in either the on or off state.

![Using the Entry state](https://ucarecdn.com/9d359af8-f3c3-4d57-8f88-7ba8dcad4847/)

### Exit State

<YouTube id="JuJwak2ikJ4" />

The Exit State tells the State Machine layer to stop playing. This niche state has uses when multiple layers are being used.

### Any State

<YouTube id="P6Z3oeAJWqY" />

Unlike normal states, states connected to the Any State can be played at any time, regardless of which state your state machine is in. Any States are great to use when you want to create an array of states that can be activated at any time, such as changing the skin of a character.

![Rating system using the Any state](https://ucarecdn.com/6c4401fc-1b7c-4748-901d-a6e237f57e51/)

## Animation States

Animation states include all states other than the default states added to a State Machine. These states will control the look and motion of your interactive content. There are three types of animation states; Single Animation, 1D blend, and Direct blend states.

To add a State to the Graph, you can drag and drop an animation from the Animations List directly onto the Graph. Notice that this will create a Single Animation state. You can change the state type using the inspector.

![Drop and drop State onto the Graph](https://ucarecdn.com/f99e2294-1915-4449-8632-71227dc4f87f/)

Additionally, you can right-click on the graph and create a blank state of any type with no associated timelines.

![Image](https://ucarecdn.com/34662198-6e61-43bd-83dd-d4d8e1ee8012/)

Right-click to add State

To assign a timeline to a state, use the timeline dropdown in the inspector.

### Single animation state


<YouTube id="bGW1tNpNt-Y" />

Any timeline that we create can be used as a single animation state. Depending on the type of animation we are using, the single animation state could be a one-shot, looping, or ping-pong state. In most cases, you’ll be using single animation states to create most of your state machines.

### Blend states

A Blend State is any state that blends together two or more timeline animations. We use these states for content like loading bars, health systems, scrolling interactions, and dynamic face rigs.

There are two types of blend states; 1D and Direct Blend states.

#### 1D Blend state:

A 1D Blend State allows us to mix multiple timelines together with a single numerical input. This state works by ramping up one animation and ramping down the other while you increase or decrease a number input. Note that this mixing is not linear, but is additive and could give you unexpected results.

![Health bar using Blend state](https://ucarecdn.com/875b9ed6-41c7-4023-aaad-f38d2042dca7/)

**Configuring a 1D Blend State:**

You'll want to start by creating a few timelines for your Blend state. Keep in mind that it's often best to use timelines with only a few properties keyed. In this health bar example, only the X scale is keyed.

![Image](https://ucarecdn.com/a2e08c89-388b-4b21-b31b-3d5fb6e94cd7/)

Timelines for health bar

After adding a 1D Blend State to the graph, use the Inspector to configure the state.

![Add Blend state](https://ucarecdn.com/266c2c6d-6719-4b65-b06a-b1ca35d2eb86/)

First, add the number input you want to drive the blend using the dropdown. If you haven’t created one yet, you’ll notice that nothing appears here.

![Create and add number input to Blend state](https://ucarecdn.com/baf39e65-5bf1-44ed-bd2e-b0f0afa24ded/)

The plus button that appears below the number input allows you to add timelines to your blend state. Use the dropdown to assign a specific timeline. Note that you can add as many timelines as you’d like.

![Add timelines to the Blend state](https://ucarecdn.com/fe5d4505-8290-4be9-b0d6-58f13d1df553/)

Next, you need to define a numerical range that your blend state will work between. This particular blend works between 0 and 100.

![Image](https://ucarecdn.com/6a92f242-2979-44c7-bb95-fc51ebeeda5d/)

Notice that once you define the range, a graphic appears above the input dropdown, visually representing how your animations will mix. When the state machine is active, as you increase or decrease your input within the defined range, you’ll see a visual representation move across that graph, showing you the mix of your timelines.

![Blend State in action](https://ucarecdn.com/44a40cb9-90d9-4aca-920f-6042cc52340f/)

#### Additive Blend state:

An Additive Blend state allows you to blend together multiple timelines using multiple number inputs. This allows us to create unique poses and facial positions by mixing multiple animations together. While working with an Additive Blend, you’ll either be mixing an animation by value or input. Read more below.

![Using Additive Blend for facial animations](https://ucarecdn.com/71cf4345-b728-47a4-946c-e08de2eb86dd/)

**Value vs Input blend**

When adding animations to an Additive blend state, you’ll be prompted to either add a Blend by Value animation or a Blend by Input animation.

![Adding timeline to Additive Blend](https://ucarecdn.com/8e2c7380-85cf-4e41-8dd8-82e98f34d1bd/)

A Blend by Value timeline can be thought of as the baseline animation, or default pose. This value is not tied to an input, so it can’t be used to control the state machine. Instead, this value describes its mix weighting.

An Input blend is an animation that is mixed with the default pose or motion via a number input. Each of your different Input blends should have their own number input.

## Additional State Options

When you select a state on the State Machine Graph, you’ll have a number of options that you can change.

**Change state type**

The top three icons allow you to change the type of state. You can select from single animation, 1D blend, and Additive blend.

![Convert state type](https://ucarecdn.com/185c56c3-4d69-4526-95c9-62af59675f18/)

**Change animation**

You can use the dropdown to change which animation is assigned to the current state.

![Changing animation on a state](https://ucarecdn.com/e8a8e540-b5ed-4947-b2cc-45ba793f0ea0/)

**Speed**

You can alter the playback speed of a state by changing this value. Note that you can play animations forward with a positive value, and backward with a negative value.

![Change animation speed](https://ucarecdn.com/5ada4e3d-bbba-412d-8bc3-6b4417717e16/)

**Transitions**

You can see any transitions that leave from the selected state. You also have the option to ignore specific transitions by turning off the eye icon.

## Common Issues

<YouTube id="TnTvFkMC7iI" />

## Use case: Build a simple button

In this exercise, we will use our state machine knowledge to create a simple button with two layers of interactivity. Hover and click.

<YouTube id="hlEPcxhc2pI" />
---
## editor/state-machine/transitions.mdx

---
title: 'Transitions'
description: ''
---

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="C4KNgrrqt7k" />

Transitions supply the logical map for the state machine to follow. There are a number of considerations and configurable properties for transitions that we will cover below. Note that we’ll briefly discuss Inputs as well, so be sure to read more about those as well here.

## Creating a new Transition

To create a transition, place your mouse near the state you want to leave until you notice the ellipse appear. Click and drag the ellipse to the state you want to transition to. Once you’ve connected two states, you’ll notice an ellipse with an arrow icon indicating the transition's direction.

![Creating a transition](https://ucarecdn.com/4838deb6-8760-468a-b798-f33e1f0e3b2e/)

Note that you can create multiple transitions from one state to another. Each of these transitions can require a different condition to be met, which will fire the transition, thus giving you the ability to make “or” conditions.

![Creating an "or" transition](https://ucarecdn.com/373c16da-c3b4-4da8-bd01-bb153fea6c2a/)

## Configuring a Transition

Once you’ve added a transition, selecting the direction indicator will allow you to configure the transition. There are three different sections to the transition panel, the transition properties, conditions, and interpolation.

### Transition properties

The transition properties allow you to customize how a transition occurs.

![Transition properties](/images/editor/state-machine/9b35e6bf-8e06-4df9-b211-10d3e1150435.webp)

### Duration

The duration property describes how long it takes for a transition to occur.

The duration is set to zero by default, meaning the transition happens immediately. So, when we transition between these two animations, it appears as though the object snaps from one side of the artboard to the other.

![Duration of 0ms](https://ucarecdn.com/1e341e26-ece2-466e-b19f-5fa03b34c3b9/)

If we increase the duration, you’ll notice that the higher the number, the longer the transition takes.

![Duration of 500ms](https://ucarecdn.com/9a1c524a-2179-4385-8765-5ab0eb75ffec/)

In a way, transitions act as their own animation. The starting properties (coming from the state your state machine is leaving from) will be interpolated to the ending properties (the starting properties of the state your state machine is going to). If the starting properties are the first key on a timeline, and the ending properties are the second key, the duration is the timing between those two keys. Transitions are much more complex than this, but thinking about transitions this way will help you diagnose issues with your state machine.

![Interpolation on a Transition](https://ucarecdn.com/c1801cb1-13bf-44be-9da0-dc2eb7f5e404/)

Much like keys on our timeline, we can change the interpolation, which we’ll discuss more below.

### Exit Time

Exit Time tells the state machine how much of the state must play before transitioning.

By default, Exit Time is unchecked. If you want to enable the Exit Time, use the check box. Once the setting is enabled, you can use either a time value or percent.

![Using Exit Time](https://ucarecdn.com/4424da18-50d8-4aea-9371-7b57b176a12e/)

For example, if you want the state machine to play the entire animation before transitioning, you can either enter the duration of the animation, or use 100%.

### Pause when exiting

The Pause When Exiting option pauses the animation you are leaving from during the transition.

![Pause when exiting](https://ucarecdn.com/6584d924-13f7-4012-b590-d16549791638/)

As we discussed in the duration section, when a transition happens, properties from the first state are mixed with the first key of the next state. In reality, the animation your state machine leaves from continues to play as the transition happens.

### Conditions

<YouTube id="30HJo_DaLDk" />

Conditions are the rules for our transitions. Without conditions, our transitions would continuously fire and our state machine would likely look either glitchy, or only play a single animation. Conditions require us to define some inputs, which you can read more about [here](/editor/state-machine/inputs).

![Conditions](/images/editor/state-machine/a5336985-e1d4-4892-a04a-deee93e6a8b1.webp)

#### Adding a new condition

To add a new condition to a transition, hit the plus button next to the Conditions section.

![Image](https://ucarecdn.com/7a2b887e-c69d-4dd4-943b-de85d76b3a42/)

Adding a new Condition

Each new condition provides a dropdown showing all of the inputs you’ve added to the State Machine. The configuration options will be different depending on the input type you select.

Note that you can add multiple conditions to a single transition to create an “and” transition.

#### Configuring a Boolean

When you configure a boolean, you can decide if the transition happens when said boolean is either true or false.

![Configure a boolean](https://ucarecdn.com/8443963d-69c7-44a7-9ced-b01d28210b5e/)

#### Configuring a Number

When you configure a number input, you can tell the transition to happen when a numerical condition happens such as equalling a specific number, being greater than or less than a specific number.

![Configure number input](https://ucarecdn.com/3b6da0a7-b56f-4cb1-89f0-831af97fdbce/)

#### Configuring a Trigger

When you add a trigger input to a transition, you are telling the transition to fire when that trigger occurs.

![Configuring triggers](https://ucarecdn.com/c8c6a924-f62a-4e3a-80cb-83c758a37343/)

#### Custom Transitions

[Transition Condition Scripts](/scripting/protocols/transition-condition-scripts) let you define custom conditions when built-in comparisons aren’t enough—such as transitions that depend on complex logic or multiple view model properties evaluated together.

### Interpolation

You can add interpolation to your transition at the bottom of the Transitions Panel. By default, the interpolation is set to linear, but you can use the cubic and hold interpolations.

Note that the interpolation between states is most effective when your transition duration is longer.

If you are unfamiliar with the basics of Interpolation, read more [Interpolation (Easing)](/editor/animate-mode/interpolation-easing).

## Disabling a Transition

You can temporarily disable a transition without deleting it. A disabled transition is ignored by the state machine — its conditions will not be evaluated and it will not fire — until you re-enable it.

There are two ways to toggle a transition's enabled state:

- **From the transition panel:** select the transition and click the enable/disable icon in the panel.
- **From the canvas:** right-click the transition and choose **Disable transition** (or **Enable transition** if it's already disabled).

![Disable transition from the right-click menu](/images/editor/state-machine/state-machine-transition-disable.gif)

Both actions do the same thing. Disabling is useful when you want to isolate part of a state machine for testing, or temporarily remove a path without losing its configuration.
## Editor perspective — Data Binding

---
## editor/data-binding/converters.mdx

---
title: "Converters"
description: "Transform and adapt data before it’s applied to a binding using built-in and custom converters."
---

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="td59TXa_xQI" />

Converters transform values before they are applied to a binding.

Use them to adapt your data to match the property you're binding to—for example, converting numbers to strings, mapping values between ranges, or smoothing changes over time.

## Adding a Converter

![Build and apply a converter](/images/editor/data-binding/converters/add-converter.gif)

<Steps>
  <Step title="Create a Converter">
    In the Assets panel, click the `+` button and select a [converter type](#converter-types).
  </Step>
  <Step title="Set Converter Options">
    With the converter selected, update the settings in the right sidebar.

    <Note>
      Most options can be data bound.
    </Note>
  </Step>
  <Step title="Apply your Converter">
    When setting or updating a binding, set the **Converter** field..
  </Step>
</Steps>

## Converter Types

Converters can be used individually or combined into [groups](#converter-groups) to perform more complex transformations.

| Category | Converter                | Description                               |
|----------|--------------------------|-------------------------------------------|
| String   | [Pad](#pad)                      | Add padding to a string                   |
|          | Trim                     | Remove leading or trailing whitespace     |
|          | Convert to String        | Convert a value to a string               |
|          | Remove Trailing Zeros    | Remove unnecessary decimal zeros          |
| Number   | Round                    | Round to the nearest value                |
|          | Calculate                | Perform simple calculations               |
|          | [Range Map](#range-map)                | Map a value from one range to another     |
|          | [Interpolator](#numeric-interpolator)             | Smoothly interpolate between values       |
|          | [Formula](#formula)                  | Evaluate a custom expression              |
|          | Convert to Number        | Convert a value to a number               |
| Boolean  | Toggle                   | Invert a boolean value                    |
| List     | [Number to List](#number-to-list)           | Generate a list of components based on a number               |
|          | List to Length          | Get the number of items in a list         |
| Color         | [Interpolator](#color-interpolator)             | Smoothly interpolate between colors       |
| Script     | [Converter Scripts](#converter-scripts)           | Create your own custom converters              |

### Pad

Pads a string to a target length by repeating a value at the start or end.

If the string is shorter than the specified length, the pad value is repeated and added until the target length is reached.

**Example:**

- **Value:** 1
- **Pad:** "0"
- **Direction:** Start
- **Length:** 3

**Result**: "001"

---

### Range Map

Maps a number from one range to another.

Use Range Map when you want to take an input value and convert it into a different scale.

**Example**

Convert a slider value (0–100) into an opacity value (0–1):

- **Input**: 50
- **Input range**: 0 → 100
- **Output range**: 0 → 1

**Result**:
0.5

---

### Numeric Interpolator

![interpolate a shape](/images/editor/data-binding/converters/numeric-interpolator.gif)

Smoothly transitions between number values over time, easing changes instead of jumping instantly.

---

### Formula

![Generate a formula](/images/editor/data-binding/converters/formula.gif)

Formula lets you perform custom calculations using values from your View Model or the input.

You can create a formula in two ways:

**Writing it directly**

```lua
random({{NumberConvertersVM/circleX}} / {Input}) + 2
```

<Note>
  `{Input}` refers to the incoming value, while `{{...}}` references View Model properties.
</Note>

**Using the editor**

Click the + button to add values, operations, and functions. This builds the formula for you and generates the equivalent expression.

<Tip>
  **Formulas don't need inputs**

  The following formula would output a random number, regardless of input.

  ```lua
    random(2)
  ```
</Tip>

#### Random Mode

When using `random()` in your formula, the Random Mode determines when a new random value is generated.

- **Once** — Generates a random value only when the formula first runs
- **Source Change** — Generates a new value each time the input changes
- **Always** — Continuously generates new values while the input changes and during interpolation

---

### Number to List

The Number to List converter allows you to generate a specified number of Components based on a number.

See [Lists](/editor/data-binding/lists#view-model-number-with-converter) for more information.

---

### Color Interpolator

![interpolate a color](/images/editor/data-binding/converters/color-interpolator.gif)

Smoothly transitions between color values over time, easing changes instead of jumping instantly.


---

### Converter Scripts

Scripting lets you create your own custom converters when you need behavior that isn’t covered by the built-in converters.

See [Converter Scripts](/scripting/protocols/converter-scripts) for more information.

## Converter Groups

![Build and converter group](/images/editor/data-binding/converters/group.gif)

Converter groups let you chain multiple converters together, where the output of one becomes the input of the next.

<Steps>
  <Step title="Create a Converter Group">
    In the Assets panel, click the `+` button and select Converter > Group.
  </Step>
  <Step title="Add a Converter to Your Group">
    With the group selected, add the `+` button in the right sidebar and select an existing or new converter.
  </Step>
</Steps>

When binding a value, your converter group can now be used just like an individual converter.

### How execution works

Converters run from top to bottom:

- The first converter receives the original input
- Each converter passes its result to the next
- The final output is the result of the last converter

### Reordering converters

Drag a converter up or down to change when it runs.

Earlier converters affect all converters that follow.



---
## editor/data-binding/enums.mdx

---
title: "Enums"
description: "Use enums to control states, modes, and variants by selecting from a predefined set of options."
---

import { Marketplace } from '/snippets/marketplace.mdx'

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="DgDBjxWl8Aw" />


An enum lets you choose one value from a predefined set of options.

Use enums when a property should only ever be one of a few known values—like modes, states, or variants—instead of allowing any arbitrary value like a string.

For example, instead of using a string like "left", "center", or "right", an enum guarantees the value is always one of those valid options.

![Enums](/images/editor/data-binding/property-types/enum-preview.gif)

Enums can be:

- System enums — built-in sets of options used by the editor (for example, Horizontal Align)
- [Custom enums](#custom-enums) — your own defined sets of options for your specific use case

<Marketplace
  href="https://rive.app/community/files/27312-control-editor-properties-with-enums"
/>

<Note>
  **Why not use strings or numbers?**

  Imagine a calendar app that shows different backgrounds based on the day of the week.

  You could use a string like "Monday", but it breaks if someone sets it to "Mon".

  You could use a number, but it’s unclear whether the week starts on Sunday or Monday—or whether the index starts at 0 or 1.

  With an enum, the value must be one of the defined options, so it’s always valid and unambiguous.
</Note>

## Adding an enum property

![Enums](/images/editor/data-binding/property-types/add-enum.gif)

<Steps>
  <Step title="Create a new enum property">
    Create a new enum view model property inside your view model.
  </Step>
  <Step title="Set the enum type">
    Click the dropdown next to the property name and select an enum type.
  </Step>
  <Step title="Set the default enum value">
    Select your enum view model property and in the right sidebar, select the default value.
  </Step>
</Steps>

## Binding enums

![Bind an enum](/images/editor/data-binding/property-types/binding-enums.gif)

Enums can be bound to editor properties that use the same set of options. For example, an enum named “Layout Direction” can be bound to a layout’s Direction property.

When binding enums, the System Enum to Uint converter is required and is applied automatically.

## Custom enums


![Create custom enum](/images/editor/data-binding/property-types/custom-enum.gif)

<Steps>
  <Step title="Create a new enum">
    Open the Data panel, click the `+` icon and select enum.
  </Step>
  <Step title="Add enum options">
    With your enum selected, click the `+` icon in the right sidebar.
  </Step>
  <Step title="Assign the enum to a property">
    Assign your custom enum to your enum view model property.
  </Step>
</Steps>

## Controlling Solos with enums

Use an enum to control which Solo is active by mapping each enum value to a Solo.

![Bind enum to solo](/images/editor/data-binding/property-types/bind-enum-to-solo.gif)


<Steps>
  <Step title="Create a matching enum"> Create a [custom enum](#custom-enums) with values that match the **names and order** of your Solos. </Step>
  <Step title="Bind the enum"> Bind the enum to the Solo’s **Active** property and apply a **Convert to Number** converter. </Step>
</Steps>


---
## editor/data-binding/lists.mdx

---
title: "Lists"
description: "Use Data Binding to generate lists at runtime"
---

import { YouTube } from '/snippets/youtube.mdx'


<YouTube id="VCWcOtUfIc8" />

A List is a way to display a set of items that are dynamically generated based on bound data values that you set up in your View Models. This allows you to build Rive files that can change in real time based on updates to those values. You can use Lists to create:

- Menus with a dynamic amount of options
- Product listings
- Notifications or activity feeds
- Chat messages
- Dropdown menus
- Contacts, friends, or followers lists
- High scores, tables, and more

---

## Artboard Lists

Artboard Lists enable you to generate a number of list items using an Artboard to represent each item in your List. Artboard Lists must be added as children of an Artboard or Layout.

To add an Artboard List to the stage, first select either an Artboard or a Layout. In the inspector on the right side of the editor, you will see a button to add an Artboard List. Click it to add the List to your hierarchy. It will appear as a child of the Artboard or Layout you had previously selected.

![Image](/images/editor/add-artboard-list.png)

Once the Artboard List is added to your hierarchy, you can select it and see its inspector.

![Image](/images/editor/artboard-list-property.png)

The next step is to bind data to it using Data Binding. This will determine the content and number of items in your List. There are 2 ways to generate List content:

- Using the View Model List property
- Using a View Model Number property together with a Number to List converter

## View Model List Property

<Note>
  Before continuing, it's important to understand the fundamentals of Data Binding, in particular, what a View Model is, how to create one and how to bind it to an object's properties. Learn more in the [Data Binding Overview](/editor/data-binding/overview).
</Note>

A View Model List is a property that can contain a dynamic number of items which each represent a View Model instance. In order to be used in a List, the View Model must be bound to an Artboard.

To Create a View Model List and bind it to an Artboard List:

<Steps>
  <Step title="Create a List Item View Model">
    Navigate to the Data tab in the Editor. Click the + button beside View Models to create a View Model (this will represent your List item)
  </Step>
  <Step title="Bind the List Item View Model to your Item Artboard">
    Bind that View Model to an Artboard that you want to use to render your List item. This is where you may also want to create additional View Model properties and bind those to object properties on that Artboard.
  </Step>
  <Step title="Create your Main View Model">
    Click the + button beside View Models to create another View Model (this will be the View Model that contains your List and should be bound to the Artboard where you want your List to render)
  </Step>
  <Step title="Add a List property">
    Select the newly created View Model and click the + button next to it. From the popout select **List**. This adds a List property to the View Model <img src="/images/editor/list-property.png" alt="Image" />
  </Step>
  <Step title="Add List Items">
    Select the List property and in the inspector on the right, you can add items by clicking Add List item <img src="/images/editor/list-items.png" alt="Image" /> Once a List item is added, you can click the settings button to the left of its name in order to set the View Model and View Model instance for that item
  </Step>
  <Step title="Bind the List property to your Artboard List">
    After adding your List items, go back to the Hierarchy tab, select the Artboard List, and from the Artboard List property dropdown, select the ViewModel List property you created above.
  </Step>
</Steps>

Run the state machine and you should see your list items. Remember that the layout will be determined by the Artboard List's parent, so modify the parent's settings in order to tweak your List's layout

<Note>
  Rive's runtimes provide [APIs to modify the List and List items at runtime](/runtimes/data-binding#lists) (for example, adding or removing items).
</Note>

## View Model Number with Converter

The second way to populate your list is by specifying the number of items you want in your List along with the ViewModel (Artboard) you want to instance. This can be done using a View Model Number property in combination with the new Number to List converter.

To Create a View Model Number to List converter and bind it to an Artboard List:

<Steps>
  <Step title="Create a List Item View Model">
    Navigate to the Data tab in the Editor. Click the + button beside View Models to create a View Model (this will represent your List item)
  </Step>
  <Step title="Bind the List Item View Model to your Item Artboard">
    Bind that View Model to an Artboard that you want to use to render your List item. This is where you may also want to create additional View Model properties and bind those to object properties on that Artboard.
  </Step>
  <Step title="Create your Main View Model">
    Click the + button beside View Models to create another View Model (this will be the View Model that contains your Number property and should be bound to the Artboard where you want your List to render)
  </Step>
  <Step title="Add a Number property">
    Select the newly created View Model and click the + button next to it. From the popout select Number. Select the newly created Number and in the inspector, set the number of items you want in your List
  </Step>
  <Step title="Add a Number to List converter">
    Click the + button and choose **Converters \> List \> Number to List**. <img src="/images/editor/number-to-list.png" alt="Image" />
  </Step>
  <Step title="Set the View Model to use in the converter">
    Select the created converter and in the inspector, choose the View Model that you created earlier that represents your List item. The converter will convert the Number of items to actual Artboard items <img src="/images/editor/number-to-list-property.png" alt="Image" />
  </Step>
  <Step title="Bind the Number property and converter to your Artboard List">
    After adding your Number property and converter, go back to the Hierarchy tab, select the Artboard List, and from the Artboard List property dropdown, select the ViewModel Number property you created above. The Combobox will show a yellow outline. Right click the Combobox and choose Update Bind. In the converter field, select the Number to List converter you created. The yellow outline should change to green.
  </Step>
</Steps>

Run the state machine and you should see your list items. Remember that the layout will be determined by the Artboard List's parent, so modify the parent's settings in order to tweak your List's layout

## View Model List Item Index

There may be times where it is useful for the Artboard to know at which index it exists within its parent List. This is available using the View Model list item index property.

<YouTube id="CHXIOKQOq6Y" />

This can be added to your item's View Model by clicking the + button and selecting **List Attributes \> Index**.

![Image](/images/editor/list-index.png)

This property can then be bound to an object's properties and used directly (for example, to change the position of an object based on the index), used together with a converter (to display the index value as a string) or used as a condition in a state machine (to provide different behavior depending on the item's index).

<Info>
  When using item index with the [List property](/editor/data-binding/lists#view-model-list-property) and list items, be aware that if more than 1 list item is bound to the same View Model instance, they will share the same index value
</Info>

## Lists & Scrolling

If you add your Artboard List as a child of a Layout, your List items will behave as children of its parent's Layout. This means things like direction, wrapping, padding, gap, alignment, etc. are all dictated by the parent Layout's properties.

In addition, if you have applied a [Scroll Constraint](/editor/layouts/scrolling) to the parent Layout, the List items will have the ability to scroll out of the box without any additional setup.

There are additional Scroll properties that can be applied when scrolling Lists. See [List Scrolling](/editor/layouts/scrolling#list-scrolling) for more details.
---
## editor/data-binding/migration-guide.mdx

---
title: "Migration Guide"
description: "Migrate from State Machine Inputs and Listening to Events at runtime to Data Binding"
---

Data binding replaces both **state machine inputs** and **runtime event listeners**, and also removes the need to directly modify elements like text runs from code.

It provides more data types in a more flexible, consistent system for both sending data into Rive and reacting to changes from Rive.

|                        | Inputs | Events | View Model Properties |
| ---------------------- | :----- | :----- | :-------------------- |
| Floating point numbers | ✅      | ✅      | ✅                   |
| Booleans               | ✅      | ✅      | ✅                   |
| Triggers               | ✅      | ❌      | ✅                   |
| Strings                | ❌      | ✅      | ✅                   |
| Enumerations (Enums)   | ❌      | ❌      | ✅                   |
| Colors                 | ❌      | ❌      | ✅                   |
| View Model Nesting     | ❌      | ❌      | ✅                   |
| Lists                  | ❌      | ❌      | ✅                   |
| Images                 | ❌      | ❌      | ✅                   |
| Artboards              | ❌      | ❌      | ✅                   |

<Note>
  You do **not** need to update existing files. Inputs and events will continue to work as expected. Data binding is recommended for new work and future updates.
</Note>


## Migrating from Deprecated Features

### State Machine Inputs

State machine inputs were previously the main way to control animations from code.

With data binding, you instead expose **view model properties** that can drive State machine transitions, Blend states, and Any bindable property in the editor

<Steps>
  <Step>Open the **hamburger menu** in the editor</Step>
  <Step>Select **Convert Inputs to View Models**</Step>
  <Step>Update your runtime code to set values on the view model instead of inputs</Step>
</Steps>

<Note>
  **Why are State Machine Inputs deprecated?**

  Inputs are limited to driving state machine transitions and must be used as-is.

  View model properties:
  - Can drive more than just transitions
  - Can be transformed using [Converters](/editor/data-binding/converters)
  - Can be shared across multiple parts of a file
  - Provide a more flexible and scalable data model
</Note>

#### How to migrate


### Communicating with Code via Events

Events were previously used to send information from a Rive file back to runtime code.

With data binding, you instead **listen to changes on view model properties**, including trigger and lists.

<Note>
  **Why is listening for Events at runtime deprecated?**

  Events had several limitations:

  - Difficult to pass dynamic or changing data
  - Required manual handling to work across nested artboards
  - Represented a one-time signal rather than a persistent value

  View model properties always reflect the latest value and can be observed directly.
</Note>

#### How to migrate

Instead of listening for an event:

- Create a **view model property**
- Update it from your Rive file (via animation, listener, or script)
- Subscribe to that property in your runtime

For more info, see [Data Binding](/runtimes/data-binding)

---

### Updating Text Runs at Runtime

Previously, updating text required:
- Knowing the exact **name**
- Knowing the **hierarchy/path**
- Accessing the text run directly from code

This approach was brittle and easy to break when files changed.

With data binding:
- Bind a **string property** to a text run
- Update the value through the view model

This keeps your runtime code stable even if the structure of your file changes.



## When to Use Data Binding vs Other Features

### Constraints

Constraints are still fully supported and remain the best option for many use cases.

#### When to use constraints

Use constraints when:
- You are linking one object directly to another
- The relationship is purely visual or spatial
- You want a simple, editor-only solution

#### When to use data binding instead

Use data binding when:
- The value needs to come from **runtime code**
- Multiple elements depend on the same value
- You want to introduce **logic or transformation** (via [Converters](/editor/data-binding/converters))
- The relationship isn’t strictly object-to-object

<Tip>

**Example:**

You could:
- Use a **constraint** to link the rotation of multiple wheels together

Or:
- Use a **data-bound `rotation` property** that:
  - Is controlled at runtime
  - Drives all wheels
  - Can be reused elsewhere (speed, effects, UI, etc.)
</Tip>

Data binding is more flexible, while constraints are more direct.
---
## editor/data-binding/overview.mdx

---
title: "Data Binding Overview"
sidebarTitle: "Overview"
description: "Connect editor elements to data and code using View Models"
---

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="M6goAzrDop4" />

Data binding is a powerful way to create reactive connections between editor elements, data, and code. For instance, you might:

- Bind the color of an icon to a color data property that can be adjusted by a developer at runtime
- Bind the X-position of an animated object so that it can be followed with an offset by another object
- Listen for a click event on two buttons to increment and decrement a counter

# Why Use Data Binding?

Data binding decouples design and code by introducing intermediate data that both sides can bind to. This forms the "contract" between designers and developers. Once this contract is in place, both sides can iterate independently, speeding your ability to deliver new features and experiment with what's possible.

Within the editor, data binding allows for more reactivity in your designs. You can establish relationships between objects and ensure that certain invariants hold true, no matter the state of the artboard. The data binding system will ensure that these relationships are always up to date as animations and calls from code change the values.

It also offers the opportunity to shift more logic into the Rive file and out of code. You will need to decide whether a piece of logic lives in code or data binding for your given use case, but one consideration is that any data binding logic will be universal across runtimes, rather than needing separate re-implementations.

# Glossary

Data binding introduces a number of concepts that you will need to familiarize yourself with. The names of these concepts are loosely derived from the Model, View, Viewmodel (MVVM) pattern in software development.

### Editor Element

For the purposes of data binding, an "editor element" simply refers to an editable UI element in the editor with a value that can have a binding attached to it.

### View Model

A view model is a blueprint for a collection of data. Developers might think of this as similar to a class in object-oriented programming. View models typically describe all of the associated data with a given use case - commonly one per artboard. View models themselves don't have concrete values. For that, you must have [an instance](#view-model-instance).

### View Model Property

<YouTube id="NrGz_thkD0g" />

A view model property is one piece of data within a view model. Developers might think of this as similar to a field in object-oriented programming. Properties have a data type which is selected when they are created and a name which can be referenced in code. Each property can be bound to different editor elements of the same type.

#### Adding View Model properties

In the Data panel, click the **Add View Model Property** button next to the view model name and select your [property type](/editor/data-binding/property-types).

![Create a new Enum](/images/editor/data-binding/property-types/add-property.png)

### View Model Instance

A view model instance is the living version of a view model with actual values. Developers might think of this as similar to a class instance in object-oriented programming. Instances have the same properties as the view model they are derived from, except now each of these properties has a living value that can change over time.

You may create as many instances as you'd like from a given view model. Each can be given a unique name associated with what those values represent. Each can have different initial values for its properties, representing a design-time configuration. For example, if you had a menu with three buttons with icons: 🏠 Home, 👤 Profile, and ❓ About, you might have a single artboard representing the menu item, but three view model instances, each with the menu item's label and associated icon, that can be applied to that artboard to configure the buttons.

Artboards are assigned an instance to populate the data bindings. Changing which instance is applied will change the initial state of the properties and all associated bound elements.

In order for an instance to be visible to developers, it must be marked as Exported. Otherwise, it is considered internal to the file. One reason you may want to keep it internal is if you only use the instance to test your design when it is configured with a given set of values, including edge cases.

These exported instances can then be assigned to an artboard at runtime by developers. Alternatively, developers can create empty instances which have default values, such as zero for numbers and empty strings. Once the instance is assigned, its values will begin updating according to the bindings.

### Binding

A binding is an association between a view model property and an editor element. For instance, you might have a string property called "name" bound to a text run. Once bound, the text run will take the value from the view model property. See [Bind Direction](#bind-direction) for additional options.

#### Absolute & Relative Binding
By default, new data binding connections are created as absolute binds.

- Absolute Binding: the bind points the value at a specific property location within the view model tree. For example, "the second property of the first view model".
- Relative Binding: the bind finds the value of property with a specific name, regardless of where it falls within the view model tree. For example, a relative binding to "myNumber" will look for a property of that name within the view model available.

<YouTube id="4LOXhXesG74" />

#### Bind Direction
Bindings can be source to target, target to source, or bidirectional. In this case, "source" means the property, and "target" means the editor element.

<YouTube id="Syt6i4-Bkm4" />

The default binding is source to target. This means that changes to the property update the value of the element. For example, an XPos property updates the X position of an object.

Target to source means that changes to the element's value update the property. For example, the X position of an object updates the XPos property.

Bidirectional means that changes are applied in both directions, meaning either the element or the property can update the other.

Additionally, a binding may be marked as "Bind Once". This means that the initial value will apply and thereafter the binding will not apply any updates.

<YouTube id="OBmP-KxqIyU" />

### View Model Nesting

View models can have another view model as one of their properties. This is referred to as "nesting". This is useful when a parent instance wants to associate with a particular child instance, similar to components.

# Runtime APIs

<YouTube id="IvkNSOFLdNg" />

To continue reading about how to interact with data binding in code, see the [Runtime Overview](/runtimes/data-binding) page.

<Card title="Data Binding Runtime Overview" icon={<svg xmlns="http://www.w3.org/2000/svg" height="100%" fill="none" viewBox="0 0 16 16" class="size-4 text-gray-500/80 dark:text-gray-400" aria-hidden="true"><path fill="currentColor" d="M7.31 7.111 2.406 5.15l4.61-1.844.328-.126a2.3 2.3 0 0 1 1.647 0l.33.126L13.93 5.15 9.024 7.112c-.55.22-1.163.22-1.712 0"></path><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m2.405 10.911 4.906 1.963c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 8.031 7.31 9.992c.55.22 1.162.22 1.712 0l4.906-1.963M2.405 5.15 7.31 7.111c.55.22 1.162.22 1.712 0l4.906-1.962-4.61-1.844-.329-.126a2.3 2.3 0 0 0-1.647 0l-.329.126z"></path></svg>} href="/runtimes/data-binding">
  A dive into using data binding at runtime.
</Card>
---
## editor/data-binding/property-groups.mdx

---
title: "Property Groups"
description: "Create local values that can be keyed, animated, and bound to View Model properties."
---

import { YouTube } from '/snippets/youtube.mdx'
import { Marketplace } from '/snippets/marketplace.mdx'

Property Groups are local, artboard-level values that can be keyed, animated, and bound to View Model properties.

View Model properties are global and shared, while timelines and state machines are local. Property Groups bridge that gap, allowing local animation and logic to read from or drive global data.

## Creating a Property Group

<Steps>
  <Step title="Create a Property Group">
    Select your Property Group tool and click the stage to add one to your artboard.
    ![Create property group](/images/editor/data-binding/property-groups/create-a-group.png)
  </Step>
  <Step title="Add a property">
    Select your Property Group and in the right sidebar, click the `+` icon and select your property type.
    ![Add property to group](/images/editor/data-binding/property-groups/new-property.png)
  </Step>
</Steps>


## Common Use Cases

### Controlling a View Model Property with a Timeline

You can’t key a View Model property directly in the timeline. Instead, you key a Property Group value, then bind that value to a View Model property.

This lets you use [Keyframes](/editor/animate-mode/keys) in a timeline to update View Model data at runtime.

<Info>
  **Why can't I key View Model Properties directly?**

  View Model properties represent global data shared across your app, while keyframes are local to a timeline—so they can’t be keyed directly.
</Info>

<YouTube id="V7GYhd8ZHYg" />

<Marketplace
  href="https://rive.app/community/files/27294-property-groups-demo"
/>

<Steps>
  <Step title="Key a property">
      With the Property Group selected, move the timeline playhead and change the property value to create keyframes.

      ![New Property](/images/editor/data-binding/property-groups/key-property.png)
  </Step>
  <Step title="Bind the property">
      Right-click the property and select the View Model property you want to control. Set the direction to Target → Source so the keyed value drives the View Model property.

      ![Bind Property](/images/editor/data-binding/property-groups/bind-property.png)
  </Step>
</Steps>

When you run your state machine, the View Model property updates based on the keyed Property Group values.

### Controlling one View Model Property with another

You can't directly control one View Model Property with another View Model Property. Instead, you can use a Property Group value that reads one View Model Property and sets another.

<Info>
  **Why can't I control one View Model property with another?**

  Allowing View Model properties to control each other would create hidden dependencies and update loops, so relationships between values are handled explicitly through bindings.
</Info>

In this example we'll have two Number View Model Properties called `myNumber` and `myOtherNumber`, which will be `myNumber` doubled.

<Marketplace
  href="https://rive.app/community/files/27294-property-groups-demo"
/>

<Steps>
  <Step title="Create a Formula Converter">
    Create a new Converter of type Numeric > Formula and add a number value, a multiply operation, and another number.

    ![Add property to group](/images/editor/data-binding/property-groups/number-converter.png)
  </Step>
  <Step title="Bind the number value">
    Bind the first number to `myNumber`.

    ![Bind the first number](/images/editor/data-binding/property-groups/bind-my-number.png)
  </Step>
  <Step title="Control the View Model Property">
    Select the Property Group, right-click the property, and bind it to the `myOtherNumber` value using the converter. Set the direction to Target → Source so the converted value drives the View Model property.

    ![Control a View Model Property](/images/editor/data-binding/property-groups/bind-my-number.png)
  </Step>
</Steps>

When you run your state machine, you should see that `myOtherNumber` is double `myNumber`.

![Doubled](/images/editor/data-binding/property-groups/doubled.png)
---
## editor/data-binding/property-types.mdx

---
title: "Property Types"
sidebarTitle: "Overview"
description: ""
---

import { YouTube } from '/snippets/youtube.mdx'
import { Marketplace } from '/snippets/marketplace.mdx'


| Type                  | Description                         |
| --------------------- | ----------------------------------- |
| Number                | Numeric value                       |
| String                | Text value                          |
| Boolean               | True/false value                    |
| Color                 | RGBA color value                    |
| [Trigger](#trigger)   | Fire-and-forget event               |
| [Enum](#enum)         | One value from a predefined list    |
| [Image](#image)       | Image asset reference               |
| [Artboard](#artboard) | Artboard reference                  |
| [List](#list)         | Collection of values or view models |


## Trigger

Trigger properties represent fire-and-forget events. Use them when you want to signal that something happened, such as a button press or one-time action.

## Enum

Select from a fixed set of options to control states and variants. Use enums when the possible values are known ahead of time.

[Learn more](/editor/data-binding/enums) about enums.

## Image

![Bind an image](/images/editor/data-binding/property-types/image-bind.gif)

Image properties store a reference to an image, allowing you to change which image is displayed.

They are typically bound to image nodes in your design.

Use image properties when each instance needs its own image, such as user avatars, thumbnails, or dynamically loaded content.

For example, in a game or social UI, each player can have their own avatar by binding a different image to the same property.

<Note>
  Image properties affect a **single instance**.

  If you need to update an image globally across your entire file, use [asset loading instead](/runtimes/loading-assets). Asset loading replaces the underlying asset, updating all instances that use it.
</Note>

## Artboard

![Bind an artboard](/images/editor/data-binding/property-types/artboards.gif)

Artboard properties let you reference an artboard and dynamically swap it at runtime.

The artboard can come from your current Rive file or be loaded from another .riv file.

To use an artboard as a property, it must first be [converted to a Component](/editor/fundamentals/components#creating-a-component).

## List

List properties store collections of properties.

For more information, see [Lists](/editor/data-binding/lists)

## Editor perspective — Events

---
## editor/events/audio-events.mdx

---
title: 'Audio Events'
description: ''
---

import { YouTube } from '/snippets/youtube.mdx'

<YouTube id="62j3fbNgxFY" />

Event-based audio provides the means to trigger sound effects within your animations and/or in response to user interactions. Just like existing events, they can be triggered by a keyframe on a timeline, during a state transition, or via a listener.

Audio events represent the first phase of audio features in Rive — they provide an ideal way to trigger sound effects that can be layered on top of each other.

Previously, triggering audio with events would require some work with one of the Rive runtimes and your application or game. The introduction of audio events directly inside the Rive editor streamlines the process of adding sound to your animations — further empowering designers, whilst simplifying the implementation for developers.

<Info>
Audio events are ideal for triggering shorter sounds in response to user interactions or to compliment character animations. Whilst longer form audio — such as background music and voice overs — can also be triggered with audio events, they lack a level of control to manipulate volume, panning, and more over time. 

For use cases requiring greater control over volume and playback, consider using [Scripting](/scripting/getting-started). Check out [AudioSound](/scripting/api-reference/interfaces/audio-sound) and [AudioSource](/scripting/api-reference/interfaces/audio-source) for more information.
</Info>

---

## Audio assets

### Importing audio

Drag and drop audio assets into your Rive file to add them to the assets panel. Alternatively, you can navigate to the assets panel via the tabs at the top of the hierarchy. Select the add action alongside the audio category to prompt your operating system's file browser.

<Info>The integrated sound library provided by Soundly is available to everyone. However, uploading custom audio files is reserved for Pro users.</Info>

### Soundly

We've partnered with Soundly to provide everyone with direct access to their free library of over 3,000 sounds sourced from audio professionals. Find the 'Browse Sounds' option in the toolbar burger menu to browse Soundly's free library.

Select the play action or click on the waveform to preview sounds throughout the Sounds panel. Select the add action to move a chosen sound into your assets panel to use within your Rive file.

### Creating clips

You may want to create a shorter clip from a longer source audio asset, particularly if a selection of sound effects are contained within a single file. To create a clip, start by selecting the source audio file within the assets panel. With a chosen asset selected, a waveform panel will surface at the base of the stage. Use the expander to reveal the waveform.

To create a new clip, click and drag on the waveform to highlight a range. The start and end points can be adjusted via the grey borders. Once you're happy with the clip range, select the add action to save the clip. It'll show up beneath the original audio source in the assets panel.

<info>Clips get generated into new audio files at export time.</info>

Additional clips can be created by selecting the source audio asset and repeating the process. The waveform clipper includes a dropdown menu to switch between existing clips, which can be adjusted as needed.

### Setting volume

Select an audio asset or corresponding clip to set its volume in the inspector. Note that volume can't be keyed over time yet. Upcoming audio features including 'Audio Groups' and 'Audio Emitters' will introduce options to key volume, panning, and more.

### Export options

Like other asset formats, you can configure export options for your audio assets to optimise for runtime.

**Export Type:** Select the audio file in the **Assets** panel and change the **Type** option to define where you'd like the audio file to export to.

![Image](/images/editor/events/a4ebb837-e3fa-4d3d-a730-39faf4914047.webp)

- **Embedded:** Embed the audio file inside the `.riv`. Embedding the audio inside the Rive file is the simplest option, however will increase the size of the file.
- **Referenced:** Export the audio file alongside the `.riv`. This option is ideal if you have multiple Rive files using the same audio asset, or if you'd like to change the audio asset at runtime. Using a referenced audio file will reduce the size of your Rive files.
- **Hosted:** Hosted audio files are uploaded to Rive's CDN for a runtime to download from on demand. Similar to referenced, choosing to host the asset on Rive's CDN will omit it from the `.riv` and reduce the exported file size. The Rive runtimes will fetch the audio when your animation plays in your app, game, or website.

<Info>Assets hosted on Rive's CDN can be accessed by anyone with the link.</Info>

<Note>Hosted assets are available on Voyager and Enterprise plans. [Learn more about our plans and pricing](https://rive.app/pricing?utm_source=docs&utm_medium=content).</Note>

**Format:** choose to export your audio file as a `.wav`, `.flac`, or `.mp3`.

**Quality:** when exporting your audio as an mp3 file, you can additionally set the level of compression via the quality field.

---

## Creating an audio event

The simplest way to create an audio event is to drag your audio asset or clip directly from the assets panel onto the stage. In doing so, an event is created with the preassigned asset. Alternatively, create a regular event by activating the event tool (`SHIFT + E`) and clicking on the stage. Once created, set the type setting in the inspector to Audio. Additional options to assign an asset and browse the Soundly library will be presented for audio events.

## Triggering an audio event

Like regular events, audio events can be triggered in a selection of different ways:

- **Timeline:** Whilst in animate mode, with a timeline selected, the event inspector will surface a button to key the event. Keying an event causes it to be reported. In the context of an audio event, reporting it will start the playback of the assigned audio asset.
- **Transitions:** Select a transition node within a State Machine and add an event via the inspector. You can choose whether the event should be reported at the start or at the end of the transition.
- **Listeners:** Select a listener within a State Machine and add a 'report event' action via the inspector. The pointer option will determine when the audio will play. For example, a pointer down listener with an assigned audio event targeting a shape will start playback when the user clicks on the shape.

### Monitoring audio

Audio levels can be monitored via the VU meter at the base of the inspector. Use the VU meter to check for clipping. This may occur if multiple audio events are playing at once, causing the overall output to clip. If you notice peak levels turning red, consider lowering the volume of your audio asset to provide more headroom.

---
## editor/events/general-events.mdx

---
title: 'Events at Runtime'
description: "Using events to communicate with runtime code (deprecated)"
noindex: true;
---
import { YouTube } from "/snippets/youtube.mdx";

<Warning>
  **DEPRECATION NOTICE:**

  [Rive Events](/editor/events/overview) are still fully supported within a Rive file. However, using events to communicate with runtime code is deprecated.

  **For new projects:** Use [Data Binding](/editor/data-binding) instead.

  **This content is provided for legacy support only.**
</Warning>

For general information about adding, creating, and signaling events, see [Rive Events](/editor/events/overview).

<YouTube id="M5DIDVtYI_Y" />

General Events were previously used to send signals from a Rive file to runtime code. They allowed designers and developers to coordinate behavior by passing event data at specific moments in an animation.

This approach has been deprecated in favor of [Data Binding](/editor/data-binding/), which provides a more structured and predictable way to communicate with runtime code.

## Properties

Properties allow you to attach additional data to an Event that can be read by the runtime.

To add a new property, click the `+` button next to Properties.

![Add New Property](https://ucarecdn.com/d4cd3b8f-3765-4c28-9204-e5daf7fff0d8/)

Give your property a clear name, then choose the type of value it represents, which can be a Number, Boolean, or String.

![Rename and select input](https://ucarecdn.com/73d05fb1-7c9c-4c9c-a17c-51781ef30d0e/)

You can key a property on the timeline to update its value over time. When the Event is reported, the runtime receives the current value of each property.
---
## editor/events/open-url-events.mdx

---
title: 'Open URL Events'
description: "Using events to open URLs at runtime"
noindex: true;
---

<Warning>
  Open URL Events are not supported on Apple or Android runtimes.
</Warning>

<Note>
  For security reasons, Open URL Events are disabled by default in web runtimes.

  To enable them, set `automaticallyHandleEvents` to `true`.
</Note>

<Note>
  For security reasons, Open URL Events are disabled in share links and on the Rive Marketplace.
</Note>

For general information about adding, creating, and signaling events, see [Rive Events](/editor/events/overview).

### URL Properties

When you select the **Open URL** Event type, additional configuration options become available.

![Image](https://1159711764-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F-M3EXlibk6bj2FzPQW-9%2Fuploads%2FrDR98sXAUkNZXqBbv0sy%2FCleanShot%202023-09-18%20at%2013.06.14%402x.png?alt=media&token=0c681b87-2667-48d3-aa24-3b550732032e)

Enter the URL you want to open.

<Info>
  Include the URL protocol (for example, `http://` or `https://`) when linking to external domains.
</Info>

The **Target** determines where the URL opens in the browser.

- `Blank` — Opens the link in a new tab or window, depending on browser settings.
  **Note:** If the Event is not triggered by a user interaction (for example, via a Listener), the browser may block it as a popup.
- `Parent` — Opens in the parent browsing context. If no parent exists, behaves like `Self`.
- `Self` — Opens in the current browsing context.
- `Top` — Opens in the topmost browsing context. If no ancestor exists, behaves like `Self`.

<Info>
  For security reasons, URLs are not opened by default in embeds or Marketplace posts. This behavior may change in the future.
</Info>

### Properties (Deprecated)

Properties allow an Event to carry additional data to the runtime.

This feature is deprecated and has been replaced by [Data Binding](/editor/data-binding).

---
## editor/events/overview.mdx

---
title: 'Events Overview'
sidebarTitle: 'Overview'
description: "Creating and signaling Rive Events"
---
import { YouTube } from "/snippets/youtube.mdx";

Events live within an artboard and are used to signal that something has happened. They can be fired from timelines, states, transitions, or listeners.

Rive supports three types of events:

- [Open URL Event](/editor/events/open-url-events) — Opens a URL at runtime
- [Audio Event](/editor/events/audio-events) — Plays a sound
- [General Event (deprecated)](/editor/events/general-events) — Previously used to communicate with runtime code

## Creating an Event

<Steps>
  <Step title="Create an Event">
    Use the Events tool located in the toolbar and click anywhere on the artboard.

    ![Adding a new event](https://ucarecdn.com/4ed6c563-4c59-42c8-b40c-f502d5a8e1a4/)

    You'll notice that the event is displayed on the artboard and in the Hierarchy.
  </Step>
  <Step title="Name your Event">
    Give your event a name so it’s easy to identify and reference.

    You can rename it using the **Name** field, or by double-clicking the name directly on the artboard.

    ![Renaming an event](https://ucarecdn.com/4558fb61-4649-4210-9ec6-c828c48ab2b2/)
  </Step>
  <Step title="Select an Event type">
    The Type dropdown allows you to change the event type between Audio, URL, and General.

    ![Image](https://ucarecdn.com/9621c007-de2e-428c-95d7-837615a37caa/)
  </Step>
  <Step title="Set your Event Properties">
    Each event type has its own set of properties.

    For more information on the specific event types, see [Open URL Events](/editor/events/open-url-events), [Audio Events](/editor/events/audio-events), and [General Events (deprecated)](/editor/events/general-events).
  </Step>
</Steps>


## Signaling an Event

We can signal an event in four ways: from a timeline, a listener, a state, or a transition.

### Timeline

Signaling an event from the timeline lets you control the exact moment in an animation when the event fires.

First, select the timeline you want to add the event to. Then use the **Report Event** button in the Inspector.

![Keying an Event on the timeline](https://ucarecdn.com/bd8d36f9-9cd1-4eec-9c37-85d4a0a19643/)

### Transition & State

You can report an event on a transition or a state. To report an event, select the desired state or transition and use the `+` button next to the Events section in the Inspector.


![Signaling an event via state or transition](https://ucarecdn.com/d1a63666-0cce-408f-9364-826eed66b241/)

Now that we've selected the event, we can decide whether it is signaled at the start or end of the transition or state.

### Listeners

With your [Listener](/editor/state-machine/listeners) selected, click the `+` below the State Machine Graph, and select **Report Event**.

![Trigger an event with a listener](/images/editor/events/trigger-events-with-listeners.gif)
