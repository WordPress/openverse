import VInputField from "~/components/VInputField/VInputField.vue"

const defaultArgs = {
  fieldId: "field",
  size: "medium",
  labelText: "Label",
}

const Template = (args) => ({
  template: `
    <VInputField :field-id="fieldId" :size="size" v-bind="rest" v-on="rest" label-text="Test label">
      <span class="whitespace-nowrap me-2">Extra info</span>
    </VInputField>
  `,
  components: { VInputField },
  setup() {
    const { fieldId, size, ...rest } = args
    return { fieldId, size, rest }
  },
})

const vModelTemplate = () => ({
  template: `
    <div>
      <VInputField v-bind="defaultArgs" v-model="text">
        {{ text.length }}
      </VInputField>
      {{ text }}
    </div>
  `,
  components: { VInputField },
  data() {
    return {
      text: "Hello, World!",
    }
  },
  setup() {
    return { defaultArgs }
  },
})

const labelTemplate = () => ({
  template: `
    <div>
      <label for="field">Label:</label>
      <VInputField field-id="field" v-bind="defaultArgs" />
    </div>
  `,
  components: { VInputField },
  setup() {
    return { defaultArgs }
  },
})

export default {
  title: "Components/VInputField",
  component: VInputField,

  argTypes: {
    "update:modelValue": {
      action: "update:modelValue",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: {
    ...defaultArgs,
    value: "Text goes here",
  },
}

export const VModel = {
  render: vModelTemplate.bind({}),
  name: "v-model",
}

export const WithPlaceholder = {
  render: Template.bind({}),
  name: "With placeholder",

  args: {
    ...defaultArgs,
    placeholder: "Enter something here",
  },
}

export const WithLabelText = {
  render: Template.bind({}),
  name: "With label text",

  args: {
    ...defaultArgs,
    labelText: "Label:",
  },
}

export const WithCustomLabel = {
  render: labelTemplate.bind({}),
  name: "With custom label",
}

export const WithConnections = {
  render: Template.bind({}),
  name: "With connections",

  args: {
    ...defaultArgs,
    connectionSides: ["start", "end"],
  },
}
