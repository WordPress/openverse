import AudioTrack from '~/components/AudioTrack/AudioTrack'
import { render } from '@testing-library/vue'
import Vuei18n from 'vue-i18n'

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

const stubs = {
  AudioController: true,
  PlayPause: true,
  NuxtLink: true,
  Waveform: true,
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
    }
  })

  it('should render the full audio track component even without duration', () => {
    const { getByText } = render(AudioTrack, options, useVueI18n)
    getByText(props.audio.creator)
  })

  it('should render the row audio track component even without duration', () => {
    options.propsData = {
      ...options.propsData,
      layout: 'row',
    }
    const { getByText } = render(AudioTrack, options, useVueI18n)
    getByText('by ' + props.audio.creator)
  })
})
