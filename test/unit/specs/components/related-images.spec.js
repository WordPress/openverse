import VueI18n from 'vue-i18n'
import { createLocalVue } from '@vue/test-utils'
import { render, screen } from '@testing-library/vue'

import VRelatedImages from '~/components/VImageDetails/VRelatedImages.vue'

const media = [
  { id: 'img1', url: 'https://wp.org/img1.jpg' },
  { id: 'img2', url: 'https://wp.org/img2.jpg' },
]
const localVue = createLocalVue()
localVue.use(VueI18n)

describe('RelatedImage', () => {
  let props = null
  let options = null
  beforeEach(() => {
    props = { media, fetchState: { isFetching: false } }
    options = {
      localVue,
      propsData: props,
      stubs: ['VLicense', 'NuxtLink'],
    }
  })
  it('should render an image grid', () => {
    render(VRelatedImages, options)

    expect(screen.getByRole('heading').textContent).toContain(
      'image-details.related-images'
    )
    expect(screen.queryAllByRole('img').length).toEqual(2)
    expect(screen.queryAllByRole('figure').length).toEqual(2)
  })

  it('should not render data when media array is empty', () => {
    options.propsData.media = []
    render(VRelatedImages, options)
    expect(screen.getByRole('heading').textContent).toContain(
      'image-details.related-images'
    )
    expect(screen.queryAllByRole('img').length).toEqual(0)
  })
})
