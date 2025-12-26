import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

import warnings
warnings.filterwarnings('ignore')
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR)
logging.getLogger('peft').setLevel(logging.ERROR)

import streamlit as st
import psycopg2
import pandas as pd
import datetime
from pymongo import MongoClient
import torch
from peft import PeftModel
from transformers import AutoTokenizer, AutoModelForCausalLM

# --- 1. CONFIGURATION ---
DB_CONFIG = {
    "dbname": "hospital_db",
    "user": "postgres",
    "password": "Maiya@21", # <--- UPDATE THIS
    "host": "localhost",
    "port": "5432"
}

MONGO_URI = "mongodb://localhost:27017/"
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    audit_db = mongo_client["hospital_audit_db"]
    audit_collection = audit_db["access_logs"]
    mongo_status = "✅ Connected"
except Exception:
    mongo_status = "❌ Not Connected"

# --- 2. FAIL-SAFE MODEL LOADING ---
# We force the app to ignore GPU libraries entirely to stop the loop.

model = None
tokenizer = None

@st.cache_resource
def load_model():
    print("Loading AI Model (Safe Mode - CPU)...")
    base_model_name = "unsloth/llama-3-8b-bnb-4bit" 
    adapter_path = "./lora_model" 
    
    # 1. Load Tokenizer
    tokenizer_obj = AutoTokenizer.from_pretrained(base_model_name)
    
    # 2. Load Base Model (STRICT CPU SETTINGS)
    # We purposefully do NOT use load_in_4bit or bitsandbytes here.
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        device_map="cpu",          # Force CPU
        dtype=torch.float32, # Standard Math (No specialized libraries needed)
        low_cpu_mem_usage=True
    )
    
    # 3. Apply Adapters
    model_obj = PeftModel.from_pretrained(base_model, adapter_path)
    return model_obj, tokenizer_obj

# Try loading
try:
    with st.spinner("Loading Model... (This will take 2-3 mins, please be patient)"):
        model, tokenizer = load_model()
    st.success("✅ System Online (CPU Safe Mode)")
except Exception as e:
    st.error("Critical Error")
    st.error(f"Details: {e}")

# --- 3. HELPER FUNCTIONS ---

def run_sql_query(query):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)

def log_audit(user_role, question, sql_query, status):
    if mongo_status.startswith("❌"): return
    try:
        audit_collection.insert_one({
            "timestamp": datetime.datetime.now(),
            "user_role": user_role,
            "question": question,
            "sql": sql_query,
            "status": status
        })
    except: pass

def generate_sql(question):
    if model is None: return "Error: Model not loaded"

    prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
Convert this natural language query into SQL for the hospital database.

### Input:
{question}

### Response:
"""
    # Force inputs to CPU (Safe Mode)
    inputs = tokenizer(prompt, return_tensors="pt")

    # Move tensors to CPU explicitly (avoid calling .to on the dict)
    inputs = {k: v.to("cpu") for k, v in inputs.items()}

    # Generate safely without gradients
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=150, do_sample=False)

    # Decode the first generated sequence
    if isinstance(outputs, torch.Tensor):
        # outputs shape: (batch, seq_len)
        out_ids = outputs[0] if outputs.dim() == 2 else outputs
    else:
        out_ids = outputs[0]

    response = tokenizer.decode(out_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)

    # Extract SQL after the Response marker
    sql = response.split("### Response:")[-1].strip().replace("<|end_of_text|>", "")
    return sql

# --- 4. UI ---
st.title("🏥 AI Hospital DB (Safe Mode)")
st.caption(f"Audit Status: {mongo_status}")

user_role = st.sidebar.selectbox("User Role", ["Doctor", "Billing Admin", "Nurse"])
st.sidebar.info(f"Role: {user_role}")

question = st.text_input("Ask a question:")

if st.button("Generate Query"):
    if not question:
        st.warning("Enter a question.")
    elif model is None:
        st.error("Model failed to load.")
    else:
        with st.spinner("Thinking..."):
            sql = generate_sql(question)
        
        if user_role == "Billing Admin" and "medical_records" in sql:
             st.error("ACCESS DENIED: Restricted Table.")
             log_audit(user_role, question, sql, "DENIED")
        else:
             st.code(sql, language="sql")
             st.session_state['generated_sql'] = sql
             st.session_state['question'] = question

if 'generated_sql' in st.session_state:
    if st.button("Execute"):
        res, err = run_sql_query(st.session_state['generated_sql'])
        if err: st.error(err)
        else: st.dataframe(res)