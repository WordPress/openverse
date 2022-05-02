import { render, screen } from '@testing-library/vue'
import VueI18n from 'vue-i18n'
import { createPinia, PiniaVuePlugin } from 'pinia'
import { createLocalVue } from '@vue/test-utils'

import messages from '~/locales/en.json'

import VImageGrid from '~/components/VImageGrid/VImageGrid.vue'

const i18n = new VueI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en: messages },
})

const propsData = {
  images: [
    { id: 'i1', url: 'http://localhost:8080/i1.png', title: 'image1' },
    { id: 'i2', url: 'http://localhost:8080/i2.jpg', title: 'image2' },
    { id: 'i3', url: 'http://localhost:8080/i3.svg', title: 'image3' },
  ],
  fetchState: {
    isFetching: false,
    fetchingError: null,
  },
}

describe('VImageGrid', () => {
  let localVue
  let pinia
  let options
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(PiniaVuePlugin)
    pinia = createPinia()
    options = {
      localVue,
      pinia,
      props: propsData,
      stubs: ['NuxtLink', 'VLicense'],
      mocks: { $nuxt: { context: { i18n } } },
    }
  })
  it('renders images without load more button', () => {
    render(VImageGrid, options)
    expect(screen.queryAllByRole('img').length).toEqual(propsData.images.length)
    expect(screen.queryAllByRole('figure').length).toEqual(
      propsData.images.length
    )
    expect(screen.queryByTestId('load-more')).not.toBeVisible()
  })
})
