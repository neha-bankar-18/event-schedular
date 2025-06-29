# 📅 Event Scheduler System

A full-stack Flask-based application to manage and schedule events with recurring options, email reminders, and a responsive dashboard.

---

## 🚀 Features

- 📝 Create, view, update, and delete events
- ⏰ Reminders for events starting within the next hour
- 🔁 Recurring events: daily, weekly, or monthly
- ✉️ Optional email notifications
- 🔍 Search functionality (title or description)
- 📊 Dashboard with real-time stats
- 🧱 Responsive Bootstrap UI with modular sidebar
- 🧪 Unit tests using `pytest`
- 💾 Data is stored persistently in a JSON file

---

## 🛠 Tech Stack

- **Backend**: Python 3, Flask
- **Frontend**: HTML, Bootstrap 5
- **Storage**: JSON File (`events.json`)
- **Email**: SMTP (Gmail)
- **Testing**: Pytest

---

## 📦 Installation

### 1. Clone the repository

git clone https://github.com/neha-bankar-18/event-schedular.git
cd event-scheduler

## ▶️ Running the App

Make sure Python 3.8+ is installed.

### 1. Start the Flask Server

python app.py

🚀 Event Scheduler App Running...
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)

## 🧪 Running Unit Tests (with Pytest)

This app includes unit tests using [Pytest](https://docs.pytest.org/) to validate all critical endpoints.

### 1. Install Pytest (if not already)

pip install pytest
pytest test_app.py

