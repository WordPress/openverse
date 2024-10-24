import { h } from "vue"

import VContentSettingsButton from "~/components/VHeader/VHeaderMobile/VContentSettingsButton.vue"
import VSearchBarButton from "~/components/VHeader/VHeaderMobile/VSearchBarButton.vue"

const meta = {
  title: "Components/VHeader/VHeaderMobile/VSearchBarButton",
  component: VSearchBarButton,

  argTypes: {
    icon: {
      control: { type: "select" },
      options: ["close-small", "chevron-back", "source"],
    },

    rtlFlip: { control: { type: "boolean" } },

    variant: {
      control: { type: "select" },
      options: [
        "filled-white",
        "filled-gray",
        "transparent-gray",
        "transparent-dark",
      ],
    },
    pressed: { control: { type: "boolean" } },

    onClick: { action: "click" },
  },
  args: {
    icon: "close-small",
    label: "VSearchBarButton",
    variant: "filled-white",
  },
}
export default meta

const Template = (args) => ({
  components: { VSearchBarButton },
  setup() {
    return () =>
      h(
        "div",
        { class: "wrapper border-gray-2 inline-flex justify-start p-2" },
        [
          h(VSearchBarButton, {
            label: "VSearchBarButton",
            icon: args.icon,
            ...args,
            onClick: args.click,
          }),
        ]
      )
  },
})

const contentSettingsTemplate = (args) => ({
  components: { VContentSettingsButton },
  setup() {
    return () =>
      h(
        "div",
        { class: "wrapper rounded-sm inline-flex justify-end bg-secondary" },
        [
          h(VContentSettingsButton, {
            label: "VContentSettingsButton",
            areFiltersSelected: true,
            ...args,
          }),
        ]
      )
  },
})

const activeButtonsTemplate = () => ({
  components: { VContentSettingsButton, VSearchBarButton },
  setup() {
    return () =>
      h(
        "div",
        {
          class:
            "wrapper rounded-sm bg-default flex justify-between ring ring-focus",
        },
        [
          h(VSearchBarButton, {
            icon: "chevron-back",
            label: "header.back-button",
            variant: "filled-gray",
            rtlFlip: true,
          }),
          h(VSearchBarButton, {
            icon: "close-small",
            label: "browsePage.searchForm.clear",
            variant: "transparent-gray",
          }),
        ]
      )
  },
})

export const Default = {
  render: Template.bind({}),
  name: "Default",
}

export const ContentSettingsButtonWithFiltersSelected = {
  render: contentSettingsTemplate.bind({}),
  name: "Content Settings Button with filters selected",
}

export const ClearAndBackButtons = {
  render: activeButtonsTemplate.bind({}),
  name: "Clear and Back Buttons",
}
