import { provide, ref } from "vue"

import { IsSidebarVisibleKey } from "~/types/provides"

import VHeaderDesktop from "~/components/VHeader/VHeaderDesktop.vue"

const Template = () => ({
  template: `<VHeaderDesktop />`,
  components: { VHeaderDesktop },
  setup() {
    provide(IsSidebarVisibleKey, ref(false))
    return {}
  },
})

export default {
  title: "Components/VHeader/VHeaderDesktop",
  component: VHeaderDesktop,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}
