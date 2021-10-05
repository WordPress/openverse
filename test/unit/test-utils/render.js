/* eslint-disable no-param-reassign */
import Vuex from 'vuex'
import VueI18n from 'vue-i18n'
import { shallowMount, createLocalVue } from '@vue/test-utils'
import sampleStore from './sample-store'

const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(VueI18n)

const messages = require('../../../src/locales/en.json')
const i18n = new VueI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages,
})

const render = (
  Component,
  options = { localVue, i18n },
  renderer = shallowMount
) => {
  if (!options.store) {
    const store = new Vuex.Store(sampleStore)
    options.store = store
  }
  if (!options.i18n) {
    options.i18n = i18n
  }
  return renderer(Component, options)
}

export default render
