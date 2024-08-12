import VSearchBar from "~/components/VHeader/VSearchBar/VSearchBar.vue"

const Template = (args) => ({
  template: `
    <VSearchBar v-bind="args" v-on="args">
      <span class="info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default">
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
      <VSearchBar v-model="text" v-on="args">
        <span class="info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default">
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
  },
}
