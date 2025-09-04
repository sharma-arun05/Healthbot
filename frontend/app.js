const BACKEND_URL = window.BACKEND_URL || (localStorage.getItem('BACKEND_URL') || 'http://localhost:5000');

async function fetchSubscribers() {
  const res = await fetch(`${BACKEND_URL}/api/subscribers`);
  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
}

async function refresh() {
  try {
    const data = await fetchSubscribers();
    const ul = document.getElementById('subscribers');
    ul.innerHTML = '';
    if (data.subscribers.length === 0) {
        const li = document.createElement('li');
        li.textContent = "No subscribers yet.";
        ul.appendChild(li);
    } else {
        for (const s of data.subscribers) {
            const li = document.createElement('li');
            li.textContent = `${s.phone_number} — ${s.location || 'n/a'}`;
            ul.appendChild(li);
        }
    }
  } catch (e) {
    console.error(e);
    alert('Could not fetch subscribers. Is the backend running?');
  }
}

document.getElementById('refresh').addEventListener('click', refresh);
document.addEventListener('DOMContentLoaded', refresh);

document.getElementById('send').addEventListener('click', async () => {
  const messageInput = document.getElementById('message');
  const message = messageInput.value;
  const sendBtn = document.getElementById('send');
  
  if (!message) return alert('Add a message first');

  // Disable button and show a sending state
  sendBtn.textContent = 'Sending...';
  sendBtn.disabled = true;

  try {
    const res = await fetch(`${BACKEND_URL}/api/alert`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    document.getElementById('result').textContent = JSON.stringify(data, null, 2);
    messageInput.value = ''; // Clear the input field
  } catch (e) {
    console.error(e);
    alert('Failed to send alert');
  } finally {
    // Re-enable the button regardless of success or failure
    sendBtn.textContent = 'Send to all subscribers';
    sendBtn.disabled = false;
  }
});