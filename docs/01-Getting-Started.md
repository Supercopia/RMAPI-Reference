# Chapter 1 — Getting Started

[Back to Index](index.md) | [Next: Events](02-Events.md)

---

## A Note on Names in This Guide

Every name you see in these examples is **completely arbitrary**. You can change any of them
to whatever you want:

- **Variable names** — `bundlePath`, `hitSound`, `myMods`, `textObj` — pick whatever makes sense to you
- **Folder names** — `UserData\MyMod\` could be `UserData\CoolStuff\` or `UserData\Bob\`
- **File names** — `myassets`, `bonk.wav`, `hat` — name them anything
- **Namespace and class names** — `MyMod`, `HitSound`, `MatchLogger` — your choice
- **Asset Bundle extensions** — `.bundle`, `.assetbundle`, no extension at all — Unity doesn't enforce one

The only names that are **not** arbitrary are:
- **RMAPI method and class names** — `Actions.onMatchStarted`, `Create.NewText()`, `Calls.Players.GetLocalPlayer()`, etc.
- **MelonLoader attributes** — `[assembly: MelonInfo(...)]`, `[assembly: MelonGame(...)]`
- **The game name in MelonGame** — must be `"Buckethead Entertainment"` and `"RUMBLE"`

If an example says `string bundlePath = @"UserData\MyMod\myassets"`, all three parts
(`bundlePath`, `MyMod`, `myassets`) are names we made up. Only `AssetBundles.LoadAssetBundleFromFile()`
is the real API call.

---

## What is RMAPI?

RumbleModdingAPI (RMAPI) is a **MelonLoader mod** that acts as a shared foundation for other RUMBLE mods.
It does the heavy lifting so you don't have to:

- Caches every important GameObject in each scene so you can access them by name
- Fires events when interesting things happen (match starts, player spawns, health changes, etc.)
- Provides helpers for reading VR controller input, loading assets, playing audio, and creating UI
- Handles Photon networking plumbing for mod-to-mod communication

**You don't run RMAPI on its own.** You build your mod on top of it, referencing it as a dependency.

---

## Prerequisites

1. **RUMBLE** installed (Steam VR game)
2. **MelonLoader** installed into RUMBLE
3. A C# development environment (Visual Studio, Rider, or VS Code)
4. Basic familiarity with C# and Unity concepts (GameObjects, Components, Transforms)

---

## Setting Up Your Mod Project

### Step 1 — Create a new C# Class Library

Target **.NET 6.0**.

### Step 2 — Add references to your .csproj

Your project needs `<Reference>` entries pointing to DLLs from your RUMBLE install folder.
**Without these, your code won't compile** — the compiler needs to know where RMAPI, MelonLoader,
and the game's types live.

Here's a minimal `.csproj` showing the references. Replace the paths with your own RUMBLE install location:

```xml
<ItemGroup>
  <!-- MelonLoader runtime (from MelonLoader/net6/) -->
  <Reference Include="MelonLoader">
    <HintPath>YOUR_RUMBLE_PATH\MelonLoader\net6\MelonLoader.dll</HintPath>
  </Reference>
  <Reference Include="0Harmony">
    <HintPath>YOUR_RUMBLE_PATH\MelonLoader\net6\0Harmony.dll</HintPath>
  </Reference>
  <Reference Include="Il2CppInterop.Runtime">
    <HintPath>YOUR_RUMBLE_PATH\MelonLoader\net6\Il2CppInterop.Runtime.dll</HintPath>
  </Reference>

  <!-- Game assemblies (from MelonLoader/Il2CppAssemblies/) -->
  <Reference Include="Il2Cppmscorlib">
    <HintPath>YOUR_RUMBLE_PATH\MelonLoader\Il2CppAssemblies\Il2Cppmscorlib.dll</HintPath>
  </Reference>
  <Reference Include="Il2CppRUMBLE.Runtime">
    <HintPath>YOUR_RUMBLE_PATH\MelonLoader\Il2CppAssemblies\Il2CppRUMBLE.Runtime.dll</HintPath>
  </Reference>
  <Reference Include="UnityEngine.CoreModule">
    <HintPath>YOUR_RUMBLE_PATH\MelonLoader\Il2CppAssemblies\UnityEngine.CoreModule.dll</HintPath>
  </Reference>
  <!-- Add more Il2Cpp/Unity assemblies as needed by your mod -->

  <!-- RMAPI itself (from Mods/) — THIS IS THE KEY ONE -->
  <Reference Include="RumbleModdingAPI">
    <HintPath>YOUR_RUMBLE_PATH\Mods\RumbleModdingAPI.dll</HintPath>
  </Reference>
</ItemGroup>
```

Add more references as your mod needs them:
- `Assembly-CSharp.dll` — the game's main assembly (in `Il2CppAssemblies/`)
- `Unity.TextMeshPro.dll` — if using text
- `Unity.InputSystem.dll` — if reading controller input
- `Il2CppPhotonUnityNetworking.dll` and other Photon assemblies — if doing networking
- Any `Il2CppRUMBLE.*` assemblies for specific game systems

### Step 3 — Write your mod class

```csharp
using MelonLoader;
using RumbleModdingAPI.RMAPI;

// MelonLoader metadata — required
[assembly: MelonInfo(typeof(MyNamespace.MyMod), "My Mod", "1.0.0", "MyName")]
[assembly: MelonGame("Buckethead Entertainment", "RUMBLE")]

// Optional but recommended — tells MelonLoader to load RMAPI before your mod
[assembly: MelonAdditionalDependencies("RumbleModdingAPI")]

namespace MyNamespace
{
    public class MyMod : MelonMod
    {
        public override void OnLateInitializeMelon()
        {
            // Subscribe to RMAPI events here
            Actions.onMapInitialized += OnMapReady;
        }

        private void OnMapReady(string sceneName)
        {
            Melon<MyMod>.Logger.Msg($"Map loaded: {sceneName}");
        }
    }
}
```

The `.csproj` reference to `RumbleModdingAPI.dll` is what actually lets your code compile.
The `MelonAdditionalDependencies` attribute is optional but recommended — it tells MelonLoader
to load RMAPI before your mod and warn the user if RMAPI is missing, instead of crashing
with a confusing error.

### Step 4 — Build and install

1. Build your project (produces `MyMod.dll`)
2. Place `MyMod.dll` into `RUMBLE/Mods/`
3. Make sure `RumbleModdingAPI.dll` is also in `RUMBLE/Mods/`
4. Launch RUMBLE — MelonLoader loads both mods

---

## Folder Structure

Here's what a typical RUMBLE install looks like with mods:

```
RUMBLE/
├── RUMBLE.exe
├── Mods/                              ← mod DLLs only
│   ├── RumbleModdingAPI.dll
│   └── MyMod.dll
├── UserData/                          ← mod assets, configs, and other files
│   └── MyMod/
│       ├── myassets
│       └── mysound.wav
└── MelonLoader/
    ├── net6/                          ← MelonLoader runtime DLLs
    │   ├── MelonLoader.dll
    │   ├── 0Harmony.dll
    │   └── ...
    └── Il2CppAssemblies/              ← game's unhollowed assemblies
        ├── Il2CppRUMBLE.Runtime.dll
        ├── UnityEngine.CoreModule.dll
        └── ...
```

- **`Mods/`** is for `.dll` files only
- **`UserData/`** is for everything else — asset bundles, audio files, configs, etc. Create a subfolder with your mod's name to keep things organized

---

## Initialization Order

Understanding when things are ready is important:

```
Game boots
  └─ MelonLoader loads all mods
       └─ OnLateInitializeMelon() runs for each mod
            └─ RMAPI sets up controller input bindings
            └─ RMAPI scans for Photon RPCs
            └─ onMyModsGathered fires (your mod list is ready)

Scene loads (e.g., "Gym")
  └─ RMAPI caches the scene's root GameObjects
  └─ RMAPI waits for the local player to exist
  └─ onMapInitialized fires (scene name passed as string)
  └─ If in a match (Map0/Map1) with 2 players:
       └─ onMatchStarted fires
       └─ onRoundStarted fires
       └─ Health watcher begins polling
```

**Key rule:** Don't access GameObjects or Players before `onMapInitialized` fires.
Use that event as your "safe to go" signal.

---

## Checking if RMAPI is Ready

Most of the time you should use `onMapInitialized` (see [Chapter 2](02-Events.md)) instead of polling
these. But if you're in a coroutine or update loop and need to check on the spot:

```csharp
// Is the API initialized at all? (happens once on first load)
bool ready = Calls.IsInitialized();

// Have the current map's GameObjects been cached?
bool mapReady = Calls.IsMapInitialized();
```

---

## Scenes in RUMBLE

RMAPI tracks these scenes:

| Scene Name | What it is |
|------------|-----------|
| `"Loader"` | Initial loading screen — RMAPI initializes here |
| `"Gym"` | The solo gym / lobby area |
| `"Park"` | The park hangout area |
| `"Map0"` | Battle arena #1 |
| `"Map1"` | Battle arena #2 |

---

[Back to Index](index.md) | [Next: Events](02-Events.md)
