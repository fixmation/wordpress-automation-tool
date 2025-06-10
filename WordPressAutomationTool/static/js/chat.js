document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const chatMessages = document.getElementById('chatMessages');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const message = messageInput.value.trim();
        if (!message) return;

        // Disable send button and show loading state
        sendButton.disabled = true;
        sendButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

        // Add user message
        addMessage(message, 'user');
        messageInput.value = '';

        try {
            const response = await fetch('/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            addMessage(data.response || 'No reply', 'ai');

        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, there was an error processing your request.', 'system');
        } finally {
            sendButton.disabled = false;
            sendButton.innerHTML = 'Send';
        }
    });

    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        // Process markdown links [text](url) in the message
        const processedText = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, linkText, url) => {
            if (!url.startsWith('http')) {
                return `<a href="${url}" class="chat-link" onclick="window.location.href='${url}'; return false;">${linkText}</a>`;
            }
            return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="chat-link">${linkText}</a>`;
        });

        messageDiv.innerHTML = processedText;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Make links clickable
        const links = messageDiv.querySelectorAll('a');
        links.forEach(link => {
            if (!link.getAttribute('target')) {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    window.location.href = link.getAttribute('href');
                });
            }
        });
    }
});