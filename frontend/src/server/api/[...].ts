import { useRuntimeConfig } from "#imports"

import { joinURL } from "ufo"
import { defineEventHandler, proxyRequest } from "h3"
import { createConsola } from "consola"

import { getApiAccessToken } from "~/utils/api-token"

const openverseUserAgent =
  "Openverse/0.1 (https://openverse.org; openverse@wordpress.org)"

const proxyLogger = createConsola({
  level: 3,
  reporters: [
    {
      log(logObj) {
        console.log(
          JSON.stringify({
            date: logObj.date,
            message: logObj.args.join(", "),
            level: logObj.type,
          })
        )
      },
    },
  ],
})

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const proxyUrl = config.public.apiUrl + "v1/"
  const { apiClientId, apiClientSecret } = config

  const openverseApiToken = await getApiAccessToken({
    apiClientId,
    apiClientSecret,
  })

  const path = event.path.replace(/^\/api\//, "")
  const target = joinURL(proxyUrl, path)

  const response = await proxyRequest(event, target, {
    headers: {
      Authorization: `Bearer ${openverseApiToken}`,
      "User-Agent": openverseUserAgent,
      "Content-Type": "application/json",
    },
  })

  proxyLogger.info({
    message: `Proxied API request to ${target}, status: ${response.statusCode}`,
  })
  return response.data
})
