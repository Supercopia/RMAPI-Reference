# Chapter 4 — Controller Input

[Back to Index](index.md) | [Previous: Game Queries](03-Game-Queries.md) | [Next: UI Creation](05-UI-Creation.md)

---

## Overview

RMAPI gives you two ways to read VR controller input:

1. **Raw values** via `Calls.ControllerMap` — simple float/Vector2 reads
2. **ControllerInputPoller** — a richer system with pressed/released detection per frame

Both work for left and right controllers and cover: trigger, grip, primary button (A/X),
secondary button (B/Y), joystick position, and joystick click.

---

## Option 1: Raw Values (`Calls.ControllerMap`)

Simple one-shot reads. Good for checking "is the trigger held right now?"

```csharp
using RumbleModdingAPI.RMAPI;
```

### Right Controller

| Method | Returns | What it reads |
|--------|---------|---------------|
| `Calls.ControllerMap.RightController.GetTrigger()` | `float` (0.0 - 1.0) | Right trigger squeeze |
| `Calls.ControllerMap.RightController.GetGrip()` | `float` (0.0 - 1.0) | Right grip squeeze |
| `Calls.ControllerMap.RightController.GetPrimary()` | `float` (0.0 or 1.0) | Right A button |
| `Calls.ControllerMap.RightController.GetSecondary()` | `float` (0.0 or 1.0) | Right B button |
| `Calls.ControllerMap.RightController.GetJoystick()` | `Vector2` (-1 to 1) | Right joystick XY |
| `Calls.ControllerMap.RightController.GetJoystickClick()` | `float` (0.0 or 1.0) | Right stick pressed |

### Left Controller

Same methods, just replace `RightController` with `LeftController`:

| Method | Returns | What it reads |
|--------|---------|---------------|
| `Calls.ControllerMap.LeftController.GetTrigger()` | `float` (0.0 - 1.0) | Left trigger squeeze |
| `Calls.ControllerMap.LeftController.GetGrip()` | `float` (0.0 - 1.0) | Left grip squeeze |
| `Calls.ControllerMap.LeftController.GetPrimary()` | `float` (0.0 or 1.0) | Left X button |
| `Calls.ControllerMap.LeftController.GetSecondary()` | `float` (0.0 or 1.0) | Left Y button |
| `Calls.ControllerMap.LeftController.GetJoystick()` | `Vector2` (-1 to 1) | Left joystick XY |
| `Calls.ControllerMap.LeftController.GetJoystickClick()` | `float` (0.0 or 1.0) | Left stick pressed |

**Example:**
```csharp
float triggerValue = Calls.ControllerMap.RightController.GetTrigger();
if (triggerValue > 0.5f)
{
    Log("Right trigger is squeezed");
}
```

---

## Option 2: ControllerInputPoller (Recommended)

This is a more advanced system that tracks **state changes** across frames.
It tells you not just "is the button pressed" but "was it pressed THIS frame" and
"was it released THIS frame."

```csharp
using RumbleModdingAPI.RMAPI;
using static RumbleModdingAPI.RMAPI.Utilities;
```

### What's Available Per Button

Every button exposes a `Button` object with these fields:

| Field | Type | Meaning |
|-------|------|---------|
| `.pressed` | `bool` | Is the button currently held down? |
| `.value` | `float` | Raw analog value (0.0 to 1.0) |
| `.wasPressedThisFrame` | `bool` | Did the button go from up to down THIS frame? |
| `.wasReleasedThisFrame` | `bool` | Did the button go from down to up THIS frame? |

> A button counts as "pressed" when its value exceeds **0.25** (the deadzone threshold).

### Available Buttons

```csharp
// Right controller
ControllerInputPoller.RightController.trigger
ControllerInputPoller.RightController.grip
ControllerInputPoller.RightController.primaryButton       // A button
ControllerInputPoller.RightController.secondaryButton     // B button
ControllerInputPoller.RightController.joystickClick
ControllerInputPoller.RightController.joystickPosition    // Vector2 (not a Button)

// Left controller
ControllerInputPoller.LeftController.trigger
ControllerInputPoller.LeftController.grip
ControllerInputPoller.LeftController.primaryButton        // X button
ControllerInputPoller.LeftController.secondaryButton      // Y button
ControllerInputPoller.LeftController.joystickClick
ControllerInputPoller.LeftController.joystickPosition     // Vector2 (not a Button)
```

### Examples

**Detect a single button press (not held):**
```csharp
// In an Update loop or coroutine:
if (ControllerInputPoller.RightController.primaryButton.wasPressedThisFrame)
{
    Log("A button just pressed!");
    // This only fires ONCE per press, not every frame
}
```

**Detect button release:**
```csharp
if (ControllerInputPoller.LeftController.grip.wasReleasedThisFrame)
{
    Log("Left grip released");
}
```

**Check if held down:**
```csharp
if (ControllerInputPoller.RightController.trigger.pressed)
{
    Log("Right trigger is held");  // fires every frame while held
}
```

**Read analog trigger value:**
```csharp
float squeeze = ControllerInputPoller.RightController.trigger.value;
// 0.0 = not squeezed, 1.0 = fully squeezed
```

**Read joystick direction:**
```csharp
Vector2 stick = ControllerInputPoller.LeftController.joystickPosition;
if (stick.y > 0.5f)
{
    Log("Left stick pushed forward");
}
```

---

## Quick Comparison

| Feature | Raw (`Calls.ControllerMap`) | `ControllerInputPoller` |
|---------|----------------------------|------------------------|
| Current value | Yes | Yes (`.value`) |
| Is pressed? | Manual check (`> threshold`) | Yes (`.pressed`) |
| Pressed this frame? | No | Yes (`.wasPressedThisFrame`) |
| Released this frame? | No | Yes (`.wasReleasedThisFrame`) |
| Best for | Simple checks | Game logic, menus, toggles |

**Recommendation:** Use `ControllerInputPoller` for most things. Use raw values if you need
the exact analog float and don't care about state transitions.

---

## Full Example: Toggle with A Button

```csharp
using MelonLoader;
using RumbleModdingAPI.RMAPI;
using static RumbleModdingAPI.RMAPI.Utilities;
using System.Collections;
using UnityEngine;

namespace MyMod
{
    public class MyMod : MelonMod
    {
        private bool featureEnabled = false;
        private bool inputLoopRunning = false;

        public override void OnLateInitializeMelon()
        {
            Actions.onMapInitialized += (scene) =>
            {
                if (!inputLoopRunning)
                {
                    inputLoopRunning = true;
                    MelonCoroutines.Start(InputLoop());
                }
            };
        }

        private IEnumerator InputLoop()
        {
            while (true)
            {
                if (ControllerInputPoller.RightController.primaryButton.wasPressedThisFrame)
                {
                    featureEnabled = !featureEnabled;
                    Melon<MyMod>.Logger.Msg($"Feature: {(featureEnabled ? "ON" : "OFF")}");
                }
                yield return null; // wait one frame
            }
        }
    }
}
```

---

[Back to Index](index.md) | [Previous: Game Queries](03-Game-Queries.md) | [Next: UI Creation](05-UI-Creation.md)
