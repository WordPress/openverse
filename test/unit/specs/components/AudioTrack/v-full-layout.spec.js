import { render, screen } from '@testing-library/vue'

import { getAudioObj } from '~~/test/unit/fixtures/audio'

import VFullLayout from '~/components/VAudioTrack/layouts/VFullLayout.vue'

describe('VFullLayout', () => {
  it('should render the download button with the foreign landing url', () => {
    const audio = getAudioObj()
    render(VFullLayout, {
      props: {
        audio,
        size: 's',
        status: 'playing',
        currentTime: 1,
      },
    })

    const downloadButton = screen.getByText('download-button.download')
    expect(downloadButton).toHaveAttribute('href', audio.foreign_landing_url)
  })
})
