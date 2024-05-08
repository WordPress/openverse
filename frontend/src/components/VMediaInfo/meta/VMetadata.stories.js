import { image as testImage } from "~~/test/unit/fixtures/image"
import { getAudioObj } from "~~/test/unit/fixtures/audio"

import { useI18n } from "~/composables/use-i18n"
import { getMediaMetadata } from "~/utils/metadata"
import { useProviderStore } from "~/stores/provider"

import VMetadata from "~/components/VMediaInfo/VMetadata.vue"
import VLanguageSelect from "~/components/VLanguageSelect/VLanguageSelect.vue"

const testAudio = getAudioObj()

const Template = (args) => ({
  template: `
    <div class="flex flex-col gap-y-2">
      <VLanguageSelect />
      <section class="wrapper flex flex-col p-2 gap-y-2 bg-dark-charcoal-06">
        <VMetadata
        v-for="datum in data"
        :key="datum.media.id"
        :metadata="datum.metadata"
        :media="datum.media"
        v-bind="datum"
        class="bg-white"/>
      </section>
    </div>
  `,
  components: { VMetadata, VLanguageSelect },
  setup() {
    const providerStore = useProviderStore()
    providerStore.$patch({
      providers: {
        audio: [{ source_name: testAudio.source }],
        image: [{ source_name: testImage.source }],
      },
      sourceNames: { audio: [testAudio.source], image: [testImage.source] },
    })
    const i18n = useI18n()
    const data = [
      {
        metadata: getMediaMetadata(testImage, i18n, {
          width: testImage.width,
          height: testImage.height,
          type: testImage.filetype,
        }),
        media: testImage,
      },
      {
        metadata: getMediaMetadata(testAudio, i18n),
        media: testAudio,
      },
    ]
    return { args, data }
  },
})

export default {
  title: "Components/VMediaInfo/VMetadata",
  components: VMetadata,
}

export const Default = {
  render: Template.bind({}),
  name: "VMetadata",
}
