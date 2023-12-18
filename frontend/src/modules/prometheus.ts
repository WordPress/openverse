import http from "http"

import { defineNuxtModule } from "@nuxt/kit"
import promBundle from "express-prom-bundle"

import { register } from "prom-client"

import type { Server as ConnectServer } from "connect"

let metricsServer: null | http.Server = null

const bypassMetricsPathParts = [
  /**
   * Exclude static paths. Remove once we've moved static file
   * hosting out of the SSR server's responsibilities.
   */
  "_nuxt",
  /**
   * Only include these paths in development. They do not exist in production
   * so we can happily skip the extra iterations these path parts introduce.
   */
  ...(process.env.NODE_ENV === "development" ? ["__webpack", "sse"] : []),
]

const bundle = promBundle({
  // We serve the Prometheus metrics on a separate port for production
  // and if we let express-prom-bundle register the `/metrics` route then
  // it exposes all the metrics on the publicly accessible port
  autoregister: false,
  promClient: {
    // Set this to an empty object to pass falsy check in express-prom-bundle
    // and default metrics get enabled with the default prom-client configuration
    collectDefaultMetrics: {},
  },
  buckets: [0.03, 0.3, 0.5, 1, 1.5, 2, 5, 10, Infinity],
  bypass: (req) =>
    bypassMetricsPathParts.some((p) => req.originalUrl.includes(p)),
  includeMethod: true,
  includePath: true,
  normalizePath: [
    ["all", "image", "audio"].map(
      // Normalize single result pages with IDs in the path
      (t) => [`/${t}/.*`, `/${t}/#id`] as [string, string]
    ),
  ],
  /**
   * promBundle creates an Express middleware function, which is type-incompatible
   * with Nuxt's "connect" middleware functions. I guess they _are_ compatible,
   * in actual code, or maybe just in the particular implementation of the prometheus
   * bundle middleware. In any case, this cast is necessary to appeas TypeScript
   * without an ugly ts-ignore.
   */
}) as unknown as ServerMiddleware

export default defineNuxtModule((options, nuxt) => {
  nuxt.hook("close", () => {
    metricsServer?.close()
    // Clear registry so that metrics can re-register when the server restarts in development
    register.clear()
  })
  nuxt.hook("listen", () => {
    // Serve Prometheus metrics on a separate port to allow production
    // metrics to be hidden behind security group settings
    metricsServer = http
      .createServer(async (_, res) => {
        res.writeHead(200, {
          "Content-Type": register.contentType,
        })
        res.end(await register.metrics())
      })
      .listen(parseFloat(process.env.METRICS_PORT || "54641"), "0.0.0.0")
  })
  nuxt.hook("render:setupMiddleware", (app: ConnectServer) => {
    /**
     * Register this here so that it's registered at the absolute top
     * of the middleware stack. Using server-middleware puts it
     * after a whole host of stuff.
     *
     * Note: The middleware only has access to server side navigations,
     * as it is indeed an express middleware, not a Nuxt page middleware.
     * There's no safe way to pipe client side metrics to Prometheus with
     * this set up and if we wanted that anyway we'll want to invest into
     * an actual RUM solution, not a systems monitoring solution like
     * Prometheus. The implication of this is that the metrics will only
     * include SSR'd requests. SPA navigations or anything else that
     * happens exclusively on the client will not be measured. This is the
     * expected behavior!
     *
     * @see {@link https://github.com/nuxt/nuxt.js/blob/dev/packages/server/src/server.js#L70-L138}
     */
    app.use(bundle)
  })
})
