# Chapter 9 — GameObject Registry

[Back to Index](index.md) | [Previous: Networking](08-Networking.md) | [Next: RumbleMod Base Class](10-RumbleMod-Base.md)

---

## Overview

RMAPI maps out nearly **every GameObject** in RUMBLE's scenes as a static class hierarchy.
Instead of searching for objects by name at runtime, you navigate a tree of nested classes
and call `.GetGameObject()` to get the actual Unity `GameObject`.

```csharp
using RumbleModdingAPI.RMAPI;
using UnityEngine;
```

> **Important:** Only access these after `onMapInitialized` fires for the relevant scene.
> The objects are cached when the scene loads — calling `.GetGameObject()` before that returns `null`.

---

## How It Works

Every node in the hierarchy is a nested class with a static `GetGameObject()` method:

```csharp
// Get the match console in the Gym
GameObject matchConsole = GameObjects.Gym.INTERACTABLES.MatchConsole.GetGameObject();

// Get the leaderboard
GameObject leaderboard = GameObjects.Gym.INTERACTABLES.Leaderboard.GetGameObject();

// Get a child deeper in the tree
GameObject slider = GameObjects.Gym.INTERACTABLES.MatchConsole
    .MatchmakingSettings.InteractionSliderHorizontalGrip.GetGameObject();
```

Under the hood, each `GetGameObject()` calls `transform.GetChild(index).gameObject` starting
from the cached root objects. It's just shorthand for navigating the transform hierarchy by index.

---

## Scenes Available

The registry covers five areas:

| Class | Scene | Description |
|-------|-------|-------------|
| `GameObjects.DDOL` | DontDestroyOnLoad | Persistent managers (audio, pools, players) |
| `GameObjects.Gym` | Gym | The solo gym / lobby |
| `GameObjects.Park` | Park | The park hangout area |
| `GameObjects.Map0` | Map0 | Battle arena #1 |
| `GameObjects.Map1` | Map1 | Battle arena #2 |

---

## DDOL (DontDestroyOnLoad)

These objects persist across all scenes. Available after `Calls.IsInitialized()` is true.

```
GameObjects.DDOL
├── LanguageManager
├── PhotonMono
├── GameInstance
│   ├── PreInitializable
│   │   ├── AudioManager
│   │   ├── PoolManager
│   │   │   ├── Pool (Wrapped Wall)
│   │   │   ├── Pool (Prisoned Pillar)
│   │   │   ├── Pool (Docked Disk)
│   │   │   ├── Pool (Cage Cube)
│   │   │   ├── Pool (Fruit variants)
│   │   │   ├── Pool (VFX)
│   │   │   ├── Pool (Match pedestals, slabs, info slabs)
│   │   │   └── ... many more pools
│   │   ├── SceneManager
│   │   ├── RecordingCamera
│   │   └── PlayerManager
│   ├── Initializable
│   │   ├── PlayFabManager
│   │   ├── MatchmakingHandler
│   │   ├── SocialHandler
│   │   ├── LeaderboardManager
│   │   ├── DailyShiftStoneManager
│   │   └── ... more managers
│   └── PostInitializable
│       ├── NetworkManager
│       └── QualityManager
└── TimerUpdater
```

**Example — Access the PlayerManager:**
```csharp
GameObject playerMgr = GameObjects.DDOL.GameInstance.PreInitializable.PlayerManager.GetGameObject();
```

---

## Gym

The solo training gym with all its interactables.

```
GameObjects.Gym
├── ftraceLightmaps
├── ProbeVolumePerSceneData
├── SCENEVFXSFX
├── SCENE
│   └── (geometry, environment objects)
├── INTERACTABLES
│   ├── MatchConsole
│   │   └── MatchmakingSettings
│   │       └── InteractionSliderHorizontalGrip (queue type slider)
│   ├── Leaderboard
│   │   └── PlayerTags / HighscoreTag / Nr (text templates)
│   ├── Boulderball
│   ├── CombatReader
│   └── ... more interactables
├── TUTORIAL
│   └── Statictutorials
│       └── RUMBLEStarterGuide
│           └── NextPageButton (button template)
├── LIGHTING
└── LOGIC
```

**Common uses:**

```csharp
// Get the match console (the thing you interact with to queue)
GameObject console = GameObjects.Gym.INTERACTABLES.MatchConsole.GetGameObject();

// Get the combat reader / training dummy area
// (navigate the specific child path you need)
```

---

## Park

The multiplayer park hangout area.

```
GameObjects.Park
├── LOGIC
├── ftraceLightmaps
├── ProbeVolumePerSceneData
├── INTERACTABLES
├── LIGHTING
├── SCENEVFXSFX
└── SCENE
```

---

## Map0 and Map1

The battle arenas. The most important objects here are the **match slabs** (the UI that
appears at match end).

```
GameObjects.Map0
├── Logic
│   └── MatchSlabOne
│       └── MatchSlab
│           └── Slabbuddymatchvariant
│               └── MatchForm
│                   └── MatchFormCanvas  ← used to detect match end
├── LightingEffects
└── Scene

GameObjects.Map1
├── LightingEffects
├── Logic
│   └── MatchSlabTwo
│       └── MatchSlab
│           └── Slabbuddymatchvariant
│               └── MatchForm
│                   └── MatchFormCanvas
└── Scene
```

**Example — Check if the match end UI is showing:**
```csharp
bool matchEndVisible = GameObjects.Map0.Logic.MatchSlabOne.MatchSlab
    .Slabbuddymatchvariant.MatchForm.MatchFormCanvas.GetGameObject().activeSelf;
```

---

## Getting Root Objects

Each scene has a method to get the cached root arrays:

```csharp
GameObject[] ddolRoots = GameObjects.DDOL.GetBaseDDOLGameObjects();
GameObject[] gymRoots  = GameObjects.Gym.GetBaseGymGameObjects();
GameObject[] parkRoots = GameObjects.Park.GetBaseParkGameObjects();
GameObject[] map0Roots = GameObjects.Map0.GetBaseMap0GameObjects();
GameObject[] map1Roots = GameObjects.Map1.GetBaseMap1GameObjects();
```

---

## Full Object Trees

Need to find a specific object? Browse the complete collapsible trees:

- [DDOL](tree-ddol.md) — persistent managers, pools, UI
- [Gym](tree-gym.md) — interactables, tutorial, leaderboard
- [Park](tree-park.md) — notifications, gondola, interactables
- [Map0](tree-map0.md) — match slabs, pedestals, scene geometry
- [Map1](tree-map1.md) — match slabs, pedestals, scene geometry

---

## Tips

- **The hierarchy is huge** (~42,000 lines of code). Use your IDE's autocomplete to navigate it,
  or browse the [full object trees](#full-object-trees) above.
  Type `GameObjects.Gym.` and let IntelliSense show you what's available.
- **Each `.GetGameObject()` walks the transform tree from a cached root.** It's cheap but not free.
  Cache the result in a variable if you'll access it repeatedly.
- **Objects are scene-specific.** Don't access `GameObjects.Gym.*` when you're in Map0.
  Check `Calls.Scene.GetSceneName()` first.
- **If you get `null`**, you're probably accessing before `onMapInitialized` or in the wrong scene.

---

## Full Example: Hide the Leaderboard in the Gym

```csharp
using MelonLoader;
using RumbleModdingAPI.RMAPI;

namespace HideLeaderboard
{
    public class HideLeaderboard : MelonMod
    {
        public override void OnLateInitializeMelon()
        {
            Actions.onMapInitialized += OnMap;
        }

        private void OnMap(string scene)
        {
            if (scene != "Gym") return;

            var leaderboard = GameObjects.Gym.INTERACTABLES.Leaderboard.GetGameObject();
            leaderboard.SetActive(false);
            Melon<HideLeaderboard>.Logger.Msg("Leaderboard hidden");
        }
    }
}
```

---

[Back to Index](index.md) | [Previous: Networking](08-Networking.md) | [Next: RumbleMod Base Class](10-RumbleMod-Base.md)
