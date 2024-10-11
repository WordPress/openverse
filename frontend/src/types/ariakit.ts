import { Component, ComponentInstance, h } from "vue"

type ComponentProps<T extends Component> = ComponentInstance<T>["$props"]

export type Renderable = Parameters<typeof h>[0]

export interface AsProps<E extends Renderable> {
  as?: E
  asProps?: E extends Component ? ComponentProps<E> : never
}
