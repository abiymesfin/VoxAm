# VoxAm — Current Status and Acceptance Checklist

## Current starting point
- The package has a single-file responsive HTML/CSS/JavaScript player prototype.
- Music UI includes Folders and All Tracks views, search/library flows, mini-player, full player/Now Playing, queue interactions, and no demo media entries.
- Video UI includes local-file choice, browser-dependent video playback, speed/fullscreen, SRT/VTT subtitle loading, and AI dubbing controls wired to an API endpoint.
- A FastAPI backend prototype can accept a video, run FFmpeg extraction, request transcription/translation/speech generation, and return segment metadata/audio plus SRT.
- Prior QA notes said 30 UI checks passed for a previous browser UI build; this is not proof that the full backend/AI API or a production APK works.

## Not yet production-complete
- Android native app packaging/APK/AAB is not included in this handoff.
- Full native media library scan needs Android `MediaStore`, runtime media permissions, and preferably Media3/ExoPlayer; a plain web page cannot do a full device scan.
- Backend model identifiers and SDK methods in the initial source may be stale/unsupported and MUST be checked against current official provider documentation and fixed.
- CORS, access token, upload validation, timeouts, cleanup, concurrency, logs and rate limiting need a security review.
- Static Netlify frontend currently needs to be configured to talk to the public Render API origin; it must not assume the backend shares `location.origin`.
- Do not claim long-form/full-film dubbing, accurate speaker diarization, gender matching, or lip sync until implemented and tested.
- Render free service may sleep, has resource/runtime constraints and is not necessarily appropriate for large/long video conversion.

## Acceptance checklist
1. Install/run dependencies in clean environment; lint/compile Python code.
2. Health endpoint returns success only when service is up; missing API key/access token produces safe clear errors.
3. Frontend's backend URL is configurable and can call deployed Render API from the Netlify domain.
4. CORS allows only intended site origins after deployment. Public requests require auth or another documented safe protection.
5. Browser flow tested using a short, permitted MP4 clip, with generated subtitle and audio segments verified; errors, oversize files and unsupported files are handled.
6. Confirm current Gemini model names, API methods, quota/cost terms, and whether the selected models support needed transcription timestamps/speaker labeling/Amharic TTS.
7. Music/Video visual functions have a regression test; no sample media is injected into a real user's library.
8. Android native build (if delivered) has permissions, local playback, background/lock-screen behavior, audio focus and file access reviewed on a real Android phone.
9. Push changes to the user's selected GitHub repository with a clear commit, without leaking keys.
10. Deploy frontend on Netlify and backend on Render, confirm live URLs/health checks, and write the exact URL/config steps for the user.
11. Report honestly what was tested and what remains incomplete; don't claim a deployment or test was successful unless verified.
