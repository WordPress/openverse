import { render } from '@testing-library/vue'
import Vuei18n from 'vue-i18n'
import { createLocalVue } from '@vue/test-utils'

import { getAudioObj } from '~~/test/unit/fixtures/audio'

import VBoxLayout from '~/components/VAudioTrack/layouts/VBoxLayout.vue'

const enMessages = require('~/locales/en.json')

const i18n = new Vuei18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en: enMessages },
})

describe('VBoxLayout', () => {
  let options = null
  let localVue
  let props = {
    audio: getAudioObj(),
    size: 'm',
  }

  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuei18n)
    options = {
      propsData: props,
      mocks: { $nuxt: { context: { i18n } } },
      localVue,
      i18n,
    }
  })

  it('renders audio title, license and category in v-box-layout', () => {
    props.audio.category = 'music'
    const screen = render(VBoxLayout, options)
    screen.getByText(props.audio.title)
    screen.getByLabelText('Attribution-NonCommercial-Share-Alike')
    screen.getByText('Music')
  })

  it('should not render category string if category is null', () => {
    props.audio.category = null
    const screen = render(VBoxLayout, options)
    const categoryLabel = screen.queryByText('Music')
    expect(categoryLabel).toBeNull()
  })
})
