import os
import re
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load environment variables if available
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Text-to-SQL RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .reportview-container {
        margin-top: -2em;
    }
    .badge {
        display: inline-block;
        padding: 0.25em 0.5em;
        font-size: 75%;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.25rem;
        background-color: #0366d6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("🗣️ Text-to-SQL Generative AI Chatbot")
st.caption("Talk to your relational database using Natural Language, powered by Google Gemini & LangChain.")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key = st.text_input(
        "Google Gemini API Key",
        value=os.getenv("GOOGLE_API_KEY", ""),
        type="password",
        help="Enter your Google AI Studio Gemini API Key"
    )
    
    model_name = st.selectbox(
        "Gemini Model",
        options=["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        index=0
    )
    
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1)

    st.markdown("---")
    st.header("🗄️ Database Connection")
    db_mode = st.radio("Database Engine", options=["SQLite (Local Tutorial DB)", "MySQL Server"], index=0)

    if db_mode == "SQLite (Local Tutorial DB)":
        db_path = os.path.join(os.path.dirname(__file__), "regional_sales_data.db")
        if not os.path.exists(db_path):
            st.warning("regional_sales_data.db not found. Creating it from CSV files...")
            try:
                from setup_database import setup_sqlite
                setup_sqlite()
                st.success("Database created successfully!")
            except Exception as e:
                st.error(f"Error creating database: {e}")
        db_uri = f"sqlite:///{db_path}"
    else:
        mysql_host = st.text_input("Host", value=os.getenv("MYSQL_HOST", "localhost"))
        mysql_port = st.text_input("Port", value=os.getenv("MYSQL_PORT", "3306"))
        mysql_user = st.text_input("Username", value=os.getenv("MYSQL_USER", "root"))
        mysql_pass = st.text_input("Password", value=os.getenv("MYSQL_PASSWORD", ""), type="password")
        mysql_db = st.text_input("Database Name", value=os.getenv("MYSQL_DATABASE", "regional_sales_data"))
        db_uri = f"mysql+pymysql://{mysql_user}:{mysql_pass}@{mysql_host}:{mysql_port}/{mysql_db}"

    approach = st.selectbox(
        "Execution Mode",
        options=["LCEL Chain (Prompt to SQL)", "Agentic Approach (ReAct Agent)"],
        index=0,
        help="LCEL Chain translates to SQL directly. Agentic approach uses LangChain SQL toolkit to validate schemas and execute iteratively."
    )

    st.markdown("---")
    st.header("💡 Sample Questions")
    sample_questions = [
        "What was the budget of Product 12?",
        "What are the names of all products in the products table?",
        "List all customer names from the customers table.",
        "Find the name and state of all regions in the regions table.",
        "What is the name of the customer with Customer Index = 1?",
        "What are the top 5 highest order quantities in sales_order?"
    ]
    selected_sample = st.selectbox("Click to populate question:", [""] + sample_questions)

# Initialize Database connection
@st.cache_resource
def get_database_connection(uri: str):
    return SQLDatabase.from_uri(uri, sample_rows_in_table_info=2)

try:
    db = get_database_connection(db_uri)
    tables = db.get_usable_table_names()
    with st.sidebar:
        st.success(f"Connected! Tables: {', '.join(tables)}")
        with st.expander("🔍 View Table Schemas"):
            st.text(db.get_table_info())
except Exception as e:
    st.error(f"Failed to connect to database: {e}")
    db = None

# Helper to clean up SQL markdown block
def extract_sql_query(raw_text: str) -> str:
    match = re.search(r"```(?:sql)?\s*(.*?)\s*```", raw_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    clean = raw_text.strip()
    # Strip any leading 'sql' keyword
    if clean.lower().startswith("sql"):
        clean = clean[3:].strip()
    return clean

# Prompt Template matching the tutorial
TEMPLATE_SQL = """Based on the table schema below, write a SQL query that would answer the user's question:
Remember:
1. Only provide the SQL query, don't include anything else.
2. Provide the SQL query in a single line or standard SQL format.
3. Do not wrap with extra commentary or pleasantries.

Table Schema:
{schema}

Question: {question}
SQL Query:
"""

prompt_sql = ChatPromptTemplate.from_template(TEMPLATE_SQL)

TEMPLATE_RESPONSE = """Based on the table schema, user question, SQL query generated, and SQL result fetched from database, answer the user question in clean, concise natural language.

Table Schema:
{schema}

User Question: {question}
SQL Query: {query}
SQL Result: {result}

Answer:
"""
prompt_response = ChatPromptTemplate.from_template(TEMPLATE_RESPONSE)

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sql" in msg:
            with st.expander("🛠️ Generated SQL Query"):
                st.code(msg["sql"], language="sql")
        if "data" in msg and msg["data"] is not None:
            with st.expander("📊 Database Records"):
                st.dataframe(msg["data"])

# Chat input
user_query = st.chat_input("Ask a question about the regional sales data...")
if selected_sample and not user_query:
    user_query = selected_sample

if user_query:
    if not api_key:
        st.warning("⚠️ Please provide a Google Gemini API Key in the sidebar to proceed.")
        st.stop()

    if db is None:
        st.error("Database connection is not available.")
        st.stop()

    os.environ["GOOGLE_API_KEY"] = api_key

    # Display user question
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Processing question..."):
            try:
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=temperature
                )

                if approach == "LCEL Chain (Prompt to SQL)":
                    schema = db.get_table_info()
                    sql_chain = (
                        prompt_sql
                        | llm.bind(stop=["\nSQLResult:"])
                        | StrOutputParser()
                    )
                    raw_sql = sql_chain.invoke({"schema": schema, "question": user_query})
                    clean_sql = extract_sql_query(raw_sql)

                    st.markdown("**Generated SQL Query:**")
                    st.code(clean_sql, language="sql")

                    # Execute query
                    try:
                        db_result = db.run(clean_sql)
                    except Exception as sql_err:
                        db_result = f"Error executing SQL: {sql_err}"

                    # Natural language explanation chain
                    synthesizer_chain = prompt_response | llm | StrOutputParser()
                    final_answer = synthesizer_chain.invoke({
                        "schema": schema,
                        "question": user_query,
                        "query": clean_sql,
                        "result": str(db_result)
                    })

                    st.markdown(final_answer)

                    # Try to format result into DataFrame if tabular
                    df_preview = None
                    try:
                        import ast
                        parsed_eval = ast.literal_eval(db_result) if isinstance(db_result, str) else db_result
                        if isinstance(parsed_eval, list) and len(parsed_eval) > 0:
                            df_preview = pd.DataFrame(parsed_eval)
                            with st.expander("📊 Database Records"):
                                st.dataframe(df_preview)
                    except Exception:
                        pass

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_answer,
                        "sql": clean_sql,
                        "data": df_preview
                    })

                else:
                    # Agentic Approach using LangChain SQL Toolkit
                    from langchain_community.agent_toolkits.sql.base import create_sql_agent
                    from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

                    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
                    agent_executor = create_sql_agent(
                        llm=llm,
                        toolkit=toolkit,
                        verbose=True,
                        handle_parsing_errors=True
                    )
                    agent_response = agent_executor.run(user_query)
                    st.markdown(agent_response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": agent_response
                    })

            except Exception as e:
                st.error(f"An error occurred: {e}")
