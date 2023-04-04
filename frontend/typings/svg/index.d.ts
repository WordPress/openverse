declare module "*.svg" {
  const SVG: string
  export default SVG
}

declare module "*.svg?inline" {
  import type { Component } from "vue"

  const SVG: Component
  export default SVG
}

declare module "*.png" {
  const PNG: string
  export default PNG
}
