import { render } from '@testing-library/vue'
import Vuei18n from 'vue-i18n'
import Vuex from 'vuex'

import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'

jest.mock('~/composables/use-browser-detection', () => ({
  useBrowserIsBlink: jest.fn(() => false),
}))

const enMessages = require('~/locales/en.json')

const useVueI18n = (vue) => {
  vue.use(Vuei18n)

  const i18n = new Vuei18n({
    locale: 'en',
    fallbackLocale: 'en',
    messages: { en: enMessages },
  })

  return {
    i18n,
  }
}
const useVuexStore = (vue) => {
  vue.use(Vuex)

  const store = new Vuex.Store({
    modules: {
      active: {
        namespaced: true,
        state: {
          type: 'audio',
          id: 'e19345b8-6937-49f7-a0fd-03bf057efc28',
          message: null,
          state: 'paused',
        },
      },
    },
  })

  return {
    store,
  }
}

const configureVue = (vue) => {
  const { i18n } = useVueI18n(vue)
  const { store } = useVuexStore(vue)

  return {
    i18n,
    store,
    /** @todo Create a better mock that can be configured to test this behavior.  */
  }
}

const stubs = {
  DownloadButton: true,
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
      audio: {
        id: 'e19345b8-6937-49f7-a0fd-03bf057efc28',
        title: 'La vie des bêtes',
        foreign_landing_url: 'https://www.jamendo.com/track/11188',
        creator: 'AS-POTIRONT!',
        creator_url: 'https://www.jamendo.com/artist/264/as-potiront',
        url: 'https://mp3d.jamendo.com/download/track/11188/mp32',
        license: 'by-nc-sa',
        license_version: '2.5',
        license_url: 'https://creativecommons.org/licenses/by-nc-sa/2.5/',
        provider: 'jamendo',
        source: 'jamendo',
        filetype: 'mp32',
        tags: [
          {
            name: 'vocal',
          },
          {
            name: 'male',
          },
          {
            name: 'speed_medium',
          },
          {
            name: 'party',
          },
          {
            name: 'cuivres',
          },
        ],
        fields_matched: ['tags.name'],
        thumbnail:
          'https://localhost:8000/v1/audio/e19345b8-6937-49f7-a0fd-03bf057efc28/thumb',
        waveform:
          'https://localhost:8000/v1/audio/e19345b8-6937-49f7-a0fd-03bf057efc28/waveform',
        genres: ['pop', 'rock', 'manouche'],
        detail_url:
          'http://localhost:8000/v1/audio/e19345b8-6937-49f7-a0fd-03bf057efc28',
        related_url:
          'http://localhost:8000/v1/audio/e19345b8-6937-49f7-a0fd-03bf057efc28/recommendations',
      },
    }

    options = {
      propsData: props,
      stubs,
      mocks: {
        $nuxt: { context: { i18n: { t: jest.fn() } } },
      },
    }
  })

  it('should render the full audio track component even without duration', () => {
    const { getByText } = render(VAudioTrack, options, configureVue)
    getByText(props.audio.creator)
  })

  it('should render the row audio track component even without duration', () => {
    options.propsData = {
      ...options.propsData,
      layout: 'row',
    }
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
})
