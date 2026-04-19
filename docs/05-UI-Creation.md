# Chapter 5 — UI Creation

[Back to Index](index.md) | [Previous: Controller Input](04-Controller-Input.md) | [Next: Asset Bundles](06-Asset-Bundles.md)

---

## Overview

RMAPI can create two types of in-world UI elements:

- **Text** — floating TextMeshPro labels in 3D space
- **Buttons** — interactive buttons that players can press (using RUMBLE's interaction system)

Both are cloned from existing game objects, so they look and behave like native RUMBLE UI.

```csharp
using RumbleModdingAPI.RMAPI;
using UnityEngine;
```

> **Important:** These objects are only available after the Gym scene has loaded at least once
> (that's when RMAPI clones the templates). Use them inside `onMapInitialized` or later.

---

## Creating Text

### Basic Text (empty, configure it yourself)

```csharp
GameObject textObj = Create.NewText();
```

Returns a new active TextMeshPro GameObject. You configure it manually:

```csharp
using Il2CppTMPro;

GameObject textObj = Create.NewText();
TextMeshPro tmp = textObj.GetComponent<TextMeshPro>();
tmp.text = "Hello World";
tmp.fontSize = 2.0f;
tmp.color = Color.white;
textObj.transform.position = new Vector3(0, 2, 0);
textObj.transform.rotation = Quaternion.identity;
```

### Text with Parameters (all-in-one)

Parameters in order:

| # | Parameter | Type | What it sets |
|---|-----------|------|-------------|
| 1 | `text` | `string` | The displayed text |
| 2 | `textSize` | `float` | Font size |
| 3 | `textColor` | `Color` | Text color |
| 4 | `textPosition` | `Vector3` | World position |
| 5 | `textRotation` | `Quaternion` | World rotation |

```csharp
GameObject textObj = Create.NewText("Score: 0", 1.5f, Color.green, new Vector3(0, 2.5f, 3), Quaternion.Euler(0, 180, 0));
```

### Updating Text Later

Keep a reference and modify it whenever you need:

```csharp
private TextMeshPro scoreText;

void Setup()
{
    GameObject obj = Create.NewText("0", 2f, Color.white, Vector3.up * 2, Quaternion.identity);
    scoreText = obj.GetComponent<TextMeshPro>();
}

void UpdateScore(int score)
{
    scoreText.text = $"Score: {score}";
    scoreText.color = score > 10 ? Color.green : Color.red;
}
```

---

## Creating Buttons

Buttons use RUMBLE's `InteractionButton` component — players interact with them the same way
they interact with in-game buttons (by pressing/touching them in VR).

`NewButton` has four versions — pick the one that matches what you need:

| Version | What you get |
|---------|-------------|
| `NewButton()` | Button at default position, no action |
| `NewButton(position, rotation)` | Button at a specific spot, no action |
| `NewButton(action)` | Button at default position, runs your code when pressed |
| `NewButton(position, rotation, action)` | Button at a specific spot, runs your code when pressed |

> **Note:** You always need `()` after `Create.NewButton` — writing `Create.NewButton` alone
> without parentheses doesn't create anything and will cause a compile error.
> Even `Create.NewButton()` with empty parentheses is valid — it creates a button with defaults.

### Basic Button (no position, no action)

```csharp
GameObject buttonObj = Create.NewButton();
```

### Button at a Position

| # | Parameter | Type | What it sets |
|---|-----------|------|-------------|
| 1 | `buttonPosition` | `Vector3` | World position |
| 2 | `buttonRotation` | `Quaternion` | World rotation |

```csharp
GameObject buttonObj = Create.NewButton(new Vector3(1, 1.5f, 2), Quaternion.Euler(0, 90, 0));
```

### Button with an Action

| # | Parameter | Type | What it sets |
|---|-----------|------|-------------|
| 1 | `action` | `Action` | Method to call when pressed |

Pass a method or lambda that runs when the button is pressed:

```csharp
GameObject buttonObj = Create.NewButton(() => Melon<MyMod>.Logger.Msg("Button was pressed!"));
```

> **What's `() =>`?** This is a **lambda** — a short inline function. `() =>` means "a function
> that takes no parameters", and what follows is the code it runs. There are two ways to pass
> an action, and both work:
>
> **Inline lambda** — write the code directly:
> `Create.NewButton(() => Melon<MyMod>.Logger.Msg("pressed!"))`
>
> **Method reference** — define a method and pass its name (without `()`, because you're
> handing the method itself to be called later, not calling it now):
> `Create.NewButton(OnPressed)` where you have `void OnPressed() { ... }` elsewhere.

### Button with Position and Action

| # | Parameter | Type | What it sets |
|---|-----------|------|-------------|
| 1 | `buttonPosition` | `Vector3` | World position |
| 2 | `buttonRotation` | `Quaternion` | World rotation |
| 3 | `action` | `Action` | Method to call when pressed |

```csharp
GameObject buttonObj = Create.NewButton(new Vector3(1, 1.5f, 2), Quaternion.identity, () => Melon<MyMod>.Logger.Msg("Button was pressed!"));
```

### Adding an Action to an Existing Button

If you used `NewButton()` without an action, you can add one later:

```csharp
using Il2CppRUMBLE.Interactions.InteractionBase;

GameObject buttonObj = Create.NewButton();
InteractionButton interactBtn = buttonObj.transform.GetChild(0)
    .gameObject.GetComponent<InteractionButton>();
interactBtn.onPressed.AddListener((Action)(() =>
{
    Log("Pressed!");
}));
```

---

## Cleaning Up

GameObjects that aren't in `DontDestroyOnLoad` are **automatically destroyed on scene change**
(including between matches). So in most cases you don't need to clean up — your text and
buttons disappear on their own when the player leaves the scene.

If you need to remove something **mid-scene** (e.g., hiding a label after a timer expires),
you can either destroy it or deactivate it:

```csharp
// Destroy — permanently removes it (cleaner if you won't need it again)
GameObject.Destroy(textObj);

// Deactivate — hides it but keeps it around (useful if you want to show it again later)
textObj.SetActive(false);
// ... later:
textObj.SetActive(true);
```

If you want an object to survive scene changes, call `DontDestroyOnLoad` on it:

```csharp
GameObject.DontDestroyOnLoad(textObj);
```

---

## Full Example: In-World Scoreboard

```csharp
using MelonLoader;
using RumbleModdingAPI.RMAPI;
using Il2CppTMPro;
using Il2CppRUMBLE.Players;
using UnityEngine;

namespace Scoreboard
{
    public class Scoreboard : MelonMod
    {
        private TextMeshPro display;
        private int myScore = 0;
        private int theirScore = 0;

        public override void OnLateInitializeMelon()
        {
            Actions.onMatchStarted += OnMatch;
            Actions.onRoundEnded += OnRoundEnd;
        }

        private void OnMatch()
        {
            myScore = 0;
            theirScore = 0;

            // Create a scoreboard floating in front of the player
            Player local = Calls.Players.GetLocalPlayer();
            Transform t = local.Controller.transform;
            Vector3 pos = t.position + t.forward * 2 + Vector3.up * 1.5f;
            Quaternion rot = Quaternion.LookRotation(pos - t.position);

            GameObject displayObj = Create.NewText("0 - 0", 3f, Color.white, pos, rot);
            display = displayObj.GetComponent<TextMeshPro>();
        }

        private void OnRoundEnd()
        {
            // Simple: whoever has more HP wins the round
            var players = Calls.Players.GetAllPlayers();
            if (players.Count < 2) return;

            Player local = Calls.Players.GetLocalPlayer();
            if (local.Data.HealthPoints > 0)
                myScore++;
            else
                theirScore++;

            if (display != null)
                display.text = $"{myScore} - {theirScore}";
        }
    }
}
```

---

[Back to Index](index.md) | [Previous: Controller Input](04-Controller-Input.md) | [Next: Asset Bundles](06-Asset-Bundles.md)
