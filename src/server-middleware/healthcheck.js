/**
 * A simple healthcheck that is always true.
 *
 * @todo Update to a resource-sensitive version that fails when
 * memory and/or cpu usage reach a configurable threshhold.
 * @type {import('@nuxt/types').ServerMiddleware}
 */
export default function healthcheck(_, res) {
  res.setHeader("Content-Type", "text/plain")
  res.end("OK")
}
