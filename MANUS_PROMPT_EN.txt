# MAIN TASK — Finish VoxAm and deploy it (Android-only owner workflow)

You are the engineering agent responsible for completing the supplied VoxAm project. The attached ZIP is the source handoff. Inspect every file first. Do not discard existing work or replace the product with an unrelated template. Work in the connected GitHub repository if repository integration is available, and use Netlify for the static frontend and Render for the AI backend. The owner uses an Android phone only and wants a workflow that does not require Termux, a laptop, Android Studio, or manual command-line work. Use your own supported build/deploy tools and browser UI where possible. Ask the user only for essential external authorization/secrets that cannot be supplied safely through an official connection UI.

## Product vision
Build **VoxAm**, a polished Android-first music and video player with a distinctive dark, modern audio/video interface and a purple/magenta/indigo accent system consistent with the included prototype/logo. The name is “VoxAm”. Do not add “Video Player” to the logo/app name. The product should feel like a finished consumer app, not a dashboard template.

### Music requirements
- Separate Music and Video sections/pages.
- Bottom navigation uses icons only; no text captions and no separate decorative background behind each icon.
- Music opens on Folders with a second All Tracks view. Search, folder browsing, track selection, a Spotify-inspired mini-player and a dedicated Now Playing/full-player page should work.
- No fake/demo songs. Real local media should be discovered on-device.
- Show embedded album art when available; use the VoxAm logo if a track has no artwork.
- Implement full-device library scanning correctly in native Android using MediaStore and runtime permission (`READ_MEDIA_AUDIO` for applicable Android versions, with a compatible older-version path as required by the chosen target SDK). A plain browser HTML page cannot enumerate the entire Android library.
- Prefer Android Media3/ExoPlayer for reliable native playback, audio focus, background playback/lock-screen controls and content URI handling. Preserve a responsive web preview if feasible, but do not represent the HTML preview as an installed native app.

### Video requirements
- Browse/select local video, playback, seeking, playback speed, fullscreen, volume, and local SRT/VTT subtitles.
- Handle unsupported codecs and permission/errors gracefully.
- Long-term product feature: translate English dialogue to natural Ethiopian Amharic, generate synchronized Amharic voice-over and Amharic subtitles, identify distinct speakers and assign consistent voices when reliable. Do not claim gender detection or exact lip-sync unless actually implemented and tested.
- Initial existing AI prototype only targets short clips (defaults around 100 MB, 5 minutes, and up to 36 dialogue segments); keep limits explicit until a tested background-job/object-storage architecture supports long films.
- Explain consent and privacy clearly before uploading audio derived from a video to an external AI provider.

## Files in this handoff
- `frontend/index.html`: current integrated UI prototype, with Music/Video and AI dubbing panel.
- `ai_backend/app.py`: initial FastAPI AI backend prototype.
- `ai_backend/requirements.txt`, `ai_backend/Dockerfile`, `ai_backend/.env.example`: backend support files.
- `netlify.toml`: starter static-site config.
- `render.yaml`: starter Render Docker service config.
- `references/`: previous UI QA notes, Android media-scan contract/notes and logo.
- `PROJECT_STATUS_AND_ACCEPTANCE.md`: known limitations and acceptance tests.
Treat this as existing prototype code, not verified production-ready software. Preserve useful working features, refactor as needed, and update duplicated frontend files if you keep `ai_backend/public/index.html` synchronized.

## Work to execute
1. Audit the entire ZIP and existing connected GitHub repository before editing. Identify the current default branch, existing files, frontend/backend split and any preexisting work. Do not blindly overwrite unrelated files. Keep a branch or backup if supported.
2. Make the minimum sensible repository layout to deploy both parts from one GitHub repo. Ensure Netlify builds/publishes the correct static frontend folder and Render uses `ai_backend` as root/build context (or document a cleaner alternative).
3. Review/repair the code. Resolve broken references, JavaScript errors, Python syntax/API mismatches and mobile layout issues. Add useful automated checks/tests, run them, and fix failures rather than merely reporting them.
4. Verify every Gemini model name, SDK call shape, transcription feature, word timestamps, speaker labels, TTS support for Amharic and output format against current official Google documentation. The current IDs in `.env.example` may be stale/inaccurate; do not assume they work. Replace with currently supported choices, report availability/pricing/quota caveats, and keep model names configurable via environment variables.
5. Implement secure backend configuration. The Gemini key MUST be a Render secret environment variable and never appear in frontend HTML/JS, Git commits, repository files, build logs, or prompts. Never commit `.env`. Use `.env.example` only as placeholders. Public deployment must not allow unauthenticated AI processing. Generate/use a strong private access token or a better auth scheme; set appropriate CORS to the actual deployed Netlify origin after it is known, not unrestricted wildcard if avoidable. Validate file type/content, size and duration; impose safe timeouts; delete temporary files; avoid logging sensitive contents; prevent abuse/rate exhaustion. Do not expose arbitrary file or command execution.
6. Fix API endpoint configuration: because Netlify frontend and Render backend are on different domains, the frontend must not automatically assume `location.origin` is the API server. Add a safe, obvious, persistent backend URL setting or a build-time public base URL variable and a connection/health test. Handle CORS/network/auth errors in understandable English/Amharic messages.
7. Ensure the backend's `/api/health` is a lightweight status endpoint and the frontend can verify the Render service. Ensure the FastAPI root behavior and the Netlify-published frontend do not conflict.
8. Deploy the web frontend to the connected Netlify site and backend to Render only after the repository is ready. Use the connected accounts/integration wherever possible. When external authorization is required, pause only for that specific authorization; do not ask the owner to run shell/Termux commands. Set secret environment values in the official hosting UI. If a secret requires owner input, tell them exactly where to paste it privately, never request it in public chat.
9. If native Android build is feasible in your environment, complete a native Android app package using an appropriate supported build pipeline (Kotlin/Java + Media3 or another reliable native framework) so the owner can install it on Android without Android Studio. Do not claim an APK exists unless you actually build and verify it. If the environment cannot build the native APK, deliver a tested responsive frontend now, and clearly list what access/build capability is missing for the APK; do not substitute a PWA/webpage and call it a native app.
10. Test the product from the phone-sized viewport and test backend integration with a short legally usable sample clip. Verify actual generated audio and SRT output when API access is available. If live AI calls cannot be tested due to missing keys/quota, mark them NOT LIVE-TESTED and still test error handling.
11. Commit and push completed work to the owner’s selected GitHub repository through the connected integration. Never force-push over existing work and never include any secrets. If repository integration is unavailable, prepare a clean deployable ZIP with exact file paths and explain the one permission needed; do not claim you pushed.
12. Configure Netlify and Render, run live health checks, test frontend-to-backend connectivity, and provide the exact deployed URLs and required owner action (if any). Do not invent deployment URLs or claim success without verification.

## Hosting constraints and expectations
- Netlify serves the static frontend; it is not a general always-on Python/FFmpeg worker.
- Render can host FastAPI/Docker, but free services may sleep or impose limits. Verify current limitations and say whether the selected plan can process the intended clip sizes. Never promise free unlimited full-film dubbing.
- A complete long-film translation/dubbing service may need queued background jobs, persistent/object storage, job status polling, cancellation, cleanup and a paid worker. Implement a scalable design only where supported by the available environment; otherwise document the next step.
- The AI pipeline should ideally be: client upload → backend validation → temporary storage/FFmpeg extraction → reliable transcription/timestamps/diarization → Amharic translation → per-speaker TTS → aligned audio/subtitle response or job output → cleanup. Preserve video playback locally when technically feasible and make clear which audio/transcript data are sent to the AI provider.

## Definition of done
- Frontend deploy exists and loads over HTTPS from Netlify.
- Backend deploy exists and `/api/health` works over HTTPS from Render.
- Frontend can call backend using the configured Render URL with correct CORS and access token.
- Valid test video produces actual Amharic SRT and generated voice audio, or the response explicitly states that live AI could not be tested and why.
- No sample music is presented as a real library; no secret appears in GitHub or static frontend.
- Mobile layout is usable; core player controls and errors are tested.
- If APK is claimed: an actual APK/AAB build is supplied and installation/permission/native playback are validated or limitations clearly identified.
- GitHub changes are pushed and the commit/branch is reported.
- Provide a concise final report: what changed, what was tested (with pass/fail), GitHub branch/commit, Netlify URL, Render URL/health status, costs/free-tier constraints, and any remaining blockers. No fake claims, placeholders disguised as results, or requests for the owner to repeat steps already completed.

Start by inspecting the attached ZIP and connected repository. Then implement and verify; do not return only a plan or a tutorial.
