import { h } from "vue"

import VContentReportModal from "~/components/VContentReport/VContentReportModal.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VContentReportModal",
  component: VContentReportModal,
} satisfies Meta<typeof VContentReportModal>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VContentReportModal },
    setup() {
      return () =>
        h("div", { id: "teleports" }, [
          h("div", [h(VContentReportModal, { ...args, class: "float-right" })]),
        ])
    },
  }),
  name: "Default",

  args: {
    media: {
      id: "0aff3595-8168-440b-83ff-7a80b65dea42",
      foreign_landing_url: "https://wordpress.org/openverse/",
      provider: "provider",
      providerName: "providerName",
      frontendMediaType: "image",
    },
  },
}
