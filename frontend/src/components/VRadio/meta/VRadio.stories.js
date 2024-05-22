import VRadio from "~/components/VRadio/VRadio.vue"

const Template = (args) => ({
  template: `
    <div>
      <VRadio :id="args.id" v-bind="args" v-on="args" :value_="args.value_">Label text</VRadio>
    </div>
  `,
  components: { VRadio },
  setup() {
    return { args }
  },
})

const vModelTemplate = (args) => ({
  template: `
    <div>
      <form class="flex flex-col gap-2 mb-2">
        <VRadio id="a" name="test" value_="A" v-model="picked">A</VRadio>
        <VRadio id="b" name="test" value_="B" v-model="picked">B</VRadio>
      </form>
      {{ picked ?? 'None' }}
    </div>
  `,
  data() {
    return { picked: null }
  },
  components: { VRadio },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VRadio",
  components: VRadio,

  argTypes: {
    change: {
      action: "change",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  // if same as value, radio is checked
  args: {
    id: "default",
    value_: "value",
    modelValue: "modelValue",
  },
}

export const Disabled = {
  render: Template.bind({}),
  name: "Disabled",

  // if same as value, radio is checked
  args: {
    id: "disabled",
    value_: "value",
    modelValue: "modelValue",
    disabled: true,
  },
}

export const VModel = {
  render: vModelTemplate.bind({}),
  name: "v-model",
}
