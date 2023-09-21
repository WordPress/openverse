import { computed, Ref, ref } from "@nuxtjs/composition-api"

import type { ImageDimensions } from "~/types/media"

const minAspect = 3 / 4
const maxAspect = 16 / 9
const panoramaAspect = 21 / 9
const minRowWidth = 250
const widthBasis = minRowWidth / maxAspect
const squareSize = 250
const defaultImgSize = 100

const getImgAspectRatio = (aspect: number) => {
  if (aspect > maxAspect) return maxAspect
  if (aspect < minAspect) return minAspect
  return aspect
}

export const useImageCellSize = ({
  imageSize,
  isSquare,
}: {
  imageSize: ImageDimensions
  isSquare: Ref<boolean>
}) => {
  const imgHeight = ref(
    isSquare.value ? squareSize : imageSize.height || defaultImgSize
  )
  const imgWidth = ref(
    isSquare.value ? squareSize : imageSize.width || defaultImgSize
  )

  const naturalAspectRatio = computed(() => imgWidth.value / imgHeight.value)
  const isPanorama = computed(() => naturalAspectRatio.value > panoramaAspect)

  /**
   * Returns the style declarations for the container width, aspect ratio and flex-grow value.
   * For the square cell, the styles are empty.
   */
  const styles = computed(() => {
    const styles = {}
    if (isSquare.value) {
      return styles
    }

    const aspect = naturalAspectRatio.value
    /**
     * The aspect-ratio for `img` is clamped between the min and max aspect ratios.
     */
    const imgAspectRatio = getImgAspectRatio(aspect)
    const containerWidth = Math.round(imgAspectRatio * widthBasis)

    return {
      "--container-width": `${containerWidth}px`,
      "--container-grow": containerWidth,
      "--img-aspect-ratio": imgAspectRatio,
    }
  })

  return {
    imgHeight,
    imgWidth,
    isPanorama,
    styles,
  }
}
