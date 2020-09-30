/* eslint-disable no-param-reassign */
import Vuex from 'vuex'
import VueI18n from 'vue-i18n'
import { shallowMount, createLocalVue } from '@vue/test-utils'
import sampleStore from '../sampleStore/'
import { glob } from 'glob'

const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(VueI18n)

const messages = require('../../../src/locales/en.json')
const i18n = new VueI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages,
})

// Since we're using @nuxt/components to auto-register vue components
// (which means we're not including `components: {}` in our single-file vue components)
// We need to register all components globally here!
glob('src/components/**/*.vue', (_, matches) => {
  matches.forEach((path) => {
    const name = path.match(/(\w*)\.vue$/)[1]
    localVue.component(name, require(`../../../${path}`).default)
  })
})

const render = (Component, options = { localVue, i18n }) => {
  if (!options.store) {
    const store = new Vuex.Store(sampleStore)
    options.store = store
  }

  return shallowMount(Component, options)
}

export default render
