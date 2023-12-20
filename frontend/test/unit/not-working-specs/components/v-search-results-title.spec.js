import { render } from "~~/test/unit/test-utils/render"

import VSearchResultsTitle from "~/components/VSearchResultsTitle.vue"

describe("VSearchResultsTitle", () => {
  let options = {
    props: {
      size: "large",
    },
    scopedSlots: {
      default: () => "zack",
    },
  }

  it("should render an h1 tag containing the correct text", async () => {
    const { findByText } = await render(VSearchResultsTitle, options)
    const button = await findByText("zack")
    expect(button.tagName).toBe("H1")
  })
})
