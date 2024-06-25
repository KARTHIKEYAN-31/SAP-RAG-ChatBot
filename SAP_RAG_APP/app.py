import streamlit as st 
import functions as func
import os


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
    with st.chat_message("assistant"):
        st.write(response['answer'])
    st.session_state.messages.append({"role": "assistant", "content": response['answer']})
    # return 

@st.experimental_fragment
def get_uploaded_docs():
    conn = func.get_hana_db_conn()
    df = func.get_sap_table('MAV_SAP_RAG', 'DBADMIN', conn)
    if df.shape[0] != 0:
        doc_list = [eval(d).get("source") for d in df['VEC_META']]
        df['file_name'] = [os.path.basename(path) for path in doc_list]
        doc_list = df['file_name'].unique()
        return doc_list
    else: 
        return []




st.set_page_config(
    page_title="Chat-Bot",
    page_icon="🤖",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_name" not in st.session_state:
    st.session_state.file_name = ""

 

st.title("Chat with Data")

st.sidebar.header("File Manager")

if st.sidebar.button("Clear Chat"):
    clear_chat()   

# hf_key = st.sidebar.password_input("HuggingFace API Key", type="password")

# if 'hf' in hf_key:
#     hf.login(hf_key)


chat_mode = st.sidebar.selectbox("How do you want to start the chat?", ( "Chat with Pre-Uploaded Data","File Upload"))

clear_data = st.sidebar.button("Clear Data from DB", key="clear_data")

if chat_mode == "File Upload":

    file = st.sidebar.file_uploader("Upload a file to Chat with", type=["csv", "txt", "pdf"])

    doc_list = get_uploaded_docs()
    if file is not None:
        # st.session_state.messages = []
        if file.name not in doc_list:
            # file_data = func.read_file(file)
            api_output = func.call_file_api(file)
            
            st.sidebar.write(api_output["status"])
            st.session_state.file_name = api_output["file_name"]

            if api_output["status"] == "Success":

                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                
                if prompt := st.chat_input("Come on lets Chat!"):
                    init_chat()
        else:
            if file.name in doc_list:
                st.sidebar.write("File Name already Exist")



elif chat_mode == "Chat with Pre-Uploaded Data":

    doc_list = get_uploaded_docs()

    all_doc = st.sidebar.toggle("All Documents", )
    if all_doc == False:
        file_name = st.sidebar.selectbox("Select Document", doc_list)
        st.session_state.file_name = file_name

    # st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Come on lets Chat!"):
        init_chat()


if clear_data == True:
    func.clear_data()
    


