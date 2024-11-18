import { fireEvent, waitFor } from "@testing-library/vue"

import { createApp } from "vue"

import { render } from "~~/test/unit/test-utils/render"

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
        stubs: { RouterLink: RouterLinkStub },
      },
      props: {
        sensitivity: [
          "sensitive_text",
          "provider_supplied_sensitive",
          "user_reported_sensitive",
        ],
        id: "123",
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
    const backToSearchPath = "/search"
    searchStore.setBackToSearchPath(backToSearchPath)
    const { findByText } = await render(VSafetyWall, options)

    const backToSearchButton = await findByText("Back to results")
    expect(backToSearchButton).toBeInTheDocument()
    expect(backToSearchButton.getAttribute("href")).toEqual(backToSearchPath)
  })
})
