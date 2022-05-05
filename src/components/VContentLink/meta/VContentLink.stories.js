import VContentLink from '~/components/VContentLink/VContentLink.vue'

export default {
  title: 'Components/VContentLink',
  component: VContentLink,
  argTypes: {
    mediaType: {
      options: ['audio', 'image'],
      control: { type: 'radio' },
    },
    resultsCount: {
      control: { type: 'number' },
    },
    isSelected: {
      control: { type: 'boolean' },
    },
    layout: {
      options: ['stacked', 'horizontal'],
      control: { type: 'radio' },
    },
  },
}

const VContentLinkStory = (args) => ({
  template: `<VContentLink v-bind="args" />`,
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
    />
  </div>
  `,
  components: { VContentLink },
  data() {
    return {
      types: [
        { mediaType: 'image', resultsCount: 4321 },
        { mediaType: 'audio', resultsCount: 1234 },
      ],
      selected: 'audio',
    }
  },
  methods: {
    onSelected(mediaType) {
      this.selected = mediaType
    },
  },
})

export const Default = VContentLinkStory.bind({})
Default.args = {
  mediaType: 'image',
  resultsCount: 5708,
  isSelected: false,
}

const VContentLinkHorizontalStory = (args) => ({
  template: `<div class="max-w-md"><VContentLink v-bind="args" /></div>`,
  components: { VContentLink },
  setup() {
    return { args }
  },
})

export const Horizontal = VContentLinkHorizontalStory.bind({})
Horizontal.args = {
  mediaType: 'audio',
  resultsCount: 4561,
  isSelected: false,
  layout: 'horizontal',
}

export const Mobile = TwoVContentLinkStory.bind({})
Mobile.parameters = {
  viewport: { defaultViewport: 'mob' },
}
