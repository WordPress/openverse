import { h } from "vue"

import { WithScreenshotArea } from "~~/.storybook/decorators/with-screenshot-area"

import VCheckbox from "~/components/VCheckbox/VCheckbox.vue"
import VLicense from "~/components/VLicense/VLicense.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VCheckbox",
  component: VCheckbox,
  decorators: [WithScreenshotArea],

  args: {
    id: "default",
    name: "Code is Poetry",
    value: "codeIsPoetry",
    checked: false,
    isSwitch: false,
  },

  argTypes: {
    onChange: { action: "change" },
  },
} satisfies Meta<typeof VCheckbox>

export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VCheckbox },
    setup() {
      return () => h(VCheckbox, args, { default: () => args.name })
    },
  }),
}

export const Default: Story = {
  ...Template,
  name: "Default",
}

export const Switch: Story = {
  ...Template,
  name: "Switch",

  args: {
    isSwitch: true,
  },
}

export const LicenseCheckbox: Story = {
  name: "License Checkbox",
  render: (args) => ({
    components: { VCheckbox, VLicense },
    setup() {
      return () =>
        h("fieldset", {}, [
          h("legend", {}, "License"),
          h(VCheckbox, { ...args, class: "mb-4" }, [
            h(VLicense, { license: "by-nc", class: "me-4" }),
          ]),
        ])
    },
  }),
  args: {
    id: "cc-by",
    name: "license",
    value: "cc-by",
    checked: true,
  },
}
