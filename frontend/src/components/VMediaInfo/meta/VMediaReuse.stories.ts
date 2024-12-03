import { h } from "vue"

import type { ImageDetail } from "#shared/types/media"

import VMediaReuse from "~/components/VMediaInfo/VMediaReuse.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const image = {
  id: "f9384235-b72e-4f1e-9b05-e1b116262a29",
  frontendMediaType: "image",
  title: "Cat",
  originalTitle: "Cat",
  foreign_landing_url: "https://www.flickr.com/photos/7788419@N05/15218475961",
  url: "https://live.staticflickr.com/3903/15218475961_963a4c116e_b.jpg",
  creator: "strogoscope",
  creator_url: "https://www.flickr.com/photos/7788419@N05",
  license: "by",
  license_version: "2.0",
  license_url: "https://creativecommons.org/licenses/by/2.0/",
  provider: "flickr",
  source: "flickr",
  detail_url:
    "http://localhost:49153/v1/images/f9384235-b72e-4f1e-9b05-e1b116262a29/",
}

const meta = {
  title: "Components/VMediaInfo/VMediaReuse",
  component: VMediaReuse,
} satisfies Meta<typeof VMediaReuse>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VMediaReuse },
    setup() {
      return () => h(VMediaReuse, args)
    },
  }),
  name: "VMediaReuse",
  args: {
    media: image as ImageDetail,
  },
}
