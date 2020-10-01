import NavSection from '~/components/NavSection'
import { SET_QUERY } from '~/store-modules/mutation-types'
import render from '../../test-utils/render'

describe('NavSection', () => {
  it('should render correct contents', () => {
    const wrapper = render(NavSection)
    expect(wrapper.find('nav').vm).toBeDefined()
  })

  it('commits a mutation when the form is submitted', async () => {
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
      mocks: { $store: storeMock },
    }

    const wrapper = render(NavSection, opts)
    await wrapper.setData({ form: { searchTerm: 'foo' } })
    wrapper.find('.hero_search-form').trigger('submit')

    expect(storeMock.commit).toHaveBeenCalledWith(SET_QUERY, {
      query: { q: 'foo' },
    })
  })
})
