# Chapter 3 — Game Queries

[Back to Index](index.md) | [Previous: Events](02-Events.md) | [Next: Controller Input](04-Controller-Input.md)

---

## Overview

The `Calls` class lets you **read** game state — what scene you're in, who's playing,
what matchmaking type was selected, and what mods everyone has.

```csharp
using RumbleModdingAPI.RMAPI;
// Then use: Calls.Scene.GetSceneName(), Calls.Players.GetLocalPlayer(), etc.
```

---

## API Status

```csharp
// Has RMAPI finished its one-time setup? (true after Loader scene)
bool ready = Calls.IsInitialized();

// Have the current scene's GameObjects been cached?
bool mapReady = Calls.IsMapInitialized();
```

---

## Scene

```csharp
Calls.Scene.GetSceneName()       // Returns: "Loader", "Gym", "Park", "Map0", or "Map1"
Calls.Scene.GetLastSceneName()   // Returns the previous scene name
```

**Example:**
```csharp
Actions.onMapInitialized += (sceneName) =>
{
    string previous = Calls.Scene.GetLastSceneName();
    Log($"Moved from {previous} to {sceneName}");
};
```

---

## Players

All player queries require the scene to be initialized. Use them inside `onMapInitialized` or later.

| Method | Returns | Description |
|--------|---------|-------------|
| `Calls.Players.GetLocalPlayer()` | `Player` | Your own player |
| `Calls.Players.GetLocalPlayerController()` | `PlayerController` | Your own player's controller |
| `Calls.Players.GetAllPlayers()` | `Il2CppSystem...List<Player>` | Everyone in the session |
| `Calls.Players.GetEnemyPlayers()` | `List<Player>` | Everyone except you |
| `Calls.Players.IsHost()` | `bool` | Are you the Photon master client? |
| `Calls.Players.GetClosestPlayer(position, ignoreLocalController)` | `Player` | Nearest player to a point |
| `Calls.Players.GetClosestPlayer(position, ignoreController)` | `Player` | Nearest player, ignoring a specific one |
| `Calls.Players.GetPlayerByActorNo(actorNumber)` | `Player` | Find player by Photon actor number |
| `Calls.Players.GetPlayerByControllerType(controllerType)` | `Player` | Find player by controller type |
| `Calls.Players.GetPlayersInActorNoOrder()` | `List<Player>` | Players sorted by who joined first |

> **Note:** `GetAllPlayers()` returns an `Il2CppSystem.Collections.Generic.List<Player>`, not a
> regular C# `List<Player>`. You can still iterate over it with `foreach` and access `.Count`,
> but be aware of the difference if you need to pass it to methods expecting a standard `List`.

**Example — Get opponent's name:**
```csharp
Actions.onMatchStarted += () =>
{
    var enemies = Calls.Players.GetEnemyPlayers();
    if (enemies.Count > 0)
    {
        string opponentName = enemies[0].Data.GeneralData.PublicUsername;
        Log($"Fighting: {opponentName}");
    }
};
```

**Example — Closest player to a world position:**
```csharp
Vector3 somePosition = new Vector3(0, 1, 0);
Player nearest = Calls.Players.GetClosestPlayer(somePosition, true);
```

### Useful Player Properties

Once you have a `Player` object, here's what you can read from it:

```csharp
Player player = Calls.Players.GetLocalPlayer();

player.Data.GeneralData.PublicUsername    // Display name (string)
player.Data.GeneralData.PlayFabMasterId  // Unique account ID (string)
player.Data.GeneralData.ActorNo          // Photon actor number (int)
player.Data.HealthPoints                 // Current HP, max 20 (int)
player.Controller                        // The PlayerController component
player.Controller.gameObject             // The player's root GameObject
```

---

## Matchmaking

Only meaningful on Map0/Map1 (returns `"NULL"` / `-1` elsewhere).

```csharp
// As a readable string
string type = Calls.Matchmaking.getMatchmakingTypeAsString();
// Returns: "Any Rank", "Same Rank", or "Friends Only"

// As an integer
int typeInt = Calls.Matchmaking.getMatchmakingTypeAsInt();
// Returns: 0 = Any Rank, 1 = Same Rank, 2 = Friends Only, -1 = not in a match
```

**Example:**
```csharp
Actions.onMatchStarted += () =>
{
    string queue = Calls.Matchmaking.getMatchmakingTypeAsString();
    Log($"Queue type: {queue}");
};
```

---

## Mods

### Your Mods

```csharp
// Get your mod list as a pipe-separated string
string myModString = Calls.Mods.getMyModString();
// Example: "RumbleModdingAPI|5.1.1|MyMod|1.0.0"

// Get your mod list as structured objects
List<ModInfo> myMods = Calls.Mods.getMyMods();
foreach (var mod in myMods)
{
    Log($"{mod.ModName} v{mod.ModVersion}");
}

// Check if you have a specific mod
bool hasMod = Calls.Mods.findOwnMod("SomeMod", "1.0.0");            // exact version
bool hasModAny = Calls.Mods.findOwnMod("SomeMod", "", false);       // any version
```

### Opponent's Mods

These only work **during a match** (Map0/Map1) after `onModStringRecieved` fires.

```csharp
// Get opponent's mod list as a string
string theirMods = Calls.Mods.getOpponentModString();

// Get as structured objects
List<ModInfo> opponentMods = Calls.Mods.getOpponentMods();

// Check if opponent has a specific mod
bool compatible = Calls.Mods.doesOpponentHaveMod("SharedMod", "1.0.0");          // exact version
bool hasItAtAll = Calls.Mods.doesOpponentHaveMod("SharedMod", "", false);        // any version
```

**Example — Compatibility check:**
```csharp
Actions.onModStringRecieved += () =>
{
    if (Calls.Mods.doesOpponentHaveMod("MyCoolMod", "2.0.0"))
    {
        Log("Opponent has MyCoolMod v2.0.0 — enabling shared features");
    }
    else
    {
        Log("Opponent doesn't have MyCoolMod — disabling shared features");
    }
};
```

---

## ModInfo Class

```csharp
public class ModInfo
{
    public string ModName;      // e.g., "RumbleModdingAPI"
    public string ModVersion;   // e.g., "5.1.1"
}
```

You don't create these yourself — they come from `getMyMods()` and `getOpponentMods()`.

---

[Back to Index](index.md) | [Previous: Events](02-Events.md) | [Next: Controller Input](04-Controller-Input.md)
