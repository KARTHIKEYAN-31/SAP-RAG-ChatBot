import streamlit as st 
import functions as func



@st.experimental_fragment
def clear_chat():
    st.session_state.messages = []

@st.experimental_fragment
def init_chat():
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if all_doc == True:
        # st.write('exe')
        response = func.call_chat_api(prompt)
    else:
        response = func.call_chat_api(prompt, st.session_state.file_name)
    ans = func.get_source(response)
    with st.chat_message("assistant"):
        st.markdown(ans)
    st.session_state.messages.append({"role": "assistant", "content": ans})



st.set_page_config(
    page_title="Chat-Bot",
    page_icon="🤖",
    layout="wide",
)

# st.write("""<p style='text-align: center;
#           font-size: 20px;
#           font-weight: bold;
#           position: fixed;
#           top: 0;
#           left: 25%;
#           background-color: #0e1117;'>CHAT WITH DATA</p>""", unsafe_allow_html=True)
 

if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_name" not in st.session_state:
    st.session_state.file_name = ""


# st.markdown(
#     """<style>
#         .element-container:nth-of-type(2) button {
#             height: 0.5em;
#             position: fixed;
#             bottom: 7em;
#         }
#         </style>""",
#     unsafe_allow_html=True,
# )
# st.write("Chat with Data")


# if st.button("Clear Chat"):
#     clear_chat()


all_doc = True
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Come on lets Chat!"):
    if prompt.lower() == "clear chat":
        st.session_state.messages = []

    else:
        init_chat()

