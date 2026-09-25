const form = document.querySelector('#chat-form');
const input = document.querySelector('#message-input');
const messages = document.querySelector('#messages');

function addMessage(text, role, meta = 'Just now') {
  const item = document.createElement('div');
  item.className = `message ${role}`;
  item.innerHTML = role === 'bot'
    ? `<div class="avatar">N</div><div><p class="message-text"></p><time>${meta}</time></div>`
    : `<div><p class="message-text"></p><time>${meta}</time></div>`;
  item.querySelector('.message-text').textContent = text;
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
}

function setTyping(isTyping) {
  const existing = document.querySelector('#typing-indicator');
  if (isTyping && !existing) {
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'message bot typing';
    indicator.innerHTML = '<div class="avatar">E</div><div><p class="message-text">Emerspark Assistant is thinking...</p></div>';
    messages.appendChild(indicator);
    messages.scrollTop = messages.scrollHeight;
  } else if (!isTyping && existing) {
    existing.remove();
  }
}

async function sendMessage(message) {
  addMessage(message, 'user');
  input.value = '';
  input.disabled = true;
  setTyping(true);
  try {
    const response = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message}) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Something went wrong.');
    const meta = data.source === 'ai' ? 'AI response' : `Match ${Math.round(data.score * 100)}%`;
    addMessage(data.answer, 'bot', meta);
  } catch (error) {
    addMessage(error.message, 'bot');
  } finally {
    setTyping(false);
    input.disabled = false;
    input.focus();
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (message) sendMessage(message);
});
document.querySelectorAll('[data-suggestion]').forEach((button) => button.addEventListener('click', () => sendMessage(button.dataset.suggestion)));
