import VFilterTab from "~/components/VHeader/VHeaderMobile/VFilterTab.vue"
import VTab from "~/components/VTabs/VTab.vue"
import VTabs from "~/components/VTabs/VTabs.vue"

const Template = (args, { argTypes }) => ({
  template: `
<div class="p-2">
<VTabs label="tabs"
  :selected-id="args.selected" id="wrapper" variant="plain"
  tablist-style="ps-6 pe-2 gap-x-4" class="flex min-h-0"
>
  <template #tabs>
    <VTab id="tab1" label="Tab 1" size="medium">Tab1</VTab>
    <VFilterTab v-bind="args" v-on="args" />
  </template>
</VTabs>
<div class="border-t border-gray-3 h-2 w-full" />
</div>`,
  components: { VFilterTab, VTabs, VTab },
  props: Object.keys(argTypes),
  setup() {
    args["selected"] = args.isSelected ? "filters" : "tab1"
    return { args }
  },
})

export default {
  title: "Components/VHeader/VHeaderMobile/VFilterTab",
  component: VFilterTab,

  argTypes: {
    appliedFilterCount: {
      type: "number",
    },

    isSelected: {
      type: "boolean",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}
