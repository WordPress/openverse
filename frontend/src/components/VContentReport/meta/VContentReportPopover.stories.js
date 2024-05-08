import VContentReportPopover from "~/components/VContentReport/VContentReportPopover.vue"

const Template = (args) => ({
  template: `<VContentReportPopover v-bind="args" class="float-right"/>`,
  components: { VContentReportPopover },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VContentReportPopover",
  component: VContentReportPopover,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: {
    media: {
      identifier: "0aff3595-8168-440b-83ff-7a80b65dea42",
      foreign_landing_url: "https://wordpress.org/openverse/",
      provider: "provider",
    },
  },
}
