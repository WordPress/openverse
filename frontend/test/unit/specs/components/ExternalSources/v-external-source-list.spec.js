import { screen } from "@testing-library/vue"
import userEvent from "@testing-library/user-event"

import { render } from "~~/test/unit/test-utils/render"

import { useAnalytics } from "~/composables/use-analytics"
import { IMAGE } from "~/constants/media"

import VExternalSourceList from "~/components/VExternalSearch/VExternalSourceList.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))

describe("VExternalSourceList", () => {
  let propsData
  let sendCustomEventMock

  beforeEach(() => {
    sendCustomEventMock = jest.fn()
    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))
    propsData = {
      searchTerm: "cat",
      mediaType: IMAGE,
      externalSources: [
        { name: "source1", url: "https://source1.com/?q=cat" },
        { name: "source2", url: "https://source2.com/?q=cat" },
      ],
    }
    render(VExternalSourceList, {
      props: propsData,
    })
  })

  it("should render external sources links", () => {
    expect(screen.queryAllByRole("link")).toHaveLength(
      propsData.externalSources.length
    )
  })

  it("should send SELECT_EXTERNAL_SOURCE analytics event on CTA button click", async () => {
    const source1Link = screen.getByRole("link", {
      name: propsData.externalSources[0].name,
    })

    const user = userEvent.setup()
    await user.click(source1Link)

    expect(sendCustomEventMock).toHaveBeenCalledWith("SELECT_EXTERNAL_SOURCE", {
      mediaType: IMAGE,
      name: propsData.externalSources[0].name,
      query: propsData.searchTerm,
      component: "VExternalSourceList",
    })
  })
})
