console.log('🤖 Sales AI loaded');

/**
 * Sales AI Assistant
 * Uses Claude API to answer questions based on knowledge base
 */

class SalesAI {
    constructor() {
        this.apiEndpoint = '/api/sales-ai/query';
        this.conversationHistory = [];
        this.isProcessing = false;
    }

    /**
     * Initialize the AI chat interface
     */
    init() {
        this.createChatUI();
        this.attachEventListeners();
        console.log('✅ Sales AI initialized');
    }

    /**
     * Create the chat UI elements
     */
    createChatUI() {
        const chatHTML = `
            <div id="sales-ai-container" class="sales-ai-collapsed">
                <!-- Toggle Button -->
                <button id="sales-ai-toggle" class="sales-ai-toggle" aria-label="Toggle Sales AI">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                        <circle cx="9" cy="10" r="1"/>
                        <circle cx="12" cy="10" r="1"/>
                        <circle cx="15" cy="10" r="1"/>
                    </svg>
                </button>

                <!-- Chat Panel -->
                <div id="sales-ai-panel" class="sales-ai-panel">
                    <div class="sales-ai-header">
                        <div>
                            <h3>🤖 Sales AI Assistant</h3>
                            <p>Ask me about sales processes, playbooks, and customer insights</p>
                        </div>
                        <button id="sales-ai-close" class="sales-ai-close">&times;</button>
                    </div>

                    <div id="sales-ai-messages" class="sales-ai-messages">
                        <div class="ai-message">
                            <div class="message-avatar">🤖</div>
                            <div class="message-content">
                                <p>Hi! I'm your Sales AI assistant. I have access to:</p>
                                <ul>
                                    <li>📞 Call transcripts and best practices</li>
                                    <li>📚 Sales playbooks and methodologies</li>
                                    <li>💰 Pricing strategies and objection handling</li>
                                    <li>🎯 Discovery questions and qualification criteria</li>
                                    <li>📊 Case studies and success stories</li>
                                </ul>
                                <p><strong>Try asking:</strong></p>
                                <ul>
                                    <li>"What questions should I ask in a discovery call?"</li>
                                    <li>"How do we handle pricing objections?"</li>
                                    <li>"Show me a healthcare case study"</li>
                                    <li>"What's our positioning vs competitors?"</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <div class="sales-ai-input-container">
                        <textarea
                            id="sales-ai-input"
                            class="sales-ai-input"
                            placeholder="Ask me anything about sales..."
                            rows="2"
                        ></textarea>
                        <button id="sales-ai-send" class="sales-ai-send">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="22" y1="2" x2="11" y2="13"/>
                                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                            </svg>
                        </button>
                    </div>

                    <div class="sales-ai-quick-actions">
                        <button class="quick-action" data-prompt="What questions should I ask in a discovery call?">
                            Discovery Questions
                        </button>
                        <button class="quick-action" data-prompt="How do we handle pricing objections?">
                            Pricing Objections
                        </button>
                        <button class="quick-action" data-prompt="What's included in IT360 vs IT Assist?">
                            Service Tiers
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', chatHTML);
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const toggle = document.getElementById('sales-ai-toggle');
        const close = document.getElementById('sales-ai-close');
        const send = document.getElementById('sales-ai-send');
        const input = document.getElementById('sales-ai-input');
        const container = document.getElementById('sales-ai-container');

        // Toggle chat
        toggle.addEventListener('click', () => {
            container.classList.toggle('sales-ai-collapsed');
        });

        // Close chat
        close.addEventListener('click', () => {
            container.classList.add('sales-ai-collapsed');
        });

        // Send message
        send.addEventListener('click', () => this.sendMessage());

        // Send on Enter (but Shift+Enter for new line)
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Quick actions
        document.querySelectorAll('.quick-action').forEach(button => {
            button.addEventListener('click', () => {
                const prompt = button.getAttribute('data-prompt');
                input.value = prompt;
                this.sendMessage();
            });
        });
    }

    /**
     * Send a message to the AI
     */
    async sendMessage() {
        const input = document.getElementById('sales-ai-input');
        const message = input.value.trim();

        if (!message || this.isProcessing) return;

        this.isProcessing = true;
        input.value = '';
        input.disabled = true;

        // Add user message to UI
        this.addMessage('user', message);

        try {
            // Show typing indicator
            this.showTypingIndicator();

            // Call API (or use mock response for now)
            const response = await this.queryAI(message);

            // Remove typing indicator
            this.hideTypingIndicator();

            // Add AI response to UI
            this.addMessage('ai', response);

        } catch (error) {
            console.error('Sales AI Error:', error);
            this.hideTypingIndicator();
            this.addMessage('ai', '❌ Sorry, I encountered an error. Please try again or contact support if the issue persists.');
        } finally {
            this.isProcessing = false;
            input.disabled = false;
            input.focus();
        }
    }

    /**
     * Query the AI backend
     */
    async queryAI(question) {
        // TODO: Replace with actual API call to backend
        // For now, return mock responses based on keywords

        const lowerQuestion = question.toLowerCase();

        // Discovery questions
        if (lowerQuestion.includes('discovery') ||
            lowerQuestion.includes('qualification') ||
            lowerQuestion.includes('what questions') ||
            lowerQuestion.includes('ask in') ||
            lowerQuestion.includes('bant')) {
            return this.getMockResponse('discovery');
        }

        // Pricing objections
        else if ((lowerQuestion.includes('pricing') || lowerQuestion.includes('price') || lowerQuestion.includes('expensive') || lowerQuestion.includes('cost')) &&
                 (lowerQuestion.includes('objection') || lowerQuestion.includes('handle') || lowerQuestion.includes('respond'))) {
            return this.getMockResponse('pricing');
        }

        // Service tiers
        else if (lowerQuestion.includes('tier') ||
                 lowerQuestion.includes('it360') ||
                 lowerQuestion.includes('it assist') ||
                 lowerQuestion.includes('it essentials') ||
                 lowerQuestion.includes('difference between') ||
                 lowerQuestion.includes('compare') ||
                 lowerQuestion.includes('which service')) {
            return this.getMockResponse('tiers');
        }

        // General objections
        else if (lowerQuestion.includes('objection') ||
                 lowerQuestion.includes('think about it') ||
                 lowerQuestion.includes('too small') ||
                 lowerQuestion.includes('internal it') ||
                 lowerQuestion.includes('laer')) {
            return this.getMockResponse('objections');
        }

        // Default response
        else {
            return this.getMockResponse('general');
        }

        // Real implementation would be:
        /*
        const response = await fetch(this.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                conversation_history: this.conversationHistory
            })
        });

        const data = await response.json();
        return data.answer;
        */
    }

    /**
     * Mock responses (until backend is connected)
     * These responses are based on the knowledge base in /knowledge-base/sales/general/
     */
    getMockResponse(type) {
        const responses = {
            'discovery': `**Key Discovery Questions (From 37-Question Framework):**

**Opening (5 min):**
- "Tell me about your role and how IT impacts your day-to-day"
- "What prompted you to reach out to us / explore managed services?"
- "What's working well with your current IT setup?"

**Current State (15 min):**
- "How many employees do you have? How many locations?"
- "Do you have on-premise servers? What do they do?"
- "Who manages your IT currently?"

**Pain Points (Critical!):**
- "What are your top 3 IT frustrations right now?"
- "How often do IT issues impact business operations?"
- "Are you confident in your cybersecurity posture?"
- "Have you ever had a security incident?"

**Compliance:**
- "Do you have any compliance requirements?" (HIPAA, PCI-DSS, CMMC)
- "Do you have cyber insurance? What do they require?"

**Budget Discovery:**
- "What are you currently spending on IT per month?"
- "What's an hour of downtime worth to your business?"

**Decision Process:**
- "Who else needs to be involved in this decision?"
- "What's your timeline for making a change?"
- "What would need to happen for this to be a clear yes?"

**💡 Pro tip:** Use BANT qualification - Budget, Authority, Need, Timeline

📚 *Source: knowledge-base/sales/general/discovery-questions.md*`,

            'pricing': `**Handling Pricing Objections (LAER Framework):**

**Common objection:** "You're more expensive than [competitor]"

**L - Listen:** Let them explain the price difference

**A - Acknowledge:** "I appreciate you being upfront about the numbers."

**E - Explore:**
- "What's included in their quote? 24/7 monitoring or business hours?"
- "What security tools are included?"
- "What are their response time SLAs?"

**R - Respond:**

**Compare apples to apples:**
"Our pricing includes 24/7 monitoring, advanced security (EDR, MFA, email security), unlimited help desk, proactive patch management, and quarterly business reviews. Many competitors charge extra for these."

**Total Cost of Ownership:**
"What's an hour of downtime worth to your business? Our clients see 60% reduction in IT incidents. If you're experiencing 5 incidents/month at 2 hours each, that's 6 hours saved monthly. At $2K/hour, that's $12K saved."

**Case study approach:**
"I had a client in [industry] who switched from [competitor] who was $20/user cheaper. Within 3 months, they saved $5,000/month in reduced downtime. Net savings: $3,500/month after our higher fee."

**Bottom line:** "The question isn't 'What's the monthly fee?' but 'What's the total cost including downtime, security risks, and productivity loss?'"

📚 *Source: knowledge-base/sales/general/objection-handling.md*`,

            'tiers': `**Service Tier Comparison:**

**IT Essentials - $75/user/month**
- Help desk (business hours M-F 8am-5pm)
- Basic network monitoring
- Patch management
- Antivirus protection
- Monthly reporting
- **Best for:** 5-25 employees, low compliance, cost-conscious

**IT Assist - $115/user/month** ⭐ MOST POPULAR
- Everything in IT Essentials, PLUS:
- **24/7 network monitoring** (alerts to NOC)
- After-hours emergency support
- Advanced security (EDR, MFA, email security, web filtering)
- Cyber insurance support documentation
- Priority response (30 min critical, 2 hours high)
- Quarterly business reviews
- **Best for:** 25-100 employees, moderate compliance

**IT360 - $165/user/month**
- Everything in IT Assist, PLUS:
- **Full compliance:** HIPAA, CMMC, PCI-DSS, SOC 2
- **Dedicated vCIO** (Virtual CIO)
- Strategic IT planning & 3-year roadmap
- Executive-level reporting
- Annual security assessments
- **Best for:** 100+ employees, regulated industries

**Positioning Tips:**
- **IT Essentials:** "Solid fundamentals without bells and whistles"
- **IT Assist:** "The sweet spot - 24/7 security without enterprise pricing" (This is our Goldilocks tier)
- **IT360:** "For regulated industries, compliance alone would cost more than the tier upgrade"

**Common Add-Ons:**
- Security Awareness Training: $5/user/month
- Dark Web Monitoring: $10/user/month
- Enhanced Backup (Datto BCDR): $150+/server/month
- DaaS (Device as a Service): $55-75/device/month

📚 *Source: knowledge-base/sales/general/service-tiers.md*`,

            'objections': `**Common Objections & Responses:**

**"We need to think about it"**
→ "What specifically? Is it pricing, service tier, or something else?"
→ Surface the real objection, then address it

**"We have an internal IT person"**
→ "We're not looking to replace them - we support them. They become strategic while we handle monitoring, after-hours, and specialized expertise (security, compliance, cloud)."

**"We're too small for managed services"**
→ "Actually, small businesses benefit MORE. Large companies can absorb downtime and afford in-house teams. One security incident can put a small business out of business. Our IT Essentials tier was designed specifically for 5-25 employees."

**"We're moving to the cloud - do we still need you?"**
→ "The cloud makes IT support MORE important. Who manages Office 365 accounts? Who configures Azure security? Who handles user support when email doesn't work? The cloud is a tool, but you need someone who knows how to use it."

**"What if we're not happy?"**
→ "30-day onboarding with weekly check-ins. Quarterly business reviews. [X] day termination notice if we're not meeting expectations. Our average client relationship is [X] years with [Y%] retention rate."

**💡 Always use LAER:** Listen, Acknowledge, Explore, Respond

📚 *Source: knowledge-base/sales/general/objection-handling.md*`,

            'general': `**👋 Welcome to Sales AI!**

I have access to TotalCareIT's sales knowledge base with:

**📚 Available Knowledge:**
- **Service Tiers** - IT Essentials ($75), IT Assist ($115), IT360 ($165) with positioning
- **Discovery Questions** - 37-question framework organized by topic (BANT qualification)
- **Objection Handling** - LAER framework for pricing, competitor, trust, timing objections

**💬 Try asking:**
- "What questions should I ask in a discovery call?"
- "How do we handle pricing objections?"
- "What's included in IT Assist vs IT360?"
- "How do I respond to 'you're too expensive'?"
- "What are red flags in qualification?"
- "How do we position against competitors?"

**🎯 Quick Actions Below:**
Use the buttons below for common questions, or type your own!

📂 *Knowledge Base: /knowledge-base/sales/general/*`
        };

        return responses[type] || responses['general'];
    }

    /**
     * Add message to chat UI
     */
    addMessage(sender, content) {
        const messagesContainer = document.getElementById('sales-ai-messages');
        const isUser = sender === 'user';

        const messageHTML = `
            <div class="${isUser ? 'user-message' : 'ai-message'}">
                ${!isUser ? '<div class="message-avatar">🤖</div>' : ''}
                <div class="message-content">
                    ${this.formatMessage(content)}
                </div>
            </div>
        `;

        messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Add to conversation history
        this.conversationHistory.push({
            role: sender,
            content: content
        });
    }

    /**
     * Format message content (support markdown-like formatting)
     */
    formatMessage(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>')
            .replace(/- (.*?)(<br>|$)/g, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)+/g, '<ul>$&</ul>');
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        const messagesContainer = document.getElementById('sales-ai-messages');
        const typingHTML = `
            <div id="typing-indicator" class="ai-message">
                <div class="message-avatar">🤖</div>
                <div class="message-content typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        messagesContainer.insertAdjacentHTML('beforeend', typingHTML);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }
}

// Initialize Sales AI when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.salesAI = new SalesAI();
        window.salesAI.init();
    });
} else {
    window.salesAI = new SalesAI();
    window.salesAI.init();
}
