import { SENSITIVITIES } from "~/constants/content-safety"

import VSafetyWall from "~/components/VSafetyWall/VSafetyWall.vue"

const Template = (args) => ({
  template: `<VSafetyWall v-bind="args" :media="media" />`,
  components: { VSafetyWall },
  setup() {
    const media = {
      id: "f9384235-b72e-4f1e-9b05-e1b116262a29",
      frontendMediaType: "image",
      title: "Cat",
      originalTitle: "Cat",
      foreign_landing_url:
        "https://www.flickr.com/photos/7788419@N05/15218475961",
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
      isSensitive: true,
      sensitivity: args.sensitivities,
    }
    return { args, media }
  },
})

export default {
  title: "Components/VSafetyWall",
  component: VSafetyWall,

  argTypes: {
    sensitivities: {
      control: { type: "check" },
      options: SENSITIVITIES,
    },
  },

  args: {
    sensitivities: SENSITIVITIES,
  },
}

export const Default = {
  render: Template.bind({}),
  name: "default",
}
