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


def generate_script(prompt, reference_path, prompt_path, model_name="gpt-3.5-turbo"):
    script = chat_gpt(prompt, model_name)
    return script
