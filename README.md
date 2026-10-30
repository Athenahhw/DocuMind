# DocuMind
An AI-powered document management and knowledge retrieval system  使用者可以上傳 PDF、TXT、Markdown 等文件，系統自動擷取內容、建立索引、分類文件，並透過 AI 回答與文件相關的問題，附上可追溯的引用來源。

documind/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── documents.py
│   │   │   ├── search.py
│   │   │   └── chat.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── document_parser.py
│   │   │   ├── chunking.py
│   │   │   ├── embedding.py
│   │   │   └── rag.py
│   │   ├── workers/
│   │   └── database.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   └── app.py
├── migrations/
├── evaluation/
│   ├── questions.json
│   └── evaluate.py
├── docs/
│   ├── architecture.png
│   ├── erd.png
│   └── screenshots/
├── .github/
│   └── workflows/
│       └── test.yml
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── LICENSE
