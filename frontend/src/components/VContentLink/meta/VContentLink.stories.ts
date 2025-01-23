import { h } from "vue"

import { SupportedMediaType } from "#shared/constants/media"

import VContentLink from "~/components/VContentLink/VContentLink.vue"

import type { StoryObj } from "@storybook/vue3"

const contentLinkArgTypes = {
  mediaType: { options: ["audio", "image"], control: { type: "radio" } },
  isSelected: { control: { type: "boolean" } },
  layout: { options: ["stacked", "horizontal"], control: { type: "radio" } },
}

const meta = {
  title: "Components/VContentLink",
  component: VContentLink,
  argTypes: contentLinkArgTypes,
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VContentLink },
    setup() {
      return () => h(VContentLink, args)
    },
  }),
  name: "Default",

  args: {
    mediaType: "image",
    labels: {
      aria: `View 5708 image results for cat`,
      visible: `View 5708 image`,
    },
    to: "/search/image/?q=cat",
  },
}

export const Horizontal: Story = {
  name: "Horizontal",
  render: (args) => ({
    components: { VContentLink },
    setup() {
      const count = { image: 5708, audio: 4561 }[args.mediaType]
      const labels = {
        aria: `View ${count} ${args.mediaType} results for cat`,
        visible: `View ${count} ${args.mediaType}`,
      }
      return () =>
        h("div", { class: "max-w-md" }, [h(VContentLink, { ...args, labels })])
    },
  }),
  args: {
    mediaType: "audio",
    layout: "horizontal",
  } as typeof VContentLink.props,
}

export const Mobile: Omit<Story, "args"> = {
  render: () => ({
    components: { VContentLink },
    setup() {
      const types = [
        { mediaType: "image", resultsCount: 4321 },
        { mediaType: "audio", resultsCount: 1234 },
      ]
      return () =>
        h(
          "div",
          { class: "max-w-md mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0" },
          types.map(({ mediaType, resultsCount }, key) =>
            h(VContentLink, {
              mediaType: mediaType as SupportedMediaType,
              labels: {
                aria: `View ${resultsCount} ${mediaType} results for cat`,
                visible: `View ${resultsCount} ${mediaType}`,
              },
              to: `/search/${mediaType}/?q=cat`,
              key,
            })
          )
        )
    },
  }),
  name: "Mobile",

  parameters: {
    viewport: {
      defaultViewport: "xs",
    },
  },
}
