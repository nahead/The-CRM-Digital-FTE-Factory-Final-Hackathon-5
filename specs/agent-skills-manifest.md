# Agent Skills Manifest

## Overview
This document defines the reusable capabilities (skills) that the Customer Success FTE can invoke to handle customer interactions across multiple channels.

---

## Skill 1: Knowledge Retrieval

### Purpose
Search product documentation to answer customer questions accurately.

### When to Use
- Customer asks about product features
- Customer needs how-to guidance
- Customer reports a bug (to find known issues)
- Customer asks for best practices

### Inputs
```python
{
    "query": str,              # Customer's question
    "category": str,           # Optional: technical|billing|general
    "max_results": int = 5     # Maximum documents to return
}
```

### Outputs
```python
{
    "results": [
        {
            "title": str,
            "content": str,
            "category": str,
            "relevance_score": float
        }
    ],
    "total_found": int
}
```

### Implementation
- Uses PostgreSQL full-text search on knowledge_base table
- Optional: pgvector for semantic search
- Filters by category if provided
- Returns top 5 most relevant results
- Caches frequent queries

### Success Criteria
- Response time: <500ms
- Relevance: >85% accuracy on test queries
- Coverage: Finds answer for >90% of in-scope questions

---

## Skill 2: Sentiment Analysis

### Purpose
Detect customer emotion to identify frustrated customers and prevent escalation delays.

### When to Use
- **Every incoming customer message** (mandatory)
- Before closing a conversation
- When deciding escalation

### Inputs
```python
{
    "message": str,           # Customer's message text
    "conversation_history": List[str]  # Optional: last 3 messages for context
}
```

### Outputs
```python
{
    "sentiment_score": float,  # -1.0 (very negative) to +1.0 (very positive)
    "confidence": float,       # 0.0 to 1.0
    "emotion": str,           # angry|frustrated|neutral|satisfied|happy
    "should_escalate": bool   # True if sentiment < 0.3
}
```

### Implementation
- Uses Gemini AI for sentiment analysis
- Considers conversation context (trend)
- Tracks sentiment over time per customer
- Stores in messages table

### Escalation Triggers
- Sentiment score < 0.3 (negative)
- Sentiment declining over 3+ messages
- Keywords: "angry", "frustrated", "terrible", "lawsuit"

### Success Criteria
- Accuracy: >80% on labeled test set
- Response time: <200ms
- False positive rate: <10%

---

## Skill 3: Escalation Decision

### Purpose
Determine when to hand off to a human agent based on complexity, sentiment, and business rules.

### When to Use
- After generating a response (before sending)
- When sentiment is negative
- When customer explicitly requests human
- After 2 failed resolution attempts

### Inputs
```python
{
    "ticket_id": str,
    "conversation_context": dict,
    "sentiment_score": float,
    "category": str,
    "attempt_count": int
}
```

### Outputs
```python
{
    "should_escalate": bool,
    "reason": str,
    "priority": str,          # low|medium|high|urgent
    "suggested_team": str     # billing|technical|management
}
```

### Escalation Rules

**Immediate Escalation:**
- Refund requests
- Legal/compliance questions
- Security incidents
- Angry customers (sentiment < 0.3)
- Account access issues
- Threats or abuse

**Standard Escalation:**
- Pricing negotiations
- Custom feature requests
- Complex technical (after 2 attempts)
- Billing disputes

**Never Escalate:**
- Product questions (in docs)
- How-to guides
- Bug report intake
- General feedback

### Implementation
- Rule-based decision tree
- Sentiment threshold check
- Attempt counter check
- Keyword matching for immediate triggers
- Logs escalation reason

### Success Criteria
- Precision: >90% (correct escalations)
- Recall: >85% (catches issues needing escalation)
- Response time: <100ms

---

## Skill 4: Channel Adaptation

### Purpose
Format responses appropriately for each communication channel (email, WhatsApp, web form).

### When to Use
- **Before sending any response** (mandatory)
- When customer switches channels mid-conversation

### Inputs
```python
{
    "message": str,           # Raw response text
    "channel": str,           # email|whatsapp|web_form
    "customer_name": str,
    "ticket_id": str
}
```

### Outputs
```python
{
    "formatted_message": str,
    "metadata": {
        "length": int,
        "tone": str,
        "includes_greeting": bool,
        "includes_signature": bool
    }
}
```

### Channel-Specific Rules

**Email:**
```
Format:
Hi [Name],

[Detailed response with paragraphs]

[Additional resources if applicable]

Best regards,
TechCorp Support Team
Ticket ID: [ID]

Constraints:
- Max 500 words
- Formal tone
- Include greeting and signature
- Can use bullet points
- Include links
```

**WhatsApp:**
```
Format:
Hi [Name]! [Concise answer in 1-2 sentences]

Need more help? Just ask!

Constraints:
- Max 300 characters (preferred)
- Conversational tone
- No formal signature
- Break long answers into multiple messages
- Use emojis sparingly
```

**Web Form:**
```
Format:
Thank you for your inquiry about [topic].

[Balanced answer with key points]

Your ticket ID: [ID]
We'll follow up via email if needed.

Constraints:
- Max 300 words
- Semi-formal tone
- Include ticket ID
- Mention follow-up method
```

### Implementation
- Template-based formatting
- Length checking and truncation
- Tone adjustment based on channel
- Automatic greeting/signature insertion

### Success Criteria
- All responses within length limits
- Tone appropriate for channel
- 100% include required elements (greeting, ticket ID)

---

## Skill 5: Customer Identification

### Purpose
Link messages from different channels to the same customer for unified history.

### When to Use
- **On every incoming message** (mandatory)
- When creating a new ticket
- When retrieving customer history

### Inputs
```python
{
    "identifier": str,        # Email or phone number
    "identifier_type": str,   # email|phone
    "message_metadata": dict  # Additional context
}
```

### Outputs
```python
{
    "customer_id": str,       # UUID
    "is_new_customer": bool,
    "linked_identifiers": List[str],  # All known identifiers
    "conversation_history": List[dict],  # Past interactions
    "total_tickets": int
}
```

### Identification Logic

**Primary Identifier:** Email address
**Secondary Identifier:** Phone number

**Matching Rules:**
1. Exact email match → Return existing customer
2. Exact phone match → Return existing customer
3. No match → Create new customer
4. Multiple matches → Merge customers (manual review)

**Cross-Channel Linking:**
- Customer emails from Gmail: customer@example.com
- Same customer messages from WhatsApp: +1234567890
- System links phone to email in customer_identifiers table
- Future messages from either channel show unified history

### Implementation
- Query customer_identifiers table
- Normalize email (lowercase, trim)
- Normalize phone (remove formatting)
- Cache frequent lookups
- Log all identification attempts

### Success Criteria
- Accuracy: >95% correct identification
- Response time: <50ms (with caching)
- Zero duplicate customers for same person

---

## Skill 6: Conversation Context Management

### Purpose
Maintain conversation state and context across multiple messages and channels.

### When to Use
- When customer sends follow-up message
- When retrieving conversation history
- When customer switches channels

### Inputs
```python
{
    "customer_id": str,
    "current_message": str,
    "channel": str
}
```

### Outputs
```python
{
    "conversation_id": str,
    "context_summary": str,    # Summary of conversation so far
    "last_messages": List[dict],  # Last 5 messages
    "topics_discussed": List[str],
    "resolution_status": str,  # open|pending|resolved
    "channel_history": List[str]  # Channels used in this conversation
}
```

### Context Window
- Keep last 5 messages in active context
- Summarize older messages
- Track key facts:
  - Customer name
  - Issue type
  - Resolution attempts
  - Sentiment trend
  - Channel switches

### Implementation
- Store in conversations and messages tables
- Generate summary using AI when context > 5 messages
- Track channel switches
- Maintain conversation state

### Success Criteria
- Context retrieval: <100ms
- Accurate summaries: >90%
- No context loss on channel switch

---

## Skill 7: Ticket Management

### Purpose
Create, update, and track support tickets throughout their lifecycle.

### When to Use
- **On every customer interaction** (mandatory)
- When updating ticket status
- When closing resolved tickets

### Inputs
```python
{
    "customer_id": str,
    "subject": str,
    "category": str,
    "priority": str,
    "channel": str,
    "initial_message": str
}
```

### Outputs
```python
{
    "ticket_id": str,
    "status": str,
    "created_at": str,
    "estimated_resolution": str
}
```

### Ticket Lifecycle

```
Open → Pending → Resolved → Closed
  ↓
Escalated → Human Agent
```

**Status Definitions:**
- **Open:** New ticket, agent responding
- **Pending:** Waiting for customer reply
- **Resolved:** Issue solved, awaiting confirmation
- **Escalated:** Handed to human agent
- **Closed:** Completed and archived

### Implementation
- Create ticket in PostgreSQL
- Link to conversation
- Track status changes
- Store channel metadata
- Generate ticket ID (UUID)

### Success Criteria
- 100% of interactions have tickets
- Ticket creation: <50ms
- No lost tickets

---

## Skill 8: Response Generation

### Purpose
Generate helpful, accurate responses to customer questions using product knowledge.

### When to Use
- After understanding customer question
- After retrieving relevant documentation
- Before channel adaptation

### Inputs
```python
{
    "customer_question": str,
    "knowledge_base_results": List[dict],
    "conversation_context": dict,
    "customer_name": str
}
```

### Outputs
```python
{
    "response": str,
    "confidence": float,
    "sources_used": List[str],
    "requires_escalation": bool
}
```

### Response Guidelines

**Structure:**
1. Acknowledge the question
2. Provide clear answer
3. Include relevant details
4. Offer additional help

**Tone:**
- Professional but friendly
- Clear and concise
- Avoid jargon (or explain it)
- Positive and helpful

**Content:**
- Based on documentation only
- No speculation
- No promises about future features
- No competitor comparisons

### Implementation
- Use Gemini AI with system prompt
- Include knowledge base context
- Apply guardrails
- Validate response before sending

### Success Criteria
- Accuracy: >85% on test set
- Response time: <2s
- Customer satisfaction: >4.0/5.0

---

## Skill Orchestration

### Typical Workflow

```
1. Incoming Message
   ↓
2. Customer Identification (Skill 5)
   ↓
3. Sentiment Analysis (Skill 2)
   ↓
4. Conversation Context (Skill 6)
   ↓
5. Knowledge Retrieval (Skill 1)
   ↓
6. Response Generation (Skill 8)
   ↓
7. Escalation Decision (Skill 3)
   ↓
   If escalate → Hand to human
   If continue ↓
8. Channel Adaptation (Skill 4)
   ↓
9. Ticket Management (Skill 7)
   ↓
10. Send Response
```

### Skill Dependencies

```
Customer Identification → All other skills
Sentiment Analysis → Escalation Decision
Knowledge Retrieval → Response Generation
Response Generation → Channel Adaptation
Channel Adaptation → Ticket Management
```

---

## Testing Each Skill

### Unit Tests
- Test each skill in isolation
- Mock dependencies
- Verify inputs/outputs
- Check error handling

### Integration Tests
- Test skill combinations
- Verify data flow
- Check state management
- Test error propagation

### Performance Tests
- Measure response time per skill
- Test under load
- Verify caching
- Check resource usage

---

## Monitoring & Metrics

### Per-Skill Metrics

**Knowledge Retrieval:**
- Query count
- Average response time
- Cache hit rate
- Results found rate

**Sentiment Analysis:**
- Analysis count
- Average sentiment score
- Escalation trigger rate
- Accuracy (sampled)

**Escalation Decision:**
- Escalation rate
- Precision/recall
- Average decision time
- False positive rate

**Channel Adaptation:**
- Messages formatted per channel
- Length violations
- Format errors
- Average adaptation time

**Customer Identification:**
- Identification rate
- New vs returning customers
- Cross-channel links created
- Identification errors

---

## Version History

- **v1.0** - Initial skill definitions
  - 8 core skills defined
  - Multi-channel support
  - Performance requirements
  - Testing strategy
