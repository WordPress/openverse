import HeroSection from '~/components/HeroSection'
import render from '../../test-utils/render'
import i18n from '../../test-utils/i18n'

describe('HeroSection', () => {
  let options = {}
  let commitMock = null
  const $t = (key) => i18n.messages[key]
  beforeEach(() => {
    commitMock = jest.fn()
    options = {
      mocks: {
        $store: {
          commit: commitMock,
        },
        $t,
      },
    }
  })
  it('should render correct contents', () => {
    const wrapper = render(HeroSection)
    expect(wrapper.find('.hero').element).toBeDefined()
    expect(wrapper.find('.hero_search-form').element).toBeDefined()
  })

  it('should search when a query is entered', () => {
    const wrapper = render(HeroSection, options)
    const form = wrapper.find('.hero_search-form')
    const input = wrapper.find('input[type="search"]')
    input.setValue('me')
    input.trigger('change')
    form.trigger('submit.prevent')
    expect(commitMock).toHaveBeenCalledWith('SET_QUERY', {
      query: { q: 'me' },
    })
  })
})
