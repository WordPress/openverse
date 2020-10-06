import getLegacySourceUrl, { legacySourceMap } from '~/utils/getLegacySourceUrl'

/**
 * Note, this doesn *not* test the accuracy of urls in terms of getting the correct results,
 * but only that a valid url is returned for each avaliable provider
 */
describe('getLegacySourceUrl', () => {
  it('returns a url for each audio source', () => {
    const search = { q: 'dogs' }
    const audioSources = Object.keys(legacySourceMap).filter(
      (sourceName) => legacySourceMap[sourceName].audio
    )
    const getAudioSourceUrl = getLegacySourceUrl('audio')
    const urls = audioSources.map((sourceName) =>
      getAudioSourceUrl(sourceName, search)
    )

    expect(urls.every((url) => url.startsWith('http'))).toBeTruthy()
  })

  it('returns a url for each video source', () => {
    const search = { q: 'dogs' }
    const audioSources = Object.keys(legacySourceMap).filter(
      (sourceName) => legacySourceMap[sourceName].video
    )
    const getVideoSourceUrl = getLegacySourceUrl('video')
    const urls = audioSources.map((sourceName) =>
      getVideoSourceUrl(sourceName, search)
    )

    expect(urls.every((url) => url.startsWith('http'))).toBeTruthy()
  })

  it('returns a url for each image source', () => {
    const search = { q: 'dogs' }
    const audioSources = Object.keys(legacySourceMap).filter(
      (sourceName) => legacySourceMap[sourceName].image
    )
    const getImageSourceUrl = getLegacySourceUrl('image')
    const urls = audioSources.map((sourceName) =>
      getImageSourceUrl(sourceName, search)
    )

    expect(urls.every((url) => url.startsWith('http'))).toBeTruthy()
  })

  it('throws an error for invalid sources', () => {
    const search = { q: 'dogs' }
    const getImageSourceUrl = getLegacySourceUrl('image')

    expect(() => {
      getImageSourceUrl('Fake Source', search)
    }).toThrow('Fake Source')
  })

  it('throws an error for valid sources but an invalid content type', () => {
    const search = { q: 'dogs' }
    const getImageSourceUrl = getLegacySourceUrl('paintings')

    expect(() => {
      getImageSourceUrl(Object.keys(legacySourceMap)[0], search)
    }).toThrow('paintings')
  })
})
