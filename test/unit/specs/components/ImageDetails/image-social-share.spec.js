import ImageSocialShare from '~/components/ImageDetails/ImageSocialShare'
import render from '../../../test-utils/render'

describe('ImageSocialShare', () => {
  let options = null
  let props = null

  beforeEach(() => {
    props = {
      image: {
        id: 0,
        title: 'foo',
        provider: 'flickr',
        url: 'foo.bar',
        thumbnail: 'http://foo.bar',
        foreign_landing_url: 'http://foo.bar',
        license: 'BY',
        license_version: '1.0',
        creator: 'John',
        creator_url: 'http://creator.com',
      },
    }

    options = {
      propsData: props,
    }
  })

  it('should render social buttons', () => {
    const wrapper = render(ImageSocialShare, options)
    expect(
      wrapper.findComponent({ name: 'SocialShareButtons' }).exists()
    ).toBeTruthy()
  })

  it('should invoke social share buttons with the right props', () => {
    const wrapper = render(ImageSocialShare, options)
    const sourceURL = options.propsData.image.foreign_landing_url
    const url = options.propsData.image.url
    expect(wrapper.vm.imageURL).toBe(url)
    expect(wrapper.vm.imageSourceURL).toBe(sourceURL)
    expect(wrapper.vm.shareText).toBe(
      encodeURI(
        `I found an image through WP Photos @creativecommons: ${sourceURL}`
      )
    )
  })
})
