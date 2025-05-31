class ChatBot {
    constructor() {
        this.messagesDiv = document.getElementById('messages');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.typingIndicator = document.querySelector('.typing-indicator');
        
        this.isProcessing = false;
        this.conversationHistory = [];
        this.maxRetries = 3;
        
        this.initializeEventListeners();
        this.showWelcomeMessage();
        this.focusInput();
    }

    initializeEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize input
        this.userInput.addEventListener('input', () => {
            this.adjustInputHeight();
        });

        // Focus input when clicking anywhere in chat
        this.messagesDiv.addEventListener('click', () => {
            this.focusInput();
        });

        // Handle connection status
        window.addEventListener('online', () => this.updateConnectionStatus(true));
        window.addEventListener('offline', () => this.updateConnectionStatus(false));
    }

    showWelcomeMessage() {
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        welcomeDiv.innerHTML = `
            <strong>🤖 Welcome to your Data Engineering Assistant!</strong><br>
            I can help you with data pipelines, databases, streaming, and more.<br>
            <em>Try asking: "What is a data pipeline?" or "Hello"</em>
        `;
        this.messagesDiv.appendChild(welcomeDiv);
    }

    focusInput() {
        if (!this.isProcessing) {
            this.userInput.focus();
        }
    }

    adjustInputHeight() {
        this.userInput.style.height = 'auto';
        this.userInput.style.height = this.userInput.scrollHeight + 'px';
    }

    async sendMessage(retryCount = 0) {
        const message = this.userInput.value.trim();
        
        if (!message || this.isProcessing) {
            return;
        }

        // Validate message length
        if (message.length > 500) {
            this.showError('Message too long. Please keep it under 500 characters.');
            return;
        }

        // Add user message
        this.addMessage(message, 'user');
        this.userInput.value = '';
        this.adjustInputHeight();
        
        // Set processing state
        this.setProcessingState(true);
        
        try {
            // Show typing indicator
            this.showTyping();
            
            // Send request with timeout
            const response = await this.sendRequest(message);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTyping();
            
            // Add bot response
            if (data.response) {
                this.addMessage(data.response, 'bot');
                this.saveToHistory(message, data.response);
            } else {
                throw new Error('Invalid response format');
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTyping();
            
            // Retry logic
            if (retryCount < this.maxRetries && this.isNetworkError(error)) {
                setTimeout(() => {
                    this.sendMessage(retryCount + 1);
                }, 1000 * (retryCount + 1)); // Exponential backoff
                
                this.showError(`Connection issue. Retrying... (${retryCount + 1}/${this.maxRetries})`);
            } else {
                this.handleError(error);
            }
        } finally {
            this.setProcessingState(false);
        }
    }

    async sendRequest(message) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message,
                    timestamp: Date.now(),
                    history: this.conversationHistory.slice(-5) // Send last 5 messages for context
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            return response;
            
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        // Add message content
        const contentSpan = document.createElement('span');
        contentSpan.textContent = text;
        messageDiv.appendChild(contentSpan);
        
        // Add timestamp
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'timestamp';
        timestampDiv.textContent = this.formatTime(new Date());
        messageDiv.appendChild(timestampDiv);
        
        this.messagesDiv.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Add animation class after a brief delay
        setTimeout(() => {
            messageDiv.classList.add('animate');
        }, 10);
    }

    showTyping() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'block';
            this.scrollToBottom();
        }
    }

    hideTyping() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'none';
        }
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        this.messagesDiv.appendChild(errorDiv);
        this.scrollToBottom();
        
        // Auto-remove error after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }

    handleError(error) {
        let errorMessage = 'Sorry, something went wrong. Please try again.';
        
        if (error.name === 'AbortError') {
            errorMessage = 'Request timed out. Please check your connection and try again.';
        } else if (!navigator.onLine) {
            errorMessage = 'You appear to be offline. Please check your internet connection.';
        } else if (error.message.includes('500')) {
            errorMessage = 'Server error. Please try again in a moment.';
        } else if (error.message.includes('404')) {
            errorMessage = 'Service unavailable. Please refresh the page.';
        }
        
        this.showError(errorMessage);
    }

    isNetworkError(error) {
        return error.name === 'TypeError' || 
               error.message.includes('fetch') ||
               error.message.includes('network') ||
               !navigator.onLine;
    }

    setProcessingState(processing) {
        this.isProcessing = processing;
        this.userInput.disabled = processing;
        this.sendBtn.disabled = processing;
        
        if (processing) {
            this.sendBtn.innerHTML = `
                <div class="spinner"></div>
                <span>Sending...</span>
            `;
        } else {
            this.sendBtn.innerHTML = 'Send';
            this.focusInput();
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesDiv.scrollTop = this.messagesDiv.scrollHeight;
        }, 100);
    }

    formatTime(date) {
        return date.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    saveToHistory(userMessage, botResponse) {
        this.conversationHistory.push({
            user: userMessage,
            bot: botResponse,
            timestamp: Date.now()
        });
        
        // Keep only last 20 conversations
        if (this.conversationHistory.length > 20) {
            this.conversationHistory = this.conversationHistory.slice(-20);
        }
        
        // Save to localStorage if available
        try {
            localStorage.setItem('chatHistory', JSON.stringify(this.conversationHistory));
        } catch (e) {
            console.warn('Could not save chat history:', e);
        }
    }

    loadHistory() {
        try {
            const saved = localStorage.getItem('chatHistory');
            if (saved) {
                this.conversationHistory = JSON.parse(saved);
            }
        } catch (e) {
            console.warn('Could not load chat history:', e);
        }
    }

    updateConnectionStatus(online) {
        const statusIndicator = document.querySelector('.status-indicator');
        if (statusIndicator) {
            statusIndicator.style.background = online ? '#4CAF50' : '#f44336';
        }
        
        if (!online) {
            this.showError('Connection lost. Messages will be sent when reconnected.');
        }
    }

    // Public methods for external use
    clearChat() {
        this.messagesDiv.innerHTML = '';
        this.conversationHistory = [];
        localStorage.removeItem('chatHistory');
        this.showWelcomeMessage();
    }

    exportHistory() {
        const data = {
            conversations: this.conversationHistory,
            exportDate: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-history-${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatBot = new ChatBot();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K to clear chat
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (confirm('Clear chat history?')) {
                window.chatBot.clearChat();
            }
        }
        
        // Ctrl/Cmd + E to export history
        if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
            e.preventDefault();
            window.chatBot.exportHistory();
        }
    });
});

// Service Worker registration (for offline support)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}