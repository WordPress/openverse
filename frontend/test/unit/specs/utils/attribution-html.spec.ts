import { describe, expect, it } from "vitest"
import { i18n } from "~~/test/unit/test-utils/i18n"

import type { AttributableMedia } from "#shared/utils/attribution-html"
import { getAttribution } from "#shared/utils/attribution-html"

const t = i18n.t

const mediaItem: AttributableMedia = {
  originalTitle: "Title",
  foreign_landing_url: "https://foreign.landing/url",
  creator: "Creator",
  creator_url: "https://creator/url",
  license: "pdm",
  license_version: "1.0",
  license_url: "https://license/url",
  frontendMediaType: "image",
  attribution:
    '"Title" by Creator is marked with Public Domain Mark 1.0 . To view a copy of this license, visit https://creativecommons.org/publicdomain/zero/1.0/?ref=openverse.',
}

describe("getAttribution", () => {
  it("returns attribution for media with i18n", async () => {
    const attributionText =
      '"Title" by Creator is marked with Public Domain Mark 1.0 .'
    document.body.innerHTML = getAttribution(mediaItem, t)
    const attributionP = document.getElementsByClassName("attribution")[0]
    expect(attributionP.textContent?.trim()).toEqual(attributionText)
  })

  it("returns attribution for media without i18n", async () => {
    const attributionText = '"Title" by Creator is marked with PDM 1.0 .'
    console.log(getAttribution(mediaItem, null))
    document.body.innerHTML = getAttribution(mediaItem, null)
    const attributionP = document.getElementsByClassName("attribution")[0]
    expect(attributionP.textContent?.trim()).toBe(attributionText)
  })

  it("uses generic title if not known", async () => {
    const mediaItemNoTitle = { ...mediaItem, originalTitle: "" }
    const attrText = getAttribution(mediaItemNoTitle, t, {
      isPlaintext: true,
    })
    const expectation =
      "This work by Creator is marked with Public Domain Mark 1.0"
    expect(attrText).toContain(expectation)
  })

  it("omits creator if not known", async () => {
    const mediaItemNoCreator = { ...mediaItem, creator: undefined }
    const attrText = getAttribution(mediaItemNoCreator, t, {
      isPlaintext: true,
    })
    const expectation = '"Title" is marked with Public Domain Mark 1.0'
    expect(attrText).toContain(expectation)
  })

  it("escapes embedded HTML", async () => {
    const mediaItemWithHtml = {
      ...mediaItem,
      originalTitle: '<script>console.log("HELLO");</script>',
    }
    const attrText = getAttribution(mediaItemWithHtml, t)
    const expectation =
      "&lt;script&gt;console.log(&quot;HELLO&quot;);&lt;/script&gt;"
    expect(attrText).toContain(expectation)
    expect(attrText).not.toContain(mediaItemWithHtml.originalTitle)
  })

  it("escapes HTML in URL fields to prevent attribute-injection XSS", async () => {
    const mediaItemWithUrlPayload = {
      ...mediaItem,
      creator_url: 'https://x"><img src=x onerror=alert(1)>',
    }
    const attrText = getAttribution(mediaItemWithUrlPayload, t, {
      includeIcons: false,
    })
    expect(attrText).not.toContain("<img src=x onerror")
    expect(attrText).toContain("&quot;&gt;&lt;img")
    document.body.innerHTML = attrText
    expect(document.getElementsByTagName("img")).toHaveLength(0)
  })

  it("drops javascript: URLs from hrefs", async () => {
    const mediaItemWithJsUrl = {
      ...mediaItem,
      creator_url: "javascript:alert(document.domain)",
    }
    document.body.innerHTML = getAttribution(mediaItemWithJsUrl, t)
    const links = Array.from(document.getElementsByTagName("a"))
    expect(
      links.some((a) => a.getAttribute("href")?.startsWith("javascript"))
    ).toBe(false)
    expect(links.some((a) => a.getAttribute("href") === "about:blank")).toBe(
      true
    )
  })

  it("drops javascript: URLs obfuscated with control characters", async () => {
    const mediaItemWithObfuscatedUrl = {
      ...mediaItem,
      creator_url: "java\tscript:alert(1)",
    }
    document.body.innerHTML = getAttribution(mediaItemWithObfuscatedUrl, t)
    const links = Array.from(document.getElementsByTagName("a"))
    // The raw attribute keeps the obfuscation verbatim; only the parsed `href` property reveals the effective javascript: scheme.
    expect(links.some((a) => a.href.startsWith("javascript:"))).toBe(false)
    expect(links.some((a) => a.getAttribute("href") === "about:blank")).toBe(
      true
    )
  })

  it("preserves safe http(s) URLs in hrefs", async () => {
    document.body.innerHTML = getAttribution(mediaItem, t)
    const creatorLink = Array.from(document.getElementsByTagName("a")).find(
      (a) => a.getAttribute("href") === mediaItem.creator_url
    )
    expect(creatorLink).toBeTruthy()
  })

  it("does not use anchors in plain-text mode", async () => {
    document.body.innerHTML = getAttribution(mediaItem, t)
    expect(document.getElementsByTagName("a")).not.toHaveLength(0)
    document.body.innerHTML = getAttribution(mediaItem, t, {
      isPlaintext: true,
    })
    expect(document.getElementsByTagName("a")).toHaveLength(0)
  })

  it("renders the correct text in plain-text mode", async () => {
    const attrText = getAttribution(mediaItem, t, { isPlaintext: true })
    const expectation =
      '"Title" by Creator is marked with Public Domain Mark 1.0. To view the terms, visit https://license/url?ref=openverse.'
    expect(attrText).toEqual(expectation)
  })

  it("skips the link if URL is missing", async () => {
    const mediaItemNoLicenseUrl = { ...mediaItem, license_url: undefined }
    const attrText = getAttribution(mediaItemNoLicenseUrl, t, {
      isPlaintext: true,
    })
    const antiExpectation = "To view"
    expect(attrText).not.toContain(antiExpectation)
  })

  it("does not add license element icons in no-icons mode", () => {
    document.body.innerHTML = getAttribution(mediaItem, t)
    expect(document.getElementsByTagName("img")).not.toHaveLength(0)
    document.body.innerHTML = getAttribution(mediaItem, t, {
      includeIcons: false,
    })
    expect(document.getElementsByTagName("img")).toHaveLength(0)
  })
})
