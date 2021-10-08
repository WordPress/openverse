import ImageGrid from '~/components/ImageGrid/ImageGrid'
import { render, screen } from '@testing-library/vue'

const propsData = {
  images: [
    { id: 'i1', url: 'http://localhost:8080/i1.png', title: 'image1' },
    { id: 'i2', url: 'http://localhost:8080/i2.jpg', title: 'image2' },
    { id: 'i3', url: 'http://localhost:8080/i3.svg', title: 'image3' },
  ],
  canLoadMore: false,
}
const options = {
  props: propsData,
  stubs: ['NuxtLink', 'LicenseIcons'],
}
describe('ImageGrid', () => {
  it('renders images without load more button if canLoadMore is false', () => {
    options.props.canLoadMore = false
    render(ImageGrid, options)
    expect(screen.queryAllByRole('img').length).toEqual(propsData.images.length)
    expect(screen.queryAllByRole('figure').length).toEqual(
      propsData.images.length
    )
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('renders images and load more button if canLoadMore is true', async () => {
    options.props.canLoadMore = true
    render(ImageGrid, options)
    expect(screen.queryAllByRole('img').length).toEqual(propsData.images.length)
    expect(screen.queryAllByRole('figure').length).toEqual(
      propsData.images.length
    )
    const loadMoreButton = screen.queryByRole('button')
    expect(loadMoreButton).toBeVisible()
    expect(loadMoreButton).toHaveTextContent('browse-page.load')
  })

  it('shows LoadingIcon instead of LoadMoreButton when isFetching', async () => {
    options.props.canLoadMore = true
    options.props.isFetching = true
    render(ImageGrid, options)
    // getByRole('button') does not find the button
    expect(screen.getByText('browse-page.load')).not.toBeVisible()
  })
})
