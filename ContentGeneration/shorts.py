import moviepy.editor as mpe
import os
import random

def get_file_names(folder, file_type='.mp4'):
    folder_path = folder
    file_names = []
    
    for file in os.listdir(folder_path):
        if file.endswith(file_type):
            file_name = os.path.splitext(os.path.basename(file))[0]
            file_names.append(file_name)
    
    return file_names


def get_voiceover(voiceover_path, music_path):
    """
    Get the voiceover audio clip for a given ID.

    Args:
        id (int): The ID of the voiceover file.
        file_path (str): The path to the voiceover file.
        music_path (str): The path to the music file.

    Returns:
        list: A list containing the final audio clip and its duration.
    """
    sound1 = mpe.AudioFileClip(voiceover_path)
    sound2 = mpe.AudioFileClip(music_path).volumex(0.3)

    dur = sound1.duration

    final_audio = mpe.CompositeAudioClip([sound1, sound2]).subclip(0, dur)

    return [final_audio, dur]


def make_video(duration, clips_folder, clip_length=5):
    """
    Create a video by combining hooks and clips.

    Args:
        duration (float): The desired duration of the final video in seconds.
        hooks_folder (str): The path to the folder containing the hook videos.
        clips_folder (str): The path to the folder containing the clip videos.
        clip_length (float, optional): The maximum length of each clip in seconds. Defaults to 5.

    Returns:
        moviepy.video.io.VideoFileClip: The final video clip.
    """
    clips = []
    for file in os.listdir(clips_folder):
        if file.endswith('.mp4'):
            vid_path = os.path.join(clips_folder, file)
            clips.append(mpe.VideoFileClip(vid_path))
    if len(clips) == 0:
        return 'No clips found.'
    total_dur = 0
    order = random.sample(clips, len(clips))
    new_clips = []
    while total_dur < duration:
        for clip in order:
            new_clip = clip.without_audio().fx(mpe.vfx.speedx, 1.8).fx(mpe.vfx.mirror_x)
            end = min(clip_length, new_clip.duration)
            if clip_length < new_clip.duration:
                new_clip = new_clip.subclip(0, end)
            new_clips.append(new_clip)
            total_dur += end
    final_video = mpe.concatenate_videoclips(new_clips, method='compose')
    return final_video.subclip(0, min(final_video.duration, duration))


def add_avatar(video, avatar_path):
    """
    Add an avatar to a video.

    Args:
        video (VideoClip): The video to add the avatar to.
        avatar_path (str): The path to the avatar image file.

    Returns:
        CompositeVideoClip: The video with the avatar added.
    """
    avatar = mpe.ImageClip(avatar_path).set_duration(video.duration)
    avatar = avatar.resize(height=video.h / 4)
    avatar = avatar.set_position((video.w - avatar.w - (2 * avatar.w), 4 * avatar.w))
    return mpe.CompositeVideoClip([video, avatar])

def add_vfx(vid, VFX_FOLDER):
    pass


def add_clip(vid1, vid2):
    new_vid = vid1.mask_color(vid2, color=[255,0,0], thr=200, s=3)
    return vid1