import { h } from "vue"

import { audioFeatures } from "#shared/constants/audio"

import VWaveform from "~/components/VAudioTrack/VWaveform.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/Audio track/Waveform",
  component: VWaveform,

  argTypes: {
    onSeeked: { action: "seeked" },
  },
  args: {
    audioId: "audio-1",
  },
} satisfies Meta<typeof VWaveform>

export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VWaveform },
    setup() {
      return () => h(VWaveform, { class: "w-full h-30", ...args })
    },
  }),
}

const timeArgs = { currentTime: 2, duration: 10 }
const timeArgsWithFeatures = { ...timeArgs, features: audioFeatures }
const timeArgsWithFeaturesAndPeaks = {
  ...timeArgsWithFeatures,
  peaks: [0.5, 1, 0.5, 0, 0.5],
}

export const Upsampling = {
  ...Template,
  name: "Upsampling",

  // triangular wave with 9 points
  args: {
    ...timeArgsWithFeatures,
    peaks: [0.5, 1, 0.5, 0, 0.5, 1, 0.5, 0, 0.5],
  },
}

const sineWaveWith1000Points = Array.from(
  { length: 1000 },
  (_, k) => 0.5 * Math.sin((k * 2 * Math.PI) / 500) + 0.5
)

export const Downsampling = {
  ...Template,
  name: "Downsampling",

  args: {
    peaks: sineWaveWith1000Points,
    ...timeArgsWithFeatures,
  },
}

export const Background = {
  ...Template,
  name: "Background",

  args: {
    ...timeArgsWithFeaturesAndPeaks,
    style: {
      "--waveform-background-color": "#d7fcd4",
    },
  },
}

export const WithBlankSpace: Story = {
  ...Template,
  name: "With blank space",

  args: {
    ...timeArgsWithFeaturesAndPeaks,
    usableFrac: 0.5,
  },
}

export const Message: Story = {
  ...Template,
  name: "Message",

  args: {
    message: "Hello, World!",
  },
}
