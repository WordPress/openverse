import { createApp } from "vue"

import { screen } from "@testing-library/vue"
import { beforeEach, describe, expect, it } from "vitest"
import { render } from "~~/test/unit/test-utils/render"

import VContentLink from "~/components/VContentLink/VContentLink.vue"

const RouterLinkStub = createApp({}).component("RouterLink", {
  template: "<a :href='href'><slot /></a>",
  props: ["to"],
  computed: {
    href() {
      return this.to
    },
  },
})._context.components.RouterLink

describe("VContentLink", () => {
  let options = {}

  beforeEach(() => {
    options = {
      global: {
        stubs: { RouterLink: RouterLinkStub },
      },
      props: {
        mediaType: "image",
        labels: {
          aria: "See the top 240 images found for cat.",
          visual: "Top 240 results",
        },
        to: "/images",
      },
    }
  })

  it("is enabled when there are results", async () => {
    await render(VContentLink, options)
    const btn = screen.getByRole("link")

    expect(btn).toHaveAttribute("href")
    expect(btn).not.toHaveAttribute("aria-disabled")
  })
})
