# Chapter 2 — Events

[Back to Index](index.md) | [Previous: Getting Started](01-Getting-Started.md) | [Next: Game Queries](03-Game-Queries.md)

---

## Overview

RMAPI provides a set of **C# events** you can subscribe to. When something happens in the game,
RMAPI fires the matching event and your code runs automatically.

All events live in:
```csharp
using RumbleModdingAPI.RMAPI;
// Then use: Actions.onSomething += YourMethod;
```

**Where to subscribe:** In your mod's `OnLateInitializeMelon()` method.

**Safety:** If your listener throws an exception, RMAPI catches it and continues calling the other
listeners. Your bug won't break other mods.

---

## All Events

### onMyModsGathered

```csharp
public static event Action onMyModsGathered;
```

**When it fires:** Once, shortly after the game boots (during the Loader scene).
Your local mod list has been collected.

**Use case:** Initialize anything that depends on knowing which mods are loaded.

```csharp
Actions.onMyModsGathered += () =>
{
    var myMods = Calls.Mods.getMyMods();
    Melon<MyMod>.Logger.Msg($"I have {myMods.Count} mods loaded");
};
```

---

### onMapInitialized

```csharp
public static event Action<string> onMapInitialized;
```

**When it fires:** Each time a scene finishes loading AND the local player exists.
Passes the scene name as a string (`"Gym"`, `"Park"`, `"Map0"`, `"Map1"`).

**Use case:** This is your main "scene is ready" hook. Access GameObjects after this fires.

```csharp
Actions.onMapInitialized += (sceneName) =>
{
    if (sceneName == "Gym")
    {
        // Safe to access Gym GameObjects now
    }
};
```

---

### onPlayerSpawned

```csharp
public static event Action<Player> onPlayerSpawned;
```

**When it fires:** Every time a player's `PlayerController` is initialized (local or remote).
Passes the `Player` object.

**Use case:** React to players joining — e.g., display info, track them, customize appearance.

```csharp
using Il2CppRUMBLE.Players;

Actions.onPlayerSpawned += (Player player) =>
{
    string name = player.Data.GeneralData.PublicUsername;
    Melon<MyMod>.Logger.Msg($"Player spawned: {name}");
};
```

---

### onMatchStarted

```csharp
public static event Action onMatchStarted;
```

**When it fires:** When you load into Map0 or Map1 with another player present.

**Use case:** Start tracking match-related state, display a HUD, reset scores.

```csharp
Actions.onMatchStarted += () =>
{
    Melon<MyMod>.Logger.Msg("Match started!");
};
```

---

### onMatchEnded

```csharp
public static event Action onMatchEnded;
```

**When it fires:** When the match ends normally (the match slab UI appears) or when an
opponent disconnects mid-match.

**Use case:** Clean up match state, show results.

---

### onRoundStarted

```csharp
public static event Action onRoundStarted;
```

**When it fires:** At the beginning of each round within a match. Also fires at the same time as
`onMatchStarted` for the first round.

**Use case:** Reset per-round state (timers, counters, etc.).

---

### onRoundEnded

```csharp
public static event Action onRoundEnded;
```

**When it fires:** When any player's health hits 0, ending the round.

**Use case:** Record round results, show a round summary.

---

### onPlayerHealthChanged

```csharp
public static event Action<Player, int> onPlayerHealthChanged;
```

**When it fires:** Every frame that a player's health is different from the previous frame.
Passes the `Player` and the **damage amount** (positive = damage taken, the delta is
`previousHealth - currentHealth`).

**Use case:** Damage tracking, hit counters, health-bar mods.

```csharp
Actions.onPlayerHealthChanged += (Player player, int damage) =>
{
    string name = player.Data.GeneralData.PublicUsername;
    Melon<MyMod>.Logger.Msg($"{name} took {damage} damage");
};
```

> **Note:** Health is polled every fixed update starting 3.2 seconds after scene load
> (to skip the initial heal-to-full). Max health is 20.

---

### onModStringReceived

```csharp
public static event Action onModStringReceived;
```

> **Note:** The old spelling `onModStringRecieved` still works but is deprecated.
> Use `onModStringReceived` (correct spelling) for new code.

**When it fires:** When the opponent's mod list arrives over the network (Map0/Map1 only).

**Use case:** Check mod compatibility, display opponent's mods.

```csharp
Actions.onModStringReceived += () =>
{
    var theirMods = Calls.Mods.getOpponentMods();
    foreach (var mod in theirMods)
    {
        Melon<MyMod>.Logger.Msg($"Opponent has: {mod.ModName} v{mod.ModVersion}");
    }
};
```

---

## Event Lifecycle Diagram

Here's the order events fire in a typical match:

```
Scene loads (Map0 or Map1)
  │
  ├── onPlayerSpawned(localPlayer)       ← may fire before or after map init
  ├── onPlayerSpawned(remotePlayer)      ← may fire before or after map init
  │
  ├── onMapInitialized("Map0")
  ├── onMatchStarted                     ← fires right after map init if 2 players
  ├── onRoundStarted                     ← round 1 (fires right after match start)
  │     │
  │     ├── onModStringReceived          ← arrives asynchronously over the network
  │     │
  │     ├── onPlayerHealthChanged(...)   ← repeated as hits land
  │     │
  │     └── onRoundEnded                 ← someone hit 0 HP
  │
  ├── onRoundStarted                     ← round 2 (health resets to 20)
  │     │
  │     └── onRoundEnded
  │
  └── onMatchEnded                       ← match slab appears or opponent disconnects
```

> **Note:** `onPlayerSpawned` fires from a separate Harmony patch, so its timing relative to
> `onMapInitialized` is not guaranteed. `onModStringReceived` arrives over the network and
> could fire at any point during the match — don't assume it arrives before the first round.

---

## Full Example: Match Logger

```csharp
using MelonLoader;
using RumbleModdingAPI.RMAPI;
using Il2CppRUMBLE.Players;

[assembly: MelonInfo(typeof(MatchLogger.MatchLogger), "MatchLogger", "1.0.0", "Me")]
[assembly: MelonGame("Buckethead Entertainment", "RUMBLE")]

namespace MatchLogger
{
    public class MatchLogger : MelonMod
    {
        public override void OnLateInitializeMelon()
        {
            Actions.onMatchStarted += () => Log("=== MATCH START ===");
            Actions.onRoundStarted += () => Log("--- Round Start ---");
            Actions.onPlayerHealthChanged += OnDamage;
            Actions.onRoundEnded += () => Log("--- Round End ---");
            Actions.onMatchEnded += () => Log("=== MATCH END ===");
        }

        private void OnDamage(Player player, int damage)
        {
            Log($"{player.Data.GeneralData.PublicUsername} took {damage} damage");
        }

        private void Log(string msg)
        {
            Melon<MatchLogger>.Logger.Msg(msg);
        }
    }
}
```

---

[Back to Index](index.md) | [Previous: Getting Started](01-Getting-Started.md) | [Next: Game Queries](03-Game-Queries.md)
