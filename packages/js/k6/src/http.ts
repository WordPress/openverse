/**
 * Wrap k6/http functions to sign requests to allow firewall bypass.
 */

import {
  get,
  post,
  del,
  options,
  head,
  patch,
  put,
  type RequestBody,
  type RefinedParams,
  type ResponseType,
} from "k6/http"
import { HttpURL } from "k6/experimental/tracing"

// Polyfills URL
import "core-js/web/url"
import "core-js/web/url-search-params"

import { sign } from "./crypto"

const signingSecret = __ENV.signing_secret

function getSignedParams<
  RT extends ResponseType | undefined,
  P extends RefinedParams<RT>,
>(url: string | HttpURL, params: P): P {
  if (!signingSecret) {
    return params
  }

  const _url = new URL(url.toString())

  const timestamp = Math.floor(Date.now() / 1000)
  const resource = `${_url.pathname}${_url.search}${timestamp}`
  const mac = sign(resource, "sha256", signingSecret)

  return {
    ...params,
    headers: {
      ...(params.headers ?? {}),
      "x-ov-cf-mac": mac,
      "x-ov-cf-timestamp": timestamp.toString(),
    },
  }
}

type BodylessHttpFn = typeof get
type BodiedHttpFn = typeof post

function wrapHttpFunction<F extends BodylessHttpFn | BodiedHttpFn>(fn: F): F {
  // url is always the first argument, params is always the last argument
  const urlIdx = 0
  const paramsIdx = fn.length - 1

  return (<RT extends ResponseType | undefined>(...args: Parameters<F>) => {
    const signedParams = getSignedParams(
      args[urlIdx],
      (args[paramsIdx] as RefinedParams<RT>) ?? {}
    )

    return paramsIdx === 1
      ? (fn as BodylessHttpFn)(args[urlIdx], signedParams)
      : (fn as BodiedHttpFn)(args[urlIdx], args[1] as RequestBody, signedParams)
  }) as F
}

/**
 * Wrapper around k6/http that signs requests with Openverse's
 * HMAC shared secret, enabling firewall bypass for load testing.
 */
export const http = {
  get: wrapHttpFunction(get),
  post: wrapHttpFunction(post),
  del: wrapHttpFunction(del),
  options: wrapHttpFunction(options),
  head: wrapHttpFunction(head),
  put: wrapHttpFunction(put),
  patch: wrapHttpFunction(patch),
}
