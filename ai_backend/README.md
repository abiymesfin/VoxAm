# VoxAm AI Backend (prototype)

FastAPI + FFmpeg + Gemini prototype. This backend is not yet production verified.

## Local setup
- Python 3.12+
- FFmpeg and ffprobe installed
- Install `requirements.txt`
- Copy `.env.example` to `.env`, then configure values privately
- Start with `uvicorn app:app --host 0.0.0.0 --port 8000`

The defaults require an `APP_ACCESS_TOKEN` and an explicit `CORS_ORIGINS` value before browser clients can call the service. Never commit `.env` or any API key. The verified default models are `gemini-3.8-flash` for translation, `gemini-3.5-transcribe` for word timestamps/diarization, and `gemini-3.8-flash-lite-tts` for Amharic speech. For remote deployment, Render uses the `Dockerfile` and `render.yaml` at repository root.

The current implementation prepares timed Amharic subtitle/audio segments for short clips. It does not render a final dubbed MP4, remove the original dialogue stem, or provide lip-sync. The frontend schedules the returned WAV segments over the local video while reducing the original track.
