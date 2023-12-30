import moviepy.editor as mpe
import whisper_timestamped as whisper
import json
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import random
import os

def get_file_names(folder, file_type='.mp4'):
    folder_path = folder
    file_names = []
    
    for file in os.listdir(folder_path):
        if file.endswith(file_type):
            file_name = os.path.splitext(os.path.basename(file))[0]
            file_names.append(file_name)
    
    return file_names

def make_transcription(audio_filename):
    audio = whisper.load_audio(audio_filename)
    # model = whisper.load_model("tiny", device="gpu")
    model = whisper.load_model('base')
    result = whisper.transcribe(model, audio, language="en")
    return result

def make_timestamps(transcription):
    timestamps = []
    for seg in transcription['segments']:
        for word in seg['words']:
            timestamps.append([(word['start'], word['end']), word['text']])
    return [timestamps, transcription]

# Function to create a TextClip for each subtitle
def make_textclip(sub, font_name, font_size, font_color):
    start, end = sub[0]
    txt = sub[1]
    return [TextClip(txt, fontsize=font_size, font=font_name, color=font_color, stroke_color='black', stroke_width=3), start, end]

def resize(t, duration):
    # Starting scale factor
    duration = min(duration, 0.2)
    start_scale = 1
    # End scale factor (the size to which the text should grow)
    end_scale = 1.2
    # Calculate the scaling factor based on elapsed time and total duration
    t * start_scale + ((duration - t) / duration) ** 0.3 * (end_scale - start_scale)
    scale_factor = min(start_scale + t/duration * (end_scale - start_scale), end_scale)
    return scale_factor

# Function to overlay the text clips on the video
def overlay_video(video_filename, audio_data, watermark_path, endcard_path, animate=False):
    [subtitles, transcription] = audio_data
    # Create a list of TextClips
    text_clips = []
    if animate:
        for sub in subtitles:
            color = 'rgb(126, 217, 87)' if (random.choice(range(10)) > 7) else 'white'
            color = 'yellow' if (random.choice(range(10)) > 6) else color
            [clip, start, end] = make_textclip(sub, font_size=65, font_color=color)
            duration = end - start
            resize_clip = clip.resize(lambda t: resize(t, duration))
            new_clip = resize_clip.set_start(start).set_duration(end - start).set_position('center')
            text_clips.append(new_clip)
    else:
        for sub in subtitles:
            #color = '#FF7ED957' if (random.choice(range(10)) >= 4) else 'white'
            [clip, start, end] = make_textclip(sub, 70, color)
            new_clip = clip.set_start(start).set_duration(end - start).set_position('center')
            text_clips.append(new_clip)
    # Overlay the text on the video
    video = mpe.VideoFileClip(video_filename)
    overlay = mpe.CompositeVideoClip([video, *text_clips])
    video_duration = overlay.duration
    logo = (mpe.ImageClip(watermark_path)
          .set_duration(video_duration)
          .resize(height=150) # if you need to resize...
          #.margin(right=8, top=8, opacity=.5) # (optional) logo-border padding
          .set_pos(("left","bottom")))
    video_h = overlay.h
    video_w = overlay.w
    end_card = mpe.VideoFileClip(endcard_path).resize(height=video_h, width=video_w).set_start(video_duration)
    final = mpe.CompositeVideoClip([overlay, logo, end_card])
    return final