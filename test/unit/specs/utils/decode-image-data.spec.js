import { decodeMediaData } from '~/utils/decode-media-data'
import { IMAGE } from '~/constants/media'

describe('decodeImageData', () => {
  it('returns empty string for empty string', () => {
    const data = {
      creator: 'S\\xe3',
      title: 'S\\xe9',
      tags: [{ name: 'ma\\xdf' }],
    }

    const expected = {
      title: 'Sé',
      creator: 'Sã',
      tags: [{ name: 'maß' }],
      frontendMediaType: IMAGE,
    }

    expect(decodeMediaData(data, IMAGE)).toEqual(expected)
  })
})
