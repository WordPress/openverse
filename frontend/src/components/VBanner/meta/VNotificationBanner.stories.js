import VNotificationBanner from "~/components/VBanner/VNotificationBanner.vue"

const Template = (args) => ({
  template: `<VNotificationBanner id="banner" v-bind="args" v-on="args">{{ args.text }}</VNotificationBanner>`,
  components: { VNotificationBanner },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VNotificationBanner",
  component: VNotificationBanner,

  argTypes: {
    close: {
      action: "close",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: {
    text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec justo eget felis facilisis fermentum.",
    nature: "success",
    variant: "regular",
  },
}

export const Dark = {
  render: Template.bind({}),
  name: "Dark",

  args: {
    text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec justo eget felis facilisis fermentum.",
    nature: "info",
    variant: "dark",
  },
}
