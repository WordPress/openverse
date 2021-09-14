import DownloadButton from '~/components/DownloadButton'

export default {
  title: 'Components/DownloadButton',
  component: DownloadButton,
}

export const Default = () => ({
  template: `<DownloadButton :file-name="fileName" :formats="formats" />`,
  components: { DownloadButton },
  data: () => ({
    formats: [
      {
        extension_name: 'MP3 98kbs',
        download_url: 'https://mp3d.jamendo.com/download/track/1532771/mp31/',
        filesize: 676352,
      },
      {
        extension_name: 'MP3 VBR',
        download_url: 'https://mp3d.jamendo.com/download/track/1532771/mp32/',
        filesize: 1362432,
      },
      {
        extension_name: 'FLAC',
        download_url: 'https://mp3d.jamendo.com/download/track/1532771/flac/',
        filesize: 6333717,
      },
      {
        extension_name: 'OGG',
        download_url: 'https://mp3d.jamendo.com/download/track/1532771/ogg/',
        filesize: 1362432,
      },
    ],
  }),
})
