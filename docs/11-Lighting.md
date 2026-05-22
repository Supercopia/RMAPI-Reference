# Chapter 11 — Lighting

[Back to Index](index.md) | [Previous: RumbleMod Base Class](10-RumbleMod-Base.md)

---

## Overview

The `Lighting` class (added in RMAPI **5.3.0**) controls a scene's **ambient
lighting** — the soft, directionless light applied to every dynamically lit
surface. It is the merged form of the old "Optimized Graphics Fix" mod.

```csharp
using RumbleModdingAPI.RMAPI;
using UnityEngine;
```

Ambient lighting is a **per-scene** setting in Unity, so RMAPI reapplies your
chosen values automatically every time a new scene loads — set them once and
they stick.

---

## Ambient Modes

Unity has two ambient modes, and `UseBounceLighting` switches between them:

```csharp
Lighting.UseBounceLighting(true);   // Trilight — sky/horizon/ground colors apply
Lighting.UseBounceLighting(false);  // Skybox — ambient comes from the skybox (default)
```

- **Trilight** blends three colors across each surface (top, sides, bottom).
  The three `Set*Color` methods below only have a visible effect in this mode.
- **Skybox** derives ambient light from the scene's skybox. This is RUMBLE's
  default for most scenes (the Loader scene already uses Trilight).

---

## Ambient Colors

Three methods set the Trilight colors. Each takes a nullable `Color` — pass
`null` (or call with no argument) to reset that color to RUMBLE's default.

```csharp
Lighting.SetSkyLightColor(new Color(0.5f, 0.6f, 0.9f));   // light on surface tops
Lighting.SetHorizonLightColor(Color.gray);                // light on surface sides
Lighting.SetGroundLightColor(new Color(0.1f, 0.05f, 0f)); // light on surface bottoms

Lighting.SetSkyLightColor();      // reset sky color to default
Lighting.SetHorizonLightColor();  // reset horizon color to default
Lighting.SetGroundLightColor();   // reset ground color to default
```

| Method | Affects | Default color (RGB) |
|--------|---------|---------------------|
| `SetSkyLightColor` | Top of lit surfaces | `0.350, 0.428, 0.584` |
| `SetHorizonLightColor` | Sides of lit surfaces | `0.114, 0.125, 0.133` |
| `SetGroundLightColor` | Bottom of lit surfaces | `0.047, 0.043, 0.035` |

---

## Locking

Multiple mods may want to control lighting. The lock prevents your settings
from being changed by another mod.

```csharp
Lighting.Lock();          // lock with priority 1 (default)
Lighting.Lock(5);         // lock with a higher priority

Lighting.Unlock();        // unlock with priority 1
Lighting.Unlock(5);       // unlock with priority 5
```

- While locked, **every** `Lighting` setter (`UseBounceLighting`, `Set*Color`)
  is a no-op — including calls from the mod that holds the lock.
- `Unlock` is **ignored** if the current lock has a higher priority *and* was
  taken by a different mod. A mod can always unlock its own lock.

> **Be a good citizen.** Pick a low lock priority. Your mod is not the main
> character — only raise the priority if you have a genuine reason to override
> everyone else, and expect other mods to respect the same courtesy.

---

## Method Summary

| Method | Description |
|--------|-------------|
| `UseBounceLighting(bool)` | `true` = Trilight, `false` = Skybox |
| `SetSkyLightColor(Color?)` | Top-of-surface light color (`null` resets) |
| `SetHorizonLightColor(Color?)` | Side-of-surface light color (`null` resets) |
| `SetGroundLightColor(Color?)` | Bottom-of-surface light color (`null` resets) |
| `Lock(int priority = 1)` | Block other mods from changing lighting |
| `Unlock(int priority = 1)` | Release the lock (ignored if outranked) |

---

## Full Example: Warm Evening Lighting

```csharp
using MelonLoader;
using RumbleModdingAPI.RMAPI;
using UnityEngine;

namespace WarmLighting
{
    public class WarmLighting : MelonMod
    {
        public override void OnLateInitializeMelon()
        {
            // Switch to Trilight so the color methods take effect
            Lighting.UseBounceLighting(true);

            Lighting.SetSkyLightColor(new Color(0.9f, 0.6f, 0.4f));
            Lighting.SetHorizonLightColor(new Color(0.4f, 0.25f, 0.2f));
            Lighting.SetGroundLightColor(new Color(0.1f, 0.06f, 0.04f));

            // Hold the look so other mods don't overwrite it
            Lighting.Lock();
        }
    }
}
```

---

[Back to Index](index.md) | [Previous: RumbleMod Base Class](10-RumbleMod-Base.md)
