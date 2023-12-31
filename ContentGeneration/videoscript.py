import json
import os
import random
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

OPENAI_KEY  = os.gentenv("OPENAI_KEY")
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key= OPENAI_KEY,
)

def save_script(post, rawscript_path = '../videos/raw_scripts'):
    """
    Save the script to a text file.

    Args:
        post (tuple): A tuple containing the post information.
            The tuple should have the following elements:
            - id (int): The ID of the post.
            - url (str): The URL of the post.
            - question (str): The question of the post.
            - context (str): The context of the post.
            - answers (list): A list of answers for the post.
            - citation (list): A list of citations for the post.
        rawscript_path (str, optional): The path to the directory where the script file will be saved.
            Defaults to '../videos/raw_scripts'.

    Returns:
        None
    """
    id = post[0]
    url = post[1]
    question = post[2]
    context = post[3]
    answers = post[4]
    citation = post[5]

    long_answer = ''
    for answer in answers:
        long_answer += answer + '\n\n'

    long_citation = ''
    long_citation += url + '\n\n'
    for cite in citation:
        long_citation += cite[0] + '\n\n'
    
    script = f"--BEGIN QUESTION--\n\n{question}\\n\n--END QUESTION--\n\n" \
             f"--BEGIN CONTEXT--\n\n{context}\n\n--END CONTEXT--\n\n" \
             f"--BEGIN ANSWER--\n\n{long_answer}\n\n--END ANSWER--\n\n" \
             f"--BEGIN CITATION--\n\n{long_citation}\n\n--END CITATION--\n\n"

    with open(f'{rawscript_path}/{id}.txt', 'w') as file:
        file.write(script)


def make_prompt(preprompt_filename, reference_filename):
    with open(preprompt_filename, 'r') as file:
        PRE_PROMPT = file.read()
    with open(reference_filename, 'r') as file:
        post_prompt = file.read()
    return PRE_PROMPT + '\n' +  post_prompt


def chat_gpt(prompt, model_name="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def script_write(script_id, rawscript_path = '../videos/raw_scripts' ,prompt_path='../data/gpt_prompts/script_writer.txt', script_path='../videos/scripts/', model_name="gpt-3.5-turbo"):
    prompt = make_prompt(prompt_path, f'{rawscript_path}/{script_id}.txt')
    script = chat_gpt(prompt, model_name)
    with open(script_path + script_id + '.txt', 'w') as file:
        file.write(script)


def make_video(script_id, clips_folder, voiceover_folder, save_folder, clip_length):
    file_path = f'{save_folder}/{script_id}.mp4'
    if not os.path.exists(file_path):
        [audio, dur] = get_voiceover2(script_id, voiceover_folder)
        final_clip = make_video(dur, CLIPS_FOLDER, clip_length)
        final_clip.set_audio(audio).write_videofile(file_path, audio_codec='aac')
    else:
        return f'{script_id} already exists.'
