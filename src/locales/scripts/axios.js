const axios = require("axios")

const userAgent =
  "Openverse/0.1 (https://wordpress.org/openverse; openverse@wordpress.org)"

module.exports = axios.create({
  headers: { "User-Agent": userAgent },
})
