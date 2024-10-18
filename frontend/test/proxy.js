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
const process = require("process")
const zlib = require("zlib")

// TS doesn't pull the type in correctly for the next dependency when it's `require`'d.

/** @type {import('talkback')['default']} */

// @ts-ignore
const talkback = require("talkback")

// Talkback does not export its types so we've got to pull them out of the Options
/** @typedef {Required<typeof talkback['Options']['Default']>} TalkbackOptions */
/** @typedef {ReturnType<TalkbackOptions['tapeDecorator']>} Tape */

const port = 49153
const host = "https://api.openverse.org"

const urlPatterns = {
  search: /\/(?<mediaType>images|audio|video|model-3d)\/*\?(?<query>.*?)$/u,
  thumb:
    /\/(?<mediaType>images|audio|video|model-3d)\/(?<uuid>[\w-]{32,})\/thumb/,
  related:
    /\/(?<mediaType>images|audio|video|model-3d)\/(?<uuid>[\w-]{32,})\/related/,
  detail: /\/(?<mediaType>images|audio|video|model-3d)\/(?<uuid>[\w-]{32,})\//,
}

/**
 * @param {string} urlString
 * @returns {{match: ({groups}|*), type: string}|null}
 */
const findTypeMatch = (urlString) => {
  for (let [matchName, matchPattern] of Object.entries(urlPatterns)) {
    const patternMatch = urlString.match(matchPattern)
    if (patternMatch && patternMatch.groups) {
      return { type: matchName, match: patternMatch }
    }
  }
  return null
}
/** @type {TalkbackOptions['tapeNameGenerator']} */
const tapeNameGenerator = (tapeNumber, tape) => {
  const typeMatch = findTypeMatch(tape.req.url)
  if (typeMatch && typeMatch.type) {
    const groups = typeMatch.match.groups
    const prefix = `${typeMatch.type}/${groups.mediaType}`
    let suffix = `${tape.req.headers.connection}`
    if (tape.req.method !== "GET") {
      suffix = `${suffix}_${tape.req.method}`
    }
    if (typeMatch.type === "search") {
      return `${prefix}/${groups.query}_${suffix}`
    } else {
      return `${prefix}/${groups.uuid}_${suffix}`
    }
  } else {
    return `response-${tapeNumber}`
  }
}

const updatingTapes =
  process.argv.includes("--update-tapes") || process.env.UPDATE_TAPES === "true"

/** @type {TalkbackOptions['record']} */
const recordMode = updatingTapes
  ? talkback.Options.RecordMode.NEW
  : talkback.Options.RecordMode.DISABLED

/**
 * @template T
 * @param {T} x
 * @returns {T}
 */
const identity = (x) => x

const BodyUtils = Object.freeze({
  gzip: { read: zlib.gunzipSync, save: zlib.gzipSync },
  br: { read: zlib.brotliDecompressSync, save: zlib.brotliCompressSync },
  deflate: { read: zlib.inflateSync, save: zlib.deflateSync },
  default: {
    read: identity,
    save: identity,
  },
})

/**
 * @param {Tape} tape
 */
const getBodyUtil = (tape) =>
  Object.entries(BodyUtils).find(([key]) =>
    tape.res?.headers["content-encoding"]?.includes(key)
  )?.[1] ?? BodyUtils.default

const MAX_PEAKS = 200

/**
 * Transform any response values to use the talkback
 * proxy instead of pointing directly upstream for
 * RESTful references.
 *
 * Ignore thumbnail and non-successful requests, those
 * don't return JSON bodies so we can save them as-is.
 *
 * Sometimes we get a raw compressed buffer back from upstream
 * and we need to decompress it. Sometimes we get the actual
 * JSON. I'm fairly confident this has something to do with Cloudflare
 * cached responses being compressed and others not? In any case,
 * if the response comes back compressed then we need to
 * decompress it, fix the upstream API references, and then
 * compress it back before saving. We could mess with the
 * `content-encoding` header instead of re-compressing it but
 * I think that would sort of violate the contract talkback is meant
 * to have and furthermore would eliminate a complexity in
 * our stack that apparently exists in production. Given e2e
 * tests should aim to test as close to production conditions as
 * possible I think it makes sense to retain both the compressed
 * and uncompressed responses.
 *
 * A note to future contributors: If you find that JSON.parse is
 * complaining about unknown characters then you're either
 * dealing with an error response that isn't being caught by
 * the status check on the first line OR you've discovered
 * another compression algorithm being used (or, of course, it
 * could be something else entirely). Don't discount that it could
 * be something else, but I'd check those two things first
 * before digging elsewhere.
 *
 * @type {TalkbackOptions['tapeDecorator']}
 */
const tapeDecorator = (tape) => {
  if (!tape.res || tape.req.url.endsWith("/thumb/") || tape.res.status >= 399) {
    return tape
  }

  const bodyUtil = getBodyUtil(tape)
  const responseBody = bodyUtil.read(tape.res.body).toString()

  let fixedResponseBody = responseBody.replace(
    /https?:\/\/api.openverse.org/g,
    `http://localhost:${port}`
  )

  if (
    tape.req.url.includes("/audio/") &&
    !tape.req.url.includes("/audio/stats")
  ) {
    const responseBodyJson = JSON.parse(fixedResponseBody)

    // The search or related requests
    if (responseBodyJson.results) {
      responseBodyJson.results.map((result) => {
        if (result.peaks && result.peaks.length > MAX_PEAKS) {
          result.peaks = result.peaks.slice(0, MAX_PEAKS)
        }
      })
      // The single result requests
    } else if (
      responseBodyJson.peaks &&
      responseBodyJson.peaks.length > MAX_PEAKS
    ) {
      responseBodyJson.peaks = responseBodyJson.peaks.slice(0, MAX_PEAKS)
    }
    fixedResponseBody = JSON.stringify(responseBodyJson)
  }

  tape.res.body = Buffer.from(bodyUtil.save(fixedResponseBody))
  return tape
}

const opts = /** @type {Partial<TalkbackOptions>} */ ({
  host,
  port,
  path: "./test/tapes",
  record: recordMode,
  silent: true,
  fallbackMode: talkback.Options.FallbackMode.NOT_FOUND,
  ignoreBody: true,
  allowHeaders: ["connection"],
  name: "Openverse e2e proxy",
  summary: false,
  tapeNameGenerator,
  tapeDecorator,
  responseDecorator: (tape, req, context) => {
    // Log responses to make debugging easier
    console.log(req.method, req.url, tape.res?.status, context.id)
    return tape
  },
})

const server = talkback(opts)

server.start(() =>
  console.log(
    `Talkback started at http://localhost:${port} with record mode ${recordMode}`
  )
)
function closeServer() {
  server.close()
  console.log("Server closed, exiting process")
  process.exit(0)
}
process.on("SIGTERM", () => {
  console.log("Received SIGTERM")
  closeServer()
})
