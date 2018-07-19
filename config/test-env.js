'use strict'
const merge = require('webpack-merge')
const devEnv = require('./dev-env')

module.exports = merge(devEnv, {
  NODE_ENV: '"testing"',
  API_URL: process.env.API_URL
})
