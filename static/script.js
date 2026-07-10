  let chatStarted = false;
        const chatBox = document.getElementById('chat-box');
        const input = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');
        const typingIndicator = document.getElementById('typing-indicator');
        const welcomeState = document.getElementById('welcome-state');

        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        input.addEventListener('input', function() {
            sendBtn.disabled = input.value.trim() === '';
        });

        function getTimeString() {
            return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }

        function addMessage(message, sender) {
            if (!chatStarted) {
                chatStarted = true;
                if (welcomeState) welcomeState.style.display = 'none';

                const dateSep = document.createElement('div');
                dateSep.className = 'date-sep';
                const today = new Date();
                dateSep.innerHTML = `<span>${today.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}</span>`;
                chatBox.appendChild(dateSep);
            }

            const row = document.createElement('div');
            row.className = `message-row message-row--${sender}`;

            const avatarIcon = sender === 'bot'
                ? '<i class="fa-solid fa-bolt"></i>'
                : '<i class="fa-solid fa-user"></i>';

            row.innerHTML = `
                <div class="msg-avatar msg-avatar--${sender}">${avatarIcon}</div>
                <div class="msg-content">
                    <div class="bubble bubble--${sender}">${message}</div>
                    <div class="msg-time">${getTimeString()}</div>
                </div>
            `;

            chatBox.appendChild(row);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function showTyping() {
            typingIndicator.classList.add('active');
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function hideTyping() {
            typingIndicator.classList.remove('active');
        }

        function sendSuggestion(el) {
            const text = el.textContent.trim();
            input.value = text;
            sendBtn.disabled = false;
            sendMessage();
        }

        async function sendMessage() {
            const message = input.value.trim();
            if (message === '') return;

            input.disabled = true;
            sendBtn.disabled = true;
            input.value = '';

            addMessage(message, 'user');
            showTyping();

            try {
                const response = await fetch('/get_response', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();

                setTimeout(() => {
                    hideTyping();
                    addMessage(data.response, 'bot');
                    input.disabled = false;
                    input.focus();
                }, 600);

            } catch (err) {
                hideTyping();
                addMessage('Something went wrong. Please try again.', 'bot');
                input.disabled = false;
                input.focus();
            }
        }

        function clearChat() {
            chatStarted = false;
            chatBox.querySelectorAll('.message-row, .date-sep').forEach(el => el.remove());
            if (welcomeState) welcomeState.style.display = 'flex';
            input.disabled = false;
            input.focus();
        }

        input.focus();