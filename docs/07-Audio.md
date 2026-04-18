# Chapter 7 — Audio

[Back to Index](index.md) | [Previous: Asset Bundles](06-Asset-Bundles.md) | [Next: Networking](08-Networking.md)

---

## Overview

RMAPI lets you load **.wav files** from disk and play them as 3D positional audio using
RUMBLE's native audio system.

```csharp
using RumbleModdingAPI.RMAPI;
using Il2CppRUMBLE.Audio;
using UnityEngine;
```

> **Reminder:** All names in these examples are arbitrary — variable names (`hitSound`, `mySound`),
> folder names (`MyMod`, `HitSound`), and file names (`explosion.wav`, `bonk.wav`) can be whatever
> you want. Only the RMAPI method names are real. See [Chapter 1](01-Getting-Started.md#a-note-on-names-in-this-guide) for details.

The workflow is:

1. **Create** an `AudioCall` from a .wav file (do this once — in `OnLateInitializeMelon` or on the first `onMapInitialized`, which fires for Gym, Park, Map0, and Map1)
2. **Play** it whenever you want at a world position (only after a scene has loaded and the game's AudioManager is ready)

---

## Step 1: Create an AudioCall

### Single Sound

```csharp
AudioCall mySound = AudioManager.CreateAudioCall(
    filePath: @"UserData\MyMod\explosion.wav",
    volume:   0.8f    // 0.0 = silent, 1.0 = full volume
);
```

Returns `null` if the file doesn't exist or can't be parsed.

### Multiple Sounds at Once

```csharp
string[] paths = new string[]
{
    @"UserData\MyMod\hit1.wav",
    @"UserData\MyMod\hit2.wav",
    @"UserData\MyMod\hit3.wav"
};

AudioCall[] sounds = AudioManager.CreateAudioCalls(paths, volume: 0.5f);
// sounds[0] = hit1, sounds[1] = hit2, sounds[2] = hit3
// Any entry will be null if that file failed to load
```

### What Happens Under the Hood

- The .wav file is parsed manually (supports standard PCM WAV)
- A Unity `AudioClip` is created in memory
- An `AudioCall` ScriptableObject is created with the clip attached
- Both are marked `HideAndDontSave` so they persist across scenes

---

## Step 2: Play the Sound

```csharp
// Play at a specific world position
AudioManager.PlaySound(mySound, new Vector3(0, 1, 0));

// Play with looping
AudioManager.PlaySound(mySound, somePosition, isLooping: true);
```

`PlaySound` returns a `PooledAudioSource` — RUMBLE manages the audio source lifecycle for you.

### Play at the Player's Position

```csharp
Vector3 playerPos = Calls.Players.GetLocalPlayer().Controller.transform.position;
AudioManager.PlaySound(mySound, playerPos);
```

---

## Loading Raw AudioClips

If you want just the `AudioClip` without wrapping it in an `AudioCall`:

```csharp
AudioClip clip = AudioManager.LoadWavFile(@"UserData\MyMod\mysound.wav");
// Returns null if the file doesn't exist or is invalid
```

You can use this clip with your own `AudioSource` components.

---

## Method Summary

| Method | Returns | Description |
|--------|---------|-------------|
| `CreateAudioCall(filePath, volume)` | `AudioCall` | Create a playable sound from a .wav file |
| `CreateAudioCalls(filePaths[], volume)` | `AudioCall[]` | Batch-create multiple sounds |
| `PlaySound(audioCall, position, isLooping?)` | `PooledAudioSource` | Play a sound at a world position |
| `LoadWavFile(filePath)` | `AudioClip` | Load a raw AudioClip from a .wav file |

---

## Requirements and Limitations

- **Only .wav files** are supported (not .mp3, .ogg, etc.)
- The .wav must be standard **PCM format** (16-bit)
- Create your `AudioCall` objects **once** (e.g., at startup) — don't recreate them every time you play
- Sounds are **3D positional** — they get quieter with distance from the listener

---

## Full Example: Hit Sound on Damage

```csharp
using MelonLoader;
using RumbleModdingAPI.RMAPI;
using Il2CppRUMBLE.Audio;
using Il2CppRUMBLE.Players;
using UnityEngine;

namespace HitSound
{
    public class HitSound : MelonMod
    {
        private AudioCall hitSound;

        public override void OnLateInitializeMelon()
        {
            hitSound = AudioManager.CreateAudioCall(@"UserData\HitSound\bonk.wav", 0.7f);

            if (hitSound == null)
            {
                Melon<HitSound>.Logger.Error("Failed to load bonk.wav!");
                return;
            }

            Actions.onPlayerHealthChanged += OnDamage;
        }

        private void OnDamage(Player player, int damage)
        {
            if (damage <= 0) return; // only on actual damage, not healing

            Vector3 pos = player.Controller.transform.position;
            AudioManager.PlaySound(hitSound, pos);
        }
    }
}
```

---

[Back to Index](index.md) | [Previous: Asset Bundles](06-Asset-Bundles.md) | [Next: Networking](08-Networking.md)
