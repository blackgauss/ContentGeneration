import moviepy.editor as mpe
import whisper_timestamped as whisper
import json
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import random
import os

def get_file_names(folder, file_type):
    """
    Get the names of files in a folder with a specific file type.

    Parameters:
    folder (str): The path to the folder.
    file_type (str, optional): The file type to filter the files. Defaults to '.mp4'.

    Returns:
    list: A list of file names without the file extension.
    """
    folder_path = folder
    file_names = []
    
    for file in os.listdir(folder_path):
        if file.endswith(file_type):
            file_name = os.path.splitext(os.path.basename(file))[0]
            file_names.append(file_name)
    
    return file_names

def make_transcription(audio_filename):
    """
    Transcribes the audio file using the Whisper ASR model.

    Args:
        audio_filename (str): The path to the audio file.

    Returns:
        str: The transcription of the audio file.
    """
    audio = whisper.load_audio(audio_filename)
    model = whisper.load_model('base')
    result = whisper.transcribe(model, audio, language="en")
    return result

def make_timestamps(transcription):
    """
    Create timestamps for each word in the transcription.

    Args:
        transcription (dict): The transcription containing segments and words.

    Returns:
        list: A list of timestamps and the original transcription.
    """
    timestamps = []
    for seg in transcription['segments']:
        for word in seg['words']:
            timestamps.append([(word['start'], word['end']), word['text']])
    return [timestamps, transcription]

def make_textclip(sub, font_name, font_size, font_color):
    """
    Create a text clip with the given subtitle, font name, font size, and font color.

    Parameters:
    sub (tuple): A tuple containing the start and end time of the subtitle.
    font_name (str): The name of the font to be used.
    font_size (int): The size of the font.
    font_color (str): The color of the font.

    Returns:
    list: A list containing the text clip, start time, and end time.
    """
    start, end = sub[0]
    txt = sub[1]
    return [TextClip(txt, fontsize=font_size, font=font_name, color=font_color, stroke_color='black', stroke_width=3), start, end]

def resize(t, duration):
    """
    Resizes the content based on the given time and duration.

    Parameters:
    t (float): The current time.
    duration (float): The total duration.

    Returns:
    float: The scale factor for resizing the content.
    """
    duration = min(duration, 0.2)
    start_scale = 1
    end_scale = 1.2
    t * start_scale + ((duration - t) / duration) ** 0.3 * (end_scale - start_scale)
    scale_factor = min(start_scale + t/duration * (end_scale - start_scale), end_scale)
    return scale_factor

# Function to overlay the text clips on the video
def overlay_video(video, audio_data, watermark_path, endcard_path, colored=False, animate=False, font_name='Arial'):
    """
    Overlay text, watermark, and end card on a video.

    Args:
        video_filename (MoviePy): moviepy video object.
        audio_data (list): List containing subtitles and transcription.
        watermark_path (str): Path to the watermark image file.
        endcard_path (str): Path to the end card video file.
        animate (bool, optional): Whether to animate the text. Defaults to False.

    Returns:
        final (VideoClip): Composite video clip with text, watermark, and end card overlayed.
    """
    [subtitles, transcription] = audio_data
    text_clips = []
    for sub in subtitles:
        colored = 'white'
        if colored:
            color = 'rgb(126, 217, 87)' if (random.choice(range(10)) > 8) else 'white'
            color = 'yellow' if (random.choice(range(10)) > 6) else color
        [clip, start, end] = make_textclip(sub, font_name, font_size=65, font_color=color)
        duration = end - start
        if animate:
            resize_clip = clip.resize(lambda t: resize(t, duration))
        new_clip = resize_clip.set_start(start).set_duration(end - start).set_position('center')
        text_clips.append(new_clip)
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