const axios = require("axios")
const rateLimit = require("axios-rate-limit")

const userAgent =
  "Openverse/0.1 (https://wordpress.org/openverse; openverse@wordpress.org)"

module.exports = rateLimit(
  axios.create({
    headers: { "User-Agent": userAgent },
  }),
  {
    maxRPS: 99, // limit GlotPress calls to 99 requests per second
  }
)
