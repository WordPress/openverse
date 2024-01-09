import { render, screen } from "@testing-library/vue"

import { describe, expect, it } from "vitest"

import { i18n } from "~~/test/unit/test-utils/i18n"

import VLicense from "~/components/VLicense/VLicense.vue"

describe("VLicense", () => {
  let options = {
    props: {
      license: "by",
    },
    global: { plugins: [i18n], stubs: { VIcon: true } },
  }

  it("should render the license name and icons", async () => {
    const { container } = render(VLicense, options)
    const licenseName = screen.getByLabelText("Attribution")
    expect(licenseName).toBeInTheDocument()
    const licenseIcons = container.querySelectorAll("v-icon-stub")
    expect(licenseIcons).toHaveLength(2) // 'CC' and 'BY' icons
  })

  it("should render only the license icons", async () => {
    options.props.hideName = true
    const { container } = render(VLicense, options)
    const licenseName = screen.queryByText("CC BY")
    expect(licenseName).not.toBeVisible()
    const licenseIcons = container.querySelectorAll("v-icon-stub")
    expect(licenseIcons).toHaveLength(2)
  })

  it("should have background filled with black text", async () => {
    options.props.bgFilled = true
    const { container } = render(VLicense, options)
    const licenseIcons = container.querySelectorAll("v-icon-stub")
    expect(licenseIcons).toHaveLength(2)
    licenseIcons.forEach((icon) => {
      expect(icon).toHaveClass("bg-filled", "text-black")
    })
  })
})
