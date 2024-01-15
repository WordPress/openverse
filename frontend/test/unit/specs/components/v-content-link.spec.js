import { screen } from "@testing-library/vue"

import { beforeEach, describe, expect, it } from "vitest"

import { createApp } from "vue"

import { render } from "~~/test/unit/test-utils/render"

import { i18n } from "~~/test/unit/test-utils/i18n"

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
        plugins: [i18n],
        stubs: { RouterLink: RouterLinkStub },
      },
      props: {
        mediaType: "image",
        resultsCount: 123,
        to: "/images",
        searchTerm: "cat",
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
