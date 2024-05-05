import { computed } from "vue"

import { useProviderStore } from "~/stores/provider"
import { audioLayouts, audioSizes } from "~/constants/audio"

import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"

import flacWaveform from "./flac-waveform.json"
import mp3Waveform from "./mp3-waveform.json"
import oggWaveform from "./ogg-waveform.json"
import wavWaveform from "./wav-waveform.json"

const commonAttrs = () => ({
  id: Math.floor(Math.random() * 1e9).toString(),
  frontendMediaType: "audio",
  source: "wikimedia_audio",
  creator: "Wolfgang Amadeus Mozart",
  creator_url: "https://en.wikipedia.org/wiki/Wolfgang_Amadeus_Mozart",
  category: "music",
  thumbnail:
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Croce-Mozart-Detail.jpg/370px-Croce-Mozart-Detail.jpg",
  frontendMediaType: "audio",
  source: "wikimedia_audio",
  sourceName: "Wikimedia",
})

const formatExamples = {
  ogg: {
    title: "Eine kleine Nachtmusik - 1. Allegro",
    url: "https://upload.wikimedia.org/wikipedia/commons/2/24/Mozart_-_Eine_kleine_Nachtmusik_-_1._Allegro.ogg",
    duration: 355e3,
    peaks: oggWaveform.points,
    license: "by-sa",
  },
  mp3: {
    title: 'Serenade No. 10 "Grand Partita" - VII. Finale. Molto Allegro',
    url: "https://upload.wikimedia.org/wikipedia/commons/e/e1/Mozart%27s_Serenade_No._10_%22Grand_Partita%22_-_VII._Finale._Molto_Allegro_-_United_States_Marine_Band.mp3",
    duration: 206e3,
    peaks: mp3Waveform.points,
    license: "pdm",
  },
  wav: {
    title: "Trio from Wind Serenade K. 388",
    url: "https://upload.wikimedia.org/wikipedia/commons/b/b3/Mozart_Trio_from_Wind_Serenade_K388.wav",
    duration: 33e3,
    peaks: wavWaveform.points,
    license: "pdm",
  },
  flac: {
    title: 'Piano Concerto No. 26 in D Major, KV 537 "Coronation", 1. Allegro',
    url: "https://upload.wikimedia.org/wikipedia/commons/1/17/Mozart%3B_Piano_Concerto_No._26_in_D_Major%2C_KV_537_%22Coronation%22%2C_1._Allegro.flac",
    duration: 808e3,
    peaks: flacWaveform.points,
    license: "pdm",
  },
}

const providerStorePatch = {
  providers: {
    audio: [{ source_name: "wikimedia_audio", display_name: "Wikimedia" }],
  },
  sourceNames: { audio: ["wikimedia_audio"] },
}

const Template = (args) => ({
  template: `<VAudioTrack v-bind="args" :audio="audioObj"/>`,
  components: { VAudioTrack },
  setup() {
    const providerStore = useProviderStore()
    providerStore.$patch(providerStorePatch)
    const audioObj = computed(() => ({
      ...commonAttrs(),
      ...formatExamples[args.format],
    }))
    return { args, audioObj }
  },
})

const Multiple = () => ({
  template: `
    <div>
      <VAudioTrack
        v-for="(audio, key) in formatExamples"
        :key="key"
        class="mb-8"
        :audio="audioObj(audio)"
        layout="row"/>
    </div>
  `,
  components: { VAudioTrack },
  setup() {
    const providerStore = useProviderStore()
    providerStore.$patch(providerStorePatch)
    const audioObj = (audio) => ({ ...commonAttrs(), ...audio })
    return { formatExamples, audioObj }
  },
})

export default {
  title: "Components/Audio track",
  component: VAudioTrack,

  argTypes: {
    format: {
      options: ["mp3", "ogg", "flac", "wav"],
      control: "select",
    },

    layout: {
      options: audioLayouts,
      control: "select",
    },

    size: {
      options: audioSizes,
      control: "select",
    },

    audio: {
      control: false,
    },
  },
  args: {
    format: "mp3",
    layout: "full",
    size: "m",
  },
}

export const FullMedium = {
  render: Template.bind({}),
  name: "Full (medium)",

  // layout: 'full', (default)
  args:
    // size: 'm', (default)
    {},
}

export const FullSmall = {
  render: Template.bind({}),
  name: "Full (small)",

  // layout: 'full', (default)
  args: {
    size: "s",
  },

  parameters: {
    viewport: {
      defaultViewport: "sm",
    },
  },
}

export const RowLarge = {
  render: Template.bind({}),
  name: "Row (large)",

  args: {
    layout: "row",
    size: "l",
  },
}

export const RowMedium = {
  render: Template.bind({}),
  name: "Row (medium)",

  // size: 'm', (default)
  args: {
    layout: "row",
  },
}

export const RowSmall = {
  render: Template.bind({}),
  name: "Row (small)",

  args: {
    layout: "row",
    size: "s",
  },

  parameters: {
    viewport: {
      defaultViewport: "sm",
    },
  },
}

export const BoxLarge = {
  render: Template.bind({}),
  name: "Box (large)",

  args: {
    layout: "box",
    size: "l",
  },
}

export const BoxMedium = {
  render: Template.bind({}),
  name: "Box (medium)",

  args: {
    layout: "box",
    size: "l",
  },
}

export const BoxSmall = {
  render: Template.bind({}),
  name: "Box (small)",

  args: {
    layout: "box",
    size: "s",
  },

  parameters: {
    viewport: {
      defaultViewport: "sm",
    },
  },
}

export const Global = {
  render: Template.bind({}),
  name: "Global",

  args: {
    layout: "global",
  },

  parameters: {
    viewport: {
      defaultViewport: "sm",
    },
  },
}

export const Multiple_ = {
  render: Multiple.bind({}),
  name: "Multiple",
}
