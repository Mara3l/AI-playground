import streamlit as st
import json
import os
from openai import OpenAI

TEST_PATH = "test"
SYSTEM_MESSAGE = ("You are a security expert regarding Python and specialize in"
                  "securing vulnerabilities on code run in cloud. You are very pedantic! You always point out, problems"
                  "with importing os and other problematic imports."
                  "You are also very verbose in your concerns regarding cyber security.")


security_functions = [
    {
        'name': 'comment_out_risks',
        'description': 'Comments out all the possible vulnerabilities from the source as lines',
        'parameters': {
            'type': 'object',
            'properties': {
                'vulnerabilities': {
                    'type': 'array',
                     'items': {
                         'type': 'integer'
                     },
                    'minItems': 0,
                    'maxItems': 999,
                    'description': 'Array of indices of the lines to be commented out'
                },
                'comments': {
                    'type': 'string',
                    'description': (
                            'Comment to be printed out, explaining the vulnerabilities. If everything is OK,'
                            'just comment on what the code does. Format it in markdown, so it is easy to'
                            'print out. Provide code examples as in-line codes.'
                            'Each problem is described in its own bullet-point')
                },
            }
        },
        "required": ["vulnerabilities", "comments"]
    }
]

def reset_comments():
    st.session_state["comment_out"] = []


def list_ipynb_files(directory):
    ipynb_files = [file for file in os.listdir(directory) if file.endswith(".ipynb")]
    return ipynb_files


def test_the_code(cont: st.container):
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4-turbo-preview"

    if "jupyter_code" not in st.session_state or st.session_state["jupyter_code"] == "":
        cont.text("Seems, like there is no code to check..?")
        return

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    stream = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": f"I have a cloud-based platform and I need you to check some code for me,"
                                        f"It is very important that you help me, as I may get fired for this."
                                        f"Each line is numbered. Refer to them in the answer."
                                        f"Is this code OK to run? {st.session_state['jupyter_code']}."}

        ],
        tools=[
            {
                'type' : 'function',
                'function': {
                    'name': 'comment_out_risks',
                    'description': 'Comments out all the possible vulnerabilities from the source as lines',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'vulnerabilities': {
                                'type': 'array',
                                'items': {
                                    'type': 'integer'
                                },
                                'minItems': 0,
                                'maxItems': 999,
                                'description': 'Array of indices of the lines to be commented out'
                            },
                            'comments': {
                                'type': 'string',
                                'description': 'Comment to be printed out, explaining the vulnerabilities. If everything is OK,'
                                               'just comment on what the code does.'
                            },
                        }
                    },
                "required": ["vulnerabilities", "comments"]
                }
            }
        ],
        tool_choice='auto',
    )
    if stream and stream.choices:
        args = stream.choices[0].message.tool_calls[0].function.arguments
        args = json.loads(args)
        arg = cont.text(f'Vulnerabilities:\n{args["vulnerabilities"]}')
        comment = str(args['comments']).replace("'","`")
        cont.markdown(f"AI Comment:\n\n {comment}")
        st.session_state["comment_out"] = args['vulnerabilities']
    else:
        cont.markdown("The code passed! :)")


def run():
    if "messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "comment_out" not in st.session_state:
        st.session_state["comment_out"] = []

    files = list_ipynb_files(TEST_PATH)
    selected_file = st.selectbox("Select a file", files, on_change=reset_comments)


    st.session_state["jupyter_code"] = ""
    codeline = 0

    with st.container(height=300):
        st.title("Notebook preview:")
        with open(TEST_PATH + "/" + selected_file, "r") as f:
            a = f.read()
            a = json.loads(a)
            for cell in a["cells"]:
                if cell['cell_type'] == 'code':
                    # Process each line of code within the cell
                    lines = cell['source']
                    numbered_lines = []
                    for line in lines:
                        codeline += 1
                        if codeline in st.session_state["comment_out"]:
                            numbered_lines.append(f"{codeline} # !DANGEROUS! {line}")
                        else:
                            numbered_lines.append(f"{codeline} {line}")

                    # Join the numbered lines back into a single string
                    text = ''.join(numbered_lines)
                    st.markdown("```\n" + text + "\n```")

                    # If using st.session_state to accumulate code, update it similarly
                    if "jupyter_code" not in st.session_state:
                        st.session_state["jupyter_code"] = text
                    else:
                        st.session_state["jupyter_code"] += "\n" + text
                else:
                    # Non-code cells are processed as before
                    text = ''.join(cell['source'])
                    st.markdown(text)

    container = st.container(height=300)
    container.title("Notebook Vulnerability Analysis:")
    st.button('Test!', on_click=test_the_code, args=[container])