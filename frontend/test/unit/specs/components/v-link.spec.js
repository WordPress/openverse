import { fireEvent, screen } from "@testing-library/vue"
import Vue from "vue"

import { render } from "~~/test/unit/test-utils/render"

import { useAnalytics } from "~/composables/use-analytics"

import VLink from "~/components/VLink.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))

describe("VLink", () => {
  useAnalytics.mockImplementation(() => ({
    sendCustomEvent: jest.fn(),
  }))
  it.each`
    href                        | target      | rel
    ${"/about"}                 | ${null}     | ${null}
    ${"http://localhost:8443/"} | ${"_blank"} | ${"noopener noreferrer"}
  `(
    "Creates a correct link component based on href",
    ({ href, target, rel }) => {
      render(VLink, {
        props: { href },
        slots: { default: "Code is Poetry" },
        stubs: {
          NuxtLink: {
            props: ["to"],
            template: '<a :href="to"><slot /></a>',
          },
        },
      })
      const link = screen.getByRole("link")
      const expectedHref = href.startsWith("/")
        ? `http://localhost${href}`
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
      // eslint-disable-next-line vue/one-component-per-file
      Vue.component("VLinkWrapper", {
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
      })
    const WrapperComponent = createVLinkWrapper(href)
    render(
      WrapperComponent,
      {
        stubs: {
          NuxtLink: {
            props: ["to"],
            template: '<a :href="to"><slot /></a>',
          },
        },
      },
      (localVue) => {
        localVue.component("VLink", VLink)
      }
    )
    const linkBefore = await screen.getByRole("link")
    expect(linkBefore.textContent).toEqual("Link Text")

    await fireEvent.click(linkBefore)
    const linkAfter = await screen.findByText("Code is Poetry")
    expect(linkAfter.tagName).toBe("A")
  })
})
