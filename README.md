# 🧠 Goal-Driven AI Coach

Un assistente personale **agentico** che aiuta l’utente a raggiungere obiettivi (studio, fitness, carriera)
tramite pianificazione automatica, task giornalieri, memoria semantica e adattamento continuo.

> Non è solo un chatbot.
> È un sistema multi-agente con orchestrazione, memoria e decisioni autonome.

---

## ✨ Features

### 🎯 Pianificazione
- Goal naturale → roadmap + task atomici
- Preview e conferma piano
- Task piccoli (30–90 minuti)

### 📅 Daily coaching
- Selezione task del giorno
- Messaggio motivazionale LLM
- Feedback strutturato (done / difficulty / energy / note)

### 🧠 Memoria semantica
- Vector DB (Qdrant)
- Ricerca semantica del contesto
- Compressione memorie vecchie

### 📊 Adattamento
- CriticAgent analizza progressi
- AdvisorAgent suggerisce replan
- Supervisor decide in modo deterministico

### 💬 UI
- Frontend chat-style
- Typing indicator stile ChatGPT
- Card giornaliera interattiva

---

# 🏗 Architettura

Frontend → FastAPI → Supervisor → Agents → Tools → Storage

Agents:
- Planner
- Coach
- Memory
- Critic
- Advisor

Storage:
- SQLite (goals / tasks)
- Qdrant (memoria semantica)

---

# 🧰 Stack

- Python 3.11+
- FastAPI
- SQLite
- Qdrant (local vector DB)
- sentence-transformers
- OpenAI API
- Vanilla JS frontend

---

# 🚀 Installazione

## 1. Clona repo
git clone https://github.com/your-user/goal-agent
cd goal-agent

## 2. Virtualenv
python -m venv .venv
.venv\\Scripts\\activate  # Windows

## 3. Dipendenze
pip install -r requirements.txt

## 4. Variabili ambiente (.env)
OPENAI_API_KEY=xxx
QDRANT_PATH=./qdrant_data
LLM_MODEL=gpt-4.1-mini

---

# ▶️ Avvio applicazione

## Web app
uvicorn app.server:app --reload

Apri:
http://localhost:8000

## CLI (dev)
python app/main.py

---

# 🧪 Test
python test_planner.py
python test_coach.py
python test_memory_tools.py
python test_supervisor.py

---

# 📂 Struttura progetto

app/
agents/
tools/
storage/
supervisor/
tests/

---

# 🧠 Concetti chiave

## Event-driven
NEW_GOAL → DAILY → WEEKLY

## Stateless tools
I tool non contengono logica LLM, solo I/O.

## Deterministic Supervisor
LLM suggerisce, Supervisor decide.

## Memoria semantica
Eventi e riflessioni salvati come embeddings per personalizzazione e adattamento.

---

# 🛠 Roadmap

v1
- planner
- coach
- memory
- UI chat

v2
- critic + advisor
- replan automatico
- scheduler background

v3
- calendario
- streak gamification
- mobile UI

---

# 📜 Licenza

MIT
