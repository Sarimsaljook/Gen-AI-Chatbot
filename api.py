from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from langchain.chains import LLMChain
from langchain_aws import BedrockLLM
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import boto3
import os

os.environ["AWS_PROFILE"] = "Muhammad Chaudhry"

# Initialize the FastAPI app
app = FastAPI()

# Bedrock client
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

modelID = "anthropic.claude-v2"

llm = BedrockLLM(
    model_id=modelID,
    client=bedrock_client,
    model_kwargs={"max_tokens_to_sample": 2000, "temperature": 0.9}
)

def my_chatbot(language, freeform_text, knowledge_base):
    prompt = PromptTemplate(
        input_variables=["language", "freeform_text", "knowledge_base"],
        template="You are a chatbot. You are in {language}.\n\nKnowledge Base:\n{knowledge_base}\n\n{freeform_text}"
    )

    bedrock_chain = LLMChain(llm=llm, prompt=prompt)
    response = bedrock_chain({"language": language, "freeform_text": freeform_text, "knowledge_base": knowledge_base})
    return response

class QueryRequest(BaseModel):
    language: str
    freeform_text: str
    knowledge_base: str

@app.post("/ask")
def ask_question(query: QueryRequest):
    response = my_chatbot(query.language, query.freeform_text, query.knowledge_base)
    print(response)
    return {"response": response}

@app.post("/upload_pdf")
def upload_pdf(file: UploadFile = File(...)):
    temp_dir = "tempDir"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    temp_file_path = os.path.join(temp_dir, file.filename)
    with open(temp_file_path, "wb") as f:
        f.write(file.file.read())
    loader = PyMuPDFLoader(temp_file_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    knowledge_base = "\n\n".join([doc.page_content for doc in text_splitter.split_documents(documents)])
    return {"knowledge_base": knowledge_base}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
