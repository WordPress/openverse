import VRecentSearches from "~/components/VRecentSearches/VRecentSearches.vue"

const Template = (args) => ({
  template: `
    <VRecentSearches v-bind="args" v-on="args" />`,
  components: { VRecentSearches },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VRecentSearches",
  component: VRecentSearches,

  argTypes: {
    select: {
      action: "select",
    },

    clear: {
      action: "clear",
    },

    clearSingle: {
      action: "clearSingle",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: {
    entries: ["addition", "subtraction", "multiplication", "division"],
  },
}

export const NoHistory = {
  render: Template.bind({}),
  name: "No history",
}
