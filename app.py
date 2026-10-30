
import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


# =========================================================
# 1. CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Nemotron AI Text Optimizer",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH, override=True)

API_KEY = os.getenv("NVIDIA_API_KEY", "").strip()

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "nvidia/nemotron-3.5-super-vl-120b-a12b"


# =========================================================
# 2. SESSION STATE
# =========================================================

DEFAULTS = {
    "optimized_result": "",
    "last_input": "",
    "result_version": 0,
    "request_error": ""
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def clear_previous_result():
    """Clear stale output whenever the original input changes."""
    st.session_state.optimized_result = ""
    st.session_state.last_input = ""
    st.session_state.request_error = ""
    st.session_state.result_version += 1


def reset_application():
    """Reset both text panels and all previous results."""
    st.session_state.original_input = ""
    st.session_state.optimized_result = ""
    st.session_state.last_input = ""
    st.session_state.request_error = ""
    st.session_state.result_version += 1


# =========================================================
# 3. CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: #0b1020;
    color: #edf2ff;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: #111a2e;
    border-right: 1px solid #293957;
}

.hero {
    padding: 30px;
    border: 1px solid #293957;
    border-radius: 18px;
    background: linear-gradient(120deg, #172642, #142033);
    margin-bottom: 25px;
}

.hero h1 {
    color: #ffffff;
    font-size: 34px;
    font-weight: 750;
    margin-bottom: 8px;
}

.hero p {
    color: #bdcbe3;
    font-size: 15px;
    margin-bottom: 0;
}

.section-title {
    color: #edf2ff;
    font-size: 19px;
    font-weight: 700;
    margin-bottom: 10px;
}

.small-note {
    color: #9eacc5;
    font-size: 12px;
}

div[data-testid="stTextArea"] textarea {
    background-color: #111a2e;
    color: #edf2ff;
    border: 1px solid #334766;
    border-radius: 12px;
    font-size: 15px;
    line-height: 1.7;
}

div[data-testid="stTextArea"] textarea:disabled {
    color: #edf2ff;
    opacity: 1;
    -webkit-text-fill-color: #edf2ff;
}

div.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 10px;
    font-weight: 650;
    transition: 0.2s ease;
}

div.stButton > button[kind="primary"] {
    background: #315ce8;
    border: 1px solid #315ce8;
    color: white;
}

div.stButton > button[kind="primary"]:hover {
    background: #4770ff;
    border-color: #4770ff;
}

div[data-testid="stAlert"] {
    border-radius: 10px;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 4. SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ✦ Nemotron AI")

    st.caption("Intelligent English Writing Assistant")

    st.divider()

    st.markdown("### Writing Style")

    style = st.selectbox(
        "Select optimization style",
        [
            "Grammar Correction",
            "Professional",
            "Clear & Concise",
            "Friendly",
            "Academic"
        ]
    )

    st.divider()

    st.markdown("### Optimization Settings")

    preserve_meaning = st.checkbox(
        "Preserve original meaning",
        value=True
    )

    improve_clarity = st.checkbox(
        "Improve sentence clarity",
        value=True
    )

    remove_repetition = st.checkbox(
        "Remove unnecessary repetition",
        value=True
    )

    st.divider()

    st.markdown("### AI Model")

    st.caption("NVIDIA Nemotron")
    st.caption(MODEL)

    st.divider()

    st.markdown(
        '<p class="small-note">'
        'API credentials are loaded privately from your .env file.'
        '</p>',
        unsafe_allow_html=True
    )


# =========================================================
# 5. HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <h1>✦ AI Text Optimizer</h1>
    <p>
        Transform incorrect English into grammatically correct,
        clear and natural writing using NVIDIA Nemotron.
    </p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# 6. GRAMMAR CORRECTION FUNCTION
# =========================================================

def optimize_text(
    text,
    writing_style,
    preserve,
    clarity,
    repetition
):

    system_prompt = """
You are an expert English grammar correction and proofreading assistant.

YOUR MAIN TASK:

Correct the user's English text so that it becomes grammatically
correct, natural, fluent and easy to understand.

STRICT GRAMMAR RULES:

1. Correct subject-verb agreement.
2. Correct present, past and future tense.
3. Correct verb forms and auxiliary verbs.
4. Correct articles: a, an and the.
5. Correct prepositions: in, on, at, to, for, from, etc.
6. Correct singular and plural nouns.
7. Correct spelling and punctuation.
8. Correct pronoun usage.
9. Correct word order and sentence structure.
10. Correct incomplete and awkward sentences.
11. Ensure that time expressions agree with the verb tense.
12. Use natural and contextually appropriate English.

IMPORTANT MEANING RULES:

1. Preserve the user's intended meaning.
2. Make only the changes necessary to correct the text.
3. Do not invent facts, people, events or context.
4. Do not unnecessarily rewrite already correct sentences.
5. Do not change a sentence's meaning just to make it sound
   more professional.
6. If the sentence is ambiguous, choose the smallest reasonable
   correction rather than inventing an interpretation.
7. Do not leave obvious grammatical errors uncorrected.

EXAMPLES:

Input:
i went to temple tomorrow

Output:
I will go to the temple tomorrow.

Input:
she don't know computer

Output:
She doesn't know computers.

Input:
he have completed his work

Output:
He has completed his work.

Input:
i am study now

Output:
I am studying now.

Input:
i want apply internship in your company

Output:
I want to apply for an internship at your company.

Input:
they was playing cricket when it start raining

Output:
They were playing cricket when it started raining.

OUTPUT RULES:

- Always respond in English.
- Return only the corrected text.
- Do not provide explanations.
- Do not include headings such as "Corrected Text".
- Preserve paragraph structure where appropriate.
"""

    style_instructions = {
        "Grammar Correction": (
            "Focus primarily on grammar, spelling, punctuation "
            "and sentence correctness. Avoid unnecessary rewriting."
        ),
        "Professional": (
            "Use professional and polished English while "
            "preserving the original message."
        ),
        "Clear & Concise": (
            "Make the writing clear, direct and concise without "
            "removing important information."
        ),
        "Friendly": (
            "Use natural, friendly and approachable English "
            "while preserving the message."
        ),
        "Academic": (
            "Use formal academic English with accurate grammar "
            "and appropriate sentence structure."
        )
    }

    user_prompt = f"""
Correct the following English text.

WRITING STYLE:
{writing_style}

STYLE INSTRUCTIONS:
{style_instructions[writing_style]}

PRESERVE ORIGINAL MEANING:
{preserve}

IMPROVE CLARITY:
{clarity}

REMOVE UNNECESSARY REPETITION:
{repetition}

IMPORTANT:
Read the complete text before correcting it.
Check grammar, tense, prepositions, articles and sentence structure.
Do not make capitalization-only changes when grammar is incorrect.
Return the complete corrected text only.

TEXT:

{text}
"""

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0,
        "top_p": 1,
        "max_tokens": 2048,
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=(15, 120)
    )

    if not response.ok:

        try:
            details = response.json()
            error = details.get("error", {})
            if isinstance(error, dict):
                message = error.get("message", str(error))
            else:
                message = str(error)

        except ValueError:
            message = response.text[:400]

        raise RuntimeError(
            f"NVIDIA API Error ({response.status_code}): {message[:400]}"
        )

    try:
        data = response.json()
        message = data["choices"][0]["message"]
        optimized = message.get("content")

        if isinstance(optimized, list):
            optimized = "\n".join(
                item.get("text", "")
                for item in optimized
                if isinstance(item, dict)
            )

        if not isinstance(optimized, str) or not optimized.strip():
            raise RuntimeError(
                "The model returned an empty response. Please try again."
            )

        return optimized.strip()

    except (KeyError, IndexError, TypeError, ValueError):
        raise RuntimeError(
            "Unable to read the corrected text from the NVIDIA API response."
        )


# =========================================================
# 7. ORIGINAL AND OPTIMIZED TEXT PANELS
# =========================================================

left, right = st.columns(2, gap="large")

with left:

    st.markdown(
        '<div class="section-title">📝 Original Text</div>',
        unsafe_allow_html=True
    )

    original_text = st.text_area(
        "Enter original text",
        placeholder=(
            "Example:\n\n"
            "i am go to college yesterday and meet my friend"
        ),
        height=320,
        key="original_input",
        label_visibility="collapsed",
        on_change=clear_previous_result
    )

    st.caption(f"Characters: {len(original_text)}")


with right:

    st.markdown(
        '<div class="section-title">✨ Optimized Text</div>',
        unsafe_allow_html=True
    )

    result = st.session_state.optimized_result

    if result:

        st.text_area(
            "Corrected text",
            value=result,
            height=320,
            key=f"optimized_output_{st.session_state.result_version}",
            disabled=True,
            label_visibility="collapsed"
        )

        st.caption(
            f"Characters: {len(result)}"
        )

    else:

        st.text_area(
            "Corrected text",
            value="",
            placeholder=(
                "Your corrected English text will appear here "
                "after you click Correct & Optimize."
            ),
            height=320,
            key=f"empty_output_{st.session_state.result_version}",
            disabled=True,
            label_visibility="collapsed"
        )

        st.caption("Waiting for your text...")


# =========================================================
# 8. ACTION BUTTONS
# =========================================================

st.markdown("")

button_col1, button_col2 = st.columns([3, 1])

with button_col1:

    optimize_clicked = st.button(
        "✦ Correct & Optimize Text",
        type="primary",
        use_container_width=True
    )

with button_col2:

    st.button(
        "↺ Reset",
        use_container_width=True,
        on_click=reset_application
    )


# =========================================================
# 9. OPTIMIZATION PROCESS
# =========================================================

if optimize_clicked:

    input_text = original_text.strip()

    if not API_KEY:

        st.error(
            "NVIDIA API key not found. Please check your .env file."
        )

    elif not input_text:

        st.warning(
            "Please enter some text before optimization."
        )

    else:

        try:

            with st.spinner(
                "✦ Nemotron is analyzing and correcting your text..."
            ):

                new_result = optimize_text(
                    text=input_text,
                    writing_style=style,
                    preserve=preserve_meaning,
                    clarity=improve_clarity,
                    repetition=remove_repetition
                )

            st.session_state.optimized_result = new_result
            st.session_state.last_input = input_text
            st.session_state.request_error = ""
            st.session_state.result_version += 1

            st.rerun()

        except requests.exceptions.Timeout:

            st.error(
                "The request timed out. Please try again."
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "Unable to connect to NVIDIA API. "
                "Check your internet connection."
            )

        except requests.exceptions.RequestException as error:

            st.error(
                f"Network error: {error}"
            )

        except RuntimeError as error:

            st.error(str(error))

        except Exception as error:

            st.error(
                f"Unexpected error: {type(error).__name__}: {error}"
            )


# =========================================================
# 10. COPY RESULT
# =========================================================

if st.session_state.optimized_result:

    st.markdown("")

    st.markdown("### Corrected Text Actions")

    st.code(
        st.session_state.optimized_result,
        language=None
    )

    st.caption(
        "Use the copy icon on the code block to copy the corrected text."
    )


# =========================================================
# 11. FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <p class="small-note" style="text-align:center;">
        ✦ NVIDIA Nemotron AI Text Optimizer
        &nbsp; | &nbsp;
        Intelligent English Grammar Correction
    </p>
    """,
    unsafe_allow_html=True
)
