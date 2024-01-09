import { render } from "@testing-library/vue"

import { i18n } from "~~/test/unit/test-utils/i18n"

import VCopyLicense from "~/components/VMediaInfo/VCopyLicense.vue"

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
      propsData: props,
      global: {
        plugins: [i18n],
      },
    }
  })

  it("should contain the correct contents", () => {
    const { queryAllByText } = render(VCopyLicense, options)
    expect(queryAllByText(/Copy text/i)).toHaveLength(3)
  })
})
