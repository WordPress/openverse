import { group } from "k6"
import exec from "k6/execution"
import http from "k6/http"

import { getRandomWord, makeResponseFailedCheck } from "../utils.js"

import { FRONTEND_URL, PROJECT_ID } from "./constants.js"

import type { Options, Scenario } from "k6/options"

const STATIC_PAGES = ["about", "sources", "privacy", "sensitive-content"]
const TEST_LOCALES = ["en", "ru", "es", "fa"]
const TEST_PARAMS = "&license=by&extension=jpg,mp3&source=flickr,jamendo"

const localePrefix = (locale: string) => {
  return locale === "en" ? "" : locale + "/"
}

const visitUrl = (url: string, action: Action) => {
  // eslint-disable-next-line import/no-named-as-default-member
  const response = http.get(url, {
    headers: { "User-Agent": "OpenverseLoadTesting" },
  })
  const checkResponseFailed = makeResponseFailedCheck("", url)
  if (checkResponseFailed(response, action)) {
    console.error(`Failed URL: ${url}`)
    return 0
  }
  return 1
}

const parseEnvLocales = (locales: string) => {
  return locales ? locales.split(",") : ["en"]
}

export function visitStaticPages() {
  const locales = parseEnvLocales(__ENV.LOCALES)
  console.log(
    `VU: ${exec.vu.idInTest}  -  ITER: ${exec.vu.iterationInInstance}`
  )
  for (const locale of locales) {
    group(`visit static pages for locale ${locale}`, () => {
      for (const page of STATIC_PAGES) {
        visitUrl(
          `${FRONTEND_URL}${localePrefix(locale)}${page}`,
          "visitStaticPages"
        )
      }
    })
  }
}

export function visitSearchPages() {
  const locales = parseEnvLocales(__ENV.LOCALES)
  const params = __ENV.PARAMS
  const paramsString = params ? ` with params ${params}` : ""
  console.log(
    `VU: ${exec.vu.idInTest}  -  ITER: ${exec.vu.iterationInInstance}`
  )
  group(`search for random word on locales ${locales}${paramsString}`, () => {
    for (const MEDIA_TYPE of ["image", "audio"]) {
      for (const locale of locales) {
        const q = getRandomWord()
        return visitUrl(
          `${FRONTEND_URL}${localePrefix(locale)}search/${MEDIA_TYPE}?q=${q}${params}`,
          "visitSearchPages"
        )
      }
    }
    return undefined
  })
}

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
  staticPages: createScenario({ LOCALES: "en" }, "visitStaticPages"),
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
    "staticPages",
    "localeStaticPages",
    "englishSearchPages",
    "localesSearchPages",
    "englishSearchPagesWithFilters",
    "localesSearchPagesWithFilters",
  ]),
  "static-en": getScenarios(["staticPages"]),
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
  } satisfies Options
}
