import { Meta, type StoryObj } from "@storybook/vue3"
import { h } from "vue"

import { getAudioObj } from "~~/test/unit/fixtures/audio"

import { AudioDetail } from "~/types/media"

import VAudioThumbnail from "~/components/VAudioThumbnail/VAudioThumbnail.vue"

const sampleAudio = getAudioObj() as Pick<
  AudioDetail,
  "title" | "creator" | "thumbnail"
>

const meta = {
  title: "Components/VAudioThumbnail",
  component: VAudioThumbnail,
} satisfies Meta<typeof VAudioThumbnail>

export default meta
type Story = StoryObj<typeof meta>

const Template: Story = {
  render: (args) => ({
    components: { VAudioThumbnail },
    setup() {
      return () =>
        h("div", { class: "w-30" }, [h(VAudioThumbnail, { audio: args.audio })])
    },
  }),
  args: { audio: sampleAudio },
}

export const Square = {
  ...Template,
  name: "Square",

  args: {
    audio: {
      title: "SMPTE Color Bars",
      creator: "Guy Macon",
      thumbnail:
        "https://upload.wikimedia.org/wikipedia/commons/c/c6/500_x_500_SMPTE_Color_Bars.png",
    },
  },
}

export const Portrait = {
  ...Template,
  name: "Portrait",

  args: {
    audio: {
      title: "Cat November 2010-1a",
      creator: "Alvesgaspar",
      thumbnail:
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Cat_November_2010-1a.jpg/359px-Cat_November_2010-1a.jpg",
    },
  },
}

export const Landscape = {
  ...Template,
  name: "Landscape",

  args: {
    audio: {
      title: "Six weeks old cat (aka)",
      creator: "André Karwath aka Aka",
      thumbnail:
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Six_weeks_old_cat_(aka).jpg/320px-Six_weeks_old_cat_(aka).jpg",
    },
  },
}

export const Fallback = {
  ...Template,
  name: "Fallback",

  args: {
    audio: {
      title: "Null",
      creator: "Undefined",
    },
  },
}
