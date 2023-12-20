import { render } from "~~/test/unit/test-utils/render"

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
      props: props,
    }
  })

  it("should contain the correct contents", async () => {
    const { queryAllByText } = await render(VCopyLicense, options)
    expect(queryAllByText(/Copy text/i)).toHaveLength(3)
  })
})
