import type { MediaProvider } from "~/types/media-provider"

/**
 * Sorts providers by their source_name property.
 * @param data - initial unordered list of providers
 */
export const sortProviders = (data: MediaProvider[]): MediaProvider[] => {
  if (!data.length || !Array.isArray(data)) {
    return []
  }
  return data.sort((sourceObjectA, sourceObjectB) => {
    const nameA = sourceObjectA.source_name.toUpperCase()
    const nameB = sourceObjectB.source_name.toUpperCase()
    return nameA.localeCompare(nameB)
  })
}
