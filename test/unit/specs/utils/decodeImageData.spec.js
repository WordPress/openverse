import decodeImageData from '~/utils/decodeImageData'

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
    }

    expect(decodeImageData(data)).toEqual(expected)
  })
})
