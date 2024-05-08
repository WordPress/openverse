import VAudioThumbnail from "~/components/VAudioThumbnail/VAudioThumbnail.vue"

const Template = (args) => ({
  template: `
    <div class="w-30">
      <VAudioThumbnail :audio="args.audio" v-bind="args"/>
    </div>
  `,
  components: { VAudioThumbnail },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VAudioThumbnail",
  components: VAudioThumbnail,
}

export const Square = {
  render: Template.bind({}),
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
  render: Template.bind({}),
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
  render: Template.bind({}),
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
  render: Template.bind({}),
  name: "Fallback",

  args: {
    audio: {
      title: "Null",
      creator: "Undefined",
    },
  },
}
