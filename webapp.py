from langchain.chat_models.azure_openai import AzureChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.callbacks import StreamlitCallbackHandler
from langchain_experimental.tools import PythonAstREPLTool
from utils.parser import ReActSingleInputOutputParser
from utils.ingestion import data_ingestion
from utils.classes import run_request

from const import GPT_MODEL, EMBED_MODEL, PROMPT_TEMPLATE

from tools.custom_sql_toolkit import CustomSQLToolkit
from tools.follow_up_question_tool import FollowUpQuestionTool


from dotenv import load_dotenv
import os
import streamlit as st
import pandas as pd

load_dotenv() 

GPT_MODEL="dev-platformrecommender-westus3-gpt4"
EMBED_MODEL="dev-platformrecommender-westus3-embedding"

llm = AzureChatOpenAI(deployment_name=GPT_MODEL, model_name=GPT_MODEL, temperature = 0)

# Streamlit setup
st.set_page_config(page_title="GenBI", page_icon="📊")

if "datasets" not in st.session_state:
    datasets = {}
    st.session_state["datasets"] = {}
else:
    # use the list already loaded
    datasets = st.session_state["datasets"]

if "k" not in st.session_state:
    st.session_state.k = 5

with st.sidebar:
    st.write("### Clear message history")
    clear_history = st.sidebar.button("Clear message history")
    
    st.sidebar.write("### Agent Settings")
    st.session_state.k = st.sidebar.slider("**Memory size**", 1, 10, st.session_state.k)

st.write("# 📊 Generative BI")
# data = os.path.join("data", "data.csv")
st.write("**Upload your CSV file below.**")
data = st.file_uploader("Upload a CSV" , type="csv", label_visibility="collapsed")


if data:

    file_name = data.name
    df, db, engine, schema = data_ingestion(filename=data)

    # Prompt template
    prompt_template = PromptTemplate.from_template(PROMPT_TEMPLATE, partial_variables={"table_schema": schema})

    if 'memory' not in st.session_state:
    # conversational agent memory
        st.session_state.memory = ConversationBufferWindowMemory(
            memory_key='chat_history',
            k=st.session_state.k,
            return_messages=True
        )
    # sql_toolkit = CustomSQLToolkit(db=db, llm=llm)
    # tools = sql_toolkit.get_tools()
    tools = []
    python_tool = PythonAstREPLTool(locals = {"df": df})
    follow_up_question_tool = FollowUpQuestionTool(llm=llm)
    tools.extend([
        follow_up_question_tool,
        python_tool
        ])

    react_agent = create_react_agent(llm, tools=tools, prompt=prompt_template, output_parser=ReActSingleInputOutputParser())

    if "messages" not in st.session_state or clear_history:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    user_query = st.chat_input(placeholder="Ask me anything!")

    if user_query:

        st.session_state.messages.append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)

        with st.chat_message("assistant"):

            st_cb = StreamlitCallbackHandler(st.container())
            agent_executor = AgentExecutor(agent=react_agent, 
                                           tools=tools, 
                                           verbose=True, # set to False to not see thinking process
                                           memory=st.session_state.memory,
                                           handle_parsing_errors=True,
                                           max_iteration=1,
                                           callbacks=[st_cb])
            response_type, formatted = run_request(agent_executor, user_query)
            print(f"FORMATTED: {formatted}")
            try:
                if response_type == "plot":
                    exec(formatted)
                elif response_type == "table":
                    exec(formatted)
                elif response_type == "general":
                    st.write(formatted)
                else:
                    raise ValueError(f"Unexpected response_type: {response_type}")
            except Exception as e:
                st.error(f"An error occurred. Try again. Error: {e}")

            

        