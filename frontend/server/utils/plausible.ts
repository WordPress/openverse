import { logger } from "~~/server/utils/logger"

import type { Events } from "#shared/types/analytics"

logger.withTag("plausible:server")

export const sendServerPlausibleEvent = async <E extends keyof Events>(
  name: E,
  payload: Events[E],
  data: {
    r: string
    u: string
  }
) => {
  const host = import.meta.env.NUXT_PUBLIC_PLAUSIBLE_API_HOST
  if (!host) {
    logger.debug("Plausible API host not set, skipping server event")
    return
  }
  const d = import.meta.env.NUXT_PUBLIC_PLAUSIBLE_DOMAIN

  const fullPayload = {
    n: name,
    d,
    w: 0,
    h: 0,
    ...data,
    p: JSON.stringify(payload),
  }
  logger.info({ fullPayload })

  return fetch(`${host}/api/event`, {
    method: "POST",
    headers: {
      "Content-Type": "text/plain",
    },
    body: JSON.stringify(fullPayload),
  })
}
