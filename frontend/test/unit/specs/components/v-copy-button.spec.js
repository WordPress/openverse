/**
 * This is a short test that only tests the rendered output.
 * Actual copying is being tested by the e2e tests:
 * test/playwright/e2e/attribution.spec.ts
 */
import { render } from "@testing-library/vue"

import { i18n } from "~~/test/unit/test-utils/i18n"

import VCopyButton from "~/components/VCopyButton.vue"

describe("VCopyButton", () => {
  it("should render correct contents", () => {
    const { getByRole } = render(VCopyButton, {
      global: { plugins: [i18n] },
      props: {
        el: "#foo",
        id: "foo",
      },
    })

    expect(getByRole("button", { text: "Copy text" })).toBeVisible()
  })
})
