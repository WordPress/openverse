import VTag from "~/components/VTag/VTag.vue"

const Template = (args) => ({
  template: `<VTag :href="args.href" v-bind="args">{{ args.title }}</VTag>`,
  components: { VTag },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VTag",
  component: VTag,

  argTypes: {
    title: { type: "text" },
    href: { type: "text" },
  },
  args: {
    title: "cat",
    href: "#",
  },
}

export const Default = {
  render: Template.bind({}),
  name: "default",
}
