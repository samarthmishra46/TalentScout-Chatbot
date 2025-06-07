import streamlit as st
import openai
import json
import re
import sqlite3
from dotenv import load_dotenv
import os
from prompts import *
from datetime import datetime

# Load environment variables
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database
DB_NAME = "talent_scout.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        years_experience INTEGER NOT NULL,
        desired_position TEXT,
        current_location TEXT,
        tech_stack TEXT,
        consent_given BOOLEAN NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS interview_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_email TEXT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Save candidate info

def save_to_db(user_info, consent_given):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO candidates 
                     (name, email, phone, years_experience, 
                      desired_position, current_location, 
                      tech_stack, consent_given)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_info['name'], user_info['email'], user_info.get('phone'),
                   user_info['years_experience'], user_info.get('desired_position'),
                   user_info.get('current_location'), json.dumps(user_info.get('tech_stack', [])),
                   consent_given))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Database Error: {str(e)}")
        return False
    finally:
        conn.close()

# Save question-answer

def save_question_answer(email, question, answer):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT INTO interview_log (candidate_email, question, answer) VALUES (?, ?, ?)''',
                  (email, question, answer))
        conn.commit()
    except Exception as e:
        st.error(f"Error saving Q&A: {str(e)}")
    finally:
        conn.close()

# Init session

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_info" not in st.session_state:
        st.session_state.user_info = {
            "name": None,
            "email": None,
            "phone": None,
            "years_experience": None,
            "desired_position": None,
            "current_location": None,
            "tech_stack": None
        }
    if "phase" not in st.session_state:
        st.session_state.phase = "greeting"
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "answers" not in st.session_state:
        st.session_state.answers = []

# LLM response

def get_llm_response(prompt, model="gpt-3.5-turbo"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# JSON extraction

def extract_json_from_response(response):
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}|\[.*\]', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return None
        return None

# Info gathering handler

def handle_info_gathering(user_input):
    extraction_prompt = INFO_EXTRACTION_PROMPT.format(user_input=user_input)
    llm_response = get_llm_response(extraction_prompt)
    extracted_data = extract_json_from_response(llm_response)

    if not extracted_data:
        st.session_state.messages.append({"role": "assistant", "content": "Could not parse your data. Please retry."})
        return

    for key in st.session_state.user_info:
        if extracted_data.get(key):
            st.session_state.user_info[key] = extracted_data[key]

    missing = [f for f in ["name", "email", "years_experience"] if not st.session_state.user_info.get(f)]
    if missing:
        st.session_state.messages.append({"role": "assistant", "content": f"Missing fields: {', '.join(missing)}"})
        return

    save_to_db(st.session_state.user_info, True)
    prompt = TECH_QUESTIONS_PROMPT.format(
        num_questions=5,
        tech_stack=", ".join(st.session_state.user_info.get("tech_stack", [])),
        years_experience=st.session_state.user_info["years_experience"]
    )
    tech_questions = get_llm_response(prompt)

    if tech_questions:
        questions = []
        for line in tech_questions.split("\n"):
            match = re.match(r"(\d+)\.\s*(.*)", line.strip())
            if match:
                number = match.group(1)
                text = match.group(2)
                questions.append(f"{number}. {text}")
        st.session_state.questions = questions
        st.session_state.phase = "tech_questions"
        # Show only first question
        if questions:
            st.session_state.messages.append({"role": "assistant", "content": questions[0]})
    else:
        st.session_state.messages.append({"role": "assistant", "content": "Could not generate questions."})

# Tech Q&A handler

def handle_tech_questions(user_input):
    answered_count = len(st.session_state.answers)
    if answered_count < len(st.session_state.questions):
        question = st.session_state.questions[answered_count]
        answer = user_input
        st.session_state.answers.append(answer)
        save_question_answer(st.session_state.user_info["email"], question, answer)

        if len(st.session_state.answers) == len(st.session_state.questions):
            st.session_state.phase = "complete"
            st.session_state.messages.append({"role": "assistant", "content": EXIT_PROMPT})
        else:
            next_question = st.session_state.questions[len(st.session_state.answers)]
            st.session_state.messages.append({"role": "assistant", "content": next_question})

# Main

def main():
    st.title("TalentScout Hiring Assistant 🤖")
    init_db()
    init_session_state()

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if user_input := st.chat_input("Type your response..."):
        st.session_state.messages.append({"role": "user", "content": user_input})

        if any(cmd in user_input.lower() for cmd in ["exit", "quit", "bye"]):
            st.session_state.phase = "complete"
            st.session_state.messages.append({"role": "assistant", "content": EXIT_PROMPT})
            st.rerun()

        if st.session_state.phase == "greeting":
            greeting = get_llm_response(GREETING_PROMPT)
            st.session_state.messages.append({"role": "assistant", "content": greeting})
            st.session_state.phase = "info_gathering"

        elif st.session_state.phase == "info_gathering":
            handle_info_gathering(user_input)

        elif st.session_state.phase == "tech_questions":
            handle_tech_questions(user_input)

        st.rerun()

if __name__ == "__main__":
    main()
