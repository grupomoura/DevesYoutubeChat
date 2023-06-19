import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import YoutubeLoader
from langchain.llms import OpenAI
from langchain.docstore.document import Document

import os

open_ai_key = os.environ["OPENAI_API_KEY"]

if open_ai_key:
    print("API Key:", open_ai_key)
else:
    print("API Key not found in environment variables.")

class YoutubeQuery:
    def __init__(self, openai_api_key = open_ai_key) -> None:
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        os.environ["OPENAI_API_KEY"] = openai_api_key
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
        self.chain = None
        self.db = None

    def ask(self, question: str) -> str:
        if self.chain is None:
            response = "Por favor, adicione o link de um vídeo."
        else:
            docs = self.db.get_relevant_documents(question)
            response = self.chain.run(input_documents=docs, question=question)
        return response

    def ingest(self, url: str) -> str:
        documents = YoutubeLoader.from_youtube_url(url, add_video_info=False, language='pt').load()
        splitted_documents = self.text_splitter.split_documents(documents)
        self.db = Chroma.from_documents(splitted_documents, self.embeddings).as_retriever()
        self.chain = load_qa_chain(OpenAI(temperature=0), chain_type="stuff")
        return "Success"

    def forget(self) -> None:
        self.db = None
        self.chain = None