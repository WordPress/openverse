import VueI18n from 'vue-i18n'
import { createLocalVue } from '@vue/test-utils'
import { render, screen } from '@testing-library/vue'
import { createPinia, PiniaVuePlugin } from 'pinia'

import messages from '~/locales/en.json'

import VRelatedImages from '~/components/VImageDetails/VRelatedImages.vue'

const media = [
  { id: 'img1', url: 'https://wp.org/img1.jpg' },
  { id: 'img2', url: 'https://wp.org/img2.jpg' },
]
const i18n = new VueI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en: messages },
})
const localVue = createLocalVue()
localVue.use(VueI18n)
localVue.use(PiniaVuePlugin)
describe('RelatedImage', () => {
  let props
  let options
  let pinia
  beforeEach(() => {
    pinia = createPinia()
    props = { media, fetchState: { isFetching: false } }
    options = {
      localVue,
      pinia,
      propsData: props,
      stubs: ['VLicense', 'NuxtLink'],
      mocks: { $nuxt: { context: { i18n } } },
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
