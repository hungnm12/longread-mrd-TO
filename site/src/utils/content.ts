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
      return `/weeks/${slug}/`;
    case "papers":
      return `/papers/${slug}/`;
    case "questions":
      return `/questions/${slug}/`;
    case "hypotheses":
      return `/hypotheses/${slug}/`;
    case "experiments":
      return `/experiments/${slug}/`;
    case "runs":
      return `/runs/${slug}/`;
    case "results":
      return `/results/${slug}/`;
    case "decisions":
      return `/decisions/${slug}/`;
    case "glossary":
      return `/glossary/${slug}/`;
    default:
      return "/";
  }
}
