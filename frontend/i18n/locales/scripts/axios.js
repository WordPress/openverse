const axios = require("axios")

const { userAgent } = require("../../../shared/constants/user-agent")

module.exports = module.exports = axios.create({
  headers: { "User-Agent": userAgent },
})
