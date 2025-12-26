const conversationId = JSON.parse(document.getElementById('conversation-id').textContent);

// WebSocket Setup
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const chatSocket = new WebSocket(
    `${protocol}//${window.location.host}/ws/chat/${conversationId}/`
);

const messagesContainer = document.getElementById('messages-container');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

// Auto-parse existing messages (if any were rendered raw)
// Simple pass to markdownify what is already there if needed, 
// OR just trust server rendering for old history.
// For now, let's just make sure new messages are markdown.

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.type === 'ai_response') {
        appendMessage('ai', data.message);
    } else if (data.error) {
        console.error("Error:", data.error);
        appendMessage('system', 'Error: ' + data.error);
    }
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

function sendMessage() {
    const message = chatInput.value.trim();
    if (message) {
        chatSocket.send(JSON.stringify({
            'message': message
        }));
        
        appendMessage('user', message);
        chatInput.value = '';
    }
}

function appendMessage(sender, content) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    
    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');
    
    // Parse Markdown
    contentDiv.innerHTML = marked.parse(content);
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Initial scroll
messagesContainer.scrollTop = messagesContainer.scrollHeight;
