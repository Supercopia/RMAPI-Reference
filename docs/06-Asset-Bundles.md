# Chapter 6 — Asset Bundles

[Back to Index](index.md) | [Previous: UI Creation](05-UI-Creation.md) | [Next: Audio](07-Audio.md)

---

## Overview

Asset Bundles let you load **custom assets** (3D models, materials, prefabs, textures, etc.)
into RUMBLE. RMAPI handles the tricky Il2Cpp stream conversion so you can load bundles with
a single call.

```csharp
using RumbleModdingAPI.RMAPI;
using UnityEngine;
```

There are two ways to package your assets:

1. **As a file** on disk (in `UserData`) — simpler to set up
2. **As an embedded resource** inside your mod's DLL — cleaner distribution (single file)

---

## File Paths

All "from file" methods take a **relative path from the game's root folder** (where `RUMBLE.exe` lives).
The MelonLoader convention is to put non-DLL mod files in the `UserData` folder:

```
RUMBLE/
├── RUMBLE.exe
├── Mods/                  ← your mod DLL goes here
│   └── MyMod.dll
└── UserData/              ← your mod's extra files go here
    └── MyMod/
        ├── myassets
        └── mysound.wav
```

So a path like `@"UserData\MyMod\myassets"` resolves to `<RUMBLE install>\UserData\MyMod\myassets`.

> **Note:** The `Mods` folder is for `.dll` files only. Put assets, audio, configs, etc. in `UserData\YourModName\`.

> **AssetBundle file extensions:** Unity AssetBundles have **no required extension**. You'll see
> them with no extension (`myassets`), or `.bundle`, `.assetbundle`, `.assets`, or anything else.
> RMAPI doesn't care — it just reads the raw bytes from whatever path you provide.

> **Reminder:** All names in these examples are arbitrary — variable names (`bundlePath`, `assetName`),
> folder names (`MyMod`), and file names (`myassets`, `hat`) can be whatever you want.
> Only the RMAPI method names are real. See [Chapter 1](01-Getting-Started.md#a-note-on-names-in-this-guide) for details.

---

## Loading from a File on Disk

### Load a Single GameObject

The most common case: you have an AssetBundle file and want to get a prefab out of it.

```csharp
string bundlePath = @"UserData\MyMod\myassets";
string assetName = "MyCoolPrefab";

GameObject obj = AssetBundles.LoadAssetBundleGameObjectFromFile(bundlePath, assetName);
// obj is already instantiated and ready to use
obj.transform.position = new Vector3(0, 1, 0);
```

### Load a Specific Asset by Type

Load any asset type (Material, Texture2D, AudioClip, etc.) — not just GameObjects.

```csharp
Material mat = AssetBundles.LoadAssetFromFile<Material>(bundlePath, "MyMaterial");
Texture2D tex = AssetBundles.LoadAssetFromFile<Texture2D>(bundlePath, "MyTexture");
```

### Load All Assets of a Type

Get every asset of a given type from a bundle:

```csharp
List<Material> allMaterials = AssetBundles.LoadAllOfTypeFromFile<Material>(bundlePath);
```

### Load the Raw AssetBundle

If you need more control, load the bundle itself and manage assets manually.

```csharp
AssetBundle bundle = AssetBundles.LoadAssetBundleFromFile(bundlePath);

// Load things from it
GameObject prefab1 = bundle.LoadAsset<GameObject>("Prefab1");
GameObject prefab2 = bundle.LoadAsset<GameObject>("Prefab2");

// IMPORTANT: Unload when done to free memory
bundle.Unload(false);  // false = keep loaded assets, true = unload everything
```

> **Always call `bundle.Unload()`** when you're done with a raw bundle.
> The single-asset methods handle this for you automatically.

---

## Loading from an Embedded Resource (Stream)

### What does "from stream" mean?

When you load from a **file**, the asset bundle is a separate file sitting on disk next to your mod.
When you load from a **stream**, the asset bundle is packed **inside your mod's DLL** — there's no
separate file. At runtime, RMAPI reads the bytes directly out of the DLL's binary (via
`Assembly.GetManifestResourceStream`), which produces a `Stream` (a sequence of bytes in memory)
instead of a file path.

### Why use one over the other?

| | From File | From Stream (Embedded) |
|-|-----------|----------------------|
| **Distribution** | Ship DLL + loose asset files | Ship just the DLL (everything inside) |
| **Setup** | Drop files in a folder | Configure build action in your project |
| **Updating assets** | Swap the file, no recompile needed | Must recompile the DLL to change assets |
| **Best for** | Assets that change often, or large files | Small-to-medium assets you want bundled cleanly |

### How to Embed a Resource

1. Add your asset bundle file to your C# project
2. In its file properties, set **Build Action** to `Embedded Resource`
3. The resource path becomes: `YourNamespace.filename` (e.g., `MyNamespace.myassets`)

### Load an AssetBundle from Stream

**By mod name and author:**
```csharp
AssetBundle bundle = AssetBundles.LoadAssetBundleFromStream(
    modName:   "MyMod",
    modAuthor: "MyName",
    assetPath: "MyNamespace.myassets"
);

GameObject obj = Object.Instantiate(bundle.LoadAsset<GameObject>("MyPrefab"));
bundle.Unload(false); // don't forget!
```

**By mod instance** (if you have a reference to your MelonMod):
```csharp
AssetBundle bundle = AssetBundles.LoadAssetBundleFromStream(
    instance:  this,              // your MelonMod instance
    assetPath: "MyNamespace.myassets"
);
bundle.Unload(false);
```

### Load a Single Asset from Stream

```csharp
// By mod name/author
GameObject obj = AssetBundles.LoadAssetFromStream<GameObject>(
    modName:   "MyMod",
    modAuthor: "MyName",
    path:      "MyNamespace.myassets",
    assetName: "MyPrefab"
);

// By mod instance
Material mat = AssetBundles.LoadAssetFromStream<Material>(
    instance:  this,
    path:      "MyNamespace.myassets",
    assetName: "MyMaterial"
);
```

### Load All Assets of a Type from Stream

```csharp
List<Texture2D> textures = AssetBundles.LoadAllOfTypeFromStream<Texture2D>(
    instance: this,
    path:     "MyNamespace.myassets"
);
```

---

## Method Summary

### From File

| Method | Returns | Description |
|--------|---------|-------------|
| `LoadAssetBundleGameObjectFromFile(path, name)` | `GameObject` | Load and instantiate a prefab |
| `LoadAssetBundleFromFile(path)` | `AssetBundle` | Load raw bundle (remember to Unload!) |
| `LoadAssetFromFile<T>(path, name)` | `T` | Load one asset of any type |
| `LoadAllOfTypeFromFile<T>(path)` | `List<T>` | Load all assets of a type |

### From Embedded Resource (Stream)

| Method | Returns | Description |
|--------|---------|-------------|
| `LoadAssetBundleFromStream(name, author, path)` | `AssetBundle` | Load raw bundle by mod info |
| `LoadAssetBundleFromStream(instance, path)` | `AssetBundle` | Load raw bundle by instance |
| `LoadAssetFromStream<T>(name, author, path, asset)` | `T` | Load one asset by mod info |
| `LoadAssetFromStream<T>(instance, path, asset)` | `T` | Load one asset by instance |
| `LoadAllOfTypeFromStream<T>(instance, path)` | `List<T>` | Load all assets of a type |

---

## Full Example: Loading a Custom Hat

```csharp
using MelonLoader;
using RumbleModdingAPI.RMAPI;
using UnityEngine;

namespace HatMod
{
    public class HatMod : MelonMod
    {
        public override void OnLateInitializeMelon()
        {
            Actions.onPlayerSpawned += OnPlayerSpawned;
        }

        private void OnPlayerSpawned(Il2CppRUMBLE.Players.Player player)
        {
            if (player != Calls.Players.GetLocalPlayer()) return;

            // Load a hat prefab from an AssetBundle file
            // Note: this loads from disk every time onPlayerSpawned fires.
            // If you want to load once and reuse, load it on the first
            // onMapInitialized and call DontDestroyOnLoad on the result
            // so it survives scene changes.
            string bundlePath = @"UserData\HatMod\hat";
            GameObject hat = AssetBundles.LoadAssetBundleGameObjectFromFile(bundlePath, "TopHat");

            // Attach it to the player's head
            Transform head = player.Controller.transform.Find("Head");
            if (head != null)
            {
                hat.transform.SetParent(head);
                hat.transform.localPosition = Vector3.up * 0.2f;
                hat.transform.localRotation = Quaternion.identity;
            }
        }
    }
}
```

---

[Back to Index](index.md) | [Previous: UI Creation](05-UI-Creation.md) | [Next: Audio](07-Audio.md)
