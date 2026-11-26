import { describe, expect, it } from "vitest"
import { render } from "~~/test/unit/test-utils/render"

import VErrorImage from "~/components/VErrorSection/VErrorImage.vue"

describe("VErrorImage", () => {
  it.each(["NO_RESULT", "SERVER_TIMEOUT"] as const)(
    "does not expose license icons in the %s credit as images",
    async (errorCode) => {
      const { container } = await render(VErrorImage, {
        props: { errorCode },
      })

      const licenseIcons = container.querySelectorAll("figcaption img")
      expect(licenseIcons).toHaveLength(2) // 'CC' and 'ZERO' icons
      licenseIcons.forEach((icon) => {
        expect(icon).toHaveAttribute("alt", "")
      })
    }
  )
})
