import { createApp } from "vue"

import { beforeEach, describe, expect, it } from "vitest"
import { fireEvent, render, screen } from "@testing-library/vue"

import VLink from "~/components/VLink.vue"

const RouterLinkStub = createApp({}).component("RouterLink", {
  template: "<a :href='href'><slot /></a>",
  props: ["to"],
  computed: {
    href() {
      return this.to
    },
  },
})._context.components.RouterLink

describe("VLink", () => {
  let options = null
  beforeEach(() => {
    options = { global: { stubs: { RouterLink: RouterLinkStub } } }
  })
  it.each`
    href                        | target  | rel
    ${"/about"}                 | ${null} | ${null}
    ${"http://localhost:8443/"} | ${null} | ${"noopener noreferrer"}
  `(
    "Creates a correct link component based on href",
    async ({ href, target, rel }) => {
      options.props = { href }
      options.slots = { default: () => "Code is Poetry" }
      await render(VLink, options)
      const link = screen.getByRole("link")
      const expectedHref = href.startsWith("/")
        ? `http://localhost:3000${href}`
        : href
      expect(link.href).toEqual(expectedHref)
      expect(link.getAttribute("target")).toEqual(target)
      expect(link.getAttribute("rel")).toEqual(rel)
    }
  )
  it.each`
    href                                   | expected
    ${"javascript:alert(1)"}               | ${"about:blank"}
    ${"JavaScript:alert(1)"}               | ${"about:blank"}
    ${"java\tscript:alert(1)"}             | ${"about:blank"}
    ${"data:text/html,<script>1</script>"} | ${"about:blank"}
    ${"https://good.example.com/landing"}  | ${"https://good.example.com/landing"}
  `(
    "neutralises script-bearing external hrefs ($href)",
    async ({ href, expected }) => {
      options.props = { href }
      options.slots = { default: () => "Code is Poetry" }
      await render(VLink, options)
      const link = screen.getByRole("link")
      expect(link.getAttribute("href")).toEqual(expected)
    }
  )
  it("re-applies the guard when href changes from safe to unsafe", async () => {
    options.props = { href: "https://good.example.com/landing" }
    options.slots = { default: () => "Code is Poetry" }
    const { rerender } = render(VLink, options)
    expect(screen.getByRole("link").getAttribute("href")).toEqual(
      "https://good.example.com/landing"
    )
    await rerender({ href: "javascript:alert(1)" })
    expect(screen.getByRole("link").getAttribute("href")).toEqual("about:blank")
  })
  it.each`
    href
    ${"/about"}
    ${"http://localhost"}
  `("VLink handles click", async ({ href }) => {
    const createVLinkWrapper = (href) =>
      createApp({}).component("VLinkWrapper", {
        components: { VLink },
        data: () => ({ text: "Link Text" }),
        methods: {
          handleClick(e) {
            e.preventDefault()
            this.text = "Code is Poetry"
          },
        },
        template: `
          <div>
          <VLink href="${href}" @click="handleClick">{{ text }}</VLink>
          </div>`,
      })._context.components.VLinkWrapper
    const WrapperComponent = createVLinkWrapper(href)
    await render(WrapperComponent, options)
    const linkBefore = screen.getByRole("link")
    expect(linkBefore.textContent).toBe("Link Text")

    await fireEvent.click(linkBefore)
    const linkAfter = await screen.findByText("Code is Poetry")
    expect(linkAfter.tagName).toBe("A")
  })
})
