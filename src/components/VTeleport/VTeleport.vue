<script>
import { defineComponent } from '@nuxtjs/composition-api'

import { targets } from './meta/targets'

export default defineComponent({
  name: 'VTeleport',
  props: {
    to: { type: String, required: true },
  },
  mounted() {
    if (!(this.to in targets))
      throw new Error(`VTeleport: non-existent target ${this.to}`)
    targets[this.to].children.push(this)
  },
  beforeDestroy() {
    if (!(this.to in targets))
      throw new Error(`VTeleport: non-existent target ${this.to} on unmount`)
    const children = targets[this.to].children
    children.splice(children.indexOf(this), 1)
  },
  render: (h) => h('span'),
})
</script>
