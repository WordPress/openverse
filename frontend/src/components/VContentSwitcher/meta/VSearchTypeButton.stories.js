import { h } from "vue"

import { searchTypes } from "#shared/constants/media"
import { ON } from "#shared/constants/feature-flag"
import { WithTeleportTarget } from "~~/.storybook/decorators/with-teleport-target"
import { useFeatureFlagStore } from "~/stores/feature-flag"

import VSearchTypeButton from "~/components/VContentSwitcher/VSearchTypeButton.vue"

const meta = {
  title: "Components/VContentSwitcher/VSearchTypeButton",
  component: VSearchTypeButton,
  parameters: { height: "480px" },
  decorators: [WithTeleportTarget],

  argTypes: {
    searchType: { options: searchTypes, control: "select" },

    pressed: { control: "boolean" },

    showLabel: { control: "boolean" },

    onClick: { action: "click" },
  },

  args: {
    searchType: "all",
    pressed: false,
    showLabel: false,
  },
}
export default meta

const Template = (args) => ({
  components: { VSearchTypeButton },
  setup() {
    useFeatureFlagStore().toggleFeature("additional_search_types", ON)
    return () => h(VSearchTypeButton, args)
  },
})

export const Default = {
  render: Template.bind({}),
  name: "Default",
}

export const LargePressedWithTextLabel = {
  render: Template.bind({}),
  name: "Large pressed with text label",

  args: {
    pressed: true,
    showLabel: true,
  },
}
