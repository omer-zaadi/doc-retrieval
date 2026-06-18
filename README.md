# Document Indexing & Retrieval

A Python module that indexes PDF and DOCX files into PostgreSQL using Gemini embeddings and supports semantic search via pgvector.

## Features

- Extracts text from **PDF** and **DOCX** files
- Three **chunking strategies**: fixed-size with overlap, sentence-based (NLTK), paragraph-based
- Generates embeddings using **Gemini gemini-embedding-001** with MRL at 768 dimensions
- Stores chunks + embeddings in **PostgreSQL** with **pgvector**
- Semantic search using **Cosine Distance**
- Full error handling for all failure modes

---

## Requirements

- Docker & Docker Compose
- Python 3.10+
- A valid [Gemini API Key](https://aistudio.google.com/app/apikey)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/doc-retrieval.git
cd doc-retrieval
```

### 2. Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```env
GEMINI_API_KEY=your_gemini_api_key_here
POSTGRES_URL=postgresql://docuser:docpassword@localhost:5432/docretrieval
POSTGRES_USER=docuser
POSTGRES_PASSWORD=docpassword
POSTGRES_DB=docretrieval
```

### 3. Start PostgreSQL with pgvector

```bash
docker compose up -d
```

### 4. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

---

## Usage

### Index a document

```bash
python index_documents.py --file ./docs/example.pdf --strategy paragraph
python index_documents.py --file ./docs/example.pdf --strategy sentence
python index_documents.py --file ./docs/example.pdf --strategy fixed
```

### Search indexed documents

```bash
python search.py --query "your search query"
python search.py --query "your search query" --top-k 3
```

---

## Chunking Strategies

| Strategy    | Description                                               |
|-------------|-----------------------------------------------------------|
| `fixed`     | Fixed-size character chunks (500 chars) with overlap (50) |
| `sentence`  | Groups of 5 sentences per chunk with 1-sentence overlap   |
| `paragraph` | Splits on blank-line boundaries, min 50 chars per chunk   |

---

## Environment Variables

| Variable            | Description                                  |
|---------------------|----------------------------------------------|
| `GEMINI_API_KEY`    | Google Gemini API key                        |
| `POSTGRES_URL`      | Full PostgreSQL connection URL               |
| `POSTGRES_USER`     | PostgreSQL username (used by Docker Compose) |
| `POSTGRES_PASSWORD` | PostgreSQL password                          |
| `POSTGRES_DB`       | PostgreSQL database name                     |

---

## Database Schema

```sql
CREATE TABLE document_chunks (
    id              SERIAL PRIMARY KEY,
    chunk_text      TEXT            NOT NULL,
    embedding       vector(768),
    filename        TEXT            NOT NULL,
    split_strategy  VARCHAR(50)     NOT NULL,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);
```

---

## Error Handling

| Error                       | Handling                                                |
|-----------------------------|---------------------------------------------------------|
| Missing file                | `FileNotFoundError` with clear message                  |
| Unsupported file type       | `ValueError` — only `.pdf` and `.docx` are supported   |
| Document with no text       | `ValueError` after extraction attempt                   |
| Embedding failure           | `RuntimeError` with chunk index and API error details   |
| Database connection failure | `OperationalError` with troubleshooting hint            |
| Empty search results        | Informative message, exits cleanly                      |

---

## Example Runs

### Indexing Run

```
python index_documents.py --file "./docs/Jeen_AI_Solution_Assignment.pdf" --strategy paragraph

Indexing 'Jeen_AI_Solution_Assignment.pdf' with strategy='paragraph'
  [1/4] Extracting text...
        7,404 characters extracted.
  [2/4] Chunking...
        4 chunks produced.
  [3/4] Generating embeddings...
        dim=768.
  [4/4] Storing in PostgreSQL...

Done. 4 chunks indexed.
```

### Search Run

```
python search.py --query "PostgreSQL and pgvector table columns requirement"

Query: "PostgreSQL and pgvector table columns requirement"  —  5 result(s)

[1] score=0.7030  file=Jeen_AI_Solution_Assignment.pdf  strategy=sentence  id=27
    • Extract clean text and handle unsupported files or documents with no extractable text. • Implement three chunking strategies: fixed-size with overlap, sentence-based splitting, and paragraph-based splitting. • Generate embeddings using gemini-embedding-001 and store them in Po...

[2] score=0.7001  file=Jeen_AI_Solution_Assignment.pdf  strategy=fixed  id=10
    cuments with no extractable text. • Implement three chunking strategies: fixed-size with overlap, sentence-based splitting, and paragraph-based splitting. • Generate embeddings using gemini-embedding-001 and store them in PostgreSQL using pgvector. • The table should include at ...

[3] score=0.6726  file=Jeen_AI_Solution_Assignment.pdf  strategy=paragraph  id=2
    Part 2 – Document Indexing & Retrieval Build a Python module that receives a PDF or DOCX file, extracts clean text, splits it into chunks, creates embeddings using the Gemini API, stores the data in PostgreSQL with pgvector, and supports semantic search over the stored content. M...

[4] score=0.6726  file=Jeen_AI_Solution_Assignment.pdf  strategy=paragraph  id=39
    Part 2 – Document Indexing & Retrieval Build a Python module that receives a PDF or DOCX file, extracts clean text, splits it into chunks, creates embeddings using the Gemini API, stores the data in PostgreSQL with pgvector, and supports semantic search over the stored content. M...

[5] score=0.6657  file=Jeen_AI_Solution_Assignment.pdf  strategy=fixed  id=9
    g & Retrieval Build a Python module that receives a PDF or DOCX file, extracts clean text, splits it into chunks, creates embeddings using the Gemini API, stores the data in PostgreSQL with pgvector, and supports semantic search over the stored content. Mandatory requirements • C...
```

---

## Project Structure

```
doc-retrieval/
├── index_documents.py   # Main indexing CLI
├── search.py            # Semantic search CLI
├── extractor.py         # PDF / DOCX text extraction
├── chunkers.py          # Three chunking strategies
├── embeddings.py        # Gemini embedding calls
├── db.py                # PostgreSQL connection, schema, queries
├── docker-compose.yml   # PostgreSQL + pgvector container
├── requirements.txt
├── .env.example
└── README.md
```

---

## Screenshots

### Indexing Run
![Indexing run](./screenshots/indexing_run.png)

### Search Run
![Search run](./screenshots/search_run.png)

### Database Contents (TablePlus)

All three chunking strategies are visible in the database after indexing — `paragraph`, `fixed`, and `sentence` — each producing a different granularity of chunks from the same source document.

![document_chunks table](./screenshots/tableplus_preview.png)

---

## Stopping the Database

```bash
docker compose down        # stop containers
docker compose down -v     # stop and remove volume (deletes all data)
```
