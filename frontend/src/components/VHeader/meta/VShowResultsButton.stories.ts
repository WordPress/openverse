import { h } from "vue"

import VShowResultsButton from "~/components/VHeader/VHeaderMobile/VShowResultsButton.vue"

import type { StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VHeader/VHeaderMobile/VShowResultsButton",
  component: VShowResultsButton,
}

export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VShowResultsButton },
    setup() {
      return () => h(VShowResultsButton, args)
    },
  }),
}
export const Default = {
  ...Template,
  name: "Default",
}

export const Fetching = {
  ...Template,
  name: "Fetching",

  args: {
    isFetching: true,
  },
}
