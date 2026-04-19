# Chapter 8 — Networking

[Back to Index](index.md) | [Previous: Audio](07-Audio.md) | [Next: GameObject Registry](09-GameObject-Registry.md)

---

## Overview

RMAPI provides three networking systems built on top of Photon:

1. **Mod Exchange** — automatically shares your mod list with opponents (built-in, no code needed)
2. **RaiseEvent System** — send custom data to other players via `RumbleMod`
3. **Custom Photon RPCs** — register your own RPC methods for precise networked calls

---

## 1. Mod Exchange (Automatic)

This works out of the box. When you join a match (Map0/Map1):

- RMAPI sends your mod list to the opponent via Photon event code 15
- When the opponent's list arrives, `Actions.onModStringReceived` fires
- You can then query the opponent's mods via `Calls.Mods`

**You don't need to write any code for this.** Just subscribe to the event if you want to react:

```csharp
Actions.onModStringReceived += () =>
{
    if (Calls.Mods.doesOpponentHaveMod("MyCoolMod", "", matchVersion: false))
    {
        // Enable shared features
    }
};
```

See [Chapter 3 — Game Queries](03-Game-Queries.md#mods) for the full mod query API.

---

## 2. RaiseEvent System (Custom Data)

For sending arbitrary data to other players, use the `RumbleMod` base class instead of `MelonMod`.

> See [Chapter 10 — RumbleMod Base Class](10-RumbleMod-Base.md) for the full guide.

Quick summary:

```csharp
using Il2CppPhoton.Realtime;
using Il2CppExitGames.Client.Photon;

public class MyMod : Utilities.RumbleMod  // inherit RumbleMod instead of MelonMod
{
    public override void OnLateInitializeMelon()
    {
        RegisterEvents();  // register with the event router
    }

    void SendSomething()
    {
        var data = new List<Il2CppSystem.Object>();
        data.Add((Il2CppSystem.String)"hello");

        RaiseEventOptions options = new RaiseEventOptions()
        {
            Receivers = ReceiverGroup.Others  // send to everyone except yourself
        };
        RaiseEvent(data, options, SendOptions.SendReliable);
    }

    public override void OnEvent(List<Il2CppSystem.Object> data)
    {
        // Received data from the other player
        string message = data[0].ToString();
    }
}
```

---

## 3. Custom Photon RPCs

Photon RPCs let you call a specific method on a remote player's instance of a component.
RMAPI patches Photon to support custom RPCs in modded components.

### How It Works

1. You mark a method with `[PhotonRPCs.PunRPC]`
2. The method must be inside a class that inherits from `MonoBehaviourPun` (or a type registered with Il2Cpp)
3. RMAPI scans all loaded mods at startup and registers any methods with this attribute
4. Photon can then route RPC calls to your method

### Defining an RPC

```csharp
using RumbleModdingAPI.RMAPI;
using Il2CppPhoton.Pun;

public class MyNetworkComponent : MonoBehaviourPun
{
    [PhotonRPCs.PunRPC]
    public void SyncPosition(float x, float y, float z)
    {
        transform.position = new Vector3(x, y, z);
    }
}
```

### Calling an RPC

Use Photon's standard `photonView.RPC()` to invoke it:

```csharp
photonView.RPC("SyncPosition", RpcTarget.Others, 1.0f, 2.0f, 3.0f);
```

### Registration Details

RMAPI handles registration automatically at startup:

- Scans every loaded MelonMod's assembly for methods with `[PhotonRPCs.PunRPC]`
- Adds each method name to `PhotonNetwork.rpcShortcuts` and `PhotonNetwork.PhotonServerSettings.RpcList`
- Patches `SupportClass.GetMethods` so Photon can discover your methods at runtime

You don't need to call any registration methods yourself.

---

## Which System Should I Use?

| Scenario | Use |
|----------|-----|
| Check if opponent has a specific mod | Mod Exchange (automatic) |
| Send simple one-off data to opponent | RaiseEvent (via `RumbleMod`) |
| Sync state on a specific networked object | Custom Photon RPCs |
| Real-time continuous sync (positions, etc.) | Custom Photon RPCs |

### Key Differences

| Feature | RaiseEvent | Photon RPCs |
|---------|-----------|-------------|
| Requires specific component? | No (mod-level) | Yes (MonoBehaviourPun) |
| Routing | By mod name/author | By method name on a PhotonView |
| Data format | `List<Il2CppSystem.Object>` | Method parameters |
| Best for | Mod-to-mod messages | Component-level sync |

---

## Tips

- **Always check player count** before sending network events — don't send if you're alone
- **RaiseEvent uses Photon event code 18** — don't use that code for your own raw events
- **Mod exchange uses code 15** — also reserved
- **RPCs only work on objects with a PhotonView** — that's a Photon requirement, not an RMAPI one
- **Test with two instances** — you need two players to test any networking

---

[Back to Index](index.md) | [Previous: Audio](07-Audio.md) | [Next: GameObject Registry](09-GameObject-Registry.md)
