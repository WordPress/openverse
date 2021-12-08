// https://gist.github.com/Alan-Liang/a847559433919ecb53dff217ed9708bb

const targets = {}

export const VTeleportTarget = {
  name: 'VTeleportTarget',
  data: () => ({ children: [] }),
  props: {
    name: { type: String, required: true },
  },
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
}

export const VTeleport = {
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
}
