import Vuex from 'vuex'
import { createLocalVue } from '@vue/test-utils'
import SearchGridForm from '~/components/SearchGridForm'
import render from '../../test-utils/render'
import i18n from '../../test-utils/i18n'

const $t = (key) => i18n.messages[key]

describe('BrowsePage', () => {
  it('should render correct contents', () => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const wrapper = render(SearchGridForm, {
      localVue,
      mocks: { $route: { path: '/search' }, $t },
    })

    expect(wrapper.find('form').vm).toBeDefined()
  })
})
