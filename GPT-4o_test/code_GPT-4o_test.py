"""this code was run on Colab"""

!pip install -q pandas tqdm openai openpyxl

import os
import time
import pandas as pd
from tqdm import tqdm
from openai import OpenAI
from getpass import getpass

from google.colab import files

uploaded=files.upload()

INPUT_FILE_ADJECTIVES = "input_adjectives.xlsx"
INPUT_FILE_SENTENCES = "input_sentences.xlsx"
OUTPUT_FILE_ADJECTIVES = "output_no_context.xlsx" 
OUTPUT_FILE_SENTENCES = "output_with_context.xlsx"



MODEL = "gpt-4o"
SLEEP_TIME = 20

os.environ["OPENAI_API_KEY"] = getpass("Incolla OPENAI_API_KEY: ")
client = OpenAI()

PROMPT_NO_CONTEXT = """Given the Italian adjective:

{LEMMA}

Return its negative form using a negation prefix
(i.e., in-, im-, il-, ir-, dis-, a-, de-, s-, mis-), when attested in Italian.
When not, answer NO.

No explanation
"""

PROMPT_WITH_CONTEXT = """Consider the following Italian sentence:

{SENTENCES}

The adjective "{LEMMA}" appears in the sentence.

Rewrite the sentence by replacing the adjective
with its standard and commonly attested negative form
created using a negation prefix (e.g. in-, im-, il-, ir-, dis-, a-, de-, s-, mis-),
ONLY IF such a form exists in standard Italian usage.

If no well-established negative adjective exists,
leave the sentence unchanged.

Do not invent or guess new words.
Do not change anything else in the sentence.

Return only the final sentence."""

def call_llm(prompt: str) -> str:
    response = client.responses.create(
        model=MODEL,
        input=prompt,
        temperature=0,
        max_output_tokens=64
    )
    return response.output_text.strip()

def main_adjectives():
    df = pd.read_excel(INPUT_FILE_ADJECTIVES)

    results = []

    for row in tqdm(df.itertuples(index=False), total=len(df)):
        lemma = str(row.LEMMA).strip()

        out = call_llm(PROMPT_NO_CONTEXT.format(LEMMA=lemma))

        results.append({
            "LEMMA": lemma,
            "OUTPUT": out
        })

        time.sleep(SLEEP_TIME)

    pd.DataFrame(results).to_excel(OUTPUT_FILE_ADJECTIVES, index=False)
    print(f"✔ Salvato {OUTPUT_FILE_ADJECTIVES}")


def main_sentences():
    df = pd.read_excel(INPUT_FILE_SENTENCES)

    results = []

    for row in tqdm(df.itertuples(index=False), total=len(df)):
        lemma = str(row.LEMMA).strip()

       
        if pd.isna(row.SENTENCES):
            continue

        sentence = str(row.SENTENCES).strip()

        out = call_llm(
            PROMPT_WITH_CONTEXT.format(
                LEMMA=lemma,
                SENTENCES=sentence
            )
        )

        results.append({
            "LEMMA": lemma,
            "ORIGINAL_SENTENCE": sentence,
            "OUTPUT_SENTENCE": out
        })

        time.sleep(SLEEP_TIME)

    pd.DataFrame(results).to_excel(OUTPUT_FILE_SENTENCES, index=False)
    print(f"✔ Salvato {OUTPUT_FILE_SENTENCES}")

main_adjectives()
main_sentences()

