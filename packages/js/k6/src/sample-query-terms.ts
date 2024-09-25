import { randomItem } from "./jslib-shim"

export const SAMPLE_QUERY_TERMS = [
  "art",
  "outsourced accountant",
  "plane",
  "tree leaf nutrition",
  "games",
  "school clip art",
  "windy day music",
  "French government",
  "Dom Quixote de la Mancha",
  "graphs",
  "Juan López",
]

export const getRandomQueryTerm = () => randomItem(SAMPLE_QUERY_TERMS)
