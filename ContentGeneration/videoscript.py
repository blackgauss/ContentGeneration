import json
import os
import random
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

OPENAI_KEY  = os.getenv("OPENAI_KEY")

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key= OPENAI_KEY,
)

def format_script(post):
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
    
    return script


def make_prompt(context, refrence):
    return context + '\n' +  refrence


def chat_gpt(prompt, model_name="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def rank_interest(reference):
    with open('../data/gpt_prompts/topic_chooser.txt', 'r') as file:
        interest_prompt = file.read()
    prompt = make_prompt(interest_prompt, reference)
    interest = chat_gpt(prompt, model_name='gpt-3.5-turbo')
    try:
        return int(interest)
    except:
        return None

    return interest
def create_draft(reference):
    with open('../data/gpt_prompts/script_writer.txt', 'r') as file:
        writer_prompt = file.read()
    with open('../data/gpt_prompts/hook_editor.txt', 'r') as file:
        hook_prompt = file.read()
    with open('../data/gpt_prompts/script_editor.txt', 'r') as file:
        editor_prompt = file.read()
    first_prompt = make_prompt(writer_prompt, reference)
    script = chat_gpt(first_prompt, model_name='gpt-4-1106-preview')
    return script

def improve_hook(script):
    with open('../data/gpt_prompts/hook_editor.txt', 'r') as file:
        hook_prompt = file.read()
    prompt = make_prompt(hook_prompt, script)
    edited_hook = chat_gpt(prompt, model_name='gpt-4-1106-preview')
    return edited_hook


def edit_script(script):
    with open('../data/gpt_prompts/script_editor.txt', 'r') as file:
        editor_prompt = file.read()
    prompt = make_prompt(editor_prompt, script)
    edited_script = chat_gpt(prompt, model_name='gpt-4-1106-preview')
    return edited_script


def critique_script(script):
    with open('../data/gpt_prompts/viewer_critique.txt', 'r') as file:
        critique_prompt = file.read()
    prompt = make_prompt(critique_prompt, script)
    critique = chat_gpt(prompt, model_name='gpt-4-1106-preview')
    return critique


def revise_script(script, critique):
    with open('../data/gpt_prompts/script_reviser.txt', 'r') as file:
        revision_prompt = file.read()
    reference = f'Criticism:{critique}\n Script:{script}'
    prompt = make_prompt(revision_prompt, reference)
    revision = chat_gpt(prompt, model_name='gpt-4-1106-preview')
    return revision


def score_script(script):
    with open('../data/gpt_prompts/script_scorer.txt', 'r') as file:
        scoring_prompt = file.read()
    prompt = make_prompt(scoring_prompt, script)
    score = chat_gpt(prompt, model_name='gpt-4-1106-preview')
    return score
    