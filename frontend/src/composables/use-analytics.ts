import axios from "axios"
import { isRef } from "vue"
import { useContext } from "@nuxtjs/composition-api"

import { log } from "~/utils/console"

import type { Events, EventName } from "~/types/analytics"

import type { Context } from "@nuxt/types"

const OPENVERSE_UA =
  "Openverse/0.1 (https://wordpress.org/openverse; openverse@wordpress.org)"

type ContextReturn = ReturnType<typeof useContext>

/**
 * Get Plausible props that work identically on the server-side and the
 * client-side. This excludes props that need `window`.
 *
 * @param $ua - the User-Agent information from `express-useragent`
 * @param i18n - the Nuxt i18n instance from `@nuxtjs/i18n`
 */
export const getIsomorphicProps = ({ $ua, i18n }: Context | ContextReturn) => ({
  timestamp: new Date().toISOString(),
  language: i18n.locale,
  ...($ua
    ? {
        ua: $ua.source,
        os: $ua.os,
        platform: $ua.platform,
        browser: $ua.browser,
        version: $ua.version,
      }
    : {}),
})

/**
 * Get Plausible props that work only on the client-side. This only includes
 * props that need `window`.
 */
export const getWindowProps = () => ({
  origin: window.location.origin,
  pathname: window.location.pathname,
  referrer: window.document.referrer,
  width: window.innerWidth,
  height: window.innerHeight,
})

/**
 * Get Plausible props present in `window` through alternate channels. This uses
 * Nuxt context fields that are only present on the server-side.
 *
 * @param req - the request received by the Nuxt SSR server
 * @param route - the Vue router route being rendered from `vue-router`
 * @param $cookies - the cookies object from `cookie-universal-nuxt`
 */
export const getPseudoWindowProps = ({
  req,
  route,
  $cookies,
}: Context | ContextReturn) => ({
  origin: req.headers.host ?? "", // `Host` header includes port.
  pathname: isRef(route) ? route.value.fullPath : route.fullPath,
  referrer: req.headers.referer ?? "",
  width: $cookies.get("uiDeviceWidth") ?? -1,
  height: $cookies.get("uiDeviceHeight") ?? -1,
})

/**
 * The `ctx` parameter must be supplied if using this composable outside the
 * bounds of the composition API.
 *
 * @param ctx - the Nuxt context
 */
export const useAnalytics = (ctx?: Context) => {
  const context = ctx ?? useContext()
  const { $cookies, $plausible, route, req } = context

  /**
   * Send a custom event to Plausible. Mandatory props are automatically merged
   * with the event-specific props.
   *
   * @param name - the name of the event being recorded
   * @param payload - the additional information to record about the event
   */
  const sendCustomEvent = <T extends EventName>(
    name: T,
    payload: Events[T]
  ) => {
    $plausible.trackEvent(name, {
      props: {
        ...getIsomorphicProps(context),
        ...getWindowProps(),
        ...payload, // can override mandatory props
      },
    })
  }

  /**
   * Send a custom event to Plausible. Mandatory props are automatically merged
   * with the event-specific props. This function is meant to be used on the
   * server side because it uses their API instead of using the integration.
   *
   * @param name - the name of the event being recorded
   * @param payload - the additional information to record about the event
   */
  const sendCustomEventApi = async <T extends EventName>(
    name: T,
    payload: Events[T]
  ) => {
    const origin = req.headers.host ?? "" // `Host` header includes port.
    const pathname = isRef(route) ? route.value.fullPath : route.fullPath
    const protocol =
      origin.includes("localhost") || origin.match(/(\d{1,3}\.){3}\d{1,3}/)
        ? "http:"
        : "https:"
    const url = `${protocol}//${origin}${pathname}`

    const referrer = req.headers.referer ?? ""

    const width = $cookies.get("uiDeviceWidth") ?? -1

    const xFFHeader = req.headers["x-forwarded-for"]
    const xForwardedFor = Array.isArray(xFFHeader) // If multiple `X-Forwarded-For`...
      ? xFFHeader[0] // ...pick first.
      : xFFHeader // If single `X-Forwarded-For`...
      ? xFFHeader // ...use it.
      : req.socket.remoteAddress // If remote address known...
      ? req.socket.remoteAddress // ...use it.
      : ""

    const res = await axios.post(
      "/api/event",
      {
        domain: process.env.PLAUSIBLE_DOMAIN ?? "localhost",
        name, // Event name
        url,
        referrer,
        width,
        props: {
          ...getIsomorphicProps(context),
          ...getPseudoWindowProps(context),
          ...payload,
        },
      },
      {
        baseURL: process.env.PLAUSIBLE_API_HOST ?? "http://localhost:50288",
        headers: {
          "User-Agent": req.headers["user-agent"] ?? OPENVERSE_UA,
          Referrer: referrer,
          "X-Forwarded-For": xForwardedFor,
        },
      }
    )
    log(`Sent ${name}; Received ${res.status}: ${res.data}`)
  }

  return {
    sendCustomEvent,
    sendCustomEventApi,
  }
}
