/**
 * This is a short test that only tests the rendered output.
 * Actual copying is being tested by the e2e tests:
 * test/playwright/e2e/attribution.spec.ts
 */
import { render } from "~~/test/unit/test-utils/render"

import VCopyButton from "~/components/VCopyButton.vue"

describe("VCopyButton", () => {
  it("should render correct contents", async () => {
    const { getByRole } = await render(VCopyButton, {
      props: {
        el: "#foo",
        id: "foo",
      },
    })

    expect(getByRole("button", { text: "Copy text" })).toBeVisible()
  })
})
