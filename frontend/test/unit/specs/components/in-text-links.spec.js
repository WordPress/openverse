/**
 * Links inside running text must be distinguishable by more than colour
 * (WCAG 1.4.1, axe-core `link-in-text-block`). The link colour has a contrast
 * of only ~2.5:1 against the surrounding text, so in-sentence links must be
 * underlined. https://github.com/WordPress/openverse/issues/5653
 */
import { screen } from "@testing-library/vue"
import { describe, expect, it } from "vitest"
import { image } from "~~/test/unit/fixtures/image"
import { render } from "~~/test/unit/test-utils/render"

import ImageReportPage from "~/pages/image/[id]/report.vue"
import { useSingleResultStore } from "~/stores/media/single-result"

import VSafeBrowsing from "~/components/VSafeBrowsing/VSafeBrowsing.vue"
import VMediaLicense from "~/components/VMediaInfo/VMediaLicense.vue"
import VCopyLicense from "~/components/VMediaInfo/VCopyLicense.vue"
import VLicenseExplanation from "~/components/VFilters/VLicenseExplanation.vue"
import VDmcaNotice from "~/components/VContentReport/VDmcaNotice.vue"
import VSafetyWall from "~/components/VSafetyWall/VSafetyWall.vue"
import VContentPage from "~/components/VContentPage.vue"

const stubs = { VIcon: true, VLicenseElements: true }

describe("links inside running text are underlined", () => {
  it("VSafeBrowsing: 'sensitive' link in the filter description", async () => {
    await render(VSafeBrowsing, { global: { stubs } })
    const link = screen.getByRole("link", { name: "sensitive" })
    expect(link).toHaveClass("underline")
  })

  it("VMediaLicense: license link in the 'marked with a ... license' sentence", async () => {
    await render(VMediaLicense, {
      props: {
        license: "by-sa",
        licenseVersion: "2.0",
        licenseUrl: "https://creativecommons.org/licenses/by-sa/2.0/",
      },
      global: { stubs },
    })
    const link = screen.getByRole("link", { name: "CC BY-SA 2.0" })
    expect(link).toHaveClass("underline")
  })

  it("VMediaLicense: link in the public domain tool sentence", async () => {
    await render(VMediaLicense, {
      props: {
        license: "cc0",
        licenseVersion: "1.0",
        licenseUrl: "https://creativecommons.org/publicdomain/zero/1.0/",
      },
      global: { stubs },
    })
    const link = screen.getByRole("link")
    expect(link).toHaveClass("underline")
  })

  it("VCopyLicense: title, creator and license links in the rich attribution", async () => {
    const { container } = await render(VCopyLicense, {
      props: { media: image },
      global: { stubs },
    })
    const richPanel = container.querySelector("#panel-slot-rich")
    const links = richPanel.querySelectorAll("a")
    expect(links.length).toBeGreaterThan(0)
    // The attribution markup is generated as HTML for users to copy, so the
    // underline is applied by the container to all of its descendant links.
    expect(richPanel.firstElementChild).toHaveClass("[&_a]:underline")
  })

  it("VLicenseExplanation: 'Read more' link", async () => {
    await render(VLicenseExplanation, {
      props: { license: "by" },
      global: { stubs },
    })
    const link = screen.getByRole("link", { name: "Read more" })
    expect(link).toHaveClass("underline")
  })

  it("VDmcaNotice: links in the DMCA note", async () => {
    await render(VDmcaNotice, {
      props: {
        provider: "Flickr",
        foreignLandingUrl: image.foreign_landing_url,
      },
      global: { stubs },
    })
    for (const link of screen.getAllByRole("link")) {
      expect(link).toHaveClass("underline")
    }
  })

  it("VSafetyWall: 'sensitive content' link in the learn-more sentence", async () => {
    await render(VSafetyWall, {
      props: { sensitivity: ["sensitive_text"], id: image.id },
      global: { stubs },
    })
    const link = screen
      .getAllByRole("link")
      .find((l) => l.getAttribute("href")?.endsWith("/sensitive-content"))
    expect(link).toBeDefined()
    expect(link).toHaveClass("underline")
  })

  it("Image report page: title, creator and license links in the caption", async () => {
    useSingleResultStore().setMediaItem(image)
    const { container } = await render(ImageReportPage, {
      global: { stubs: { ...stubs, VContentReportForm: true } },
    })
    const caption = container.querySelector("figcaption")
    expect(caption.querySelectorAll("a").length).toBeGreaterThan(0)
    // The caption is generated attribution HTML, so the underline is applied
    // by the container to all of its descendant links.
    expect(caption).toHaveClass("[&_a]:underline")
  })

  it("VContentPage: links in content pages (About, Sources, etc.)", async () => {
    const { container } = await render(VContentPage, {
      slots: {
        default: '<p>See <a href="https://example.org">this page</a>.</p>',
      },
    })
    // The typography plugin styles the slotted prose, so the underline is
    // applied to its links through the `prose-a:` modifier.
    expect(container.querySelector("main > div")).toHaveClass(
      "prose-a:underline"
    )
  })
})
