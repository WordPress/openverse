import { screen } from "@testing-library/vue"
import { default as userEvent } from "@testing-library/user-event"

import { render } from "~~/test/unit/test-utils/render"

import { useAnalytics } from "~/composables/use-analytics"
import { IMAGE } from "~/constants/media"
import { getAdditionalSources } from "~/utils/get-additional-sources"

import VExternalSourceList from "~/components/VExternalSearch/VExternalSourceList.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))

describe("VExternalSourceList", () => {
  let propsData
  let sendCustomEventMock
  const searchTerm = "cat"
  const expectedImageSources = getAdditionalSources(IMAGE, { q: searchTerm })

  beforeEach(() => {
    sendCustomEventMock = jest.fn()
    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))
    propsData = {
      searchTerm,
      mediaType: IMAGE,
    }
    render(VExternalSourceList, {
      props: propsData,
    })
  })

  it("should render external sources links", () => {
    expect(screen.queryAllByRole("link")).toHaveLength(
      expectedImageSources.length
    )
  })

  it("should send SELECT_EXTERNAL_SOURCE analytics event on CTA button click", async () => {
    const source1Link = screen.getByRole("link", {
      name: expectedImageSources[0].name,
    })

    const user = userEvent.setup()
    await user.click(source1Link)

    expect(sendCustomEventMock).toHaveBeenCalledWith("SELECT_EXTERNAL_SOURCE", {
      mediaType: IMAGE,
      name: expectedImageSources[0].name,
      query: propsData.searchTerm,
      component: "VExternalSourceList",
    })
  })
})
