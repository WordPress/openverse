import { group } from "k6"
import http from "k6/http"
import {
  FRONTEND_URL,
  getRandomWord,
  makeResponseFailedCheck,
} from "./utils.js"

const STATIC_PAGES = [
  "about",
  "sources",
  "search-help",
  "privacy",
  "sensitive-content",
]
const TEST_LOCALES = ["en", "ru", "es", "ar"]
const TEST_PARAMS = "&license=by&extension=jpg,mp3&source=flickr,jamendo"

const localePrefix = (locale) => {
  return locale === "en" ? "" : locale + "/"
}

const visitUrl = (url, locale, action) => {
  const response = http.get(url, { headers: { "cache-control": "no-cache" } })
  const checkResponseFailed = makeResponseFailedCheck("", url)
  if (checkResponseFailed(response, action)) {
    console.error(`Failed URL: ${url}`)
    return 0
  }
}

const parseEnvLocales = (locales) => {
  return locales ? locales.split(",") : ["en"]
}

export function visitStaticPages() {
  const locales = parseEnvLocales(__ENV.LOCALES)
  console.log(`VU: ${__VU}  -  ITER: ${__ITER}`)
  for (let locale of locales) {
    group(`visit static pages for locale ${locale}`, () => {
      for (let page of STATIC_PAGES) {
        visitUrl(
          `${FRONTEND_URL}${localePrefix(locale)}${page}`,
          locale,
          "visitPage"
        )
      }
    })
  }
}

export function visitSearchPages() {
  let locales = parseEnvLocales(__ENV.LOCALES)
  let params = __ENV.PARAMS
  const paramsString = params ? ` with params ${params}` : ""
  console.log(`VU: ${__VU}  -  ITER: ${__ITER}`)
  for (let MEDIA_TYPE of ["image", "audio"]) {
    for (let locale of locales) {
      let q = getRandomWord()
      group(
        `${MEDIA_TYPE} search for ${q} on locale ${locale}${paramsString}`,
        () => {
          return visitUrl(
            `${FRONTEND_URL}${localePrefix(locale)}search/${MEDIA_TYPE}?q=${q}${params}`,
            locale,
            "visitSearchPage"
          )
        }
      )
    }
  }
}

const createScenario = (env, funcName) => {
  return {
    executor: "per-vu-iterations",
    env,
    exec: funcName,
    vus: 5,
    iterations: 5,
  }
}

const optionToScenario = {
  all: [
    "staticPages",
    "localeStaticPages",
    "englishSearchPages",
    "localesSearchPages",
    "englishSearchPagesWithFilters",
    "localesSearchPagesWithFilters",
  ],
  "static-en": ["staticPages"],
  "static-locales": ["localeStaticPages"],
  "search-en": ["englishSearchPages", "englishSearchPagesWithFilters"],
  "search-locales": ["localesSearchPages", "localesSearchPagesWithFilters"],
}
const getScenariosToRun = () => {
  let scenariosToRun = __ENV.SCENARIOS

  if (
    !scenariosToRun ||
    !Object.keys(optionToScenario).includes(scenariosToRun)
  ) {
    scenariosToRun = "static-en"
  }
  const allScenarios = {
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
  }

  return Object.keys(allScenarios).reduce((acc, key) => {
    if (optionToScenario[scenariosToRun].includes(key)) {
      acc[key] = allScenarios[key]
    }
    return acc
  }, {})
}

export const options = {
  scenarios: getScenariosToRun(),
}
