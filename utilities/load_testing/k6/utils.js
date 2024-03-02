import { check } from "k6"
import http from "k6/http"
import { randomItem } from "https://jslib.k6.io/k6-utils/1.2.0/index.js"

export const API_URL =
  __ENV.API_URL || "https://api-staging.openverse.engineering/v1/"
export const SLEEP_DURATION = 0.1
// Use the random words list available locally, but filter any words that end with apostrophe-s
const WORDS = open("/usr/share/dict/words")
  .split("\n")
  .filter((w) => !w.endsWith("'s"))

export const getRandomWord = () => randomItem(WORDS)

export const getProvider = (media_type) => {
  let url = `${API_URL}${media_type}/stats`
  const response = http.get(url, { headers: REQUEST_HEADERS })
  let providers = JSON.parse(response.body)
  return randomItem(providers).source_name
}

export const REQUEST_HEADERS = {
  Authorization: `Bearer ${__ENV.ACCESS_TOKEN}`,
  "User-Agent": "k6",
}

export const getUrlBatch = (urls, type = "detail_url") => {
  return urls.map((u) => {
    const params = { headers: REQUEST_HEADERS, tags: { name: type } }
    return ["GET", u, null, params]
  })
}

export const makeResponseFailedCheck = (param, page) => {
  return (response, action) => {
    if (check(response, { "status was 200": (r) => r.status === 200 })) {
      console.log(
        `Checked status 200 ✓ for param "${param}" at page ${page} for ${action}.`
      )
      return false
    } else {
      console.error(
        `Request failed ⨯ for param "${param}" at page ${page} for ${action}: ${response.body}`
      )
      return true
    }
  }
}
