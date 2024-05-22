import { ref } from "vue"

import VIcon from "~/components/VIcon/VIcon.vue"
import VSelectField from "~/components/VSelectField/VSelectField.vue"

const Template = (args) => ({
  template: `
    <VSelectField :field-id="fieldId" :label-text="labelText" v-bind="rest" v-on="rest" />`,
  components: { VSelectField },
  setup() {
    const { fieldId, labelText, ...rest } = args
    return { fieldId, labelText, rest }
  },
})

const baseArgs = {
  fieldId: "fruit",
  blankText: "Fruit",
  labelText: "Fruit",
  choices: [
    { key: "a", text: "Apple" },
    { key: "b", text: "Banana" },
    { key: "c", text: "Cantaloupe" },
  ],
}

const vModelTemplate = (args) => ({
  template: `
    <div>
    <VSelectField :field-id="args.fieldId" :label-text="args.labelText" v-model="choice" v-bind="args" />
    {{ choice }}
    </div>
  `,
  components: { VSelectField },
  setup() {
    const choice = ref("a")
    return { choice, args }
  },
})

const SlotTemplate = (args) => ({
  template: `
    <VSelectField :field-id="args.fieldId" :label-text="args.labelText" v-bind="args">
    <template #start>
      <VIcon name="radiomark" />
    </template>
    </VSelectField>
  `,
  components: { VSelectField, VIcon },
  setup() {
    return { args }
  },
})

const ConstraintTemplate = (args) => ({
  template: `<VSelectField :field-id="args.fieldId" :label-text="args.labelText"class="max-w-[100px]" v-bind="args"><template #start><VIcon name="radiomark" /></template></VSelectField>`,
  components: { VSelectField, VIcon },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VSelectField",
  component: VSelectField,

  argTypes: {
    "update:modelValue": {
      action: "update:modelValue",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
  args: baseArgs,
}

export const VModel = {
  render: vModelTemplate.bind({}),
  name: "v-model",
  args: baseArgs,
}

export const WithIcon = {
  render: SlotTemplate.bind({}),
  name: "With icon",
  args: baseArgs,
}

export const WithConstraints = {
  render: ConstraintTemplate.bind({}),
  name: "With constraints",

  args: {
    ...baseArgs,

    choices: [
      {
        key: "short",
        text: "Kiwi",
      },
      {
        key: "long",
        text: "Bob Gordon American Elderberry",
      },
    ],
  },
}

export const WithoutBorder = {
  render: Template.bind({}),
  name: "Without border",

  args: {
    ...baseArgs,
    variant: "borderless",
  },
}
