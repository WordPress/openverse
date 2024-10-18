import { check } from "k6"

import { http } from "../http.js"
import {
  getRandomQueryTerm,
  SAMPLE_QUERY_TERMS,
} from "../sample-query-terms.js"

import { FRONTEND_URL, PROJECT_ID } from "./constants.js"

import type { Options, Scenario } from "k6/options"

const STATIC_PAGES = ["about", "sources", "privacy", "sensitive-content"]
const TEST_LOCALES = ["en", "ru", "es", "ar"]
const TEST_PARAMS = "license=by&extension=jpg,mp3&source=flickr,jamendo"

const localePrefix = (locale: string) => {
  return locale === "en" ? "" : locale + "/"
}

const parseEnvLocales = (locales: string) => {
  return locales ? locales.split(",") : ["en"]
}

export function visitStaticPages() {
  const locales = parseEnvLocales(__ENV.LOCALES)
  const ovGroup = `visit static pages for locales ${locales}`

  for (const locale of locales) {
    for (const page of STATIC_PAGES) {
      const url = new URL(`${localePrefix(locale)}${page}`, FRONTEND_URL)
      const response = http.get(url.toString(), { tags: { ovGroup } })
      const result = check(
        response,
        { "status was 200": (r) => r.status === 200 },
        { ovGroup }
      )

      if (!result) {
        console.error(
          `Request failed ⨯ ${url}: ${response.status}\n${response.body}`
        )
      }
    }
  }
}

export function visitSearchPages() {
  const locales = parseEnvLocales(__ENV.LOCALES)
  const ovGroup = `search for random word on locales ${locales}`

  for (const MEDIA_TYPE of ["image", "audio"]) {
    for (const locale of locales) {
      const doSearch = (queryTerm: string) => {
        const url = new URL(
          `${localePrefix(locale)}search/${MEDIA_TYPE}`,
          FRONTEND_URL
        )
        const params = new URLSearchParams(__ENV.PARAMS)
        params.append("q", queryTerm)
        url.search = params.toString()

        const response = http.get(url.toString(), { tags: { ovGroup } })
        const result = check(
          response,
          { "status was 200": (r) => r.status === 200 },
          { ovGroup }
        )

        if (!result) {
          console.error(
            `Request failed ⨯ ${url}: ${response.status}\n${response.body}`
          )
        }
      }

      if (__ENV.search_all_sample_query_terms) {
        // This option should only be used when generating talkback tapes for the sample queries
        // Otherwise, just use `getRandomQueryTerm` and make a specific number of intentional queries
        // If consistency is needed, use a pseudo-random number generator to pick a consistently-random
        // sample query term based on information from k6/exec (e.g., vu + scenario)
        for (const queryTerm of SAMPLE_QUERY_TERMS) {
          doSearch(queryTerm)
        }
      } else {
        doSearch(getRandomQueryTerm())
      }
    }
  }
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const actions = {
  visitStaticPages,
  visitSearchPages,
} as const

type Action = keyof typeof actions

const createScenario = (
  env: Record<string, string>,
  funcName: Action
): Scenario => {
  return {
    executor: "per-vu-iterations",
    env,
    exec: funcName,
    // k6 CLI flags do not allow override scenario options, so we need to add our own
    // Ideally we would use default
    // https://community.grafana.com/t/overriding-vus-individual-scenario/98923
    vus: parseFloat(__ENV.scenario_vus) || 5,
    iterations: parseFloat(__ENV.scenario_iterations) || 40,
  }
}

export const SCENARIOS = {
  englishStaticPages: createScenario({ LOCALES: "en" }, "visitStaticPages"),
  localeStaticPages: createScenario(
    { LOCALES: TEST_LOCALES.join(",") },
    "visitStaticPages"
  ),
  englishSearchPages: createScenario(
    { LOCALES: "en", PARAMS: "" },
    "visitSearchPages"
  ),
  localesSearchPages: createScenario(
    { LOCALES: TEST_LOCALES.join(","), PARAMS: "" },
    "visitSearchPages"
  ),
  englishSearchPagesWithFilters: createScenario(
    { LOCALES: "en", PARAMS: TEST_PARAMS },
    "visitSearchPages"
  ),
  localesSearchPagesWithFilters: createScenario(
    { LOCALES: TEST_LOCALES.join(","), PARAMS: TEST_PARAMS },
    "visitSearchPages"
  ),
} as const

function getScenarios(
  scenarios: (keyof typeof SCENARIOS)[]
): Record<string, Scenario> {
  return scenarios.reduce(
    (acc, scenario) => ({ ...acc, [scenario]: SCENARIOS[scenario] }),
    {} as Record<string, Scenario>
  )
}

export const SCENARIO_GROUPS = {
  all: getScenarios([
    "englishStaticPages",
    "localeStaticPages",
    "englishSearchPages",
    "localesSearchPages",
    "englishSearchPagesWithFilters",
    "localesSearchPagesWithFilters",
  ]),
  "static-en": getScenarios(["englishStaticPages"]),
  "static-locales": getScenarios(["localeStaticPages"]),
  "search-en": getScenarios([
    "englishSearchPages",
    "englishSearchPagesWithFilters",
  ]),
  "search-locales": getScenarios([
    "localesSearchPages",
    "localesSearchPagesWithFilters",
  ]),
} satisfies Record<string, Record<string, Scenario>>

export function getOptions(group: keyof typeof SCENARIO_GROUPS): Options {
  return {
    scenarios: SCENARIO_GROUPS[group],
    cloud: {
      projectId: PROJECT_ID,
      name: `Frontend ${group} ${FRONTEND_URL}`,
    },
    userAgent: "OpenverseK6/1.0; https://docs.openverse.org",
    thresholds: {
      http_req_failed: ["rate<0.01"],
    },
  } satisfies Options
}
