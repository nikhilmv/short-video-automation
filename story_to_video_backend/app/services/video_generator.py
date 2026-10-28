import os
import json
import asyncio
import subprocess
import textwrap
import requests
import ollama
import edge_tts
from dotenv import load_dotenv

load_dotenv() 
# --- CONFIGURATION ---
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY") 
LLM_MODEL = "llama3.2:3b"
VOICE = "en-US-ChristopherNeural"
PROJECT_DIR = "output_data"
ASPECT_RATIO = "9:16"  # Options: "9:16" (Shorts/Reels/TikTok), "16:9" (YouTube Landscape), "1:1" (Square)
ENABLE_CAPTIONS = True  # Set to True to burn synchronized English captions into the video

RESOLUTIONS = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1": (1080, 1080),
}

os.makedirs(f"{PROJECT_DIR}/clips", exist_ok=True)
os.makedirs(f"{PROJECT_DIR}/audio", exist_ok=True)

# 1. Local LLM Scene Extraction
def analyze_story(story_text: str):
    prompt = f"""
    You are a video script director.
    Break down the entire provided story into sequential visual scenes.

    CRITICAL RULES:
    1. You MUST cover the COMPLETE story from start to finish. Do NOT summarize, truncate, or omit any sentences.
    2. Group the story into sequential scenes, with 1 to 2 sentences per scene.
    3. Every single sentence from the original story MUST appear in the 'narration' of exactly one scene.
    4. For each scene, output:
       - "narration": The exact narrator voice line covering that part of the story.
       - "search_query": 1 to 3 simple, physical visual keywords for stock video search (e.g. "sleeping bed", "coffee sunrise", "reading book"). Keep queries broad and concrete.

    Return strictly valid JSON with key "scenes" containing a list of objects.

    Story:
    \"\"\"{story_text}\"\"\"
    """
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        format="json"
    )
    data = json.loads(response["message"]["content"])
    raw_scenes = data.get("scenes", data) if isinstance(data, dict) else data
    # Filter out any blank or empty scenes
    return [s for s in raw_scenes if isinstance(s, dict) and s.get("narration", "").strip()]

def format_ass_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        secs += 1
        centis = 0
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

# 2. Free Edge-TTS Voiceover & Synchronized Captions
async def generate_voiceover_and_captions(text: str, audio_path: str, ass_path: str, width: int, height: int):
    communicate = edge_tts.Communicate(text, VOICE)
    sub_events = []

    with open(audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                start_sec = chunk["offset"] / 10_000_000.0
                dur_sec = chunk["duration"] / 10_000_000.0
                sub_events.append({
                    "start": start_sec,
                    "end": start_sec + dur_sec,
                    "text": chunk["text"]
                })

    if not sub_events:
        duration = get_audio_duration(audio_path)
        sub_events = [{"start": 0.0, "end": duration, "text": text}]

    # Visual subtitle styling tuned for aspect ratio (Shorts/Reels vs Landscape)
    font_size = 56 if height > width else 36
    margin_v = 300 if height > width else 80
    wrap_width = 24 if height > width else 48

    dialogue_lines = []
    for ev in sub_events:
        start_str = format_ass_time(ev["start"])
        end_str = format_ass_time(ev["end"])
        wrapped = r"\N".join(textwrap.wrap(ev["text"].strip(), width=wrap_width))
        dialogue_lines.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{wrapped}")

    events_block = "\n".join(dialogue_lines)

    ass_content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{events_block}
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

def get_audio_duration(audio_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return float(res.stdout.strip())

def check_media_streams(file_path: str) -> tuple[bool, bool]:
    """Check if a file has both valid video and audio streams."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return False, False
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type", "-of", "csv=p=0",
        file_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    streams = res.stdout.strip().split()
    has_video = "video" in streams
    has_audio = "audio" in streams
    return has_video, has_audio

def generate_fallback_video(video_path: str, width: int, height: int, duration: float = 10.0):
    """Generate a clean dark background clip if stock video cannot be downloaded."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x111827:s={width}x{height}:r=30:d={duration}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        video_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 3. Search & Download from Pixabay Video API
def download_stock_video(query, video_path: str) -> bool:
    if isinstance(query, list):
        query = " ".join(str(q) for q in query)
    query = str(query).strip()
    if not query:
        query = "nature background"

    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "video_type": "film",
        "per_page": 3
    }
    try:
        response = requests.get("https://pixabay.com/api/videos/", params=params, timeout=10)
        data = response.json() if response.status_code == 200 else {}

        # Fallback to a generic query if specific search yields zero results
        if not data.get("hits"):
            params["q"] = "nature background"
            fallback_resp = requests.get("https://pixabay.com/api/videos/", params=params, timeout=10)
            data = fallback_resp.json() if fallback_resp.status_code == 200 else {}

        if data.get("hits"):
            video_data = data["hits"][0].get("videos", {})
            # Prioritize 1080p ('large'), then 720p ('medium'), then 'small'
            chosen = video_data.get("large") or video_data.get("medium") or video_data.get("small")
            if chosen and chosen.get("url"):
                video_url = chosen["url"]
                with requests.get(video_url, stream=True, timeout=25) as stream_req:
                    if stream_req.status_code == 200:
                        with open(video_path, "wb") as f:
                            for chunk in stream_req.iter_content(chunk_size=8192):
                                f.write(chunk)
                        if os.path.exists(video_path) and os.path.getsize(video_path) > 10000:
                            has_v, _ = check_media_streams(video_path)
                            if has_v:
                                return True
    except Exception as e:
        print(f"Error fetching stock video for '{query}': {e}")

    return False

# 4. Process and Stitch with FFmpeg
async def process_story(story_text: str, output_final: str = "final_output.mp4", work_dir: str = None):
    project_dir = work_dir or PROJECT_DIR
    clips_dir = os.path.join(project_dir, "clips")
    audio_dir = os.path.join(project_dir, "audio")
    os.makedirs(clips_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    print("[1/4] Analyzing scenes with local LLM...")
    scenes = analyze_story(story_text)

    processed_scenes = []
    for i, scene in enumerate(scenes):
        print(f"  -> Processing Scene {i+1}: {scene['search_query']}")
        raw_vid = os.path.join(clips_dir, f"raw_{i}.mp4")
        aud_path = os.path.join(audio_dir, f"narration_{i}.mp3")
        scene_output = os.path.join(clips_dir, f"scene_{i}.mp4")

        target_w, target_h = RESOLUTIONS.get(ASPECT_RATIO, (1080, 1920))
        ass_path = os.path.join(audio_dir, f"narration_{i}.ass")

        # Generate TTS audio and synchronized captions
        if ENABLE_CAPTIONS:
            await generate_voiceover_and_captions(scene["narration"], aud_path, ass_path, target_w, target_h)
        else:
            communicate = edge_tts.Communicate(scene["narration"], VOICE)
            await communicate.save(aud_path)

        duration = get_audio_duration(aud_path)

        # Download Pixabay footage; generate clean background fallback if unavailable
        if not download_stock_video(scene["search_query"], raw_vid):
            print(f"Notice: Stock footage unavailable for scene {i+1}, using fallback background.")
            generate_fallback_video(raw_vid, target_w, target_h, duration=max(duration + 1.0, 5.0))

        # Standardize resolution, loop if audio is longer, add subtitles, and bind audio
        vf_filter = f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},setsar=1"
        if ENABLE_CAPTIONS and os.path.exists(ass_path):
            # Escape path properly for ffmpeg filter on Windows (C:\path -> C\:/path)
            ass_clean = os.path.abspath(ass_path).replace("\\", "/").replace(":", "\\:")
            vf_filter += f",ass='{ass_clean}'"

        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1", "-i", raw_vid,
            "-i", aud_path,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-t", str(duration),
            "-vf", vf_filter,
            "-r", "30",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-dn", "-map_metadata", "-1",
            "-avoid_negative_ts", "make_zero",
            scene_output
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            print(f"Error encoding scene {i+1}: {res.stderr}")
            continue

        # Verify scene has both video and audio before adding
        has_v, has_a = check_media_streams(scene_output)
        if not has_v:
            print(f"Warning: Scene {i+1} output is missing a video stream, skipping.")
            continue

        processed_scenes.append(scene_output)

    # Free the 3B model from VRAM immediately after use
    try:
        ollama.generate(model=LLM_MODEL, keep_alive=0)
    except Exception:
        pass

    if not processed_scenes:
        print("Error: No scenes generated.")
        return

    print("[4/4] Stitching scenes into final video...")
    concat_txt = os.path.join(project_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for sc in processed_scenes:
            clean_sc = os.path.abspath(sc).replace("\\", "/")
            f.write(f"file '{clean_sc}'\n")

    # Re-encode on concat to unify SPS/PPS, align timestamps, and add faststart for smooth web playback
    concat_res = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-movflags", "+faststart",
        output_final
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

    if concat_res.returncode != 0:
        print(f"Error concatenating scenes: {concat_res.stderr}")
    else:
        print(f"Done! Final video generated: {output_final}")

if __name__ == "__main__":
    # Option 1: Load directly from story.txt if it exists
    if os.path.exists("story.txt"):
        with open("story.txt", "r", encoding="utf-8") as f:
            story = f.read().strip()
        print("Loaded story from story.txt")
    else:
        # Option 2: Paste any plain paragraph directly between triple quotes """
        story = """
Every night, Rahul promised himself that tomorrow would be different. But every morning, he chose comfort over his dreams.

One day, he decided to make just one small change: he woke up early, read one page, and worked on his dream for just ten minutes. It seemed insignificant, but he kept going every single day.

Months passed, and those tiny steps transformed his life. Remember, you don't need to change your entire life in one day. You just need to take the first step.
""".strip()

    asyncio.run(process_story(story))