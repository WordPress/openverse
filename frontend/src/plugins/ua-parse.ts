import { parse, Details as UADetails } from "express-useragent"

import type { Plugin } from "@nuxt/types"

const uaParsePlugin: Plugin = (context, inject) => {
  let userAgent

  if (typeof context.req !== "undefined") {
    userAgent = context.req.headers["user-agent"]
  } else if (typeof navigator !== "undefined") {
    userAgent = navigator.userAgent
  }
  let ua: UADetails | null
  if (typeof userAgent == "string") {
    ua = parse(userAgent)
  } else {
    ua = null
  }

  context.$ua = ua
  inject("ua", ua)
}

export default uaParsePlugin
