import os
import json
from typing import Optional
import yaml
import asyncio
import csv
from langchain_openai import ChatOpenAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from src.utils.utils import reasoning_prompt, load_chat_model, read_file_prompt

import pandas as pd
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from cvss import CVSS2, CVSS3, CVSS4

model = load_chat_model()

# Function to generate CVSS strings asynchronously
async def generate_cvss(row):
    try:
        content = reasoning_prompt("./src/prompts/issue_scoring_prompt.txt", ISSUE_DESCRIPTION=json.dumps(row.to_dict()))
        local_messages = SystemMessage(content=read_file_prompt("./src/prompts/cybersecurity_system_prompt.txt")), HumanMessage(content=content)
        response = await model.ainvoke(local_messages)
        return response.content
    except Exception as e:
        print(f"Error generating CVSS string for row: {row.to_dict()}. Error: {e}")
        return None

# Function to calculate CVSS scores with error handling
def safe_cvss_score(cvss_string):
    try:
        return CVSS3(cvss_string).scores()[0] if cvss_string else None
    except Exception as e:
        print(f"Error processing CVSS string: {cvss_string}. Error: {e}")
        return None
