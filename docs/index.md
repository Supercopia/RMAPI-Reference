# RMAPI Reference Book

**RumbleModdingAPI v5.1.4** — The modding framework for RUMBLE (VR)

This reference is organized into chapters. Each one covers a self-contained feature of RMAPI.
Pick the chapter that matches what you're trying to do.

---

## Chapters

| # | Chapter | What it covers |
|---|---------|---------------|
| 1 | [Getting Started](01-Getting-Started.md) | What RMAPI is, how to set it up, your first mod |
| 2 | [Events](02-Events.md) | Reacting to game moments (match start, round end, player spawn, etc.) |
| 3 | [Game Queries](03-Game-Queries.md) | Reading game state: scene name, players, matchmaking type, mod lists |
| 4 | [Controller Input](04-Controller-Input.md) | Reading VR controller buttons, triggers, grips, and joysticks |
| 5 | [UI Creation](05-UI-Creation.md) | Spawning text labels and interactive buttons in the world |
| 6 | [Asset Bundles](06-Asset-Bundles.md) | Loading custom models, prefabs, and assets into the game |
| 7 | [Audio](07-Audio.md) | Loading .wav files and playing custom sounds |
| 8 | [Networking](08-Networking.md) | Sending data to other players, custom Photon RPCs, mod exchange |
| 9 | [GameObject Registry](09-GameObject-Registry.md) | Accessing any built-in GameObject by name (Gym, Park, Map0, Map1) |
| 10 | [RumbleMod Base Class](10-RumbleMod-Base.md) | Using RumbleMod instead of MelonMod for built-in networking |

---

## Quick "I want to..." Guide

| I want to... | Go to |
|---------------|-------|
| Set up my first mod project | [Getting Started](01-Getting-Started.md#setting-up-your-mod-project) |
| Run code when a match starts | [Events](02-Events.md#onmatchstarted) |
| Know when a player takes damage | [Events](02-Events.md#onplayerhealthchanged) |
| Get the local player object | [Game Queries](03-Game-Queries.md#players) |
| Check what scene I'm in | [Game Queries](03-Game-Queries.md#scene) |
| See what mods the opponent is running | [Game Queries](03-Game-Queries.md#mods) |
| Check if opponent has a specific mod | [Game Queries](03-Game-Queries.md#opponents-mods) |
| Read a button press on the VR controller | [Controller Input](04-Controller-Input.md) |
| Detect a button press/release this frame | [Controller Input](04-Controller-Input.md#option-2-controllerinputpoller-recommended) |
| Put text in the world | [UI Creation](05-UI-Creation.md#creating-text) |
| Make a clickable button | [UI Creation](05-UI-Creation.md#creating-buttons) |
| Load a custom 3D model | [Asset Bundles](06-Asset-Bundles.md) |
| Play a custom sound effect | [Audio](07-Audio.md) |
| Send data to your opponent | [Networking](08-Networking.md) |
| Access a specific in-game object | [GameObject Registry](09-GameObject-Registry.md) |

---

## Full Object Trees

Complete collapsible trees for every scene — expand any node to see its children.
Use these to find the exact class path for any GameObject.

| Scene | Description |
|-------|-------------|
| [DDOL](tree-ddol.md) | DontDestroyOnLoad — persistent managers, pools, UI |
| [Gym](tree-gym.md) | Solo gym / lobby — interactables, tutorial, leaderboard |
| [Park](tree-park.md) | Park hangout area — notifications, gondola, interactables |
| [Map0](tree-map0.md) | Battle arena #1 — match slabs, pedestals, scene geometry |
| [Map1](tree-map1.md) | Battle arena #2 — match slabs, pedestals, scene geometry |

---

## Namespaces at a Glance

```
RumbleModdingAPI                        // Main mod class, ModInfo
RumbleModdingAPI.RMAPI.Actions          // Event system
RumbleModdingAPI.RMAPI.Calls            // Game queries (scene, players, mods, input)
RumbleModdingAPI.RMAPI.Create           // UI factory (text, buttons)
RumbleModdingAPI.RMAPI.AssetBundles     // Asset bundle loading
RumbleModdingAPI.RMAPI.AudioManager     // Audio loading and playback
RumbleModdingAPI.RMAPI.GameObjects      // Static GameObject registry
RumbleModdingAPI.RMAPI.Utilities        // RumbleMod base, ControllerInputPoller, RaiseEventManager
RumbleModdingAPI.RMAPI.PhotonRPCs       // Custom Photon RPC system
```

---

*RMAPI is created and maintained by UlvakSkillz. If you find it useful, consider
[supporting them on Ko-fi](https://ko-fi.com/ulvakskillz).*
