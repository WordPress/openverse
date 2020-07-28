import Vuex from 'vuex'
import { createLocalVue } from '@vue/test-utils'
import BrowsePage from '@/pages/BrowsePage'
import render from '../../test-utils/render'

describe('BrowsePage', () => {
  it('should render correct contents', () => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const wrapper = render(BrowsePage, {
      localVue,
      mocks: { $route: { path: '/search' } },
    })

    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined()
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined()
    expect(wrapper.find({ name: 'filter-display' }).vm).toBeDefined()
    expect(wrapper.find({ name: 'search-type-tabs' }).vm).toBeDefined()
  })
})
