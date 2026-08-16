# Hyderabad Tourism AI — RAG & Hybrid Search Assistant

An AI-powered tourism assistant that combines **Retrieval-Augmented Generation (RAG)**, **Live Web Search**, and **LangChain-powered orchestration** to provide context-aware and up-to-date information about Hyderabad's history, attractions, food, culture, and travel planning.

---

## Features

- Semantic search using FAISS and Sentence Transformers
- Live web search for current information
- Hybrid retrieval combining the knowledge base and web search
- Intelligent query routing between RAG, Web, and Hybrid modes
- Conversation memory for maintaining context across recent messages
- LangChain-powered prompt and LLM orchestration
- AI-generated responses using Llama 3.3 70B via Groq
- Hyderabad tourism, culture, food, and travel guidance
- Interactive Flask-based chat interface
- Dynamic landmark image support
- Lightweight RAG evaluation
- Docker containerization

---

## System Architecture

```text
                User
                  |
                  v
       +----------------------+
       |  Flask Web Interface |
       +----------+-----------+
                  |
                  v
       +----------------------+
       |     Query Router     |
       +----+------------+----+
            |            |
            v            v
       +---------+   +---------+
       |   RAG   |   |   Web   |
       | Search  |   | Search  |
       +----+----+   +----+----+
            |             |
            v             v
       +---------+   +-----------+
       |  FAISS  |   | Live Web  |
       | Vector  |   |  Results  |
       |  Store  |   |           |
       +----+----+   +-----+-----+
             \             /
              \           /
               v         v
          +-------------------+
          |  Context Builder  |
          +---------+---------+
                    |
                    v
          +-------------------+
          |  LangChain + Groq |
          |   Llama 3.3 70B   |
          +---------+---------+
                    |
                    v
               AI Response
```

### Workflow

- **RAG Mode** retrieves information from the Hyderabad tourism knowledge base using FAISS.
- **Web Mode** retrieves current information through live web search.
- **Hybrid Mode** combines knowledge-base retrieval with web search results.
- Retrieved information is assembled into context for response generation.
- LangChain manages prompt construction and LLM interaction.
- Llama 3.3 via Groq generates the final response.

---

## Tech Stack

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- Python
- Flask

### Retrieval and AI

- FAISS
- Sentence Transformers
- Retrieval-Augmented Generation
- Semantic Search

### LLM and Orchestration

- LangChain
- Groq API
- Llama 3.3 70B Versatile

### Search

- DuckDuckGo Search (DDGS)

### Deployment

- Docker

---

## RAG Evaluation

A lightweight evaluation system is included under `evaluation/` to measure retrieval and answer quality.

### Evaluation Results

| Metric                 | Result  |
|------------------------|---------|
| Evaluation Questions   | 30      |
| Recall@3               | 65%     |
| Recall@5               | 75%     |
| Average Relevance      | 73.33%  |
| Average Faithfulness   | 53.33%  |
| Abstention Accuracy    | 60%     |

The evaluation dataset contains answerable, multi-context, and unsupported questions.

The evaluation implementation and results are available in:

```text
evaluation/
├── dataset.json
├── evaluate.py
├── results.json
└── report.md
```

The answer-quality scores are lightweight evaluator estimates and should not be treated as absolute ground truth.

---

## Project Structure

```text
hyderabad-tour-chatbot/
├── app.py
├── Dockerfile
├── requirements.txt
├── README.md
├── app/
│   ├── static/
│   │   ├── css/
│   │   └── images/
│   └── templates/
│       └── index.html
├── src/
│   ├── rag/
│   ├── retrieval/
│   ├── llm/
│   ├── search/
│   └── utils/
├── data/
│   └── vectorstore/
│       ├── faiss_index
│       └── metadata.pkl
├── evaluation/
│   ├── dataset.json
│   ├── evaluate.py
│   ├── results.json
│   └── report.md
└── tests/
```

---

## Example Queries

```text
Tell me about Golconda Fort
Charminar timings today
Best food places near Charminar
Plan a day around Hyderabad
Famous dishes other than Biryani
Best places to visit in Hyderabad with family
```

---

## Local Setup

### Clone Repository

```bash
git clone https://github.com/varunreddy-18/hyderabad-tourism-ai-chatbot.git
cd hyderabad-tourism-ai-chatbot
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

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

## Docker Setup

### Build Image

```bash
docker build -t hyderabad-tourism-ai .
```

### Run Container

```bash
docker run -p 5000:5000 -e GROQ_API_KEY=your_api_key_here hyderabad-tourism-ai
```

---

## Future Improvements

- Conversation memory
- Google Maps integration
- Weather integration
- Source citations in the UI
- Multilingual support
- Personalized itinerary generation
- Improved RAG evaluation
- Production deployment

---

## Key Concepts Demonstrated

- Retrieval-Augmented Generation (RAG)
- Vector Search
- Semantic Search
- Hybrid Retrieval
- Query Routing
- LangChain
- LLM Integration
- Prompt Engineering
- RAG Evaluation
- Flask Application Development
- Docker Containerization
- AI System Design
