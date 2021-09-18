import Vuex from 'vuex'
import { createLocalVue } from '@vue/test-utils'
import SearchGridForm from '~/components/SearchGridForm'
import render from '../../test-utils/render'
describe('BrowsePage', () => {
  it('should render correct contents', () => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const wrapper = render(SearchGridForm, {
      localVue,
      mocks: {
        $route: {
          path: '/search',
          $store: { state: { isFilterVisible: true } },
        },
      },
    })

    expect(wrapper.find('form').vm).toBeDefined()
  })
})
