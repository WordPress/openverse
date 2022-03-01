<script>
import { defineComponent } from '@nuxtjs/composition-api'

import { warn } from '~/utils/console'

import { targets } from './meta/targets'

export default defineComponent({
  name: 'VTeleportTarget',
  props: {
    name: { type: String, required: true },
    element: { type: String, default: 'div' },
    forceDestroy: { type: Boolean, default: false },
  },
  data: () => ({ children: [] }),
  created() {
    if (this.name in targets) {
      warn(
        `VTeleportTarget: duplicate name ${this.name}, deleting previous teleport`
      )
      delete targets[this.name]
    }
    targets[this.name] = this
  },
  beforeDestroy() {
    if (this.children.length > 0) {
      if (this.forceDestroy) {
        this.children.forEach((child) => {
          child.$destroy()
          child.$el.remove()
        })
        this.children = []
      } else {
        throw new Error(
          `VTeleportTarget: ${this.name} beforeDestroy but still has children mounted`
        )
      }
    }
    delete targets[this.name]
  },
  render(h) {
    return h(
      this.element,
      this.children.map((vm) => vm.$slots.default || []).flat()
    )
  },
})
</script>
