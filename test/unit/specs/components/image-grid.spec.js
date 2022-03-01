import { render, screen } from '@testing-library/vue'
import VueI18n from 'vue-i18n'

import messages from '~/locales/en.json'

import VImageGrid from '~/components/VImageGrid/VImageGrid'

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
  canLoadMore: false,
  fetchState: {
    isFetching: false,
    fetchingError: null,
  },
}
const options = {
  props: propsData,
  stubs: ['NuxtLink', 'VLicense'],
  mocks: {
    $nuxt: {
      context: {
        i18n,
      },
    },
  },
}
describe('VImageGrid', () => {
  it('renders images without load more button if canLoadMore is false', () => {
    options.props.canLoadMore = false
    render(VImageGrid, options)
    expect(screen.queryAllByRole('img').length).toEqual(propsData.images.length)
    expect(screen.queryAllByRole('figure').length).toEqual(
      propsData.images.length
    )
    expect(screen.queryByTestId('load-more')).not.toBeInTheDocument()
  })

  it('renders images and load more button if canLoadMore is true', async () => {
    options.props.canLoadMore = true
    render(VImageGrid, options)
    expect(screen.queryAllByRole('img').length).toEqual(propsData.images.length)
    expect(screen.queryAllByRole('figure').length).toEqual(
      propsData.images.length
    )
    const loadMoreButton = screen.queryByTestId('load-more')
    expect(loadMoreButton).toBeVisible()
    expect(loadMoreButton).toHaveTextContent(messages['browse-page'].load)
  })
})
