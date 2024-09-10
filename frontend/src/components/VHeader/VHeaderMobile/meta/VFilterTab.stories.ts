import { defineComponent, h } from "vue"

import VFilterTab from "~/components/VHeader/VHeaderMobile/VFilterTab.vue"
import VTab from "~/components/VTabs/VTab.vue"
import VTabs from "~/components/VTabs/VTabs.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const VFilterTabWrapper = defineComponent({
  name: "VFilterTabWrapper",
  props: {
    appliedFilterCount: { type: Number, required: true },
    selectedId: { type: String, required: true },
  },
  setup(props) {
    return () =>
      h("div", { class: "p-2" }, [
        h(
          VTabs,
          {
            label: "tabs",
            selectedId: props.selectedId,
            id: "wrapper",
            variant: "plain",
            tablistStyle: "ps-6 pe-2 gap-x-4",
            class: "flex min-h-0",
          },
          {
            tabs: () => [
              h(
                VTab,
                { id: "tab1", label: "Tab 1", size: "medium" },
                { default: () => ["Tab1"] }
              ),
              h(VFilterTab, { appliedFilterCount: props.appliedFilterCount }),
            ],
          }
        ),
        h("div", { class: "border-t border-default h-2 w-full" }),
      ])
  },
})

const meta = {
  title: "Components/VHeader/VHeaderMobile/VFilterTab",
  component: VFilterTabWrapper,
  subcomponents: { VFilterTab, VTabs, VTab },

  argTypes: {
    appliedFilterCount: { type: "number" },

    selectedId: { control: "select", options: ["filters", "tab1"] },
  },
  args: {
    appliedFilterCount: 3,
    selectedId: "filters",
  },
} satisfies Meta<typeof VFilterTabWrapper>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VFilterTab, VTabs, VTab },
    setup() {
      return () => h(VFilterTabWrapper, { ...args }, {})
    },
  }),
}
