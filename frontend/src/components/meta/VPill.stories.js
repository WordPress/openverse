import VPill from "~/components/VPill.vue"

const Default = (args) => ({
  template: `<VPill>Beta</VPill>`,
  components: { VPill },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VPill",
  components: VPill,
}

export const Default_ = {
  render: Default.bind({}),
  name: "Default",
}
