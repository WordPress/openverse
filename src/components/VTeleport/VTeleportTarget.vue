<script>
import { defineComponent } from '@nuxtjs/composition-api'
import { targets } from './meta/targets'
import { warn } from '~/utils/warn'

export default defineComponent({
  name: 'VTeleportTarget',
  props: {
    name: { type: String, required: true },
    element: { type: String, default: 'div' },
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
    delete targets[this.name]
    if (this.children.length > 0)
      throw new Error(
        `VTeleportTarget: ${this.name} beforeDestroy but still has children mounted`
      )
  },
  render(h) {
    return h(
      this.element,
      this.children.map((vm) => vm.$slots.default || []).flat()
    )
  },
})
</script>
