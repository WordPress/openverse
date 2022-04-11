import VDownloadButton from '~/components/VDownloadButton.vue'

export default {
  title: 'Components/VDownloadButton',
  component: VDownloadButton,
}

export const Default = () => ({
  template: `<VDownloadButton :formats="formats" />`,
  components: { VDownloadButton },
  data: () => ({
    formats: [
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
    ],
  }),
})
