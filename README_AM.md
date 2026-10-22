# VoxAm — Manus AI የስራ ማስረከቢያ ZIP

ይህ ፓኬጅ እስካሁን የተሰሩትን የVoxAm UI prototype እና AI backend የመጀመሪያ ኮድ፣ የቀድሞ QA/Android ማስታወሻዎች እና Manus AI ሙሉ ፕሮጀክቱን እንዲጨርስ የሚመራ ፕሮምፕት ይዟል።

## ውስጡ ምን አለ?
- `frontend/index.html` — የVoxAm የቅርብ ጊዜ የHTML player prototype፤ Music/Video UI እና የAI dubbing panel ይዟል።
- `ai_backend/app.py` — FastAPI/FFmpeg/Gemini AI backend የመጀመሪያ ኮድ።
- `ai_backend/public/index.html` — backend root page ለlocal preview የተደገመ ቅጂ።
- `ai_backend/requirements.txt`, `Dockerfile`, `.env.example` — backend deployment ፋይሎች።
- `netlify.toml` — Netlify የstatic frontend ማስተናገድ ቅንብር።
- `render.yaml` — Render የDocker backend ማስኬጃ መነሻ ቅንብር።
- `references/` — የቀድሞ QA እና Android media-scan ማስታወሻዎች፣ logo ፋይል።
- `MANUS_PROMPT_EN.md` — ለManus የተዘጋጀው ሙሉ ቴክኒካዊ ፕሮምፕት።
- `MANUS_PROMPT_AM.md` — የፕሮምፕቱ አማርኛ ማብራሪያ።
- `PROJECT_STATUS_AND_ACCEPTANCE.md` — የአሁኑ ሁኔታ እና ስራው እንዴት እንደሚመረመር።

## አስፈላጊ እውነታ
ይህ ሙሉ የሚሰራ Android APK አይደለም፤ የFrontend prototype እና የAI backend የመጀመሪያ ስሪት ነው። የAndroid ሙሉ music-library scan፣ native playback፣ ለረጅም ቪዲዮ የAI processing፣ የAPI ሞዴሎች ትክክለኛነት፣ CORS/auth እና እውነተኛ live deployment ሁሉ መፈተሽና ማሻሻል አለባቸው።

## Manus ላይ እንዴት ትጠቀማለህ?
1. ይህን ZIP ወደ Manus AI አውርድ/upload አድርግ።
2. `MANUS_PROMPT_EN.md` ውስጥ ያለውን ሙሉ prompt ቅዳ እና በManus ውስጥ ለስራው እንዲጠቀምበት ለጥፍ። ምንም እንዳይተው የሚለውን መመሪያ ይከተል።
3. ሲጠይቅ GitHub እና Netlify/Render ጋር የሚያገናኙትን ፈቃድ ራስህ በኦፊሴላዊ UI ውስጥ ስጥ። የይለፍ ቃል ወይም API key በchat/prompt አትላክ።
4. ለManus የGitHub repository መድረሻ ፈቃድ ካልሰጠኸው፣ ኮድ መፍጠር ቢችልም በራሱ push/deploy ማድረግ አይችልም።

## የAPI Key ደህንነት
- እውነተኛ API key በGitHub repository ወይም HTML/JavaScript ውስጥ አታስገባ።
- Gemini API key በRender Environment Variables ውስጥ ብቻ ይቀመጥ።
- የተጠቃሚ access token ከ`.env.example` በላይ የሚቀየር እና ለህዝብ የማይታይ መሆን አለበት።

## ፋይል አወቃቀር
```text
VoxAm_Manus_Handoff/
├── frontend/index.html
├── ai_backend/app.py
├── ai_backend/public/index.html
├── ai_backend/requirements.txt
├── ai_backend/Dockerfile
├── ai_backend/.env.example
├── netlify.toml
├── render.yaml
├── references/
├── MANUS_PROMPT_EN.md
├── MANUS_PROMPT_AM.md
└── PROJECT_STATUS_AND_ACCEPTANCE.md
```
