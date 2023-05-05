import { createLocalVue } from "@vue/test-utils"
import { render, screen } from "@testing-library/vue"
import VueI18n from "vue-i18n"

import i18n from "~~/test/unit/test-utils/i18n"
import { PiniaVuePlugin, createPinia } from "~~/test/unit/test-utils/pinia"

import { getAudioObj } from "~~/test/unit/fixtures/audio"

import VRelatedAudio from "~/components/VAudioDetails/VRelatedAudio.vue"

const audioResults = [getAudioObj(), getAudioObj()]

const localVue = createLocalVue()
localVue.use(VueI18n)
localVue.use(PiniaVuePlugin)

const doRender = () => {
  const pinia = createPinia()

  return render(VRelatedAudio, {
    localVue,
    pinia,
    i18n,
    propsData: {
      media: audioResults,
      fetchState: { isFetching: false, isError: false },
    },
    mocks: {
      $nuxt: {
        context: {
          i18n: { t: (val) => val, tc: (val) => val },
        },
      },
    },
    stubs: { LoadingIcon: true, VAudioThumbnail: true },
  })
}

describe("VRelatedAudio", () => {
  it("should render content when finished loading related audios", async () => {
    doRender()

    expect(screen.findByText("audio-details.related-audios"))

    expect(screen.queryAllByLabelText("play-pause.play")).toHaveLength(
      // Two for each as the "row" layout rendered by VRelatedAudio
      // renders a "large" and "small" version that are visually hidden by a parent
      // depending on the breakpoint (but critically still rendered in the
      // DOM)
      audioResults.length * 2
    )
  })
})
