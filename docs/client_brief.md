# Client Brief — Driftwood Capital

## The Client

**Driftwood Capital** is a fictional independent investment research firm.

Their analysts spend a significant portion of their time reading SEC filings before they can perform meaningful analysis.

The firm's value comes from turning thousands of pages of public company disclosures into concise, actionable research.

Reputation and accuracy are critical. A confidently wrong conclusion is worse than no conclusion at all.

---

# Business Context

Analysts typically cover a focused set of public companies within a sector.

Their workflow often includes:

- Reading annual reports (10-Ks)
- Reviewing quarterly reports (10-Qs)
- Comparing disclosures across years
- Tracking changes in risk factors
- Monitoring segment performance
- Identifying important management commentary

A large percentage of this work involves document intake rather than analysis.

Before an analyst can develop an opinion, they first need to find and review relevant information.

---

# The Problem

Document review is:

- Time consuming
- Repetitive
- Difficult to scale
- Often duplicated across analysts

Many questions require searching through hundreds of pages of filings before analysis can begin.

Examples:

- What changed in a company's risk disclosures?
- How has a business segment evolved?
- What did management say about AI infrastructure over time?
- How did geographic revenue exposure change?

The bottleneck is not analysis.

The bottleneck is finding and verifying information.

---

# The Solution

Build an internal research assistant called:

# Document Copilot

Document Copilot allows analysts to:

- Ask questions in natural language
- Search a curated SEC filing corpus
- Receive grounded answers
- Review citations
- Inspect supporting passages
- Access previous conversations

The goal is not to replace analyst judgment.

The goal is to accelerate document discovery and evidence gathering.

---

# Example Questions

The initial corpus contains SEC filings from:

- Apple
- Amazon
- Alphabet
- Microsoft
- NVIDIA

Example questions:

### Revenue Mix Analysis

How did Apple's revenue mix evolve between 2021 and 2025?

### Segment Comparison

How did AWS profitability compare with Amazon's North America and International businesses?

### AI Infrastructure Trends

How did Microsoft describe Azure, AI infrastructure, and cloud capacity constraints over time?

### Risk Factors

Which companies materially changed AI-related or supply-chain-related risk disclosures?

### Supplier Concentration

How did Apple and NVIDIA describe supplier dependence and manufacturing concentration?

### Capital Investment

What do company filings suggest about AI and cloud infrastructure investment?

### Geographic Exposure

How did regional revenue concentration change over time?

---

# Trust Requirements

Trust is the most important product requirement.

The system must:

## Never Invent Facts

If evidence does not exist in the corpus, the assistant must explicitly say so.

## Always Cite Sources

Every factual claim must be backed by citations.

## Show Supporting Evidence

Users should be able to inspect the exact passages used to generate the answer.

## Refuse Unsupported Conclusions

The system should not infer facts that are not supported by the retrieved documents.

Example:

If a user asks:

> Did generative AI improve margins for Company X?

The assistant should only discuss evidence found in filings.

If filings do not support a conclusion, the assistant must refuse to speculate.

---

# Corpus

Initial corpus:

- SEC 10-K filings
- SEC 10-Q filings
- S&P 500 companies
- Years 2020–2025

Initial demo dataset:

- Apple
- Microsoft
- NVIDIA
- Amazon
- Alphabet

Data source:

- SEC EDGAR

Only public filings are included.

---

# Users

Primary users:

- Research analysts
- Associate analysts
- Research partners

Expected usage:

- Small research teams
- Internal research workflows
- Demonstration and portfolio environments

The system is intentionally designed to run on modest infrastructure.

---

# Technical Constraints

## Authentication

Email-based authentication.

No SSO required.

## Hosting

Deployable on:

- Railway
- Supabase

No dedicated infrastructure team assumed.

## Retrieval

Answers must come from the filing corpus.

No external news sources.

No social media sources.

No alternative data.

## Grounding

Every answer must be traceable back to retrieved evidence.

---

# Out of Scope

The following are explicitly out of scope:

- Stock recommendations
- Trading advice
- Portfolio construction
- News aggregation
- Social media analysis
- Alternative data feeds
- Mobile applications
- Multi-tenant SaaS functionality

---

# Definition of Success

A user can:

1. Log in.
2. Ask a question about SEC filings.
3. Receive a grounded answer.
4. Review citations.
5. Verify supporting passages.
6. Reach conclusions faster than manual document review.

The project succeeds when users can trust answers because they can independently verify the underlying evidence.
