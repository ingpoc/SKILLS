---
name: llm-council
description: "Run high-stakes questions, ideas, and decisions through a council of 5 AI advisors who analyze independently, peer-review each other anonymously, and synthesize a final verdict with artifacts. Mandatory triggers: 'council this', 'run the council', 'war room this', 'pressure-test this', 'stress-test this', 'debate this'. Strong triggers when paired with a real decision or tradeoff: 'should I X or Y', 'which option', 'what would you do', 'is this the right move', 'validate this', 'get multiple perspectives', 'I can't decide', 'I'm torn between'. Do not use for factual lookups, simple yes/no questions, summarization, or low-stakes choices."
---

# LLM Council

Run a structured multi-agent council for decisions where being wrong is expensive. Use five distinct thinking styles, force anonymous peer review, then synthesize a clear verdict and save two artifacts:

- `council-report-[timestamp].html`
- `council-transcript-[timestamp].md`

## Gate the Request

Run the council only when the user presents genuine uncertainty, multiple options, meaningful tradeoffs, or real downside risk.

Use ordinary reasoning instead of the council for:

- factual questions with one correct answer
- low-stakes preference calls
- simple creation tasks like "write me a tweet"
- pure summarization or extraction tasks

If the request is vague enough that the council would debate the wrong thing, ask exactly one clarifying question, then proceed.

If the user explicitly invoked the council or asked for multiple independent perspectives, spawning sub-agents is the intended execution path for this skill.

## Frame the Question

Before convening advisors, enrich the prompt with fast local context. Spend at most 30 seconds.

Scan for:

- `CLAUDE.md` or `claude.md` near the active workspace root
- `memory/` folders or business-context docs
- files the user explicitly referenced or attached
- recent `council-transcript-*.md` files to avoid repeating the same ground
- nearby docs directly relevant to the decision, such as pricing notes, launch results, audience research, or product specs

Prefer quick file discovery and selective reads. Load only the 2-3 files that materially sharpen the council.

Then write a neutral framed question that includes:

1. the core decision
2. key user context
3. key workspace context
4. what is at stake

Save both the original question and the framed question for the transcript.

## Convene the Five Advisors

Spawn all five advisors in parallel. Do not run them sequentially.

Use these fixed thinking styles:

| Advisor | Role |
| --- | --- |
| The Contrarian | Hunt for fatal flaws, hidden risks, and avoided questions. |
| The First Principles Thinker | Strip away assumptions and rebuild the problem from first principles. |
| The Expansionist | Look for upside, asymmetry, and larger adjacent opportunity. |
| The Outsider | React with fresh eyes and no insider context or jargon tolerance. |
| The Executor | Focus on feasibility, sequencing, and what happens Monday morning. |

Instruct each advisor to lean hard into its angle rather than being balanced. Target 150-300 words per response.

Use this prompt template:

```text
You are [Advisor Name] on an LLM Council.

Your thinking style: [advisor description]

A user has brought this question to the council:

---
[framed question]
---

Respond from your perspective. Be direct and specific. Do not hedge or try to be balanced. Lean fully into your assigned angle. The other advisors will cover the angles you are not covering.

Keep your response between 150-300 words. No preamble. Go straight into your analysis.
```

Capture for each advisor:

- `name`
- `response`
- `stance`

Make `stance` a single sentence summarizing that advisor's bottom-line position. The renderer uses it for the alignment view.

## Run Anonymous Peer Review

Collect the five advisor outputs, randomize their order, and label them `Response A` through `Response E`. Record the mapping for the transcript, but do not expose it during review.

Spawn five fresh review sub-agents in parallel. Give each reviewer the same anonymized set and ask the same three questions:

1. Which response is the strongest and why?
2. Which response has the biggest blind spot and what is it?
3. What did all five responses miss that the council should consider?

Keep each review under 200 words.

Use this prompt template:

```text
You are reviewing the outputs of an LLM Council. Five advisors independently answered this question:

---
[framed question]
---

Here are their anonymized responses:

**Response A:**
[response]

**Response B:**
[response]

**Response C:**
[response]

**Response D:**
[response]

**Response E:**
[response]

Answer these three questions. Be specific. Reference responses by letter.

1. Which response is the strongest? Why?
2. Which response has the biggest blind spot? What is it missing?
3. What did ALL five responses miss that the council should consider?

Keep your review under 200 words. Be direct.
```

## Synthesize the Chairman Verdict

After peer review, run one final synthesis pass with the original question, the framed question, all named advisor responses, and all peer reviews.

Use this prompt template:

```text
You are the Chairman of an LLM Council. Your job is to synthesize the work of 5 advisors and their peer reviews into a final verdict.

The question brought to the council:

---
[framed question]
---

ADVISOR RESPONSES:

**The Contrarian:**
[response]

**The First Principles Thinker:**
[response]

**The Expansionist:**
[response]

**The Outsider:**
[response]

**The Executor:**
[response]

PEER REVIEWS:

[all peer reviews]

Produce the council verdict using this exact structure:

## Where the Council Agrees
[Points multiple advisors converged on independently. These are high-confidence signals.]

## Where the Council Clashes
[Genuine disagreements. Present both sides. Explain why reasonable advisors disagree.]

## Blind Spots the Council Caught
[Things that only emerged through peer review. Things individual advisors missed that others flagged.]

## The Recommendation
[A clear, direct recommendation. Not "it depends." A real answer with reasoning.]

## The One Thing to Do First
[A single concrete next step. Not a list. One thing.]

Be direct. Do not hedge. The whole point of the council is to give the user clarity they could not get from a single perspective.
```

The chairman may disagree with the majority if the reasoning is stronger.

## Generate the Artifacts

Always create both artifacts after the synthesis is complete.

1. Build a JSON payload with this shape:

```json
{
  "question": "Original user question",
  "framed_question": "Neutral enriched framing",
  "chairman_verdict": {
    "where_agrees": "...",
    "where_clashes": "...",
    "blind_spots": "...",
    "recommendation": "...",
    "first_step": "..."
  },
  "advisors": [
    {
      "name": "The Contrarian",
      "stance": "Bottom-line stance",
      "response": "Full advisor response"
    }
  ],
  "peer_reviews": [
    {
      "reviewer": "Review 1",
      "text": "Full peer review"
    }
  ],
  "anonymization_mapping": {
    "A": "The Executor"
  }
}
```

2. Save the payload to a temporary JSON file.
3. Run the renderer:

```bash
python3 /Users/gurusharan/.codex/skills/llm-council/scripts/render_council_report.py --input /absolute/path/to/payload.json --output-dir /absolute/path/to/output-dir
```

4. Open the generated HTML file immediately after creation.

The renderer writes:

- `council-report-[timestamp].html`
- `council-transcript-[timestamp].md`

Default the output directory to the active workspace unless the user specified another location.

## Return the Result

In the final user-facing response:

- surface the chairman recommendation first
- give the absolute paths to the HTML report and transcript
- mention any important missing context if the council had to proceed with incomplete information

Keep the response short. The report is the scanning surface; the transcript is the full record.

## Non-Negotiable Rules

- Spawn all five advisors in parallel.
- Spawn all five peer reviewers in parallel.
- Anonymize advisor outputs before peer review.
- Do not run the council for trivial questions.
- Do not let advisors see each other's responses before review.
- Do not collapse disagreement into fake consensus.
- Always create both artifacts.
