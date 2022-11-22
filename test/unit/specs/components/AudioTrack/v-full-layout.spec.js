import { createLocalVue } from '@vue/test-utils'
import { render, screen } from '@testing-library/vue'

import { getAudioObj } from '~~/test/unit/fixtures/audio'
import { PiniaVuePlugin, createPinia } from '~~/test/unit/test-utils/pinia'

import VFullLayout from '~/components/VAudioTrack/layouts/VFullLayout.vue'

const localVue = createLocalVue()
localVue.use(PiniaVuePlugin)

describe('VFullLayout', () => {
  it('should render the weblink button with the foreign landing url', () => {
    const audio = getAudioObj()

    render(VFullLayout, {
      localVue,
      pinia: createPinia(),
      propsData: {
        audio,
        size: 's',
        status: 'playing',
        currentTime: 1,
      },
    })

    const downloadButton = screen.getByText('audio-details.weblink')
    expect(downloadButton).toHaveAttribute('href', audio.foreign_landing_url)
  })
})
