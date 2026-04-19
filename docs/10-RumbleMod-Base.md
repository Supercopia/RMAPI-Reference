# Chapter 10 — RumbleMod Base Class

[Back to Index](index.md) | [Previous: GameObject Registry](09-GameObject-Registry.md)

---

## Overview

`RumbleMod` is an extended version of `MelonMod` with **built-in Photon networking**.
If your mod needs to send custom data to other players, inherit from `RumbleMod` instead
of `MelonMod`.

```csharp
using RumbleModdingAPI.RMAPI;
using static RumbleModdingAPI.RMAPI.Utilities;
```

---

## Setup

### Step 1: Inherit from RumbleMod

```csharp
public class MyMod : Utilities.RumbleMod   // NOT MelonMod
{
    // ...
}
```

### Step 2: Register for Events

Call `RegisterEvents()` once your mod is ready (typically in `OnLateInitializeMelon`):

```csharp
public override void OnLateInitializeMelon()
{
    RegisterEvents();  // registers this mod with the RaiseEventManager
}
```

This registers your mod under the key `"YourModName|YourAuthorName"` so incoming events
can be routed to the correct mod.

---

## Sending Data

Use `RaiseEvent()` to send a list of data objects to other players:

```csharp
using Il2CppPhoton.Realtime;
using Il2CppExitGames.Client.Photon;

void SendData()
{
    // Build your data list
    var data = new List<Il2CppSystem.Object>();
    data.Add((Il2CppSystem.String)"some string data");
    data.Add((Il2CppSystem.Int32)42);
    data.Add((Il2CppSystem.Single)3.14f);

    // Configure delivery
    RaiseEventOptions options = new RaiseEventOptions()
    {
        Receivers = ReceiverGroup.Others,           // send to everyone except yourself
        CachingOption = EventCaching.DoNotCache     // or AddToRoomCache to replay for late joiners
    };

    // Send it
    RaiseEvent(data, options, SendOptions.SendReliable);
}
```

### What Gets Sent

RMAPI automatically prepends your mod's identifier (`"ModName|AuthorName"`) to the data.
The receiving side uses this to route the event to the correct mod. You don't need to handle
this — just put your actual data in the list.

### Data Types

The data list uses `Il2CppSystem.Object`. Common types you can send:

| C# Type | Il2Cpp Cast |
|---------|------------|
| `string` | `(Il2CppSystem.String)"text"` |
| `int` | `(Il2CppSystem.Int32)42` |
| `float` | `(Il2CppSystem.Single)3.14f` |
| `bool` | `(Il2CppSystem.Boolean)true` |

---

## Receiving Data

Override `OnEvent()` to handle incoming data from the other player:

```csharp
public override void OnEvent(List<Il2CppSystem.Object> data)
{
    // data[0], data[1], etc. — your data (mod identifier already stripped)
    string message = data[0].ToString();
    int number = int.Parse(data[1].ToString());

    Melon<MyMod>.Logger.Msg($"Received: {message}, {number}");
}
```

> **Note:** The mod identifier is already removed from the list. `data[0]` is the first
> item YOU added, not the routing prefix.

---

## Built-in Asset Bundle Loading

`RumbleMod` also has a convenience method for loading embedded asset bundles:

```csharp
UnityEngine.Il2CppAssetBundle bundle = LoadAssetBundle("MyNamespace.myassets");
GameObject prefab = bundle.LoadAsset<GameObject>("MyPrefab");
GameObject instance = UnityEngine.Object.Instantiate(prefab);
bundle.Unload(false);
```

This loads from an embedded resource in your mod's DLL. See [Chapter 6](06-Asset-Bundles.md)
for more asset bundle options.

---

## Full Example: Synced Counter

Two players each have a button. When either presses it, both see the counter go up.

```csharp
using MelonLoader;
using RumbleModdingAPI.RMAPI;
using static RumbleModdingAPI.RMAPI.Utilities;
using Il2CppPhoton.Realtime;
using Il2CppExitGames.Client.Photon;
using Il2CppTMPro;
using UnityEngine;

[assembly: MelonInfo(typeof(SyncCounter.SyncCounter), "SyncCounter", "1.0.0", "Me")]
[assembly: MelonGame("Buckethead Entertainment", "RUMBLE")]

namespace SyncCounter
{
    public class SyncCounter : Utilities.RumbleMod
    {
        private int counter = 0;
        private TextMeshPro display;

        public override void OnLateInitializeMelon()
        {
            RegisterEvents();
            Actions.onMapInitialized += OnMap;
        }

        private void OnMap(string scene)
        {
            if (scene != "Map0" && scene != "Map1") return;

            counter = 0;

            // Create a display
            GameObject textObj = Create.NewText("Count: 0", 2f, Color.cyan, new Vector3(0, 2, 0), Quaternion.identity);
            display = textObj.GetComponent<TextMeshPro>();

            // Create a button that increments and syncs
            Create.NewButton(
                new Vector3(0, 1, 1),
                Quaternion.identity,
                (System.Action)(() => OnButtonPress())
            );
        }

        private void OnButtonPress()
        {
            // Increment locally
            counter++;
            UpdateDisplay();

            // Send to opponent
            var data = new List<Il2CppSystem.Object>();
            data.Add((Il2CppSystem.Int32)counter);

            RaiseEventOptions options = new RaiseEventOptions()
            {
                Receivers = ReceiverGroup.Others
            };

            RaiseEvent(data, options, SendOptions.SendReliable);
        }

        public override void OnEvent(List<Il2CppSystem.Object> data)
        {
            // Received counter value from opponent
            counter = int.Parse(data[0].ToString());
            UpdateDisplay();
        }

        private void UpdateDisplay()
        {
            if (display != null)
                display.text = $"Count: {counter}";
        }
    }
}
```

---

## DoNotDisable Component

RMAPI includes a utility component that prevents a GameObject from being disabled:

```csharp
myGameObject.AddComponent<Utilities.DoNotDisable>();
// Now if anything calls SetActive(false) on it, it immediately re-enables itself
```

Useful for keeping persistent UI or manager objects alive across scene transitions.

---

## Summary

| Feature | MelonMod | RumbleMod |
|---------|----------|-----------|
| Standard mod lifecycle | Yes | Yes (inherits MelonMod) |
| `RaiseEvent()` networking | No | Yes |
| `OnEvent()` handler | No | Yes |
| `RegisterEvents()` | No | Yes |
| `LoadAssetBundle()` (embedded) | No | Yes |
| Use RMAPI events/calls | Yes | Yes |

**Rule of thumb:** Use `MelonMod` if your mod is local-only. Use `RumbleMod` if you need to
send data to other players.

---

[Back to Index](index.md) | [Previous: GameObject Registry](09-GameObject-Registry.md)
