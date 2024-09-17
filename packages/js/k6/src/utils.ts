import { check } from "k6"
import { type Response } from "k6/http"

export const SLEEP_DURATION = 0.1

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
