import { Meta, StoryObj } from "@storybook/vue3"

import { h } from "vue"

import { audioStatuses } from "~/constants/audio"

import VAudioControl from "~/components/VAudioTrack/VAudioControl.vue"

const meta = {
  title: "Components/Audio track/Audio control",
  component: VAudioControl,

  argTypes: {
    status: {
      options: audioStatuses,
      control: "select",
    },

    size: {
      options: ["small", "medium", "large"],
      control: "select",
    },

    onToggle: { action: "toggle" },
  },
} satisfies Meta<typeof VAudioControl>

export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VAudioControl },
    setup() {
      return () => h(VAudioControl, args)
    },
  }),
}

export const Default = {
  ...Template,
  name: "Default",

  args: {
    status: "playing",
    size: "large",
  },
}

export const Disabled = {
  ...Template,
  name: "Disabled",

  args: {
    disabled: true,
    status: "playing",
    size: "medium",
  },
}
