#  Hyderabad Tourism AI Chatbot

An AI-powered tourism assistant that combines **Retrieval-Augmented Generation (RAG)** and **Live Web Search** to provide accurate, context-aware, and up-to-date information about Hyderabad's history, attractions, food, culture, and travel planning.

---

##  Features

* Semantic search using FAISS and Sentence Transformers
*  Live web search for current information
*  Hybrid retrieval (Knowledge Base + Web Search)
*  AI-generated responses using Llama 3.3 70B via Groq
*  Hyderabad tourism, culture, food, and travel guidance
*  Interactive Flask-based chat interface
*  Dynamic landmark image support

---

##  System Architecture

```text
                👤 User
                   │
                   ▼
      ┌─────────────────────────┐
      │  Flask Web Interface    │
      │ (HTML • CSS • JS)       │
      └───────────┬─────────────┘
                  │
                  ▼
      ┌─────────────────────────┐
      │      Query Router       │
      └───────┬─────┬───────────┘
              │     │
     ┌────────┘     └────────┐
     ▼                       ▼
┌─────────┐           ┌─────────┐
│   RAG   │           │   Web   │
│ Search  │           │ Search  │
└────┬────┘           └────┬────┘
     │                     │
     ▼                     ▼
┌─────────┐         ┌───────────┐
│  FAISS  │         │ Live Web  │
│Vector DB│         │  Results  │
└────┬────┘         └─────┬─────┘
     └────────┬───────────┘
              │
              ▼
     ┌───────────────────┐
     │  Context Builder  │
     │ (RAG / Web / Both)│
     └─────────┬─────────┘
               │
               ▼
     ┌───────────────────┐
     │  Groq Llama 3.3   │
     │   Response Engine │
     └─────────┬─────────┘
               │
               ▼
         🤖 AI Response
```

###  Workflow

* **RAG Mode** → Retrieves information from the Hyderabad tourism knowledge base using FAISS.
* **Web Mode** → Fetches current information such as timings, restaurants, and travel updates.
* **Hybrid Mode** → Combines both sources to provide richer and more accurate answers.
* Retrieved information is transformed into context and passed to **Llama 3.3 via Groq**.
* The generated response is returned through the chatbot interface.

---

##  Tech Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Flask
* Python

### AI & Machine Learning

* FAISS Vector Database
* Sentence Transformers
* Retrieval-Augmented Generation (RAG)
* Semantic Search

### LLM

* Groq API
* Llama 3.3 70B Versatile

### Search

* DuckDuckGo Search (DDGS)

---

##  Project Structure

```text
hyderabad-tour-chatbot/
│
├── app.py
├── requirements.txt
│
├── app/
│   ├── static/
│   │   ├── css/
│   │   └── images/
│   │
│   └── templates/
│       └── index.html
│
├── src/
│   ├── rag/
│   ├── retrieval/
│   ├── llm/
│   └── search/
│
└── data/
    └── vectorstore/
        ├── faiss_index
        └── metadata.pkl
```

---

##  Example Queries

```text
Tell me about Golconda Fort

Charminar timings today

Best food places near Charminar

Plan a day around Hyderabad

Famous dishes other than Biryani

Best places to visit in Hyderabad with family
```

---

##  Local Setup

### Clone Repository

```bash
git clone https://github.com/your-username/hyderabad-tour-chatbot.git
cd hyderabad-tour-chatbot
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / Mac**

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

### Run Application

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

---

##  Future Improvements

* Conversation memory
* Google Maps integration
* Weather integration
* Source citations in UI
* Multilingual support (English, Telugu, Hindi)
* Personalized itinerary generation
* Agentic tool selection

---

##  Key Concepts Demonstrated

* Retrieval-Augmented Generation (RAG)
* Vector Databases (FAISS)
* Semantic Search
* Prompt Engineering
* Hybrid Retrieval Systems
* LLM Integration
* Flask Application Development
* AI System Design


