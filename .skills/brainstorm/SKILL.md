---
name: brainstorm
description: Generate several genuinely different approaches to a research problem, each with what would confirm and refute it. Use when the user asks for options, ideas, or "how could we do this", or before committing to an experiment design.
---

# Brainstorm

Produce an option space, not a recommendation.

## Steps

1. **Read the ground first** — `research/knowledge/` (what exists, what the constraints are)
   and `research/knowledge/open-questions.md`. An option that ignores a known constraint wastes
   the reader's time.
2. **Generate 3–5 genuinely different approaches.** Different means they fail for different
   reasons. Include at least one that is cheap enough to run this week, and one that would
   falsify the current direction.
3. For each, write: the claim, the assumption it rests on, `would_confirm`, `would_refute`,
   and a rough cost (hours / days / weeks).
4. **Write each to `research/ideas/IDEA-NNNN.md`** using
   `orchestration/schemas/idea.schema.yaml`.
5. Report the options side by side, with their distinguishing assumption highlighted.

## Rules

- Do not rank or recommend. Selection happens in triage, with the critic and PI reviewer.
- Do not propose anything requiring source-data modification or a GPU — neither is available
  (`research/knowledge/constraints.md`).
- Three variants of one idea is one idea. Say so rather than padding.
- An idea that cannot fail is not an idea; it does not get a file.
