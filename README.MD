# Hyderabad Tourism AI Chatbot 🏛️

An AI-powered tourism assistant for Hyderabad that combines **Retrieval-Augmented Generation (RAG)** with **Live Web Search** to deliver accurate historical information, travel guidance, food recommendations, and real-time updates.

## Features

* 🔍 Semantic search using FAISS and Sentence Transformers
* 🌐 Live web search for current information
* 🔄 Hybrid retrieval (Knowledge Base + Web Search)
* 🤖 AI-generated responses using Llama 3.3 70B via Groq
* 🏰 Hyderabad tourism, culture, food, and travel guidance
* 💬 Interactive Flask-based chat interface

## Tech Stack

**Frontend**

* HTML
* CSS
* JavaScript

**Backend**

* Flask
* Python

**AI/ML**

* FAISS Vector Database
* Sentence Transformers
* Retrieval-Augmented Generation (RAG)
* Groq (Llama 3.3 70B)

**Search**

* DuckDuckGo Search (DDGS)

## Architecture

```text
User Query
     ↓
 Query Router
     ↓
 ┌──────────────┬──────────────┬──────────────┐
 │     RAG      │     WEB      │    HYBRID    │
 └──────────────┴──────────────┴──────────────┘
     ↓
 Context Builder
     ↓
  Groq LLM
     ↓
 Response
```

## Example Queries

* Tell me about Golconda Fort
* Charminar timings today
* Best food places near Charminar
* Plan a day around Hyderabad
* Famous dishes other than biryani

## Local Setup

```bash
git clone https://github.com/your-username/hyderabad-tour-chatbot.git
cd hyderabad-tour-chatbot

pip install -r requirements.txt

python app.py
```

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key
```

Open:

```text
http://localhost:5000
```

## Future Improvements

* Conversation memory
* Google Maps integration
* Weather integration
* Multilingual support
* Personalized itinerary generation

## Author

**Varun Reddy**
MSDS, IIIT Hyderabad
