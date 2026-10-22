# ለManus AI የሚላክ ዋና ፕሮምፕት — VoxAmን አጠናቅቅ

ከዚህ ZIP ውስጥ ያሉትን ፋይሎች ሁሉ መጀመሪያ መርምር። ያለውን ስራ አትጥል፣ ከዜሮ የተለየ ቴምፕሌት አትስራ። ከተገናኘው GitHub repository ጋር ስራ፤ Frontendን Netlify ላይ፣ AI Backendን Render ላይ አስተናግድ። ባለቤቱ Android ስልክ ብቻ ይጠቀማል፤ Termux፣ laptop፣ Android Studio ወይም manual command-line እንዲጠቀም አትጠይቀው። በራስህ የሚደገፉ build/deploy tools እና የድረ-ገጽ UI ተጠቀም። የውጭ አካውንት ፈቃድ ወይም ሚስጥራዊ key ካስፈለገ ብቻ በኦፊሴላዊ እና ደህንነቱ በተጠበቀ UI ውስጥ እንዲፈቅድ ጠይቅ።

## የምርቱ ራዕይ
VoxAm የሙዚቃና የቪዲዮ ማጫወቻ ነው። ዘመናዊ፣ ፕሮፌሽናል ጨለማ UI እና ወይንጠጅ/magenta/indigo ቀለም ተጠቀም። የአፕ ስም “VoxAm” ብቻ ይሁን፤ በሎጎው ላይ “Video Player” አትጨምር።

## Music
- Music እና Video የተለያዩ ገጾች ይሁኑ።
- የታችኛው navigation አይኮኖች ብቻ ይኖሩት፤ ጽሑፍ እና በእያንዳንዱ icon ዙሪያ የተለየ የማስዋቢያ background አያስፈልግም።
- Music በFolders ይክፈት፤ All Tracks፣ search፣ mini-player፣ queue እና Now Playing/full player በትክክል ይስሩ።
- የሐሰት/demo ዘፈኖች አታስገባ። የስልኩን እውነተኛ የሙዚቃ ላይብረሪ በNative Android MediaStore እና በruntime permission ፈትሽ። ቀላል HTML/browser ሁሉንም የስልክ ሙዚቃ መዘርዘር አይችልም።
- የአልበም ፎቶ ካለ አሳይ፤ ከሌለ የVoxAm logo ተጠቀም።
- በተቻለ መጠን Android Media3/ExoPlayer ተጠቀም፣ native playback፣ audio focus፣ background playback/lock-screen controls እና content URI access ድጋፍ ስጥ። HTML previewን እንደ APK አትቁጠር።

## Video እና AI
- Local video መምረጥ፣ play/pause፣ seek፣ playback speed፣ fullscreen፣ volume እና SRT/VTT subtitles ይስሩ።
- የእንግሊዝኛ ንግግርን ወደ ተፈጥሯዊ አማርኛ መተርጎም፣ በጊዜ የተያያዘ የአማርኛ ድምፅ፣ ንዑስ ርዕስ እና ተናጋሪ መለያ በዕቅድ ውስጥ አሉ። የተናጋሪ/ፆታ ማወቅ ወይም exact lip-sync በእውነት ካልተፈጠረና ካልተፈተነ ተሰርቷል አትበል።
- አሁን ያለው Backend የመጀመሪያ prototype ነው፤ መነሻ ገደቦቹ 100MB፣ 5 ደቂቃ እና 36 dialogue segments ናቸው። ረጅም ፊልም ድጋፍ እስኪፈተን ድረስ እንደሚሰራ አትናገር።
- የድምፅ ዳታ ወደ ውጭ AI provider ከመሄዱ በፊት ግልጽ የprivacy/consent መረጃ አሳይ።

## የZIP ውስጥ አሁን ያለው
- `frontend/index.html`: የቅርብ ጊዜ Music/Video/AI UI prototype።
- `ai_backend/app.py`: የFastAPI AI engine prototype።
- `ai_backend/requirements.txt`, `Dockerfile`, `.env.example`።
- `netlify.toml`, `render.yaml`።
- `references/`: QA እና Android media integration ማስታወሻዎች እና logo።
- `PROJECT_STATUS_AND_ACCEPTANCE.md`: የታወቁ ገደቦችና የሙከራ ዝርዝር።
እነዚህ እስካሁን production-ready እንደሆኑ አትገምት፤ ሞዴሎችን፣ SDK ጥሪዎችንና code paths ፈትሽ።

## የሚፈጽሙት ስራዎች
1. ZIPን እና GitHub repositoryን መርምር፤ ነባር ስራን በድንገት አትሰርዝ። ካስፈለገ branch/backup ፍጠር።
2. አንድ repo ውስጥ Netlify frontend እና Render backend እንዲለዩና እንዲdeploy የሚችሉ ፋይሎችን አደራጅ።
3. Python syntax፣ JavaScript errors፣ mobile layout፣ links፣ API እና backend integration ፈትሽ። ሙከራዎችን አስኬድና failuresን አስተካክል።
4. የGemini model names፣ API methods፣ transcription timestamps/speaker diarization እና Amharic TTS ድጋፍን በአሁኑ የGoogle ኦፊሴላዊ መመሪያ አረጋግጥ። በ`.env.example` ያሉት ሞዴሎች የተሳሳቱ/ያረጁ ሊሆኑ ይችላሉ፤ እንደሚሰሩ አትገምት።
5. የGemini key በRender environment secret ብቻ ይኑር፤ HTML፣ JavaScript፣ GitHub፣ commit፣ logs ወይም prompt ውስጥ ፈጽሞ አትጨምር። `.env` አትcommit አድርግ። ለpublic backend የauthentication/access token አስፈልግ። CORSን የእውነተኛው Netlify origin ብቻ እንዲቀበል አድርግ፤ ለupload size/type/duration፣ timeout፣ temp file cleanup፣ rate abuse እና sensitive logs ጥበቃ አድርግ።
6. አሁን Frontend ከ`location.origin` የAPI server አድራሻ እንደሚገኝ ይገምታል። Netlifyና Render የተለያዩ domain ስለሆኑ API base URL ሊቀየር የሚችልና health-check ያለው መፍትሄ አድርግ።
7. `/api/health` ይስራ፤ CORS፣ access token እና backend URL አስተካክል።
8. በተገናኙት ኦፊሴላዊ አካውንቶች Netlify እና Render ላይ deploy አድርግ። ማስፈቀድ ካስፈለገ ብቻ ተጠቃሚውን በዚያ እርምጃ አቁም። የshell/Termux ኮማንዶችን እንዲያስኬድ አትጠይቅ።
9. በአካባቢው ተገቢ የnative build መሳሪያ ካለ APK ስራ (Android Studio እንዳይጠቀም የሚያስችል pipeline ተጠቀም)። እውነተኛ APK ካልተገነባ የPWA/HTMLን APK ብለህ አትጥራ፤ ምን እንደሚያግድ በግልጽ ጻፍ።
10. በmobile viewport ይፈትሽ። AI key/quota ካለ በአጭር፣ ህጋዊ የሙከራ MP4 እውነተኛ ድምፅ እና SRT ፈትሽ። live API ካልተፈተነ “NOT LIVE-TESTED” ብለህ አመልክት።
11. በተገናኘው GitHub ላይ commit እና push አድርግ፤ force-push አታድርግ፣ secrets አትጫን። GitHub integration ካልተገኘ push አደረግሁ ብለህ አትናገር።
12. የNetlify እና Render የተረጋገጡ URLs፣ health-check፣ GitHub commit/branch፣ የተፈተኑ/ያልተፈተኑ ነገሮችን እና የfree-tier ገደቦችን ሪፖርት አድርግ።

## የስኬት መለኪያ
- Netlify HTTPS URL በእውነት ይክፈት።
- Render HTTPS URL እና `/api/health` ይስሩ።
- Frontend → Backend ግንኙነት፣ CORS እና auth ተፈትነው ይሰሩ።
- AI SRT እና generated voice በእውነት ከተፈተኑ ውጤቱን አሳይ፤ ካልሆነ ለምን እንዳልተፈተነ በግልጽ ተናገር።
- በGitHub ላይ secret አይኖር።
- የተሰራውን፣ የተፈተነውን፣ URLs፣ commit/branch እና የቀሩ እንቅፋቶችን ሪፖርት አድርግ። እቅድ ብቻ ሳይሆን ተግባሩን ፈጽም።

**ከZIP እና GitHub repository ምርመራ ጀምር፤ ከዚያ implement → test → deploy በቅደም ተከተል ስራ።**
