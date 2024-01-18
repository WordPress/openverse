import { createPinia, setActivePinia } from "~~/test/unit/test-utils/pinia"

import { decodeMediaData } from "~/utils/decode-media-data"
import { IMAGE } from "~/constants/media"

const requiredFields = {
  id: "id",
  url: "https://example.com/image.jpg",
  foreign_landing_url: "https://example.com",
  license: "by",
  license_version: "4.0",
  attribution: "Attribution",

  category: null,
  provider: "provider",

  detail_url: "url",
  related_url: "url",

  sensitivity: [],
  isSensitive: false,

  tags: [],
}

describe("decodeImageData", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it("decodes symbols correctly", async () => {
    const data = {
      ...requiredFields,
      creator: "S\\xe3",
      title: "S\\xe9",
      tags: [{ name: "ma\\xdf" }],
    }

    const expected = {
      ...requiredFields,
      title: "Sé",
      originalTitle: "Sé",
      creator: "Sã",
      tags: [{ name: "maß" }],
      frontendMediaType: IMAGE,
    }

    expect(decodeMediaData(data, IMAGE)).toEqual(expected)
  })

  it("strips the extension if the same as media filetype", async () => {
    const data = {
      ...requiredFields,
      creator: "Creator",
      title: "Image.JPEG",
      filetype: "jpg",
    }

    const expected = {
      ...requiredFields,
      title: "Image",
      originalTitle: "Image.JPEG",
      creator: "Creator",
      filetype: "jpg",
      frontendMediaType: IMAGE,
    }

    expect(decodeMediaData(data, IMAGE)).toEqual(expected)
  })

  it("strips the extension if the same as url extension", async () => {
    const data = {
      ...requiredFields,
      url: "https://example.com/image.jpg",
      creator: "Creator",
      title: "Image.JPG",
    }

    const expected = {
      ...requiredFields,
      title: "Image",
      originalTitle: "Image.JPG",
      creator: "Creator",
      frontendMediaType: IMAGE,
    }

    expect(decodeMediaData(data, IMAGE)).toEqual(expected)
  })

  it("does not strip the extension if different from filetype in url extension", async () => {
    const data = {
      ...requiredFields,
      url: "https://example.com/image.png",
      creator: "Creator",
      title: "Image.JPG",
    }

    const expected = {
      ...requiredFields,
      url: "https://example.com/image.png",
      title: "Image.JPG",
      originalTitle: "Image.JPG",
      creator: "Creator",
      frontendMediaType: IMAGE,
    }

    expect(decodeMediaData(data, IMAGE)).toEqual(expected)
  })
})
