import { WithScreenshotArea } from "~~/.storybook/decorators/with-screenshot-area"

import VCheckbox from "~/components/VCheckbox/VCheckbox.vue"
import VLicense from "~/components/VLicense/VLicense.vue"

const checkboxArgTypes = {
  id: { control: { type: "text" } },
  checked: { control: { type: "boolean" } },
  name: { control: { type: "text" } },
  value: { control: { type: "text" } },
  disabled: { control: { type: "boolean" } },
}

const defaultArgs = {
  id: "default",
  name: "Code is Poetry",
  value: "codeIsPoetry",
  checked: false,
  isSwitch: false,
}

const Template = (args) => ({
  template: `<VCheckbox v-bind="args" v-on="args" class="mb-4">{{ args.name }}</VCheckbox>`,
  components: { VCheckbox },
  setup() {
    return { args }
  },
})

const LicenseCheckboxTemplate = (args) => ({
  template: `
    <fieldset>
      <legend>License</legend>
      <VCheckbox v-bind="args" v-on="args" class="mb-4">
       <VLicense license="by-nc" class="me-4"/>
      </VCheckbox>
    </fieldset>
  `,
  components: { VCheckbox, VLicense },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VCheckbox",
  components: VCheckbox,
  decorators: [WithScreenshotArea],

  args: defaultArgs,

  argTypes: {
    ...checkboxArgTypes,
    change: {
      action: "change",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: defaultArgs,

  argTypes: checkboxArgTypes,
}

export const Switch = {
  render: Template.bind({}),
  name: "Switch",

  args: {
    ...defaultArgs,
    isSwitch: true,
  },

  argTypes: checkboxArgTypes,
}

export const LicenseCheckbox = {
  render: LicenseCheckboxTemplate.bind({}),
  name: "License Checkbox",

  args: {
    ...defaultArgs,
    id: "cc-by",
    name: "license",
    value: "cc-by",
    checked: true,
  },

  argTypes: checkboxArgTypes,
}
