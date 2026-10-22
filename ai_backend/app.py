"""VoxAm AI Engine v1 — local-first video-to-Amharic dubbing prototype.

The selected video is received by this local FastAPI service. FFmpeg extracts audio;
only that audio file is uploaded to Gemini for transcription. No video/audio is stored
permanently by this app. Gemini usage and its data terms still apply.
"""
from __future__ import annotations

import base64
import hmac
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai

load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("voxam")

ROOT = Path(__file__).resolve().parent
PUBLIC_DIR = ROOT / "public"
MAX_UPLOAD_MB = max(10, int(os.getenv("MAX_UPLOAD_MB", "100")))
MAX_VIDEO_SECONDS = max(30, int(os.getenv("MAX_VIDEO_SECONDS", "300")))
MAX_DUB_SEGMENTS = max(4, int(os.getenv("MAX_DUB_SEGMENTS", "36")))
FFMPEG_TIMEOUT_SECONDS = max(30, int(os.getenv("FFMPEG_TIMEOUT_SECONDS", "180")))
TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-3.8-flash")
TRANSCRIBE_MODEL = os.getenv("GEMINI_TRANSCRIBE_MODEL", "gemini-3.5-transcribe")
TTS_MODEL = os.getenv("GEMINI_TTS_MODEL", "gemini-3.8-flash-lite-tts")
ALLOWED_VOICES = {"Kore", "Aoede", "Leda", "Zephyr", "Puck", "Charon", "Fenrir", "Orus"}

app = FastAPI(title="VoxAm AI Engine", version="1.0.0", description="Audio transcription, Amharic translation and synchronized voice overlay.")
# API-token protection is used instead of browser cookies. CORS is not authenticated by itself.
# An unset origin list intentionally disables cross-origin browser calls rather than opening the
# service to every website. Configure the exact Netlify origin in production.
origins = [s.strip() for s in os.getenv("CORS_ORIGINS", "").split(",") if s.strip() and s.strip() != "*"]
if origins:
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "X-VoxAm-Access-Token"], allow_credentials=False)

_client: genai.Client | None = None


def client() -> genai.Client:
    global _client
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key.startswith("PASTE_YOUR_"):
        raise HTTPException(status_code=503, detail="Gemini API key is missing. Add GEMINI_API_KEY to the server .env file, then restart VoxAm.")
    if _client is None:
        _client = genai.Client(api_key=key)
    return _client


def authorize(x_voxam_access_token: str | None = Header(default=None, alias="X-VoxAm-Access-Token")) -> None:
    expected = os.getenv("APP_ACCESS_TOKEN", "").strip()
    allow_no_code = os.getenv("ALLOW_NO_ACCESS_CODE", "false").strip().lower() in {"true", "1", "yes"}
    if not expected:
        if allow_no_code:
            return
        raise HTTPException(status_code=503, detail="Server protection is not configured. Set APP_ACCESS_TOKEN in .env.")
    if not x_voxam_access_token or not hmac.compare_digest(x_voxam_access_token, expected):
        raise HTTPException(status_code=401, detail="The access code is missing or incorrect.")


def get_value(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def seconds_value(value: Any) -> float | None:
    """Parse common annotation offsets such as '1.24s', '00:00:01.240', or numeric seconds."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    text = re.sub(r"\s*s$", "", text, flags=re.I)
    try:
        if ":" in text:
            parts = text.split(":")
            if len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            if len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
        return float(text)
    except ValueError:
        return None


def extract_words(interaction: Any) -> list[dict[str, Any]]:
    words: list[dict[str, Any]] = []
    for step in get_value(interaction, "steps", []) or []:
        for content in get_value(step, "content", []) or []:
            for ann in get_value(content, "annotations", []) or []:
                ann_type = get_value(ann, "type", "")
                if str(ann_type) != "word_info":
                    continue
                text = str(get_value(ann, "text", "") or "").strip()
                start = seconds_value(get_value(ann, "start_offset"))
                end = seconds_value(get_value(ann, "end_offset"))
                speaker = str(get_value(ann, "speaker", "spk_1") or "spk_1")
                if text and start is not None:
                    words.append({"text": text, "start": max(0.0, start), "end": max(start + 0.05, end if end is not None else start + 0.25), "speaker": speaker})
    words.sort(key=lambda w: w["start"])
    return words


def join_words(words: list[dict[str, Any]]) -> str:
    value = " ".join(w["text"] for w in words).strip()
    value = re.sub(r"\s+([,.;:!?%\)\]\}])", r"\1", value)
    value = re.sub(r"([\(\[\{])\s+", r"\1", value)
    return value


def group_utterances(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not words:
        return []
    groups: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for word in words:
        split_before = False
        if current:
            gap = word["start"] - current[-1]["end"]
            duration = word["end"] - current[0]["start"]
            prior_text = current[-1]["text"]
            split_before = (
                word["speaker"] != current[-1]["speaker"]
                or gap > 0.78
                or duration >= 6.5
                or bool(re.search(r"[.!?…][\"'”’)]?$", prior_text))
            )
        if split_before:
            groups.append(current)
            current = []
        current.append(word)
    if current:
        groups.append(current)
    out = []
    for i, group in enumerate(groups):
        text = join_words(group)
        if not text:
            continue
        out.append({"id": i, "start": round(group[0]["start"], 3), "end": round(max(group[-1]["end"], group[0]["start"] + 0.2), 3), "original": text, "speaker": group[0]["speaker"]})
    return out


def srt_timestamp(sec: float) -> str:
    ms_total = max(0, int(round(sec * 1000)))
    hours, rem = divmod(ms_total, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def make_srt(segments: list[dict[str, Any]]) -> str:
    blocks = []
    for i, s in enumerate(segments, 1):
        blocks.append(f"{i}\n{srt_timestamp(s['start'])} --> {srt_timestamp(s['end'])}\n{s['amharic']}")
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def translate_segments(segments: list[dict[str, Any]], genai_client: genai.Client) -> list[str]:
    payload = [{"id": s["id"], "dialogue": s["original"]} for s in segments]
    prompt = (
        "You are a professional English-to-Ethiopian-Amharic dialogue translator for film dubbing. "
        "Translate each dialogue line into natural spoken Ethiopian Amharic using Ge'ez script. "
        "Preserve meaning, emotion, names and intent. Do not add explanations or speaker labels. "
        "Keep each translation concise enough to fit near the supplied timing, but never omit important meaning. "
        "Return ONLY a JSON array with exactly one object per input line, same id values, schema: "
        "[{\"id\": 0, \"amharic\": \"...\"}].\n\nINPUT:\n" + json.dumps(payload, ensure_ascii=False)
    )
    try:
        response = genai_client.models.generate_content(model=TEXT_MODEL, contents=prompt, config={"response_mime_type": "application/json"})
        raw = str(get_value(response, "text", "") or "").strip()
        # Tolerate markdown wrappers if an API response ignores the JSON response format.
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I).strip()
        data = json.loads(raw)
        if isinstance(data, dict):
            data = data.get("translations", data.get("items", []))
        by_id = {int(row["id"]): str(row["amharic"]).strip() for row in data if isinstance(row, dict) and "id" in row and "amharic" in row}
        translated = [by_id.get(int(s["id"]), "") for s in segments]
        if all(translated):
            return translated
    except Exception as exc:
        log.warning("Batch translation failed; falling back line-by-line: %s", exc)
    # Conservative fallback for a malformed JSON response.
    translated = []
    for seg in segments:
        prompt = "Translate this film dialogue from English into natural spoken Ethiopian Amharic in Ge'ez script. Return only the translation, no notes:\n" + seg["original"]
        response = genai_client.models.generate_content(model=TEXT_MODEL, contents=prompt)
        translated.append(str(get_value(response, "text", "") or "").strip())
    return translated


def synthesize_amharic(text: str, voice: str, genai_client: genai.Client) -> str:
    if voice not in ALLOWED_VOICES:
        voice = "Kore"
    interaction = genai_client.interactions.create(
        model=TTS_MODEL,
        input=[{
            "type": "user_input",
            "content": [{
                "type": "text",
                "text": text,
                "annotations": [{"type": "speech_metadata", "style": "Natural, clear spoken Ethiopian Amharic, emotionally appropriate for film dialogue. Speak only the supplied words."}],
            }],
        }],
        response_format={"type": "audio"},
        generation_config={"speech_config": [{"voice": voice}]},
    )
    audio = get_value(get_value(interaction, "output_audio", {}), "data", None)
    if not audio:
        raise RuntimeError("Gemini TTS returned no audio data")
    return str(audio)


def ensure_ffmpeg() -> None:
    for command in ("ffmpeg", "ffprobe"):
        if shutil.which(command) is None:
            raise HTTPException(status_code=503, detail=f"{command} was not found. Install FFmpeg in Termux using: pkg install ffmpeg")


def video_duration(path: Path) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise HTTPException(status_code=415, detail="Could not read this video. Try an MP4 file supported by FFmpeg.")
    try:
        return float(result.stdout.strip())
    except ValueError:
        raise HTTPException(status_code=415, detail="The video duration could not be read.")


class TranslateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=12000)


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1200)
    voice: str = "Kore"


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "service": "VoxAm AI Engine", "version": app.version, "transcribe_model": TRANSCRIBE_MODEL, "translation_model": TEXT_MODEL, "tts_model": TTS_MODEL, "limits": {"max_upload_mb": MAX_UPLOAD_MB, "max_video_seconds": MAX_VIDEO_SECONDS, "max_dub_segments": MAX_DUB_SEGMENTS, "ffmpeg_timeout_seconds": FFMPEG_TIMEOUT_SECONDS}, "gemini_key_configured": bool(os.getenv("GEMINI_API_KEY", "").strip()) and not os.getenv("GEMINI_API_KEY", "").strip().startswith("PASTE_YOUR_")}


@app.get("/")
def home() -> FileResponse:
    return FileResponse(PUBLIC_DIR / "index.html", media_type="text/html; charset=utf-8")


@app.post("/api/translate")
def translate_text(body: TranslateRequest, _: None = Depends(authorize)) -> dict[str, str]:
    prompt = "Translate into natural spoken Ethiopian Amharic written in Ge'ez script. Preserve meaning and names. Return only the translation, without commentary:\n\n" + body.text
    try:
        response = client().models.generate_content(model=TEXT_MODEL, contents=prompt)
        text = str(get_value(response, "text", "") or "").strip()
        if not text:
            raise RuntimeError("Translation model returned empty text")
        return {"amharic": text}
    except HTTPException:
        raise
    except Exception as exc:
        log.exception("Translation endpoint failed")
        raise HTTPException(status_code=502, detail=f"Gemini translation failed: {str(exc)[:250]}")


@app.post("/api/tts")
def tts_text(body: TTSRequest, _: None = Depends(authorize)) -> dict[str, str]:
    try:
        data = synthesize_amharic(body.text, body.voice, client())
        return {"mime_type": "audio/wav", "audio_b64": data}
    except HTTPException:
        raise
    except Exception as exc:
        log.exception("TTS endpoint failed")
        raise HTTPException(status_code=502, detail=f"Gemini voice generation failed: {str(exc)[:250]}")


@app.post("/api/dub-video")
def dub_video(
    video: UploadFile = File(...),
    voice_a: str = Form("Kore"),
    voice_b: str = Form("Puck"),
    _: None = Depends(authorize),
) -> dict[str, Any]:
    name = video.filename or "clip.mp4"
    suffix = Path(name).suffix.lower()
    allowed_ext = {".mp4", ".m4v", ".mov", ".mkv", ".webm", ".avi", ".3gp", ".mpeg", ".mpg"}
    if suffix and suffix not in allowed_ext:
        raise HTTPException(status_code=415, detail="Unsupported video extension. Use MP4, MOV, MKV, WEBM, AVI or 3GP.")
    if video.content_type and not (video.content_type.startswith("video/") or video.content_type == "application/octet-stream"):
        raise HTTPException(status_code=415, detail="The uploaded file is not recognized as a video.")
    try:
        return _process_video(video, name, voice_a, voice_b)
    except HTTPException:
        raise
    except Exception as exc:
        log.exception("Video dubbing failed")
        message = str(exc).strip() or exc.__class__.__name__
        raise HTTPException(status_code=502, detail=f"AI dubbing failed: {message[:300]}")


def _process_video(upload: UploadFile, original_name: str, voice_a: str, voice_b: str) -> dict[str, Any]:
    ensure_ffmpeg()
    genai_client = client()
    voice_a = voice_a if voice_a in ALLOWED_VOICES else "Kore"
    voice_b = voice_b if voice_b in ALLOWED_VOICES else "Puck"
    with tempfile.TemporaryDirectory(prefix="voxam-") as temp:
        folder = Path(temp)
        input_path = folder / ("source" + (Path(original_name).suffix.lower() or ".mp4"))
        total = 0
        with input_path.open("wb") as out:
            while True:
                chunk = upload.file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_UPLOAD_MB * 1024 * 1024:
                    raise HTTPException(status_code=413, detail=f"The video exceeds the {MAX_UPLOAD_MB} MB limit for this first prototype.")
                out.write(chunk)
        if total == 0:
            raise HTTPException(status_code=400, detail="The uploaded video is empty.")
        duration = video_duration(input_path)
        if duration > MAX_VIDEO_SECONDS:
            mins = MAX_VIDEO_SECONDS // 60
            raise HTTPException(status_code=413, detail=f"This first AI prototype supports clips up to {mins} minutes. Please test it with a shorter clip; full-movie processing is the next upgrade.")
        audio_path = folder / "extracted_audio.wav"
        extract = subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(input_path),
            "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(audio_path)
        ], capture_output=True, text=True, timeout=FFMPEG_TIMEOUT_SECONDS)
        if extract.returncode != 0 or not audio_path.exists() or audio_path.stat().st_size == 0:
            detail = (extract.stderr or "No audio track was found.").strip()[-500:]
            raise HTTPException(status_code=415, detail="Could not extract audio from this file. Try another video with an audio track. " + detail)

        uploaded_audio = None
        try:
            uploaded_audio = genai_client.files.upload(file=str(audio_path))
            interaction = genai_client.interactions.create(
                model=TRANSCRIBE_MODEL,
                input=[{"type": "audio", "uri": uploaded_audio.uri, "mime_type": uploaded_audio.mime_type or "audio/wav"}],
                generation_config={"transcription_config": {"mode": {"type": "verbatim", "diarization_mode": "speaker", "timestamp_granularities": ["word"]}}},
            )
            words = extract_words(interaction)
            if not words:
                transcript = str(get_value(interaction, "output_text", "") or "").strip()
                if not transcript:
                    raise HTTPException(status_code=422, detail="Gemini could not detect clear dialogue in this clip. Try a clip with clear spoken English.")
                raise HTTPException(status_code=422, detail="Gemini returned the transcript but not usable word timestamps, so synchronized dubbing cannot be prepared for this clip yet. Try another short clip with clearer speech.")
            segments = group_utterances(words)
            # Ignore tiny artifacts and stop runaway per-clip synthesis costs in this first version.
            segments = [s for s in segments if len(s["original"].strip()) >= 2 and s["end"] > s["start"]]
            if not segments:
                raise HTTPException(status_code=422, detail="No usable dialogue segments were detected in this clip.")
            if len(segments) > MAX_DUB_SEGMENTS:
                raise HTTPException(status_code=413, detail=f"This clip contains {len(segments)} dialogue segments; the first prototype limit is {MAX_DUB_SEGMENTS}. Please try a shorter section.")
            translated = translate_segments(segments, genai_client)
            for seg, am in zip(segments, translated):
                if not am:
                    raise HTTPException(status_code=502, detail="The translation model did not return all Amharic lines. Please retry with a shorter clip.")
                seg["amharic"] = am
            speaker_voices: dict[str, str] = {}
            for seg in segments:
                speaker = seg.get("speaker", "spk_1")
                if speaker not in speaker_voices:
                    speaker_voices[speaker] = voice_a if len(speaker_voices) % 2 == 0 else voice_b
                seg["voice"] = speaker_voices[speaker]
                seg["audio_b64"] = synthesize_amharic(seg["amharic"], seg["voice"], genai_client)
                seg["mime_type"] = "audio/wav"
            return {
                "ok": True,
                "video_name": original_name,
                "duration": round(duration, 3),
                "language_detected": "auto",
                "segments": segments,
                "srt": make_srt(segments),
                "notice": "The generated Amharic audio is overlaid on the video. Original voices are lowered, not separated; background music/sound effects remain mixed with original dialogue.",
            }
        finally:
            # Remove the reusable Gemini-uploaded audio object when possible. Local temp files
            # are removed by TemporaryDirectory even if an API request fails.
            if uploaded_audio is not None:
                try:
                    file_name = get_value(uploaded_audio, "name")
                    if file_name:
                        genai_client.files.delete(name=file_name)
                except Exception as cleanup_error:
                    log.warning("Gemini temporary file cleanup was not confirmed: %s", cleanup_error)
