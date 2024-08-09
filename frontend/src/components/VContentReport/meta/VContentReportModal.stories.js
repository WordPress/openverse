import VContentReportModal from "~/components/VContentReport/VContentReportModal.vue"

const Template = (args) => ({
  template: `<VContentReportModal :media="args.media" class="float-right"/>`,
  components: { VContentReportModal },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VContentReportModal",
  component: VContentReportModal,
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
