from flask import Flask, request, jsonify, render_template
import json, os, time
from datetime import datetime, timedelta
from threading import Thread
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

DATA_FILE = 'events.json'

# Load events
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as file:
        try:
            events = json.load(file)
        except json.JSONDecodeError:
            events = []
else:
    events = []

# Save events
def save_events():
    with open(DATA_FILE, 'w') as file:
        json.dump(events, file, indent=4)

# Parse datetime string
def parse_datetime(dt_str):
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")

# ------------------ Routes ------------------

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/create')
def create_page():
    return render_template('create.html')

@app.route('/list')
def list_page():
    sorted_events = sorted(events, key=lambda e: parse_datetime(e['start_time']))
    return render_template('list.html', events=sorted_events)

@app.route('/update')
def update_page():
    return render_template('update.html')

@app.route('/events', methods=['POST'])
def create_event():
    data = request.json
    try:
        event = {
            'id': len(events) + 1,
            'title': data['title'],
            'description': data['description'],
            'start_time': data['start_time'],
            'end_time': data['end_time'],
            'recurrence': data.get('recurrence', 'none'),
            'email_notify': data.get('email_notify', False)
        }
        parse_datetime(event['start_time'])  # validate
        parse_datetime(event['end_time'])    # validate
        events.append(event)
        save_events()
        return jsonify({'message': 'Event created!', 'event': event}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/events', methods=['GET'])
def list_events():
    return jsonify(sorted(events, key=lambda e: parse_datetime(e['start_time'])))

@app.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.json
    for event in events:
        if event['id'] == event_id:
            event['title'] = data.get('title', event['title'])
            event['description'] = data.get('description', event['description'])
            event['start_time'] = data.get('start_time', event['start_time'])
            event['end_time'] = data.get('end_time', event['end_time'])
            event['recurrence'] = data.get('recurrence', event.get('recurrence', 'none'))
            event['email_notify'] = data.get('email_notify', event.get('email_notify', False))
            save_events()
            return jsonify({'message': 'Event updated', 'event': event}), 200
    return jsonify({'error': 'Event not found'}), 404

@app.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    global events
    new_events = [e for e in events if e['id'] != event_id]
    if len(new_events) == len(events):
        return jsonify({'error': 'Event not found'}), 404
    events[:] = new_events
    save_events()
    return jsonify({'message': 'Event deleted'}), 200

@app.route('/events/search')
def search_events():
    query = request.args.get('q', '').lower()
    matched = [e for e in events if query in e['title'].lower() or query in e['description'].lower()]
    return jsonify(matched)

@app.route('/upcoming_reminders')
def upcoming_reminders():
    now = datetime.now()
    upcoming = []

    for event in events:
        start = parse_datetime(event['start_time'])
        if event.get('recurrence') != 'none':
            start = apply_recurrence(event)

        diff = (start - now).total_seconds()
        if 0 <= diff <= 3600:
            upcoming.append({
                'title': event['title'],
                'description': event['description'],
                'start_time': start.strftime('%Y-%m-%d %H:%M')
            })

    return jsonify(upcoming)

# ------------------ Email & Reminder Logic ------------------

def send_email(to, subject, body):
    user = os.getenv('EMAIL_USER')
    pwd = os.getenv('EMAIL_PASS')

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = to

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(user, pwd)
            smtp.send_message(msg)
        print(f"✅ Email sent to {to}")
    except Exception as e:
        print(f"❌ Email failed: {e}")

def apply_recurrence(event):
    now = datetime.now()
    start = parse_datetime(event['start_time'])
    while start < now:
        if event['recurrence'] == 'daily':
            start += timedelta(days=1)
        elif event['recurrence'] == 'weekly':
            start += timedelta(weeks=1)
        elif event['recurrence'] == 'monthly':
            start += timedelta(days=30)
        else:
            break
    return start

last_emailed = {}

def should_send_email(event_id, recurrence):
    now = datetime.now()
    last = last_emailed.get(event_id)
    if not last:
        return True
    interval = {
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(days=30)
    }.get(recurrence, timedelta(days=365))
    return (now - last) >= interval

def reminder_worker():
    while True:
        now = datetime.now()
        for event in events:
            start = parse_datetime(event['start_time'])
            if event['recurrence'] != 'none':
                start = apply_recurrence(event)
            if 0 <= (start - now).total_seconds() <= 3600:
                print(f"🔔 Reminder: {event['title']} starts at {start}")
                if event.get('email_notify') and should_send_email(event['id'], event['recurrence']):
                    send_email(
                        os.getenv('EMAIL_USER'),
                        f"Upcoming Event: {event['title']}",
                        f"{event['description']} starts at {start}"
                    )
                    last_emailed[event['id']] = now
        time.sleep(60)

# ------------------ Start App ------------------

if __name__ == '__main__':
    Thread(target=reminder_worker, daemon=True).start()
    print("🚀 Event Scheduler App Running...")
    app.run(debug=True)
