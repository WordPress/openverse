import { describe, expect, it } from "vitest"

import { sanitizeHref } from "#shared/utils/sanitize-href"

describe("sanitizeHref", () => {
  it.each([
    "javascript:alert(1)",
    "JavaScript:alert(document.domain)",
    "jAvAsCrIpT:alert(1)",
    "java\tscript:alert(1)",
    "java\nscript:alert(1)",
    "java\rscript:alert(1)",
    " javascript:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "vbscript:msgbox(1)",
  ])("blanks script-bearing scheme %j", (href) => {
    expect(sanitizeHref(href)).toBe("about:blank")
  })

  it.each([0, 1, 9, 31])(
    "blanks a scheme hidden behind leading control char %i",
    (code) => {
      expect(sanitizeHref(String.fromCharCode(code) + "javascript:alert(1)")).toBe(
        "about:blank"
      )
    }
  )

  it.each([
    "https://example.com/landing?a=1&b=2",
    "http://example.com",
    "mailto:someone@example.com",
    "/internal/path",
    "//scheme-relative.example.com",
    "relative/path",
    // Encoded payloads are not decoded here — and the browser doesn't decode the scheme either, so they stay inert as-is rather than being wrongly rewritten.
    "%6Aavascript:alert(1)",
    "&#106;avascript:alert(1)",
  ])("preserves safe or scheme-less URL %j", (href) => {
    expect(sanitizeHref(href)).toBe(href)
  })
})
