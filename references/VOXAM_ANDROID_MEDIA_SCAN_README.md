# VoxAm — Music library flow (design update)

## What changed
- Music screen starts on Folders; All tracks is a second library view.
- The old file-picker-based music import controls were removed.
- Scan phone now calls an Android bridge when available. In a plain HTML/browser preview, the app explains why full-device scanning is unavailable rather than opening a file chooser.
- Selecting a track starts playback and displays a Spotify-style mini-player above the bottom icon navigation. Tapping the mini-player opens a dedicated Now Playing page.
- Embedded album art is used when supplied; VoxAm logo is the fallback artwork for a selected track with no cover art.
- No demo songs or video entries are included.

## Important platform limitation
A browser-only HTML file cannot request Android's full `READ_MEDIA_AUDIO` permission and enumerate the entire phone music library. That feature must be implemented by a native Android app (MediaStore + runtime permission). The HTML exposes this bridge contract:

- Android JavaScript interface object: `VoxAmAndroid`
- Method: `requestMusicPermissionAndScan()`
- On permission result: call `window.onVoxAmPermissionResult(true_or_false)`
- On scan completion: call `window.onVoxAmLibraryLoaded(array_or_JSON_string)`

Each track object should have `uri` (or `url`/`contentUri`), `title`, `artist`, `album`, `folder` or `relativePath`, `durationMs` (milliseconds) or `durationSeconds`, and optionally `art` (a data URL for embedded/album artwork). Audio `content://` URI playback can depend on how the WebView is configured; a production Android version should ideally use Android Media3/ExoPlayer for native playback.

## Android permission
For Android 13+ the app typically needs `android.permission.READ_MEDIA_AUDIO`, requested at runtime. Older Android versions use `READ_EXTERNAL_STORAGE` with the appropriate max SDK/deprecation settings. Review Android's current SDK behavior when setting your target SDK.
