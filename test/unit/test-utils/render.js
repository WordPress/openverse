import VueI18n from 'vue-i18n'
import { shallowMount, createLocalVue } from '@vue/test-utils'

const localVue = createLocalVue()
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
  if (!options.i18n) {
    options.i18n = i18n
  }
  return renderer(Component, options)
}

export default render
