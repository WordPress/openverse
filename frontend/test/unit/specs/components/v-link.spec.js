import { beforeEach, describe, expect, it } from "vitest"

import { fireEvent, render, screen } from "@testing-library/vue"
import { createApp } from "vue"

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
