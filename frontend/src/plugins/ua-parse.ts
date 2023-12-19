import { defineNuxtPlugin, useRequestHeaders } from "#imports"

import pkg from "express-useragent"

const { parse: uaParse } = pkg

type UADetails = ReturnType<typeof uaParse>

const uaParsePlugin = defineNuxtPlugin(() => {
  let userAgent

  const headers = useRequestHeaders()
  if (headers && headers["user-agent"]) {
    userAgent = headers["user-agent"]
  } else if (typeof navigator !== "undefined") {
    userAgent = navigator.userAgent
  }
  let ua: UADetails | null
  if (typeof userAgent == "string") {
    ua = uaParse(userAgent)
  } else {
    ua = null
  }
  return {
    provide: {
      ua,
    },
  }
})

export default uaParsePlugin
