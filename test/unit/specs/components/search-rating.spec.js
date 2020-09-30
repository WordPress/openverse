import SearchRating from '~/components/SearchRating'
import render from '../../test-utils/render'
import i18n from '../../test-utils/i18n'

describe('SearchRating', () => {
  let options = {}
  let dispatchMock = null
  const $t = (key) => i18n.messages[key]

  beforeEach(() => {
    dispatchMock = jest.fn()
    options = {
      mocks: {
        $store: {
          dispatch: dispatchMock,
        },
        $t,
      },
      propsData: {
        searchTerm: 'foo',
      },
    }
  })

  it('should render rating button', () => {
    const wrapper = render(SearchRating, options)
    expect(wrapper.find('.rating').element).toBeDefined()
  })

  it('does not render rating button after clicking it', () => {
    const wrapper = render(SearchRating, options)
    const button = wrapper.find('.rating-yes')
    button.trigger('click').then(() => {
      expect(wrapper.find('.rating-yes').element).toBeUndefined()
    })
  })

  it('dispatches SEND_SEARCH_RATING_EVENT when clicking rating button', () => {
    const wrapper = render(SearchRating, options)
    const button = wrapper.find('.rating')
    button.trigger('click').then(() => {
      expect(dispatchMock).toHaveBeenLastCalledWith(
        'SEND_SEARCH_RATING_EVENT',
        {
          query: 'foo',
          relevant: true,
        }
      )
    })
  })

  it('dispatches SEND_SEARCH_RATING_EVENT when clicking rating button with relevant as false', () => {
    const wrapper = render(SearchRating, options)
    const button = wrapper.findAll('.rating').wrappers[1]
    button.trigger('click')

    expect(dispatchMock).toHaveBeenLastCalledWith('SEND_SEARCH_RATING_EVENT', {
      query: 'foo',
      relevant: false,
    })
  })

  it('should render thanks message after clicking the rating button', () => {
    const wrapper = render(SearchRating, options)
    const button = wrapper.find('.rating')
    button.trigger('click').then(() => {
      expect(wrapper.find('.thank-you').element).toBeDefined()
    })
  })

  it('renders neither rating button nor thanks message 1.5s after clicking rating button', (done) => {
    const wrapper = render(SearchRating, options)
    const button = wrapper.find('.rating-no')
    button.trigger('click').then(() => {
      setTimeout(() => {
        expect(wrapper.find('.rating-yes').element).toBeUndefined()
        expect(wrapper.find('.thank-you').element).toBeUndefined()
        done()
      }, 1550)
    })
  })
})
