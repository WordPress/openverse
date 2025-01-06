// eslint-disable-next-line no-restricted-imports
import { type Page, test as base } from "@playwright/test"

const encoder = new TextEncoder()

const signingSecret = process.env.HMAC_SIGNING_SECRET

const { subtle } = globalThis.crypto

let signingKey: null | CryptoKey = null

async function getSigningKey() {
  if (!signingSecret) {
    return null
  }

  if (!signingKey) {
    const encodedSecret = encoder.encode(signingSecret)
    signingKey = await crypto.subtle.importKey(
      "raw",
      encodedSecret,
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    )
  }

  return signingKey
}

export const test = base.extend<{
  page: Page
}>({
  page: async ({ page }, use) => {
    // Only match staging; it'll just be ignored for local testing
    await page.route(
      (url) => url.host === "staging.openverse.org",
      async (route) => {
        const key = await getSigningKey()
        if (!key) {
          return route.continue()
        }

        const request = route.request()
        const url = new URL(request.url())
        const timestamp = Math.floor(Date.now() / 1000)
        const resource = `${url.pathname}${url.search}${timestamp}`
        const mac = await subtle.sign("HMAC", key, encoder.encode(resource))

        const headers = request.headers()
        await route.continue({
          headers: {
            ...headers,
            "x-ov-cf-mac": Buffer.from(mac).toString("base64url"),
            "x-ov-cf-timestamp": timestamp.toString(),
          },
        })
      }
    )

    await use(page)
  },
})
