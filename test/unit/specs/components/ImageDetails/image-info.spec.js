import ImageInfo from '~/components/ImageDetails/ImageInfo'
import render from '../../../test-utils/render'
import i18n from '../../../test-utils/i18n'

describe('Image Info', () => {
  let props = null
  let options = {}
  const $t = (key) => i18n.messages[key]
  beforeEach(() => {
    props = {
      image: {
        id: 0,
        title: 'foo',
        source: 'flickr',
        provider: 'flickr',
        url: 'foo.bar',
        thumbnail: 'http://foo.bar',
        foreign_landing_url: 'http://foo.bar',
        license: 'BY',
        license_version: '1.0',
        creator: 'John',
        creator_url: 'http://creator.com',
      },
      ccLicenseURL: 'http://license.com',
      fullLicenseName: 'LICENSE',
      imageHeight: 1000,
      imageWidth: 500,
    }

    options = {
      propsData: props,
      mocks: {
        $store: {
          state: {
            provider: 'flickr',
            source: 'flickr',
          },
        },
        $t,
      },
    }
  })

  it('should contain the correct contents', () => {
    const wrapper = render(ImageInfo, options)
    expect(wrapper.find('.sidebar_section').element).toBeDefined()
  })

  it('should display image dimensions', () => {
    const wrapper = render(ImageInfo, options)

    expect(wrapper.html()).toContain(`${props.imageWidth}`)
    expect(wrapper.html()).toContain(`${props.imageHeight} pixels`)
  })
})
