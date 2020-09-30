import Vuex from 'vuex'
import { createLocalVue } from '@vue/test-utils'
import BrowsePage from '~/pages/search'
import render from '../../test-utils/render'

describe('BrowsePage', () => {
  it('should render correct contents', () => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const wrapper = render(BrowsePage, {
      localVue,
      mocks: { $route: { path: '/search' } },
    })

    expect(wrapper.find({ name: 'FilterDisplay' }).vm).toBeDefined()
    expect(wrapper.find({ name: 'SearchTypeTabs' }).vm).toBeDefined()
  })
})
