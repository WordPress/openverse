import { render, screen } from '@testing-library/vue'

import { getAudioObj } from '~~/test/unit/fixtures/audio'

import VAudioDetails from '~/components/VAudioDetails/VAudioDetails.vue'

describe('VAudioDetails', () => {
  let options
  let props

  const overrides = {
    audio_set: {
      title: 'Test Album',
      foreign_landing_url: 'https://www.jamendo.com/album/3661/listen',
      creator: 'Tryad',
      creator_url: 'https://www.jamendo.com/artist/104/tryad',
      url: 'https://usercontent.jamendo.com?type=album&id=3661&width=200',
    },
  }

  beforeEach(() => {
    props = {
      audio: getAudioObj(overrides),
    }
    options = {
      propsData: props,
      stubs: ['VAudioThumbnail', 'VContentReportPopover', 'VLink', 'VMediaTag'],
    }
  })

  it('renders the album title', () => {
    render(VAudioDetails, options)
    screen.getByText('audio-details.table.album')
    const album = screen.getByText(overrides.audio_set.title)
    expect(album).toHaveAttribute(
      'href',
      overrides.audio_set.foreign_landing_url
    )
  })

  it('hides the album title tag when it does not exists', () => {
    options.propsData.audio.audio_set = null
    render(VAudioDetails, options)
    expect(screen.queryByText('Album')).toBeNull()
  })

  it('displays the main filetype when no alternative files are available', () => {
    render(VAudioDetails, options)
    screen.getByText('MP32') // throw if not found
  })

  it('displays multiple filetypes when they are available in alt_files', () => {
    options.propsData.audio.alt_files = [
      { filetype: 'wav' },
      { filetype: 'ogg' },
    ]
    render(VAudioDetails, options)
    screen.getByText('MP32, WAV, OGG')
  })

  it('displays only distinct filetypes', () => {
    options.propsData.audio.alt_files = [
      { filetype: 'ogg' },
      { filetype: 'ogg' },
    ]
    render(VAudioDetails, options)
    screen.getByText('MP32, OGG')
  })
})
