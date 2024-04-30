import VHomeLink from "~/components/VHeader/VHomeLink.vue"

const Template = (args) => ({
  template: `<div class="flex p-4" :class="bg"><VHomeLink v-bind="args" /></div>`,
  components: { VHomeLink },
  setup() {
    const bg = args.variant === "dark" ? "bg-white" : "bg-black"
    return { args, bg }
  },
})

export default {
  title: "Components/VHeader/HomeLinks/VHomeLink",
  components: VHomeLink,

  argTypes: {
    variant: {
      type: "string",
      control: {
        type: "select",
        options: ["dark", "light"],
      },
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}
