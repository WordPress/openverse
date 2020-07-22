import ImageInfo from '@/components/ImageDetails/ImageInfo'
import render from '../../../test-utils/render'

describe('Image Info', () => {
  let props = null
  let options = {}
  let mocks = {}

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

    mocks = {
      $store: {
        state: {
          provider: 'flickr',
          source: 'flickr',
        },
      },
    }

    options = {
      propsData: props,
      mocks,
    }
  })

  it('should contain the correct contents', () => {
    const wrapper = render(ImageInfo, options)
    expect(wrapper.find('.sidebar_section').element).toBeDefined()
  })

  it('should contain correct information', () => {
    const wrapper = render(ImageInfo, options)
    expect(wrapper.html()).toContain(props.image.title)
    expect(wrapper.find('.photo_license').text()).toBe(props.fullLicenseName)
  })

  it('should display image dimensions', () => {
    const wrapper = render(ImageInfo, options)

    expect(wrapper.html()).toContain(`${props.imageWidth}`)
    expect(wrapper.html()).toContain(`${props.imageHeight} pixels`)
  })
})
