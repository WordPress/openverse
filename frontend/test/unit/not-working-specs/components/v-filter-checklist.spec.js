import { fireEvent, screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import FilterChecklist from "~/components/VFilters/VFilterChecklist.vue"

describe("FilterChecklist", () => {
  let options = {}
  let props = null

  beforeEach(() => {
    props = {
      // Using real values to avoid i18n warnings
      options: [
        {
          code: "music",
          name: "filters.audioCategories.music",
          checked: false,
        },
      ],
      title: "Music",
      filterType: "audioCategories",
      disabled: false,
    }
    options = {
      props: props,
    }
  })

  it("should render correct contents", async () => {
    const { container } = await render(FilterChecklist, options)
    const checkbox = screen.getByRole("checkbox", {
      checked: false,
      label: /bar/i,
    })
    expect(checkbox).toBeTruthy()
    expect(container.querySelector("svg")).not.toBeVisible()

    await fireEvent.click(checkbox)
    expect(container.querySelector("svg")).toBeVisible()
  })
})
