import { useI18n } from "#imports"

import { image as testImage } from "~~/test/unit/fixtures/image"
import { getAudioObj } from "~~/test/unit/fixtures/audio"

import { getMediaMetadata } from "~/utils/metadata"
import { useProviderStore } from "~/stores/provider"

import { AudioDetail } from "~/types/media"

import VMetadata from "~/components/VMediaInfo/VMetadata.vue"
import VLanguageSelect from "~/components/VLanguageSelect/VLanguageSelect.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const testAudio = getAudioObj({
  originalTitle: "Test Audio",
  sensitivity: [],
  isSensitive: false,
}) as unknown as AudioDetail

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    template: `
    <div class="flex flex-col gap-y-2">
      <VLanguageSelect />
      <section class="wrapper flex flex-col p-2 gap-y-2 bg-surface">
        <VMetadata
        v-for="datum in data"
        :key="datum.media.id"
        :metadata="datum.metadata"
        :media="datum.media"
        v-bind="datum"
        class="bg-default"/>
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
      const i18n = useI18n({ useScope: "global" })
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
  }),
}
const meta = {
  title: "Components/VMediaInfo/VMetadata",
  component: VMetadata,
} satisfies Meta<typeof VMetadata>

export default meta
type Story = StoryObj<typeof meta>

export const Default = {
  ...Template,
  name: "VMetadata",
}
