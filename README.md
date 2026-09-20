# 📄 PDF-Based RAG

### AI-Powered PDF Question Answering Chatbot

Advance RAG is a document question-answering application that allows users to upload PDF documents and ask questions about their content through a conversational chat interface.

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from the uploaded document before generating an answer.

---

## 🚀 Demo

> Upload a PDF → Ask a question → Get an answer based on your document.

### ✨ Key Highlights

- 📂 Upload and process PDF documents
- 🔍 Retrieve relevant document content using FAISS
- 🤖 Generate AI-powered responses using Groq
- 💬 Maintain separate conversations
- 🔐 Keep document retrieval scoped to each conversation
- ⚡ Use a local fallback when Groq is unavailable
- 🧠 Support follow-up questions using conversation history

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend API development |
| Streamlit | Interactive frontend |
| pypdf | PDF text extraction |
| Sentence Transformers | Text embeddings |
| FAISS | Vector similarity search |
| Groq API | LLM-based answer generation |

---

## 🧠 How RAG Works

```text
              📄 Upload PDF
                    |
                    ▼
           Extract PDF Text
                    |
                    ▼
             Split into Chunks
                    |
                    ▼
          Generate Embeddings
                    |
                    ▼
          Store in FAISS Index
                    |
                    ▼
             User Asks Question
                    |
                    ▼
       Convert Question to Embedding
                    |
                    ▼
        Retrieve Relevant Chunks
                    |
                    ▼
          Generate Answer with Groq
                    |
                    ▼
             💬 Display Response
```

---

## 📁 Project Structure

```text
advance-rag/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   │
│   ├── data/
│   │   └── uploads/
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── rag_pipeline.py
│   │
│   └── vector_db/
│
└── frontend/
    ├── app.py
    ├── requirements.txt
    └── chat_history.json
```

---

## ⚙️ How the Application Works

### 1. PDF Processing

- The user uploads a PDF.
- Text is extracted using `pypdf`.
- The extracted text is divided into overlapping chunks.

### 2. Embedding Generation

Each text chunk is converted into a numerical vector using:

```text
all-MiniLM-L6-v2
```

### 3. Vector Storage

The embeddings are stored in a FAISS index to support similarity-based retrieval.

### 4. Question Answering

When the user asks a question:

1. The question is converted into an embedding.
2. Relevant document chunks are retrieved.
3. Retrieved content is provided to the Groq LLM.
4. The generated response is displayed in the chat interface.

---

## 🔑 Features in Detail

### 📌 Conversation-Based Document Scope

Each conversation is associated with its own uploaded document.

This helps prevent retrieval of content from another conversation's PDF.

### 📌 Follow-Up Questions

Recent messages from the same conversation are used to support contextual follow-up questions.

### 📌 Fallback Response

If the Groq API is unavailable or no API key is configured, the application returns relevant excerpts from the retrieved document chunks.

---

## 📋 Requirements

- Python 3.10 or newer
- C++ runtime supported by `faiss-cpu`
- Optional Groq API key

---

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/advance-rag.git
cd advance-rag
```

### 2. Set Up the Backend

```powershell
cd backend

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Create a `.env` file inside the `backend` directory:

```env
GROQ_API_KEY=your_groq_api_key
```

### 3. Set Up the Frontend

Open another terminal:

```powershell
cd frontend

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

---

## ▶️ Running the Application

### Start the Backend

```powershell
cd backend

.\venv\Scripts\Activate.ps1

uvicorn main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

### Start the Frontend

Open a second terminal:

```powershell
cd frontend

.\venv\Scripts\Activate.ps1

streamlit run app.py
```

Open the Streamlit URL displayed in your terminal.

Usually:

```text
http://localhost:8501
```

---

## 🔗 API Endpoints

### Health Check

```http
GET /health
```

### Upload PDF

```http
POST /upload
Content-Type: multipart/form-data
```

### Ask a Question

```http
POST /ask
Content-Type: application/json
```

Example request:

```json
{
  "question": "What is the main conclusion?",
  "document_id": "generated-document-id",
  "history": [
    {
      "role": "user",
      "content": "Summarize the document."
    },
    {
      "role": "assistant",
      "content": "The document discusses..."
    }
  ]
}
```

---

## 🔒 Data and Privacy

- Uploaded PDFs are excluded from version control.
- Chat history is excluded from version control.
- FAISS-generated files are excluded from version control.
- API keys are stored in environment variables.
- Never commit your `.env` file or API keys.

---

## ⚠️ Limitations

- Scanned or image-only PDFs may not contain extractable text.
- The Sentence Transformer model may download during first startup.
- Retrieval quality depends on the extracted text and chunking strategy.
- Groq-generated answers require a valid API key.

---

## 📚 Learning Outcomes

Through this project, I explored:

- Retrieval-Augmented Generation (RAG)
- PDF text processing
- Text chunking
- Semantic embeddings
- Vector similarity search
- FAISS indexing
- FastAPI backend development
- Streamlit application development
- Conversation-based document retrieval
- LLM integration

---

## 👩‍💻 Author

**Vaishnavi Agrawal**

B.Tech in Artificial Intelligence

Interested in Artificial Intelligence, Generative AI, and Full-Stack Development.

---

⭐ If you find this project useful, consider giving it a star!
