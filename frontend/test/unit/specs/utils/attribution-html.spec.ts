import { i18n } from "~~/test/unit/test-utils/i18n"

import type { AttributableMedia } from "~/utils/attribution-html"
import { getAttribution } from "~/utils/attribution-html"

const mediaItem: AttributableMedia = {
  originalTitle: "Title",
  foreign_landing_url: "https://foreign.landing/url",
  creator: "Creator",
  creator_url: "https://creator/url",
  license: "pdm",
  license_version: "1.0",
  license_url: "https://license/url",
}

describe("getAttribution", () => {
  it.each`
    sendI18n | attributionText
    ${true}  | ${'"Title" by Creator is marked with Public Domain Mark 1.0 .'}
    ${false} | ${'"Title" by Creator is marked with PDM 1.0 .'}
  `(
    "returns attribution for media with i18n $sendI18n",
    ({
      sendI18n,
      attributionText,
    }: {
      sendI18n: boolean
      attributionText: boolean
    }) => {
      document.body.innerHTML = getAttribution(
        mediaItem,
        sendI18n ? i18n : null
      )
      const attributionP = document.getElementsByClassName("attribution")[0]
      expect(attributionP.textContent?.trim()).toEqual(attributionText)
    }
  )

  it("uses generic title if not known", () => {
    const mediaItemNoTitle = { ...mediaItem, originalTitle: "" }
    const attrText = getAttribution(mediaItemNoTitle, i18n, {
      isPlaintext: true,
    })
    const expectation =
      "This work by Creator is marked with Public Domain Mark 1.0"
    expect(attrText).toContain(expectation)
  })

  it("omits creator if not known", () => {
    const mediaItemNoCreator = { ...mediaItem, creator: undefined }
    const attrText = getAttribution(mediaItemNoCreator, i18n, {
      isPlaintext: true,
    })
    const expectation = '"Title" is marked with Public Domain Mark 1.0'
    expect(attrText).toContain(expectation)
  })

  it("escapes embedded HTML", () => {
    const mediaItemWithHtml = {
      ...mediaItem,
      originalTitle: '<script>console.log("HELLO");</script>',
    }
    const attrText = getAttribution(mediaItemWithHtml, i18n)
    const expectation =
      "&lt;script&gt;console.log(&quot;HELLO&quot;);&lt;/script&gt;"
    expect(attrText).toContain(expectation)
    expect(attrText).not.toContain(mediaItemWithHtml.originalTitle)
  })

  it("does not use anchors in plain-text mode", () => {
    document.body.innerHTML = getAttribution(mediaItem, i18n)
    expect(document.getElementsByTagName("a")).not.toHaveLength(0)
    document.body.innerHTML = getAttribution(mediaItem, i18n, {
      isPlaintext: true,
    })
    expect(document.getElementsByTagName("a")).toHaveLength(0)
  })

  it("renders the correct text in plain-text mode", () => {
    const attrText = getAttribution(mediaItem, i18n, { isPlaintext: true })
    const expectation =
      '"Title" by Creator is marked with Public Domain Mark 1.0. To view the terms, visit https://license/url?ref=openverse.'
    expect(attrText).toEqual(expectation)
  })

  it("skips the link if URL is missing", () => {
    const mediaItemNoLicenseUrl = { ...mediaItem, license_url: undefined }
    const attrText = getAttribution(mediaItemNoLicenseUrl, i18n, {
      isPlaintext: true,
    })
    const antiExpectation = "To view"
    expect(attrText).not.toContain(antiExpectation)
  })

  it("does not add license element icons in no-icons mode", () => {
    document.body.innerHTML = getAttribution(mediaItem, i18n)
    expect(document.getElementsByTagName("img")).not.toHaveLength(0)
    document.body.innerHTML = getAttribution(mediaItem, i18n, {
      includeIcons: false,
    })
    expect(document.getElementsByTagName("img")).toHaveLength(0)
  })
})
