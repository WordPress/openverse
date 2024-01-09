import { screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import LoadingIcon from "~/components/LoadingIcon.vue"

describe("LoadingIcon", () => {
  it("should render correct contents", async () => {
    await render(LoadingIcon)
    expect(screen.getByTestId("lds-ring")).toBeDefined()
  })
})
