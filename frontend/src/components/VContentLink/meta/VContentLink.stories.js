import VContentLink from "~/components/VContentLink/VContentLink.vue"

const contentLinkArgTypes = {
  mediaType: { options: ["audio", "image"], control: { type: "radio" } },
  searchTerm: { control: { type: "string" } },
  resultsCount: { control: { type: "number" } },
  isSelected: { control: { type: "boolean" } },
  layout: { options: ["stacked", "horizontal"], control: { type: "radio" } },
}

const VContentLinkStory = (args) => ({
  template: `<VContentLink v-bind="args" />`,
  components: { VContentLink },
  setup() {
    return { args }
  },
})

const VContentLinkHorizontalStory = (args) => ({
  template: `<div class="max-w-md"><VContentLink v-bind="args" /></div>`,
  components: { VContentLink },
  setup() {
    return { args }
  },
})

const TwoVContentLinkStory = () => ({
  template: `
  <div class="grid grid-cols-2 gap-4">
    <VContentLink
      v-for="(type, key) in types"
      :key="key"
      :media-type="type.mediaType"
      :results-count="type.resultsCount"
      search-term="cat"
    />
  </div>
  `,
  components: { VContentLink },
  data() {
    return {
      types: [
        { mediaType: "image", resultsCount: 4321 },
        { mediaType: "audio", resultsCount: 1234 },
      ],
    }
  },
  methods: {
    onSelected(mediaType) {
      this.selected = mediaType
    },
  },
})

export default {
  title: "Components/VContentLink",
  components: VContentLink,
  argTypes: contentLinkArgTypes,
}

export const Default = {
  render: VContentLinkStory.bind({}),
  name: "Default",

  args: {
    mediaType: "image",
    searchTerm: "cat",
    resultsCount: 5708,
    isSelected: false,
  },

  argTypes: contentLinkArgTypes,
}

export const Horizontal = {
  render: VContentLinkHorizontalStory.bind({}),
  name: "Horizontal",

  args: {
    mediaType: "audio",
    searchTerm: "cat",
    resultsCount: 4561,
    isSelected: false,
    layout: "horizontal",
  },

  argTypes: contentLinkArgTypes,
}

export const Mobile = {
  render: TwoVContentLinkStory.bind({}),
  name: "Mobile",

  parameters: {
    viewport: {
      defaultViewport: "xs",
    },
  },
}
