from fastapi import FastAPI, File, UploadFile, Form
from huggingface_hub import HfApi
import os
import api_functions as func
from langchain_community.vectorstores.hanavector import HanaDB
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_huggingface import HuggingFaceEndpoint




app = FastAPI()

HF_key = os.environ.get("HF_TOKEN")
HFapi = HfApi(HF_key)

#create hanaDB connection and embeddings
conn = func.get_hana_db_conn()
embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=HF_key, model_name="sentence-transformers/all-MiniLM-l6-v2"
)

@app.post("/upload")
async def process_input(file: UploadFile = File(...)):

    #store file temporarily
    file_path = func.get_temp_file_path(file)
    file_extension = os.path.splitext(file_path)[1]

    db = HanaDB(embedding=embeddings, connection=conn, table_name="MAV_SAP_RAG")
    # db.delete(filter={})

    error = 0

    if file_extension == ".pdf":
        db.add_documents(func.get_text_from_pdf(file_path))
    elif file_extension == ".txt":
        db.add_documents(func.get_text_from_txt(file_path))
    elif file_extension == ".csv":
        db.add_documents(func.get_text_from_csv(file_path))
    else:
        error = 1
    
    if error == 0:
        return {"status": "Success", "file_name": file.filename}
    else:
        return {"status": "File type not supported"}



@app.post("/chat")
async def process_input(query: str = Form(...), file_name: str = Form("Temp")):

    llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.3",
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        repetition_penalty=1.03,
    )

    db = HanaDB(embedding=embeddings, connection=conn, table_name="MAV_SAP_RAG")
    qa_chain = func.get_llm_chain(llm, db, file_name)
    # result = qa_chain({"question": query})
    result = qa_chain.invoke({"question": query, "chat_history": []})
    # answer = func.extract_between_colon_and_period(result['answer'])
    return result
    # return {"Message": answer}

@app.get("/clear_data")
async def clear_data():
    db = HanaDB(embedding=embeddings, connection=conn, table_name="MAV_SAP_RAG")
    db.delete(filter={})
    return {"status": "Success"}

 
