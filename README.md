# 🤖 TalentScout AI Assistant

**TalentScout** is a conversational AI-powered hiring assistant built with **Streamlit** and **OpenAI**. It conducts technical screenings in a human-like chat interface, collects candidate information, and asks personalized technical questions **one by one**.

---

**Live At-**[http://13.49.244.69:8501/](http://13.49.244.69:8501/)


## ✨ Features

- 📋 Candidate data extraction (name, email, experience, tech stack)
- 💬 One-by-one technical questions via AI
- 💾 SQLite database storage for user info and Q&A logs
- ✅ GDPR-style consent capture
- 🧠 Powered by OpenAI GPT-3.5/4 APIs
- 🌐 Streamlit web UI

---

## 🧰 Technologies Used

- `Streamlit` — Web UI
- `OpenAI API` — Language model for questions & info extraction
- `SQLite3` — Local database
- `Python-dotenv` — Secure API key loading

---

## 🚀 Setup Instructions

### 1. Clone this Repository

```bash
git clone https://github.com/yourusername/talent-scout-ai.git
cd talent-scout-ai
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Add Your OpenAI API Key

Create a `.env` file:

```env
OPENAI_API_KEY=your-api-key-here
```

### 4. Run the App

```bash
streamlit run main.py
```

---

## 🗃️ Database Schema

### `candidates` Table

| Column             | Type     | Description                        |
|--------------------|----------|------------------------------------|
| id                 | INTEGER  | Primary key                        |
| name               | TEXT     | Candidate’s name                   |
| email              | TEXT     | Unique candidate email             |
| phone              | TEXT     | Optional phone number              |
| years_experience   | INTEGER  | Total experience in years          |
| desired_position   | TEXT     | Optional job role                  |
| current_location   | TEXT     | Optional city or region            |
| tech_stack         | TEXT     | JSON array of technologies         |
| consent_given      | BOOLEAN  | GDPR-style consent flag            |
| timestamp          | DATETIME | Auto timestamp                     |

---

### `interview_log` Table

| Column           | Type     | Description                          |
|------------------|----------|--------------------------------------|
| id               | INTEGER  | Primary key                          |
| candidate_email  | TEXT     | Foreign key from `candidates.email` |
| question         | TEXT     | Question asked by the AI            |
| answer           | TEXT     | User’s answer                        |
| timestamp        | DATETIME | Auto timestamp                       |

---

## 📌 How It Works

1. **User starts a conversation** — Enters name, experience, email, etc.
2. **GPT extracts info** from the intro using prompts.
3. **Questions are generated** based on stack & experience.
4. **User answers questions one at a time** in a chat format.
5. **All info and Q&A saved** to `talent_scout.db`.

---

## 📂 File Structure

```
.
├── main.py            # Core Streamlit app
├── prompts.py         # GPT prompts
├── .env               # Your API key (not tracked)
├── requirements.txt   # Python dependencies
├── talent_scout.db    # SQLite database (auto-generated)
└── README.md          # This documentation
```

---

## 📄 Prompts Overview (in `prompts.py`)

- `GREETING_PROMPT` — Welcomes user
- `INFO_EXTRACTION_PROMPT` — Extracts structured data
- `TECH_QUESTIONS_PROMPT` — Creates technical questions
- `EXIT_PROMPT` — Final farewell from bot

---

## 📸 Screenshot

![Screenshot](https://github.com/user-attachments/assets/04bfbd2f-5cfc-45cf-99f6-05321cd48f59)


## 📸 Demo Video

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/3B-SFOTzllI/0.jpg)](https://www.youtube.com/watch?v=3B-SFOTzllI)

---

## 🛡️ License

MIT License © 2025 [Samarth Mishra]

---

## 🙋 Want to Contribute?

PRs welcome! Please open an issue first for major changes.  

---

## 📫 Contact

If you have questions or ideas, feel free to reach out at:  
📧 **samarthmishra46@gmail.com**

---

> Built with ❤️ using Streamlit and OpenAI.
