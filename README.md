
# 🚀 Text-to-SQL Agent using Gemini AI

**Alhamdulillah. All praise and gratitude belong to Allah, Who grants knowledge, patience, and the ability to persevere through challenges.**

This project is a **full-stack AI application** that converts **natural language questions into SQL queries**, executes them safely on a relational database, and displays the results in real time through a web interface.

---

## 🧠 Project Overview

The Text-to-SQL Agent enables users to interact with a database using plain English.  
The backend uses **Google Gemini AI** to generate SQL queries based on the database schema, validates them for safety, executes them on SQLite, and returns structured results to the frontend.

---

## ✨ Key Features

- Natural language → SQL query generation  
- Schema-aware and safe SQL generation (SELECT-only)  
- Automatic SQL execution on SQLite  
- Real-time result visualization  
- Interactive React-based UI  
- RESTful backend using Flask  
- Clean separation of frontend and backend  

---

## 🛠️ Tech Stack

### Backend
- Python  
- Flask  
- SQLite  
- Google Gemini AI (`google-generativeai`)  
- Flask-CORS  

### Frontend
- React (Create React App)  
- Tailwind CSS (CDN)  
- Lucide Icons  

---

## 📁 Project Structure

```

TextToSQL/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── sample_database.db
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   └── package-lock.json
│
├── .gitignore
├── LICENSE
└── README.md

````

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/TextToSQL.git
cd TextToSQL
````

---

## 🔙 Backend Setup (Flask)

### Create Virtual Environment

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file inside `backend/`:

```env
GOOGLE_API_KEY=your_google_ai_studio_api_key
```

> ⚠️ Do not commit `.env` to GitHub.

### Run Backend Server

```bash
python app.py
```

Backend will run at:

```
http://localhost:5000
```

---

## ⚛️ Frontend Setup (React)

### Install Dependencies

```bash
cd frontend
npm install
```

### Start Frontend

```bash
npm start
```

Frontend will run at:

```
http://localhost:3000
```

---

## 🌐 API Endpoints

| Method | Endpoint      | Description                    |
| ------ | ------------- | ------------------------------ |
| GET    | `/api/health` | Health check                   |
| GET    | `/api/schema` | Fetch database schema          |
| POST   | `/api/query`  | Process natural language query |

---

## 🧪 Example Queries

Try asking:

* `Show all customers`
* `Which city has the most customers?`
* `Top 5 expensive products`
* `Count products by category`

---

## 🔐 Security & Safety

* Only **SELECT** queries are allowed
* Dangerous SQL operations are blocked
* Schema-aware prompt construction
* Server-side SQL validation

---

## 🚧 Challenges & Learnings

* Understanding that frontend frameworks do not auto-connect to backends
* Resolving CRA vs Vite tooling confusion
* Debugging npm dependency and environment issues
* Handling CORS and API integration problems
* Managing AI model availability and SDK version mismatches
* Structuring a real-world project for GitHub

These challenges strengthened my understanding of **practical full-stack AI development**.

---

## 📌 Future Improvements

* Authentication and user management
* Support for multiple database engines
* Query history and export options
* Cloud deployment (Docker / CI/CD)

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 🤝 Acknowledgment

**Alhamdulillah**, this project was completed with patience, persistence, and continuous learning.
Feedback and contributions are welcome.


