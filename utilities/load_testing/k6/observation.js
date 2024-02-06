/**
 * This module defines tests to run on the API to observe that everything is
 * working normally while we migrate Redis. These are not load tests.
 */

import { sleep } from "k6"
import http from "k6/http"
import { Counter, Trend } from "k6/metrics"

import { API_URL, REQUEST_HEADERS } from "./utils.js"

const count200 = new Counter("count_200")
const count424 = new Counter("count_424")
const count429 = new Counter("count_429")
const count4xx = new Counter("count_4xx")
const count5xx = new Counter("count_5xx")
const countNoneUsage = new Counter("count_none_usage")

const trendBurst = new Trend("trend_usage")
const trendSustained = new Trend("trend_sustained")

const createScenario = (env, exec) => {
  return {
    executor: "constant-vus",
    duration: __ENV.DURATION || "5m",
    vus: 1,
    env,
    exec,
  }
}

export const options = {
  scenarios: {
    imageStats: createScenario({ MEDIA_TYPE: "images" }, "stats"),
    audioStats: createScenario({ MEDIA_TYPE: "audio" }, "stats"),
    imageSearch: createScenario({ MEDIA_TYPE: "images" }, "search"),
    audioSearch: createScenario({ MEDIA_TYPE: "audio" }, "search"),
    authInfo: createScenario({}, "auth"),
  },
}

const updateMetrics = (response) => {
  if (response.status === 200) {
    count200.add(1)
  } else if (response.status === 424) {
    count424.add(1)
  } else if (response.status === 429) {
    count429.add(1)
  } else if (response.status >= 400 && response.status < 500) {
    count4xx.add(1)
  } else if (response.status >= 500 && response.status < 600) {
    count5xx.add(1)
  }
}

export const auth = () => {
  let response = http.get(`${API_URL}rate_limit/`, { headers: REQUEST_HEADERS })
  updateMetrics(response)
  if (response.status === 200 || response.status === 424) {
    const burst = JSON.parse(response.body).requests_this_minute
    const sustained = JSON.parse(response.body).requests_today
    if (burst === null || sustained === null) {
      countNoneUsage.add(1)
    } else {
      trendBurst.add(burst)
      trendSustained.add(sustained)
    }
  }
  sleep(3) // seconds
}

export const stats = () => {
  const mediaType = __ENV.MEDIA_TYPE
  let response = http.get(`${API_URL}${mediaType}/stats`, {
    headers: REQUEST_HEADERS,
  })
  updateMetrics(response)
  sleep(3) // seconds
}

export const search = () => {
  const mediaType = __ENV.MEDIA_TYPE
  let response = http.get(`${API_URL}${mediaType}/?q=cat`, {
    headers: REQUEST_HEADERS,
  })
  updateMetrics(response)
  sleep(3) // seconds
}
