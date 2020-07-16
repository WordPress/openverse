/* eslint-disable no-param-reassign */
import Vuex from 'vuex'
import { shallowMount, createLocalVue } from '@vue/test-utils'
import sampleStore from '../sampleStore/'

const localVue = createLocalVue()
localVue.use(Vuex)

const render = (Component, options = { localVue }) => {
  if (!options.store) {
    const store = new Vuex.Store(sampleStore)
    options.store = store
  }

  return shallowMount(Component, options)
}

export default render
