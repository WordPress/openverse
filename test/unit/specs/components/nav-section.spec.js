import NavSection from '~/components/NavSection'
import { SET_QUERY } from '~/store-modules/mutation-types'
import render from '../../test-utils/render'
import i18n from '../../test-utils/i18n'

describe('NavSection', () => {
  it('should render correct contents', () => {
    const wrapper = render(NavSection)
    expect(wrapper.find('nav').vm).toBeDefined()
  })

  it('commits a mutation when the form is submitted', () => {
    const $t = (key) => i18n.messages[key]
    const storeMock = {
      dispatch: jest.fn(),
      commit: jest.fn(),
      state: {
        shareLists: {
          length: 2,
        },
      },
    }
    const opts = {
      propsData: {
        fixedNav: null,
        showNavSearch: 'true',
      },
      mocks: {
        $store: storeMock,
        $t,
      },
    }
    const wrapper = render(NavSection, opts)
    wrapper.setData({ form: { searchTerm: 'foo' } })
    wrapper.find('.hero_search-form').trigger('submit')
    expect(storeMock.commit).toHaveBeenCalledWith(SET_QUERY, {
      query: { q: 'foo' },
    })
  })
})
