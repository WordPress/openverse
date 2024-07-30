import axios from "axios"

export const defaultConfig = {
  apiClientId: "abcdefg_client_i_d",
  apiClientSecret: "shhhhhhhhh_1234_super_secret",
}

export const defaultPromise = Promise.resolve()
export const iAmATeapotError = new axios.AxiosError(
  "I'm a teapot",
  {},
  { status: 418 }
)

export const frozenNow = Date.now()
export const frozenSeconds = Math.floor(frozenNow / 1e3)
export const twelveHoursInSeconds = 12 * 3600

let tokenCount = 1
export const getMockTokenResponse = (expires_in = twelveHoursInSeconds) => ({
  access_token: `abcd1234_${tokenCount++}`,
  expires_in,
})
