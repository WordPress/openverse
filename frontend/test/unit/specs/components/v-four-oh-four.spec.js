import { defineComponent, h } from "vue"

import { screen, within } from "@testing-library/vue"
import { describe, expect, it } from "vitest"
import { render } from "~~/test/unit/test-utils/render"

import VFourOhFour from "~/components/VFourOhFour.vue"

describe("VFourOhFour", () => {
  it("renders recovery content without exposing raw error details", async () => {
    const error = {
      url: "/image/00000000-0000-0000-0000-000000000000",
      statusCode: 404,
      statusMessage: "Not Found",
      message: "No image with this diagnostic ID was found.",
      stack: "",
    }

    await render(
      defineComponent({
        setup: () => () => h(VFourOhFour, { error }),
      })
    )

    const main = screen.getByRole("main")
    expect(within(main).getByRole("heading", { level: 1 })).toHaveTextContent(
      /The content.*seems to have disappeared\./
    )
    expect(
      within(main).getByRole("link", { name: "Openverse" })
    ).toHaveAttribute("href", "/")
    expect(main.textContent).not.toContain(error.message)
    expect(main.textContent).not.toContain('"statusCode"')
    expect(main.textContent).not.toContain('"stack"')
  })
})
