import { image } from "~~/test/unit/fixtures/image"

import VImageCell from "~/components/VImageCell/VImageCell.vue"

const Template = (args, { argTypes }) => ({
  components: { VImageCell },
  props: Object.keys(argTypes),
  template: `
    <ol class="flex flex-wrap gap-4">
      <VImageCell
        :image="image"
        searchTerm="test"
        :aspect-ratio="aspectRatio"
        relatedTo="fake-uuid"
      />
    </ol>
  `,
})

export default {
  title: "Components/VImageCell",
  components: VImageCell,
}

export const Default = {
  render: Template.bind({}),
  name: "VImageCell",

  parameters: {
    viewport: {
      defaultViewport: "sm",
    },
  },

  argTypes: {
    aspectRatio: {
      options: ["square", "intrinsic"],

      control: {
        type: "radio",
      },
    },

    image: {
      control: {
        type: "object",
      },
    },
  },

  args: {
    aspectRatio: "intrinsic",

    image: {
      ...image,
      thumbnail: "/openverse-default.jpg",
    },
  },
}
