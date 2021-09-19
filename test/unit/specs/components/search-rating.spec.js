import SearchRating from '~/components/SearchRating'
import render from '../../test-utils/render'
import { USAGE_DATA } from '~/constants/store-modules'
import { SEND_SEARCH_RATING_EVENT } from '~/constants/usage-data-analytics-types'

describe('SearchRating', () => {
  let options = {}
  let dispatchMock = null

  beforeEach(() => {
    dispatchMock = jest.fn()
    options = {
      mocks: {
        $store: {
          dispatch: dispatchMock,
        },
      },
      propsData: {
        searchTerm: 'foo',
      },
    }
  })

  it('should render rating button', async () => {
    const wrapper = render(SearchRating, options)
    expect(wrapper.find('.rating').element).toBeDefined()
  })

  it('does not render rating button after clicking it', async () => {
    const wrapper = render(SearchRating, options)
    const button = wrapper.find('.rating-yes')
    await button.trigger('click')
    expect(wrapper.find('.rating-yes').element).toBeUndefined()
  })

  it('dispatches SEND_SEARCH_RATING_EVENT when clicking rating button', async () => {
    const wrapper = render(SearchRating, options)
    const button = wrapper.find('.rating')
    await button.trigger('click')

    expect(dispatchMock).toHaveBeenLastCalledWith(
      `${USAGE_DATA}/${SEND_SEARCH_RATING_EVENT}`,
      {
        query: 'foo',
        relevant: true,
      }
    )
  })

  it('dispatches SEND_SEARCH_RATING_EVENT when clicking rating button with relevant as false', async () => {
    const wrapper = render(SearchRating, options)
    const button = wrapper.findAll('.rating').wrappers[1]
    await button.trigger('click')

    expect(dispatchMock).toHaveBeenLastCalledWith(
      `${USAGE_DATA}/${SEND_SEARCH_RATING_EVENT}`,
      {
        query: 'foo',
        relevant: false,
      }
    )
  })

  it('should render thanks message after clicking the rating button', async () => {
    const wrapper = render(SearchRating, options)
    const button = wrapper.find('.rating')
    await button.trigger('click')
    expect(wrapper.find('.thank-you').element).toBeDefined()
  })

  it('renders neither rating button nor thanks message 1.5s after clicking rating button', async (done) => {
    const wrapper = render(SearchRating, options)
    const button = wrapper.find('.rating-no')
    await button.trigger('click')

    setTimeout(() => {
      expect(wrapper.find('.rating-yes').element).toBeUndefined()
      expect(wrapper.find('.thank-you').element).toBeUndefined()
      done()
    }, 1550)
  })
})
