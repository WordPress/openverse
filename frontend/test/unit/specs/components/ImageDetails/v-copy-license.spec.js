import { render, screen } from "@testing-library/vue"
import { createLocalVue } from "@vue/test-utils"

import i18n from "~~/test/unit/test-utils/i18n"

import { PiniaVuePlugin, createPinia } from "~~/test/unit/test-utils/pinia"

import VCopyLicense from "~/components/VMediaInfo/VCopyLicense.vue"

const localVue = createLocalVue()
localVue.use(PiniaVuePlugin)

describe("VCopyLicense", () => {
  let options = null
  let props = null

  beforeEach(() => {
    props = {
      media: {
        id: "0",
        title: "foo",
        provider: "flickr",
        url: "foo.bar",
        thumbnail: "http://foo.bar",
        foreign_landing_url: "http://foo.bar",
        license: "BY",
        license_version: "1.0",
        license_url: "http://license.com",
        creator: "John",
        creator_url: "http://creator.com",
        frontendMediaType: "image",
      },
      fullLicenseName: "LICENSE",
    }
    options = {
      localVue,
      propsData: props,
      i18n,
      pinia: createPinia(),
    }
  })

  it("should contain the correct contents", async () => {
    render(VCopyLicense, options)
    expect(
      screen.queryAllByText("media-details.reuse.copy-license.copy-text")
    ).toHaveLength(3)
  })
})
