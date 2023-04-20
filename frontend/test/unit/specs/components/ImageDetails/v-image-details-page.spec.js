import VueI18n from "vue-i18n"

import { createLocalVue } from "@vue/test-utils"
import { fireEvent, render, screen } from "@testing-library/vue"

import { PiniaVuePlugin, createPinia } from "~~/test/unit/test-utils/pinia"
import i18n from "~~/test/unit/test-utils/i18n"

import { useAnalytics } from "~/composables/use-analytics"
import { IMAGE } from "~/constants/media"

import VImageDetailsPage from "~/pages/image/_id/index.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(() => ({
    sendCustomEvent: jest.fn(),
  })),
}))

jest.mock("~/stores/media/single-result", () => ({
  useSingleResultStore: jest.fn(() => ({
    mediaType: "image",
    mediaItem: imageObject,
  })),
}))

const imageObject = {
  id: "123",
  provider: "test-provider",
  foreign_landing_url: "https://test.com",
  frontendMediaType: "image",
}

const localVue = createLocalVue()
localVue.use(PiniaVuePlugin)
localVue.use(VueI18n)

describe("VImageDetailsPage", () => {
  it("should send GET_MEDIA analytics event on CTA button click", async () => {
    const sendCustomEventMock = jest.fn()
    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))

    render(VImageDetailsPage, {
      localVue,
      pinia: createPinia(),
      i18n,
      mocks: {
        $route: {
          params: {
            meta: "url",
          },
        },
      },
    })

    const downloadButton = screen.getByText("image-details.weblink")
    await fireEvent.click(downloadButton)

    expect(sendCustomEventMock).toHaveBeenCalledWith("GET_MEDIA", {
      id: imageObject.id,
      mediaType: IMAGE,
      provider: imageObject.provider,
    })
  })
})
