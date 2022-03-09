/**
 * The talkback proxy for e2e tests. When making a request to the API during testing,
 * it tries to use the responses it previously saved in `/test/tapes` folder. If no
 * response is found there, it:
 * - by default, returns 'Not found'.
 * - if you pass `--update-tapes` as a parameter, makes an actual request, and saves the response for
 * future use.
 * This makes it possible for the e2e tests to run without internet, and makes the
 * tests less flaky due to changes in the API or API data.
 */
const process = require('process')

const talkback = require('talkback')

const host = 'https://api.openverse.engineering'

const tapeNameGenerator = (tapeNumber) => `response-${tapeNumber}`

const updatingTapes = process.argv.includes('--update-tapes')
const recordMode = updatingTapes
  ? talkback.Options.RecordMode.NEW
  : talkback.Options.RecordMode.DISABLED
const opts = {
  host,
  port: 49152,
  path: './test/tapes',
  record: recordMode,
  fallbackMode: talkback.Options.FallbackMode.NOT_FOUND,
  ignoreHeaders: ['user-agent', 'origin', 'referrer', 'content-length', 'host'],
  name: 'Openverse e2e proxy',
  summary: false,
  tapeNameGenerator,
}

const server = talkback(opts)

server.start(() => console.log('Talkback started with record mode', recordMode))
function closeServer() {
  server.close()
  console.log('Server closed, exiting process')
  process.exit(0)
}
process.on('SIGTERM', () => {
  console.log('Received SIGTERM')
  closeServer()
})
