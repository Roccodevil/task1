# 🧠 Local Agentic AI: Multimodal Document Explainer & XAI Engine

A completely offline, privacy-first, multi-agent system that ingests complex documents (PDF, CSV, Excel, images), understands charts using a custom Vision-Language workflow, and returns explainable output in text and speech mode.

This project is intentionally built as:
- A real engineering system for local-first AI workflows
- A learning resource for students and junior developers entering AI/ML

It reflects hackathon-speed building with production-minded constraints: no paid APIs, no cloud dependency for core flow, modular architecture, and CPU-aware execution.

---

## 🎯 Problem It Solves

Sensitive documents often cannot be sent to cloud AI tools. This project enables multimodal reasoning, retrieval, and explanation while keeping data local.

✅ Core objective:
- Run powerful Agentic AI pipelines on local hardware with a privacy-first approach

---

## ✨ Key Highlights

- 🛡️ Local-first architecture (parser, memory, orchestration)
- 🤖 Agentic RAG where tools are used intentionally
- 🖼️ Visual understanding path for charts/images via custom VLM setup
- 🧩 Explainable answers driven by user-specific doubts/questions
- 💻 CPU-compatible deployment pathway
- 🔊 Text and speech-ready output modes in the web UI

---

## 🏗️ Architecture Overview (Agentic RAG)

Standard RAG retrieves context and responds. Here, autonomous agents reason through tasks and actively use memory/search tools.

### Pipeline Flow

1. Ingestion & Dynamic Routing
- User uploads a file via Flask UI.
- Document parser routes logic based on file type and content.

2. OCR + Visual Extraction
- Text is extracted from document content.
- Embedded charts/images are detected, cropped, and sent through the VLM path for additional insights.

3. Embeddings & Local Memory
- Text and visual insights are chunked with RecursiveCharacterTextSplitter.
- Chunks are embedded using all-MiniLM-L6-v2.
- Vectors are stored in local ChromaDB (SQLite-backed).

4. CrewAI Multi-Agent Reasoning
- Agent 1 (Data Extraction Specialist): builds a high-level document map.
- Agent 2 (Lead AI Explainer): answers user doubt by querying local memory and invoking web search only if required.

5. Final Output Delivery
- Explanation is formatted and returned to the frontend.
- Speech mode reads from rendered explanation content.

---

## 🔄 Architecture At A Glance

```text
User Upload -> Document Parser -> Text + Visual Insights
                         |                |
                         v                v
                Chunking + Embeddings -> ChromaDB (local)
                                      |
                                      v
                         CrewAI Orchestration
                    [Data Agent -> Explainer Agent]
                                      |
                                      v
                          Formatted Explanation
                           |                    |
                           v                    v
                       Report Mode         Speech Mode
```

---

## 🧰 Tech Stack

### Backend & Orchestration
- Flask for routing and web UI rendering
- CrewAI for agents, tasks, and tool orchestration

### Local Models
- Ollama + llama3 for reasoning and generation
- Custom-adapted Qwen2-VL-2B-Instruct workflow for visual/chart understanding

### Retrieval & Memory
- ChromaDB (local vector database, SQLite-backed)
- sentence-transformers/all-MiniLM-L6-v2 for embeddings
- RecursiveCharacterTextSplitter for chunking

### Parsing & Frontend
- Modular document parser tools for multimodal extraction
- HTML/CSS/JS frontend for upload, report mode, and speech mode

---

## 🔬 Transfer Learning & Local CPU Adaptation

This project follows a practical two-phase approach:

### Phase 1: Fine-Tuning (GPU Stage)
- Base model: Qwen/Qwen2-VL-2B-Instruct
- QLoRA for efficient adaptation
- 4-bit quantization during training to reduce VRAM load
- LoRA adapter export for lightweight deployment artifacts

### Phase 2: Local Runtime (CPU Stage)
- Removed GPU-specific assumptions in local loading path
- Stabilized dependencies for torch/torchvision compatibility
- Added resilience for restricted-network model download scenarios
- Hardened module path handling for reliable local execution

---

## 📁 Project Structure

```text
.
├── app.py
├── requirements.txt
├── agents/
│   ├── crew_orchestrator.py
│   ├── data_agent.py
│   └── explainer_agent.py
├── models/
│   ├── local_vlm.py
│   ├── ollama_client.py
│   └── custom_vlm_adapter/
├── tools/
│   ├── document_parser.py
│   ├── vector_db.py
│   └── web_search.py
├── templates/
│   └── index.html
├── static/
│   └── css/
│       └── style.css
└── uploads/
```

---

## 🚀 Setup & Installation

### 1) Mandatory Prerequisites

You need all of the following before running this app:

- Docker Desktop (or Docker Engine + Compose v2)
- Ollama installed on your local machine
- `llama3` model pulled in Ollama

Install/start Ollama and pull `llama3`:

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
ollama serve
```

```powershell
# Windows PowerShell
ollama pull llama3
ollama serve
```

Important:
- Keep Ollama running on the host machine while the Docker container is running.
- This app container connects to host Ollama using `OLLAMA_BASE_URL`.
- First startup can take around 10 minutes depending on CPU, disk, and model warm-up.

### 2) Project Setup

```bash
git clone https://github.com/Roccodevil/task1.git
cd task1
```

### 3) VLM Adapter Placement

Ensure adapter artifacts are available at:
- `models/custom_vlm_adapter`

---

## 🐳 Docker Quickstart (Recommended)

This is the primary way to run the project.

### Build Image

```bash
docker build -t task1-app:latest .
```

### Run App Container (Compose)

```bash
docker compose up -d
```

Open:
- http://127.0.0.1:5000

Stop:

```bash
docker compose down
```

View logs:

```bash
docker compose logs -f
```

### Run Using Existing VS Code Tasks

If you are using this repo in VS Code, task shortcuts are already configured:

- `Run App`
- `Stop App`
- `View Logs`
- `Rebuild and Run App`

### Container Runtime Notes

- App container name: `task1-app`
- Exposed app port: `5000`
- Persistent uploaded data: `./uploads` mounted to `/app/uploads`
- Default Ollama endpoint in compose: `http://host.docker.internal:11434`
- Optional env var: `TAVILY_API_KEY` for web-search fallback

---

## 🧪 Local Python Run (Alternative To Docker)

If you prefer not to run with Docker:

```bash
python -m venv venv
```

Activate environment:

```bash
# Linux/macOS
source venv/bin/activate

# Windows PowerShell
venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Run:

```bash
python app.py
```

Open:
- http://127.0.0.1:5000

---

## 🎮 How To Use

1. Upload PDF, CSV, Excel, or image.
2. Enter a focused doubt/question.
3. Choose Text Only or Text + Speech.
4. Click Analyze and Explain.

---

## ⏱️ First-Run Behavior (Expected)

On first run, startup may take up to ~10 minutes because of:

- Initial Python dependency and model initialization
- Local embedding/model warm-up
- Vector database directory initialization

Later runs are typically much faster.

---

## ✅ Advantages Of This Design

- Better grounding through targeted memory queries
- Better control via role-separated agents
- Better maintainability through modular tools/parsers/agents
- Better privacy with local-first defaults
- Better educational value with transparent architecture

---

## ⚙️ Practical Notes

- CPU multimodal inference is possible, but slower than GPU
- ChromaDB is efficient for local single-machine workflows
- Output quality depends on adapter quality and domain fit
- Runtime cleanup and temp isolation improve stability

---

## 🌱 Future Scope

- Swap extraction-side model with faster lightweight variants (for example, phi-3 family)
- Add native DOCX parsing support
- Add WebSocket streaming to show progressive reasoning in UI
- Add configurable memory lifecycle and cleanup policies
- Add benchmark suite for latency, grounding, and hallucination metrics

---

## 👥 Who This Is For

- Students and juniors learning practical AI architecture
- Hackathon teams shipping local-first AI prototypes
- Developers requiring privacy-sensitive multimodal explainability

---

## 📄 License & Attribution

Add your preferred license (for example, MIT) and update repository owner links, model attributions, and usage notes before public release.
