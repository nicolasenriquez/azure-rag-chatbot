/**
 * AI Chatbot Assistant - Main JavaScript File
 * Handles all interactive functionality including screen navigation,
 * message handling, typing indicators, and API integration with FastAPI backend.
 */

class ChatbotInterface {
    constructor() {
        this.currentScreen = 'welcome';
        this.isTyping = false;
        this.sessionId = this.generateSessionId();
        this.messageHistory = [];
        
        // API Configuration - FastAPI Backend
        this.apiBaseUrl = 'http://bda-chatbot-backend-dkfeejcbhpfreha3.chilecentral-01.azurewebsites.net'; // Update this to match your backend URL
        this.apiEndpoints = {
            chat: '/api/chat',
            health: '/api/health',
            history: '/api/chat/history',
            stats: '/api/chat/stats'
        };
        
        this.initializeElements();
        this.bindEvents();
        this.checkApiHealth();
    }

    /**
     * Initialize DOM element references
     */
    initializeElements() {
        // Screens
        this.welcomeScreen = document.getElementById('welcome-screen');
        this.chatScreen = document.getElementById('chat-screen');
        
        // Welcome screen elements
        this.startChatBtn = document.getElementById('start-chat-btn');
        
        // Chat screen elements
        this.backBtn = document.getElementById('back-btn');
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.loadingOverlay = document.getElementById('loading-overlay');
    }

    /**
     * Bind event listeners to interactive elements
     */
    bindEvents() {
        // Welcome screen events
        this.startChatBtn.addEventListener('click', () => this.showChatScreen());
        
        // Chat screen events
        this.backBtn.addEventListener('click', () => this.showWelcomeScreen());
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize text input
        this.messageInput.addEventListener('input', () => this.autoResizeInput());
        
        // Prevent empty messages
        this.messageInput.addEventListener('input', () => this.updateSendButtonState());
    }

    /**
     * Generate a unique session ID for the chat
     */
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Show the chat screen and hide welcome screen
     */
    showChatScreen() {
        this.welcomeScreen.classList.remove('active');
        this.chatScreen.classList.add('active');
        this.currentScreen = 'chat';
        
        // Load conversation history if available
        this.loadConversationHistory();
        
        // Focus on input after transition
        setTimeout(() => {
            this.messageInput.focus();
        }, 300);
    }

    /**
     * Show the welcome screen and hide chat screen
     */
    showWelcomeScreen() {
        this.chatScreen.classList.remove('active');
        this.welcomeScreen.classList.add('active');
        this.currentScreen = 'welcome';
        
        // Clear input and reset state
        this.messageInput.value = '';
        this.updateSendButtonState();
        this.autoResizeInput();
    }

    /**
     * Send a message to the AI assistant
     */
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || this.isTyping) {
            return;
        }

        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input and reset state
        this.messageInput.value = '';
        this.updateSendButtonState();
        this.autoResizeInput();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to FastAPI backend
            const response = await this.sendMessageToAPI(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add AI response to chat
            if (response && response.llm_answer) {
                this.addMessage(response.llm_answer, 'bot');
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I\'m having trouble connecting right now. Please check your connection and try again.', 'bot');
        }
    }

    /**
     * Send message to the FastAPI backend
     */
    async sendMessageToAPI(message) {
        const payload = {
            session_id: this.sessionId,
            user_question: message
        };

        const response = await fetch(`${this.apiBaseUrl}${this.apiEndpoints.chat}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Load conversation history from the backend
     */
    async loadConversationHistory() {
        try {
            const response = await fetch(`${this.apiBaseUrl}${this.apiEndpoints.history}/${this.sessionId}`);
            
            if (response.ok) {
                const data = await response.json();
                if (data.logs && data.logs.length > 0) {
                    // Clear existing messages except welcome message
                    const welcomeMessage = this.chatMessages.querySelector('.bot-message');
                    this.chatMessages.innerHTML = '';
                    if (welcomeMessage) {
                        this.chatMessages.appendChild(welcomeMessage);
                    }
                    
                    // Add historical messages
                    data.logs.forEach(log => {
                        if (log.user_question) {
                            this.addMessage(log.user_question, 'user', false);
                        }
                        if (log.llm_answer) {
                            this.addMessage(log.llm_answer, 'bot', false);
                        }
                    });
                    
                    this.scrollToBottom();
                }
            }
        } catch (error) {
            console.warn('Could not load conversation history:', error);
        }
    }

    /**
     * Add a message to the chat interface
     */
    addMessage(content, sender, animate = true) {
        const messageElement = this.createMessageElement(content, sender);
        this.chatMessages.appendChild(messageElement);
        
        // Store in history
        this.messageHistory.push({
            content,
            sender,
            timestamp: new Date()
        });
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Add animation delay for bot messages
        if (animate && sender === 'bot') {
            messageElement.style.opacity = '0';
            messageElement.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                messageElement.style.transition = 'all 0.3s ease-out';
                messageElement.style.opacity = '1';
                messageElement.style.transform = 'translateY(0)';
            }, 100);
        }
    }

    /**
     * Create a message element
     */
    createMessageElement(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const paragraph = document.createElement('p');
        paragraph.textContent = content;
        contentDiv.appendChild(paragraph);
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = this.getCurrentTime();
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        
        return messageDiv;
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.classList.remove('hidden');
        this.scrollToBottom();
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.classList.add('hidden');
    }

    /**
     * Auto-resize the input field based on content
     */
    autoResizeInput() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    /**
     * Update send button state based on input content
     */
    updateSendButtonState() {
        const hasContent = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasContent || this.isTyping;
        
        if (this.sendBtn.disabled) {
            this.sendBtn.style.opacity = '0.5';
        } else {
            this.sendBtn.style.opacity = '1';
        }
    }

    /**
     * Scroll chat messages to bottom
     */
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    /**
     * Get current time formatted for display
     */
    getCurrentTime() {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }

    /**
     * Check API health status
     */
    async checkApiHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}${this.apiEndpoints.health}`);
            if (!response.ok) {
                console.warn('API health check failed');
                this.showApiStatusWarning();
            } else {
                console.log('API health check passed');
            }
        } catch (error) {
            console.warn('API health check failed:', error);
            this.showApiStatusWarning();
        }
    }

    /**
     * Show API status warning
     */
    showApiStatusWarning() {
        // Add a subtle warning to the welcome screen
        const warningDiv = document.createElement('div');
        warningDiv.className = 'api-warning';
        warningDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Backend service may be unavailable';
        warningDiv.style.cssText = `
            color: #ff6b6b;
            font-size: 14px;
            margin-top: 16px;
            padding: 8px 16px;
            background: rgba(255, 107, 107, 0.1);
            border-radius: 8px;
            border: 1px solid rgba(255, 107, 107, 0.3);
        `;
        
        const welcomeContainer = document.querySelector('.welcome-container');
        if (welcomeContainer && !document.querySelector('.api-warning')) {
            welcomeContainer.appendChild(warningDiv);
        }
    }

    /**
     * Show loading overlay
     */
    showLoading() {
        this.loadingOverlay.classList.remove('hidden');
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
    }

    /**
     * Get chat statistics
     */
    async getChatStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}${this.apiEndpoints.stats}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error fetching chat stats:', error);
        }
        return null;
    }

    /**
     * Export chat history
     */
    exportChatHistory() {
        const history = this.messageHistory.map(msg => ({
            sender: msg.sender,
            content: msg.content,
            timestamp: msg.timestamp.toISOString()
        }));
        
        const dataStr = JSON.stringify(history, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `chat_history_${this.sessionId}.json`;
        link.click();
    }

    /**
     * Clear chat history
     */
    clearChatHistory() {
        this.messageHistory = [];
        this.chatMessages.innerHTML = '';
        
        // Add welcome message back
        const welcomeMessage = this.createMessageElement(
            'Hello! I\'m your AI assistant. I can help you with various tasks including logistics, inventory management, warehousing, and restocking. How can I assist you today?',
            'bot'
        );
        this.chatMessages.appendChild(welcomeMessage);
    }
}

/**
 * Utility functions
 */
class ChatbotUtils {
    /**
     * Debounce function to limit API calls
     */
    static debounce(func, wait) {
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

    /**
     * Format timestamp for display
     */
    static formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffInHours = (now - date) / (1000 * 60 * 60);
        
        if (diffInHours < 1) {
            return 'Just now';
        } else if (diffInHours < 24) {
            return `${Math.floor(diffInHours)}h ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    /**
     * Sanitize user input
     */
    static sanitizeInput(input) {
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    }

    /**
     * Copy text to clipboard
     */
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (error) {
            console.error('Failed to copy text:', error);
            return false;
        }
    }
}

/**
 * Error handling class
 */
class ChatbotErrorHandler {
    static handleError(error, context = '') {
        console.error(`Chatbot Error [${context}]:`, error);
        
        // You can implement more sophisticated error handling here
        // such as sending errors to a logging service
        
        return {
            type: 'error',
            message: 'An unexpected error occurred. Please try again.',
            context
        };
    }

    static isNetworkError(error) {
        return error.name === 'TypeError' && error.message.includes('fetch');
    }

    static isApiError(error) {
        return error.status >= 400 && error.status < 600;
    }
}

/**
 * Initialize the chatbot when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the chatbot interface
    window.chatbot = new ChatbotInterface();
    
    // Add global error handler
    window.addEventListener('error', (event) => {
        ChatbotErrorHandler.handleError(event.error, 'Global Error');
    });
    
    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
        ChatbotErrorHandler.handleError(event.reason, 'Unhandled Promise Rejection');
    });
    
    console.log('AI Chatbot Assistant initialized successfully!');
});

/**
 * Service Worker registration for PWA capabilities (optional)
 */
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
} 