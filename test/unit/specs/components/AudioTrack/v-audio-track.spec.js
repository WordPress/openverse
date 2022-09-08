import { fireEvent, render } from '@testing-library/vue'
import Vuei18n from 'vue-i18n'

import {
  setActivePinia,
  createPinia,
  PiniaVuePlugin,
} from '~~/test/unit/test-utils/pinia'

import { getAudioObj } from '~~/test/unit/fixtures/audio'

import { useActiveMediaStore } from '~/stores/active-media'

import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'

const enMessages = require('~/locales/en.json')

window.HTMLMediaElement.prototype.play = () => {
  /* mock */
}

const mockI18n = new Vuei18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en: enMessages },
})

jest.mock('~/composables/use-browser-detection', () => ({
  useBrowserIsBlink: jest.fn(() => false),
}))

jest.mock('~/composables/use-i18n', () => ({
  useI18n: jest.fn(() => ({
    t: jest.fn((val) => val),
    tc: jest.fn((val) => val),
  })),
}))

const useVueI18n = (vue) => {
  vue.use(Vuei18n)

  return {
    i18n: mockI18n,
  }
}
const useStore = (vue) => {
  vue.use(PiniaVuePlugin)
  const pinia = createPinia()
  const activeMediaStore = useActiveMediaStore(pinia)
  activeMediaStore.$patch({
    state: {
      type: 'audio',
      id: 'e19345b8-6937-49f7-a0fd-03bf057efc28',
      message: null,
      state: 'paused',
    },
  })

  return {
    pinia,
  }
}

const configureVue = (vue) => {
  const { i18n } = useVueI18n(vue)
  const { pinia } = useStore(vue)

  return {
    i18n,
    pinia,
    /** @todo Create a better mock that can be configured to test this behavior.  */
  }
}

const stubs = {
  VPlayPause: true,
  NuxtLink: true,
  VLicense: true,
  VWaveform: true,
}

describe('AudioTrack', () => {
  let options = null
  let props = null

  beforeEach(() => {
    props = {
      audio: getAudioObj(),
    }

    options = {
      propsData: props,
      stubs,
    }

    setActivePinia(createPinia())
  })

  it('should render the full audio track component even without duration', () => {
    const { getByText } = render(VAudioTrack, options, configureVue)
    getByText(props.audio.creator)
  })

  it('should render the row audio track component even without duration', () => {
    options.propsData.layout = 'row'
    const { getByText } = render(VAudioTrack, options, configureVue)
    getByText('by ' + props.audio.creator)
  })

  it('should show audio title as main page title', () => {
    const { getByText } = render(VAudioTrack, options, configureVue)
    // Title text appears multiple times in the track, so need to specify selector
    const element = getByText(props.audio.title, { selector: 'H1' })
    expect(element).toBeInTheDocument()
  })

  it('should show audio creator with link', () => {
    const { getByText } = render(VAudioTrack, options, configureVue)
    const element = getByText(props.audio.creator)
    expect(element).toBeInstanceOf(HTMLAnchorElement)
    expect(element).toHaveAttribute('href', props.audio.creator_url)
  })

  it('on play error displays a message instead of the waveform', async () => {
    options.propsData.audio.url = 'bad.url'
    options.propsData.layout = 'row'
    options.stubs.VPlayPause = false
    options.stubs.VWaveform = false
    options.stubs.VAudioThumbnail = true
    const pauseStub = jest
      .spyOn(window.HTMLMediaElement.prototype, 'pause')
      .mockImplementation(() => undefined)

    const playStub = jest
      .spyOn(window.HTMLMediaElement.prototype, 'play')
      .mockImplementation(() =>
        Promise.reject(new DOMException('msg', 'NotAllowedError'))
      )
    const { getByRole, getByText } = render(VAudioTrack, options, configureVue)

    await fireEvent.click(getByRole('button'))
    await expect(playStub).toHaveBeenCalledTimes(1)
    await expect(pauseStub).toHaveBeenCalledTimes(1)
    await expect(getByText('audio-track.messages.err_unallowed')).toBeVisible()
    // It's not possible to get the vm to test that Sentry has been called
  })
})
