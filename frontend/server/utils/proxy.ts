import { createError, getQuery, getSession, type H3Event } from "h3"
import { useRuntimeConfig } from "nitropack/runtime"
import { logger } from "~~/server/utils/logger"

import {
  AUDIO,
  isSupportedMediaType,
  type SupportedMediaType,
} from "#shared/constants/media"
import { mediaSlug, validateUUID } from "#shared/utils/query-utils"

type ValidatedWithoutId = {
  mediaType: SupportedMediaType
  sessionId: string
}
type ValidatedWithId = ValidatedWithoutId & {
  id: string
}

type ValidatedRequestParams<RequireId extends boolean> = RequireId extends true
  ? ValidatedWithId
  : ValidatedWithoutId
type RequestKind = "search" | "related" | "single-result"

const getPath = <
  Kind extends RequestKind,
  RequireId extends Kind extends "search" ? false : true,
  Params extends ValidatedRequestParams<RequireId>,
>(
  requestKind: Kind,
  params: Params
): string => {
  const path = `/v1/${mediaSlug(params.mediaType)}/`
  if (requestKind === "search") {
    return path
  }

  const id = (params as ValidatedWithId).id
  return requestKind === "single-result"
    ? path + `${id}/`
    : path + `${id}/related/`
}

export const validateProxiedRequest = async <RequireId extends boolean>(
  event: H3Event,
  { requireId }: { requireId: RequireId }
): Promise<ValidatedRequestParams<RequireId>> => {
  /* Validate that the request is coming from the frontend app, and is not a direct `/api` request */
  const password = useRuntimeConfig(event).session.password
  const session = await getSession(event, { password })
  if (!session.id) {
    throw createError({
      status: 401,
      statusText: "Unauthorized",
      message: "This route is for internal use only.",
    })
  }

  const mediaType =
    event.context.params?.type &&
    isSupportedMediaType(event.context.params.type)
      ? (event.context.params.type as SupportedMediaType)
      : null

  if (!mediaType) {
    console.log("no media type?", event.context.params)
    throw createError({
      status: 404,
      statusText: "Not Found",
      message: `Invalid mediaType: ${mediaType}.`,
    })
  }

  const params = { sessionId: session.id, mediaType } as const

  if (!requireId) {
    return params as ValidatedRequestParams<RequireId>
  }

  const id = event.context.params?.id
  if (!id || !validateUUID(id)) {
    throw createError({
      status: 404,
      statusText: "Not Found",
      message: "Missing or invalid required id parameter.",
    })
  }

  return { ...params, id } as ValidatedRequestParams<RequireId>
}

export const proxyApiRequest = async (
  event: H3Event,
  requestKind: RequestKind
) => {
  const requestParams = await validateProxiedRequest(event, {
    requireId: requestKind !== "search",
  })

  const path = getPath(requestKind, requestParams)
  const query = getQuery(event)
  if (requestParams.mediaType === AUDIO && requestKind !== "single-result") {
    query.peaks = "true"
  }
  const queryString = new URLSearchParams(
    query as Record<string, string>
  ).toString()
  const requestUrl = `${path}${queryString ? `?${queryString}` : ""}`

  try {
    const { data, error } = await event.context.client.GET(path, {
      params: { query },
      headers: {
        ...event.context.headers,
        Accept: "application/json",
      },
    })
    if (data) {
      logger.info({
        status: "Fetch success",
        request: requestUrl,
        session: requestParams.sessionId,
      })
      return data
    } else {
      logger.warn({
        status: "API Error",
        detail: typeof error === "string" ? error : Object.keys(error),
        request: requestUrl,
      })
      return { error }
    }
  } catch (error) {
    logger.warn("Error fetching search results", error, typeof error)
    return { error }
  }
}
