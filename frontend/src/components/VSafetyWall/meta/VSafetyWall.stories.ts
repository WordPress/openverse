import { defineComponent, h, PropType } from "vue"

import { SENSITIVITIES, Sensitivity } from "~/constants/content-safety"

import VSafetyWall from "~/components/VSafetyWall/VSafetyWall.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const VSafetyWallWrapper = defineComponent({
  name: "VSafetyWallWrapper",
  components: { VSafetyWall },
  props: {
    id: { type: String, required: true },
    sensitivities: {
      type: Array as PropType<Sensitivity[]>,
      default: () => [] as Sensitivity[],
    },
  },
  emits: ["reveal"],
  setup(props, { emit }) {
    const onReveal = () => emit("reveal")
    return () =>
      h(VSafetyWall, {
        id: props.id,
        sensitivity: props.sensitivities,
        onReveal,
      })
  },
})

const meta = {
  title: "Components/VSafetyWall",
  component: VSafetyWallWrapper,

  argTypes: {
    sensitivities: {
      control: { type: "check" },
      options: SENSITIVITIES,
    },
    // This doesn't work, even though the events are passed through
    onReveal: { action: "reveal" },
  },

  args: {
    sensitivities: [...SENSITIVITIES],

    id: "f9384235-b72e-4f1e-9b05-e1b116262a29",
  },
} satisfies Meta<typeof VSafetyWallWrapper>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VSafetyWallWrapper },
    setup() {
      const logReveal = () => {
        console.log("Revealed")
      }
      return () =>
        h(VSafetyWallWrapper, {
          id: args.id,
          sensitivity: args.sensitivities,
          onReveal: logReveal,
        })
    },
  }),
  name: "default",
}
