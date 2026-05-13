# HonestCart API Project

Modern backend API project built with FastAPI.

## 🚀 Tech Stack

- Python
- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/QuadCoreOrg/HonestCart-API.git
cd HonestCart-API
```

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

### Mac/Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Run The Project

```bash
uvicorn app.main:app --reload
```

Server will start at:

```bash
http://127.0.0.1:8000
```

---

## 📘 API Documentation

Swagger UI:

```bash
http://127.0.0.1:8000/docs
```

ReDoc:

```bash
http://127.0.0.1:8000/redoc
```

---

## 🌱 Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your_secret_key
```

---

## 📦 Requirements

Generate requirements file:

```bash
pip freeze > requirements.txt
```

---

## 📄 License

This project is licensed under the MIT License.

```
