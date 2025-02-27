import logging
import sys
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SKLearnVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

DATA_PATH = "vector.json"

class RAGApplication:
    def __init__(self, model: str, *files: str):
        self.model = model
        vectorstore = RAGSKVectorStore(files, model).save() if len(files) > 0 else RAGSKVectorStore(files, model).load()
        prompt = PromptTemplate(
            template="""You are an assistant for question-answering tasks.
            Use the following documents to answer the question.
            If you don't know the answer, just say that you don't know.
            Use three sentences maximum and keep the answer concise:
            Question: {question}
            Documents: {documents}
            Answer:
            """,
            input_variables=["question", "documents"],
        )
        llm = ChatOllama(
            model=self.model,
            temperature=0,
        )
        self.rag_chain = prompt | llm | StrOutputParser()
        self.retriever = vectorstore.as_retriever(k=4)

    def run(self):
        while True:
            print("Ask a question: ")
            question = sys.stdin.readline()
            if question.strip() == "exit":
                print('exiting...')
                break
            # Retrieve relevant documents
            documents = self.retriever.invoke(question)
            # Extract content from retrieved documents
            doc_texts = "\\n".join([doc.page_content for doc in documents])
            # Get the answer from the language model
            answer = self.rag_chain.invoke({"question": question, "documents": doc_texts})
            print('answer:', answer)
    
class RAGSKVectorStore():
    def __init__(self, files, model):
       self.files = files
       self.path = DATA_PATH
       self.model = model

    def save(self):
        logging.info("Loading documents...")
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=250, chunk_overlap=0
        )
        logging.debug("splitter created")
        docs = [TextLoader(file, encoding='utf-8').load() for file in self.files]
        docs_list = [item for sublist in docs for item in sublist]
        logging.debug("documents loaded")
        doc_splits = text_splitter.split_documents(docs_list)
        logging.debug("documents splitted")
        vectorstore = SKLearnVectorStore(embedding=OllamaEmbeddings(model=self.model), persist_path=self.path)
        logging.debug("vector store created")
        #vectorstore.delete()
        #logging.debug("vector store cleared")
        vectorstore.add_documents(doc_splits)
        logging.debug("documents loaded into vector store")
        vectorstore.persist()
        logging.debug("vector store persisted")
        logging.info("Loading documents...done")
        return vectorstore

    def load(self):
        logging.info("Loading vector store...")
        print(self.model)
        emb = OllamaEmbeddings(model=self.model)
        vectorstore = SKLearnVectorStore(embedding=emb, persist_path=self.path)
        logging.info("Loading vector store...done")
        return vectorstore

print(sys.argv)
print(*sys.argv)
logging.basicConfig(level=logging.DEBUG)
#app = RAGApplication("llama3.1", *sys.argv[1:])
app = RAGApplication("qwen2.5-coder", *sys.argv[1:])
app.run()