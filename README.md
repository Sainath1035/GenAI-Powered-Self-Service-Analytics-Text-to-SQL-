# 🗣️ Text-to-SQL Generative AI Chatbot & Database Agent

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-v0.2-green.svg)](https://www.langchain.com/)
[![Google Gemini](https://img.shields.io/badge/LLM-Google%20Gemini%202.0%20Flash-orange.svg)](https://aistudio.google.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-yellow.svg)](https://www.mysql.com/)
[![Evaluation](https://img.shields.io/badge/Eval-RAGAS-purple.svg)](https://docs.ragas.io/)

An end-to-end Generative AI Text-to-SQL application that enables non-technical stakeholders to query complex relational databases using conversational natural language. The system bridges enterprise tabular datasets and relational databases with cutting-edge Large Language Models (LLMs) via **LangChain**, **LangGraph**, and **Google Gemini**.

---

## 📑 Table of Contents
- [📖 Project Overview](#-project-overview)
- [✨ Key Features](#-key-features)
- [🗼 System Architecture](#-system-architecture)
- [📂 Project Structure](#-project-structure)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Quickstart Guide](#-quickstart-guide)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Clone & Setup Virtual Environment](#2-clone--setup-virtual-environment)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
  - [4. Initialize the Database](#4-initialize-the-database)
  - [5. Run the Streamlit Application](#5-run-the-streamlit-application)
- [📓 Interactive Notebooks](#-interactive-notebooks)
- [📊 Evaluation with RAGAS](#-evaluation-with-ragas)
- [💡 Sample Queries for Testing](#-sample-queries-for-testing)
- [📄 License](#-license)

---

## 📖 Project Overview
In enterprise workflows, accessing relational database records requires writing SQL queries, presenting a barrier for business, product, and operations teams. 

This project solves this challenge by developing a dual-mode conversational database engine:
1. **LCEL Direct Query Chain**: Translates natural language into dialect-aware SQL in one pass, executes the query against the database, and synthesizes raw query results back into human-friendly explanations.
2. **ReAct Agentic Workflow (LangGraph)**: An autonomous agent equipped with `SQLDatabaseToolkit` tools (`ListSQLDatabaseTool`, `InfoSQLDatabaseTool`, `QuerySQLCheckerTool`, `QuerySQLDatabaseTool`) that inspects schemas, validates queries prior to execution, and handles errors with self-correction loops.
3. **Automated Evaluation Pipeline (RAGAS)**: Benchmarks generated SQL and answer quality against reference truths across metrics such as Context Precision, Helpfulness Rubrics, and Maliciousness Aspect Critics.

---

## ✨ Key Features
- **Natural Language to SQL**: Converts plain-English queries into accurate SQL statements tailored to schema definitions.
- **Dual Engine Architecture**: Supports both lightweight direct LCEL chains and autonomous ReAct reasoning agents.
- **Out-of-the-Box Local Testing**: Includes `setup_database.py` which loads all CSV tables into an embedded SQLite database (`regional_sales_data.db`) or MySQL.
- **Interactive Streamlit Web UI**: Chat interface with expandable SQL inspectors, tabular data previews, and database schema explorers.
- **Safety & Error Handling**: Query sanitation and syntax checking to prevent execution errors.
- **RAGAS Quantitative Evaluation**: Systematic benchmarking of LLM responses against ground truth reference queries.

---

## 🗼 System Architecture

```text
       +-----------------------------------------------------------+
       |                   User Natural Language                   |
       +-----------------------------+-----------------------------+
                                     |
                                     v
                       +-----------------------------+
                       |      Streamlit Web UI       |
                       +--------------+--------------+
                                      |
              +-----------------------+-----------------------+
              |                                               |
              v                                               v
     [Approach 1: LCEL Chain]                    [Approach 2: ReAct Agent]
  +-------------------------+                   +-------------------------+
  |  Dynamic Schema Fetch   |                   |   SQLDatabaseToolkit    |
  |  Gemini Prompt Template |                   |   - ListSQLDatabaseTool |
  |  Single-Pass SQL Gen    |                   |   - InfoSQLDatabaseTool |
  |  SQL Execution Engine   |                   |   - QuerySQLCheckerTool |
  |  NL Synthesizer Chain   |                   |   - QuerySQLDatabaseTool|
  +------------+------------+                   +------------+------------+
               |                                             |
               +----------------------+----------------------+
                                      |
                                      v
                       +-----------------------------+
                       |   Database (MySQL / SQLite) |
                       |   regional_sales_data       |
                       +-----------------------------+
```

---

## 📂 Project Structure

```text
Text-to-SQL-Chatbot/
├── app.py                                   # Interactive Streamlit Web Application
├── setup_database.py                        # Automated database loader (SQLite / MySQL)
├── requirements.txt                         # Python dependencies
├── .env.example                             # Environment variables template
├── .gitignore                               # Git ignore rules
├── README.md                                # Project documentation
├── INTERVIEW_PREP_GUIDE.md                  # Comprehensive interview cheat sheet & Q&A
├── Agentic Approach.ipynb                   # ReAct Agent implementation using LangGraph
├── Gemini Chatbot.ipynb                     # LCEL Text-to-SQL Chain using Google Gemini
├── Gemini Chatbot (including RAGAS).ipynb   # Pipeline evaluation using RAGAS framework
├── gemini.ipynb                             # Gemini API prototyping notebook
├── Data_CSV/                                # Regional sales dataset (CSV format)
│   ├── 2017_Budgets.csv
│   ├── Customers.csv
│   ├── Products.csv
│   ├── Regions.csv
│   ├── sales_order.csv
│   ├── Sales_Orders_old.csv
│   └── State_Regions.csv
└── data_dump/                               # Data dumps for MySQL imports
```

---

## 🛠️ Tech Stack
| Component | Technologies Used |
| :--- | :--- |
| **LLM Provider** | Google Gemini (`gemini-2.0-flash`, `gemini-1.5-pro`) |
| **Orchestration** | LangChain Core, LangChain Community, LangGraph |
| **User Interface** | Streamlit |
| **Databases** | MySQL 8.0, SQLite 3, SQLAlchemy |
| **Data Processing**| Pandas, PyMySQL, Cryptography |
| **Evaluation** | RAGAS (Retrieval Augmented Generation Assessment System) |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12 installed.
- A free Google Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### 2. Clone & Setup Virtual Environment
```bash
git clone https://github.com/YOUR_USERNAME/Text-to-SQL-Chatbot.git
cd Text-to-SQL-Chatbot

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the example environment file and add your Google Gemini API key:
```bash
cp .env.example .env
```
Edit `.env`:
```ini
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Initialize the Database
Run the automated database setup script:

- **Local SQLite Mode (Recommended for quick testing without MySQL)**:
  ```bash
  python setup_database.py --db sqlite
  ```
  *This automatically reads all CSV files from `Data_CSV/` and creates `regional_sales_data.db`.*

- **MySQL Mode (For live MySQL server)**:
  ```bash
  python setup_database.py --db mysql --host localhost --user root --password your_password --dbname regional_sales_data
  ```

### 5. Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📓 Interactive Notebooks

1. **`Gemini Chatbot.ipynb`**:
   - Demonstrates the direct LCEL pipeline.
   - Extracts schema via `db.get_table_info()`.
   - Structures query generation prompts and binds stop tokens.
   - Runs queries and formats results.

2. **`Agentic Approach.ipynb`**:
   - Implements the agentic approach with `create_react_agent` and `SQLDatabaseToolkit`.
   - Iterative reasoning: Table discovery -> Schema inspection -> Query validation -> Execution.

3. **`Gemini Chatbot (including RAGAS).ipynb`**:
   - End-to-end evaluation using `SingleTurnSample` and `EvaluationDataset`.
   - Assesses context precision, helpfulness rubrics, and maliciousness detection using Evaluator LLMs.

---

## 💡 Sample Queries for Testing
- *"What was the budget of Product 12?"*
- *"What are the names of all products in the products table?"*
- *"List all customer names from the customers table."*
- *"Find the name and state of all regions in the regions table."*
- *"What is the name of the customer with Customer Index = 1?"*
- *"What are the top 5 highest order quantities in sales_order?"*

---

## 📄 License
This project is licensed under the MIT License.
