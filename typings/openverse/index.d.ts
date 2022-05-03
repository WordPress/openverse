declare module '*.svg' {
  const SVG: string
  export default SVG
}

declare module '*.svg?inline' {
  const SVG: unknown
  export default SVG
}

declare module '*.png' {
  const PNG: string
  export default PNG
}
