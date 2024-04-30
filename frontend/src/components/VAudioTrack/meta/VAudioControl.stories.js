import { audioStatuses } from "~/constants/audio"

import VAudioControl from "~/components/VAudioTrack/VAudioControl.vue"

const Template = (args) => ({
  template: `<VAudioControl :size="args.size" :status="args.status" v-bind="args" v-on="args"/>`,
  components: { VAudioControl },
  setup() {
    return { args }
  },
})

const vModelTemplate = () => ({
  template: `
    <div>
      <VAudioControl v-model="status" size="small" status="paused" />
      {{ status }}
    </div>
  `,
  components: { VAudioControl },
  data() {
    return {
      status: "played",
    }
  },
})

export default {
  title: "Components/Audio track/Audio control",
  components: VAudioControl,

  argTypes: {
    status: {
      options: audioStatuses,
      control: "select",
    },

    size: {
      options: ["small", "medium", "large"],
      control: "select",
    },

    toggle: {
      action: "toggle",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: {
    status: "playing",
    size: "large",
  },
}

export const VModel = {
  render: vModelTemplate.bind({}),
  name: "v-model",
}

export const Disabled = {
  render: Template.bind({}),
  name: "Disabled",

  args: {
    disabled: true,
    status: "playing",
    size: "medium",
  },
}
