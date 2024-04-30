import VSearchBar from "~/components/VHeader/VSearchBar/VSearchBar.vue"

const Template = (args) => ({
  template: `
    <VSearchBar :size="args.size" v-bind="args" v-on="args">
      <span class="info text-xs font-semibold text-dark-charcoal-70 mx-4 whitespace-nowrap group-hover:text-dark-charcoal group-focus:text-dark-charcoal">
        12,345 results
      </span>
    </VSearchBar>`,
  components: { VSearchBar },
  setup() {
    return { args }
  },
})

const vModelTemplate = (args) => ({
  template: `
    <div>
      <VSearchBar v-model="text" size="standalone" v-on="args">
        <span class="info text-xs font-semibold text-dark-charcoal-70 mx-4 whitespace-nowrap group-hover:text-dark-charcoal group-focus:text-dark-charcoal">
          {{ text.length }} chars
        </span>
      </VSearchBar>
      {{ text }}
    </div>
  `,
  components: { VSearchBar },
  data() {
    return {
      text: "Hello, World!",
    }
  },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VHeader/Search bar",
  component: VSearchBar,

  argTypes: {
    input: {
      action: "input",
    },

    submit: {
      action: "submit",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: {
    value: "Search query",
    size: "medium",
  },
}

export const VModel = {
  render: vModelTemplate.bind({}),
  name: "v-model",
}

export const WithPlaceholder = {
  render: Template.bind({}),
  name: "With placeholder",

  args: {
    placeholder: "Search query",
    size: "large",
  },
}
