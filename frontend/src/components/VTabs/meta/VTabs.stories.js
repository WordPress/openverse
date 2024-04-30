import VTabs from "~/components/VTabs/VTabs.vue"
import VTabPanel from "~/components/VTabs/VTabPanel.vue"
import VTab from "~/components/VTabs/VTab.vue"

const Template = (args) => ({
  template: `<VTabs :label="label" :selected-id="selectedId" v-bind="rest" v-on="rest"><template #tabs>
<VTab id='1'>Tab1</VTab><VTab id='2'>Tab2</VTab><VTab id='3'>Tab3</VTab>
</template>
<VTabPanel id='1'>Page 1 content</VTabPanel>
<VTabPanel id='2'>Page 2 content</VTabPanel>
<VTabPanel id='3'>Page 3 content</VTabPanel>
</VTabs>`,
  component: { VTabs },
  subcomponents: { VTab, VTabPanel },
  setup() {
    const { label, selectedId, ...rest } = args
    return { label, selectedId, rest }
  },
})

export default {
  components: { VTabs },
  subcomponents: { VTabPanel, VTab },
  title: "Components/VTabs",
  component: VTabs,

  argTypes: {
    variant: {
      options: ["bordered", "plain"],

      control: {
        type: "radio",
      },
    },

    close: {
      action: "close",
    },

    change: {
      action: "change",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: {
    label: "Default tabs story",
    selectedId: "1",
  },
}

export const ManualPlainTabs = {
  render: Template.bind({}),
  name: "Manual plain tabs",

  args: {
    label: "Manual plain tabs",
    selectedId: "1",
    manual: true,
    variant: "plain",
  },
}
