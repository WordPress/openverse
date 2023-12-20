import { fireEvent, screen } from "@testing-library/vue"

import { mockNuxtImport } from "@nuxt/test-utils"

import { render } from "~~/test/unit/test-utils/render"

import VContentLink from "~/components/VContentLink/VContentLink.vue"

const sendCustomEventMock = vi.fn()
mockNuxtImport("useAnalytics", () => {
  return () => {
    return {
      sendCustomEvent: sendCustomEventMock,
    }
  }
})

describe("VContentLink", () => {
  let options = {}

  beforeEach(() => {
    options = {
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

  it("sends CHANGE_CONTENT_TYPE event when clicked", async () => {
    await render(VContentLink, options)
    const btn = screen.getByRole("link")

    await fireEvent.click(btn)
    expect(sendCustomEventMock).toHaveBeenCalledWith("CHANGE_CONTENT_TYPE", {
      component: "VContentLink",
      next: "image",
      previous: "all",
    })
  })
})
