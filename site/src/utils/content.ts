import { getCollection } from "astro:content";

export async function loadCollections() {
  const [
    weeks,
    papers,
    questions,
    hypotheses,
    experiments,
    runs,
    results,
    decisions,
    glossary
  ] = await Promise.all([
    getCollection("weeks"),
    getCollection("papers"),
    getCollection("questions"),
    getCollection("hypotheses"),
    getCollection("experiments"),
    getCollection("runs"),
    getCollection("results"),
    getCollection("decisions"),
    getCollection("glossary")
  ]);

  return { weeks, papers, questions, hypotheses, experiments, runs, results, decisions, glossary };
}

export function entryHref(collection: string, slug: string) {
  switch (collection) {
    case "weeks":
      return `/research-notes/weeks/${slug}/`;
    case "papers":
      return `/research-notes/papers/${slug}/`;
    case "questions":
      return `/research-notes/questions/${slug}/`;
    case "hypotheses":
      return `/research-notes/hypotheses/${slug}/`;
    case "experiments":
      return `/research-notes/experiments/${slug}/`;
    case "runs":
      return `/research-notes/runs/${slug}/`;
    case "results":
      return `/research-notes/results/${slug}/`;
    case "decisions":
      return `/research-notes/decisions/${slug}/`;
    case "glossary":
      return `/research-notes/glossary/${slug}/`;
    default:
      return "/research-notes/";
  }
}
