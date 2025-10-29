# TotalCareIT Sales AI Knowledge Base

This directory contains all training data for the Sales AI assistant in the partner portal.

## Directory Structure

### `/sales/general/` ✅ POPULATED
**Purpose:** Core sales content and frameworks

**Current files:**
- `service-tiers.md` - Complete breakdown of IT Essentials, IT Assist, and IT360 with pricing, positioning, objection handling, and qualification criteria
- `discovery-questions.md` - Comprehensive 37-question discovery framework with BANT qualification, red flags, and example conversation flows
- `objection-handling.md` - LAER framework with responses for pricing, competitor, trust, timing, authority, and technical objections

### `/sales/transcripts/`
**Purpose:** Store call recordings transcripts for AI training

**How to add transcripts:**
1. Export transcripts from your call recording system (HubSpot, Zoom, etc.)
2. Save as `.txt` or `.md` files
3. Name format: `YYYY-MM-DD-client-name-call-type.txt`
4. Example: `2024-10-24-acme-corp-discovery-call.txt`

**Categories:**
- `discovery-calls/` - Initial prospect conversations
- `objection-handling/` - Overcoming client concerns

**Supported formats:**
- Plain text (.txt)
- Markdown (.md)
- PDF (.pdf) - will be converted to text
- DOCX (.docx) - will be converted to text

### `/sales/playbooks/`
**Purpose:** Sales methodology and best practices

Files to create:
- `discovery-questions.md` - Questions to ask prospects
- `pricing-conversations.md` - How to discuss pricing
- `closing-strategies.md` - Techniques for closing deals
- `objection-responses.md` - How to handle common objections
- `qualification-criteria.md` - BANT/MEDDIC framework

### `/sales/case-studies/`
**Purpose:** Success stories and client examples

Format:
```markdown
# Client Name - Industry

**Challenge:** What problem did they have?
**Solution:** What did we provide?
**Results:** Measurable outcomes
**Cost:** Transparent pricing (before/after)
```

### `/products/`
**Purpose:** Product knowledge and technical details

Files:
- `managed-services.md` - IT Essentials, IT Assist, IT360 details
- `mssp.md` - Security and compliance offerings
- `daas.md` - Device as a Service details
- `pricing.md` - Complete pricing guide

### `/competitor-intel/`
**Purpose:** Competitive landscape information

Files to create:
- Competitor comparisons
- Our differentiators
- Battle cards

## AI Training Process

The Sales AI will:
1. **Ingest** all files in this directory
2. **Vectorize** content using embeddings
3. **Index** for semantic search
4. **Answer** questions based on this knowledge

## Best Practices

### For Transcripts:
✅ DO:
- Include full conversation context
- Note speaker roles (Rep: / Prospect:)
- Include outcomes and next steps
- Add metadata (date, client, stage)

❌ DON'T:
- Include personal information (redact if needed)
- Include competitor client names
- Include confidential information

### For Playbooks:
✅ DO:
- Use clear, structured format
- Include examples and scripts
- Update regularly based on learnings
- Tag content by topic

### Privacy Considerations:
- Redact sensitive client information
- Remove SSNs, credit cards, etc.
- Anonymize small clients if needed
- Follow data retention policies

## File Naming Convention

```
[DATE]-[CLIENT/TOPIC]-[TYPE]-[STAGE].md

Examples:
- 2024-10-24-acme-corp-discovery-call.txt
- pricing-playbook-2024.md
- healthcare-compliance-case-study.md
```

## Integration with Sales AI

The AI assistant will be available in:
- Partner Portal > Sales Report page
- Accessible via chat interface
- Can answer questions like:
  - "What objections do we typically face about pricing?"
  - "Show me a similar case study for healthcare"
  - "What questions should I ask in discovery?"
  - "How do we position against [competitor]?"

## Getting Started

1. **Add your first transcript:**
   ```bash
   # Copy a call transcript
   cp ~/Downloads/sales-call.txt knowledge-base/sales/transcripts/discovery-calls/
   ```

2. **Create pricing playbook:**
   ```bash
   # Document your pricing approach
   nano knowledge-base/sales/playbooks/pricing-conversations.md
   ```

3. **Train the AI:**
   ```bash
   # Run the training script (will be created)
   python scripts/train_sales_ai.py
   ```

## Technical Details

**AI Model:** Claude 3.5 Sonnet (Anthropic)
**Vector Database:** ChromaDB or Pinecone
**Embedding Model:** text-embedding-3-large (OpenAI) or voyage-2 (Voyage AI)
**Context Window:** 200k tokens (entire knowledge base fits in context)

## Maintenance

- **Weekly:** Add new successful call transcripts
- **Monthly:** Review and update playbooks
- **Quarterly:** Audit for outdated information
- **Annually:** Complete knowledge base refresh
