import DownloadButton from '~/components/DownloadButton'
import render from '../../test-utils/render'
import { mount } from '@vue/test-utils'
import axios from 'axios'

import local from '~/utils/local'

jest.mock('~/utils/local', () => ({
  get: jest.fn(),
  set: jest.fn(),
}))

const mockFilesizes = {
  'MP3 98kbs': 1000,
  'MP3 VBR': 1500,
  FLAC: 2500,
  OGG: 2000,
}

jest.mock('axios', () => ({
  head: jest.fn((extensionName) => mockFilesizes[extensionName]),
}))

const formats = [
  {
    extension_name: 'MP3 98kbs',
    download_url: 'https://mp3d.jamendo.com/download/track/1532771/mp31/',
  },
  {
    extension_name: 'MP3 VBR',
    download_url: 'https://mp3d.jamendo.com/download/track/1532771/mp32/',
  },
  {
    extension_name: 'FLAC',
    download_url: 'https://mp3d.jamendo.com/download/track/1532771/flac/',
  },
  {
    extension_name: 'OGG',
    download_url: 'https://mp3d.jamendo.com/download/track/1532771/ogg/',
  },
]

const doRender = async () => {
  const wrapper = render(DownloadButton, { propsData: { formats } }, mount)
  await DownloadButton.fetch.call(wrapper.vm)
  return wrapper
}

describe('DownloadButton', () => {
  beforeEach(() => {
    axios.head.mockReset()
  })

  // TODO(@sarayourfriend) convert this to testing-library once it's possible to get the `vm` from the wrapper
  it('should default to the first format', async () => {
    const wrapper = await doRender()
    const downloadLink = wrapper.element.querySelector('a')
    expect(downloadLink.getAttribute('href')).toEqual(formats[0].download_url)
  })

  it('should use the local storage default on first render', async () => {
    local.get.mockImplementationOnce(() => formats[1].extension_name)
    const wrapper = await doRender()
    const downloadLink = wrapper.element.querySelector('a')
    expect(downloadLink.getAttribute('href')).toEqual(formats[1].download_url)
  })

  it('should set the local storage default when a format is selected', async () => {
    const wrapper = await doRender()
    wrapper.find('[aria-haspopup="menu"]').trigger('click')
    wrapper.findAll('[role="menuitem"]').wrappers[1].trigger('click')
    expect(local.set).toHaveBeenCalledWith(
      expect.any(String),
      formats[1].extension_name
    )
  })

  it('should retrieve the filesizes using a head request', async () => {
    await doRender()
    formats.forEach(({ download_url }) =>
      expect(axios.head).toHaveBeenCalledWith(download_url)
    )
  })
})
