import RelatedImage from '~/components/RelatedImages'
import render from '../../test-utils/render'

describe('RelatedImage', () => {
  it('should render content when related images are present', () => {
    const options = {
      propsData: {
        relatedImages: ['img1', 'img2'],
      },
    }
    const wrapper = render(RelatedImage, options)
    expect(wrapper.find('.photo_related-images').element).toBeDefined()
  })

  it('should render nothing when there are no related images', () => {
    const options = {
      propsData: {
        relatedImages: [],
      },
    }
    const wrapper = render(RelatedImage, options)
    expect(wrapper.find('.photo_related-images').element).toBeUndefined()
  })
})
