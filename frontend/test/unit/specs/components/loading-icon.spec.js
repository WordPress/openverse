import { render, screen } from "@testing-library/vue"

import LoadingIcon from "~/components/LoadingIcon.vue"

describe("LoadingIcon", () => {
  it("should render correct contents", () => {
    render(LoadingIcon)
    expect(screen.queryAllByTestId("lds-ring")).toHaveLength(1)
  })
})
