const form = document.getElementById('eventForm');
const list = document.getElementById('eventList');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const event = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        start_time: document.getElementById('start_time').value.replace('T', ' '),
        end_time: document.getElementById('end_time').value.replace('T', ' ')
    };
    await fetch('/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event)
    });
    form.reset();
    loadEvents();
});

async function loadEvents() {
    const response = await fetch('/events');
    const events = await response.json();
    list.innerHTML = '';
    events.forEach(event => {
        const item = document.createElement('li');
        item.className = 'list-group-item d-flex justify-content-between align-items-start';
        item.innerHTML = `
            <div class="ms-2 me-auto">
                <div class="fw-bold">${event.title}</div>
                ${event.description} <br>
                <small>${event.start_time} to ${event.end_time}</small>
            </div>
            <button class="btn btn-danger btn-sm me-2" onclick="deleteEvent(${event.id})">Delete</button>
            <button class="btn btn-secondary btn-sm" onclick="editEvent(${event.id}, '${event.title}', '${event.description}', '${event.start_time}', '${event.end_time}')">Edit</button>
        `;
        list.appendChild(item);
    });
}

async function deleteEvent(id) {
    await fetch(`/events/${id}`, { method: 'DELETE' });
    loadEvents();
}

function editEvent(id, title, desc, start, end) {
    document.getElementById('title').value = title;
    document.getElementById('description').value = desc;
    document.getElementById('start_time').value = start.replace(' ', 'T');
    document.getElementById('end_time').value = end.replace(' ', 'T');
    
    form.onsubmit = async function (e) {
        e.preventDefault();
        const updated = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            start_time: document.getElementById('start_time').value.replace('T', ' '),
            end_time: document.getElementById('end_time').value.replace('T', ' ')
        };
        await fetch(`/events/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updated)
        });
        form.reset();
        form.onsubmit = defaultSubmit;
        loadEvents();
    };
}

const defaultSubmit = form.onsubmit;
loadEvents();
