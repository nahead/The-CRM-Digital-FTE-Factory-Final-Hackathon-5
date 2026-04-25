# Escalation Rules for Customer Success AI Agent

## When to Escalate to Human Support

### 🔴 IMMEDIATE ESCALATION (High Priority)

#### 1. Legal & Compliance Issues
- Customer mentions: "lawyer", "legal", "sue", "attorney", "court"
- GDPR, data privacy, or compliance questions
- Security audit requests
- Contract disputes
**Action:** Escalate to Legal Team immediately

#### 2. Angry/Frustrated Customers
- Profanity or aggressive language detected
- ALL CAPS messages with negative sentiment
- Threats to cancel or leave negative reviews
- Multiple failed attempts to resolve issue
- Sentiment score < 0.3
**Action:** Escalate to Senior Support with full context

#### 3. Refund Requests
- Any mention of refund, chargeback, or money back
- Billing disputes
**Action:** Escalate to Billing Team

#### 4. Security Incidents
- Account compromise suspected
- Unauthorized access reports
- Data breach concerns
**Action:** Escalate to Security Team immediately

### 🟡 STANDARD ESCALATION (Medium Priority)

#### 5. Pricing & Sales Inquiries
- Enterprise plan pricing questions
- Custom pricing requests
- Volume discount inquiries
- Contract negotiations
**Action:** Escalate to Sales Team

#### 6. Technical Issues Beyond AI Capability
- SSO/SAML setup assistance
- Custom API integration support
- Database migration help
- Performance issues requiring investigation
**Action:** Escalate to Technical Support Team

#### 7. Feature Requests & Product Feedback
- Detailed feature requests
- Product roadmap questions
- Beta program inquiries
**Action:** Log in feedback system, escalate to Product Team if urgent

#### 8. Account Management
- Workspace ownership transfer
- Account deletion requests
- Bulk user management (>50 users)
**Action:** Escalate to Account Management

### 🟢 CONDITIONAL ESCALATION (Low Priority)

#### 9. Cannot Find Answer After 2 Attempts
- AI searched knowledge base twice
- No relevant documentation found
- Customer still confused after explanation
**Action:** Escalate with note: "Knowledge gap identified"

#### 10. Customer Explicitly Requests Human
- "I want to talk to a human"
- "Connect me with an agent"
- "This bot isn't helping"
- WhatsApp: customer sends "human", "agent", or "representative"
**Action:** Escalate politely with apology

#### 11. Complex Multi-Issue Problems
- Customer has 3+ unrelated issues
- Issue spans multiple product areas
- Requires coordination between teams
**Action:** Escalate to Support Coordinator

### ❌ DO NOT ESCALATE

#### Handle These Autonomously:
- Password resets
- Basic how-to questions (covered in docs)
- Feature explanations
- Navigation help
- General product questions
- Positive feedback/thank you messages
- Status updates on known issues
- API documentation questions
- Mobile app basic troubleshooting

## Escalation Process

### Step 1: Gather Context
Before escalating, ensure you have:
- Customer ID and email
- Full conversation history (all channels)
- Issue category and priority
- Steps already attempted
- Relevant error messages or screenshots
- Customer sentiment score

### Step 2: Create Escalation Ticket
```json
{
  "ticket_id": "uuid",
  "customer_id": "uuid",
  "escalation_reason": "specific reason",
  "priority": "low|medium|high|urgent",
  "category": "legal|billing|technical|sales",
  "conversation_history": [...],
  "attempted_solutions": [...],
  "customer_sentiment": 0.0-1.0,
  "escalated_at": "timestamp",
  "escalated_to": "team_name"
}
```

### Step 3: Notify Customer
**Email/Web Form:**
```
Thank you for contacting TechCorp Support. I've escalated your request to our [TEAM] team who will be better equipped to assist you with [ISSUE]. 

You can expect a response within [TIMEFRAME]:
- Standard: 24 hours
- High Priority: 4 hours
- Urgent: 1 hour

Your ticket reference: [TICKET_ID]

Best regards,
TechCorp AI Support
```

**WhatsApp:**
```
I've connected you with our support team. They'll respond within [TIMEFRAME]. 

Ticket: [TICKET_ID]

Reply here for updates! 📱
```

## Escalation Metrics to Track

- **Escalation Rate:** Target < 20% of all conversations
- **False Escalations:** Should be < 5%
- **Escalation Resolution Time:** Track by priority
- **Customer Satisfaction Post-Escalation:** Target > 4.0/5.0

## Special Cases

### After-Hours Escalation
- Mon-Fri 6 PM - 9 AM EST: Set expectation for next business day
- Weekends: Set expectation for Monday
- Enterprise customers: Page on-call support for urgent issues

### Repeat Escalations
- If same customer escalated 3+ times in 7 days: Flag for account review
- May indicate product issue or training need

### VIP Customers
- Enterprise plan customers: Faster escalation, dedicated support
- Check customer metadata for VIP flag

## Continuous Improvement

### Learn from Escalations
- Review escalated tickets weekly
- Identify knowledge gaps
- Update documentation
- Improve AI responses
- Add new training examples

### Feedback Loop
- When escalation is resolved, update knowledge base
- Add resolution to training data
- Improve detection of similar issues
