import { check } from "k6"
import { type Response } from "k6/http"

// @ts-expect-error https://github.com/grafana/k6-template-typescript/issues/16
// eslint-disable-next-line import/extensions, import/no-unresolved
import { randomItem } from "https://jslib.k6.io/k6-utils/1.2.0/index.js"

export const SLEEP_DURATION = 0.1

// Use the random words list available locally, but filter any words that end with apostrophe-s
const WORDS = open("/usr/share/dict/words")
  .split("\n")
  .filter((w) => !w.endsWith("'s"))

export const getRandomWord = () => randomItem(WORDS)

export const makeResponseFailedCheck = (param: string, page: string) => {
  return (response: Response, action: string) => {
    const requestDetail = `${param ? `for param "${param} "` : ""}at page ${page} for ${action}`
    if (check(response, { "status was 200": (r) => r.status === 200 })) {
      console.log(`Checked status 200 ✓ ${requestDetail}.`)
      return false
    } else {
      console.error(
        `Request failed ⨯ ${requestDetail}: ${response.status}\n${response.body}`
      )
      return true
    }
  }
}
