import { audioFeatures } from "~/constants/audio"

import VWaveform from "~/components/VAudioTrack/VWaveform.vue"

const Template = (args) => ({
  template: `<VWaveform class="w-full h-30" audio-id="123" :is-tabbable="true" v-bind="args" v-on="args"/>`,
  components: { VWaveform },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/Audio track/Waveform",
  components: VWaveform,

  argTypes: {
    seeked: {
      action: "seeked",
    },
  },
}

const timeArgs = { currentTime: 2, duration: 10 }
const timeArgsWithFeatures = { ...timeArgs, features: audioFeatures }
const timeArgsWithFeaturesAndPeaks = { ...timeArgsWithFeatures, peaks: [0.5, 1, 0.5, 0, 0.5] }

export const Upsampling = {
  render: Template.bind({}),
  name: "Upsampling",

  // triangular wave with 9 points
  args: {
    ...timeArgsWithFeatures,
    peaks: [0.5, 1, 0.5, 0, 0.5, 1, 0.5, 0, 0.5],
  },
}

const sineWaveWith1000Points = Array.from({ length: 1000 }, (_, k) => 0.5 * Math.sin((k * 2 * Math.PI) / 500) + 0.5)

export const Downsampling = {
  render: Template.bind({}),
  name: "Downsampling",

  args: {
    peaks: sineWaveWith1000Points,
    ...timeArgsWithFeatures,
  },
}

export const Background = {
  render: Template.bind({}),
  name: "Background",

  args: {
    ...timeArgsWithFeaturesAndPeaks,
    style: {
      "--waveform-background-color": "#d7fcd4",
    },
  },
}

export const WithBlankSpace = {
  render: Template.bind({}),
  name: "With blank space",

  args: {
    ...timeArgsWithFeaturesAndPeaks,
    usableFrac: 0.5,
  },
}

export const Message = {
  render: Template.bind({}),
  name: "Message",

  args: {
    message: "Hello, World!",
  },
}
