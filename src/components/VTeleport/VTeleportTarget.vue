<script>
import { defineComponent } from '@nuxtjs/composition-api'
import { targets } from './meta/targets'

export default defineComponent({
  name: 'VTeleportTarget',
  props: {
    name: { type: String, required: true },
  },
  data: () => ({ children: [] }),
  created() {
    if (this.name in targets)
      throw new Error(`VTeleportTarget: duplicate name ${this.name}`)
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
    return h('div', this.children.map((vm) => vm.$slots.default || []).flat())
  },
})
</script>
