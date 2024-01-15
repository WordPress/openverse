import { fireEvent, waitFor } from "@testing-library/vue"

import { createApp } from "vue"

import { render } from "~~/test/unit/test-utils/render"

import { i18n } from "~~/test/unit/test-utils/i18n"

import { useSearchStore } from "~/stores/search"

import VSafetyWall from "~/components/VSafetyWall/VSafetyWall.vue"

const RouterLinkStub = createApp({}).component("RouterLink", {
  template: "<a :href='href'><slot /></a>",
  props: ["to"],
  computed: {
    href() {
      return this.to
    },
  },
})._context.components.RouterLink
describe("VSafetyWall.vue", () => {
  let options = {}

  beforeEach(() => {
    options = {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: RouterLinkStub },
      },
      props: {
        media: {
          sensitivity: [
            "sensitive_text",
            "provider_supplied_sensitive",
            "user_reported_sensitive",
          ],
        },
      },
    }
  })

  it("emits reveal event when showMedia method is called", async () => {
    const { getByText, emitted } = await render(VSafetyWall, options)
    const showButton = getByText("Show content")

    await fireEvent.click(showButton)

    await waitFor(() => {
      expect(emitted().reveal).toBeTruthy()
    })
  })

  it("backToSearchPath gets the value from the store", async () => {
    const searchStore = useSearchStore()
    searchStore.setBackToSearchPath("/search")
    const { findByText } = await render(VSafetyWall, options)

    const backToSearchButton = await findByText("Back to results")
    expect(backToSearchButton).toBeInTheDocument()
    expect(backToSearchButton.getAttribute("href")).toEqual("/search")
  })
})
