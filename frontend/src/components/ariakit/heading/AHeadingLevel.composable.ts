import { HeadingContext, type HeadingLevels } from "./HeadingContext"

export interface HeadingLevelOptions {
  level?: HeadingLevels
}

export function useHeadingLevel({ level }: HeadingLevelOptions) {
  const contextLevel = HeadingContext.inject() || 0
  const nextLevel = Math.max(
    Math.min(level || contextLevel + 1, 6),
    1
  ) as HeadingLevels
  HeadingContext.provide(nextLevel)
  return nextLevel
}
