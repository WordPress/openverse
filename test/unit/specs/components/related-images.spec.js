import RelatedImage from '~/components/RelatedImages'
import render from '../../test-utils/render'
import i18n from '../../test-utils/i18n'

describe('RelatedImage', () => {
  it('should render content when related images are present', () => {
    const $t = (key) => i18n.messages[key]
    const options = {
      propsData: {
        relatedImages: ['img1', 'img2'],
      },
      mocks: {
        $t,
      },
    }
    const wrapper = render(RelatedImage, options)
    expect(wrapper.find('.photo_related-images').element).toBeDefined()
  })

  it('should render nothing when there are no related images', () => {
    const $t = (key) => i18n.messages[key]
    const options = {
      propsData: {
        relatedImages: [],
      },
      mocks: {
        $t,
      },
    }
    const wrapper = render(RelatedImage, options)
    expect(wrapper.find('.photo_related-images').element).toBeUndefined()
  })
})
