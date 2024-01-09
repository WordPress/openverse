import { render } from "@testing-library/vue"

import { describe, expect, it } from "vitest"

import VSearchResultsTitle from "~/components/VSearchResultsTitle.vue"

describe("VSearchResultsTitle", () => {
  let options = {
    props: {
      size: "large",
    },
    slots: {
      default: () => "zack",
    },
  }

  it("should render an h1 tag containing the correct text", async () => {
    const { getByRole } = render(VSearchResultsTitle, options)
    const title = getByRole("heading", { level: 1, name: "zack" })
    expect(title).toBeInTheDocument()
  })
})
