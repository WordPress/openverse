import { describe, expect, it } from "vitest"

import { sanitizeHref } from "#shared/utils/sanitize-href"

describe("sanitizeHref", () => {
  it.each([
    "javascript:alert(1)",
    "JavaScript:alert(document.domain)",
    "java\tscript:alert(1)",
    "javascript:alert(1)",
    " javascript:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "vbscript:msgbox(1)",
  ])("blanks script-bearing scheme %j", (href) => {
    expect(sanitizeHref(href)).toBe("about:blank")
  })

  it.each([
    "https://example.com/landing?a=1&b=2",
    "http://example.com",
    "mailto:someone@example.com",
    "/internal/path",
    "//scheme-relative.example.com",
    "relative/path",
  ])("preserves safe or scheme-less URL %j", (href) => {
    expect(sanitizeHref(href)).toBe(href)
  })
})
