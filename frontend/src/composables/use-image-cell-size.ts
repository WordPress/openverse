import { computed, Ref, ref } from "@nuxtjs/composition-api"

import type { ImageDimensions } from "~/types/media"

const minAspect = 3 / 4
const maxAspect = 16 / 9
const panoramaAspect = 21 / 9
const minRowWidth = 450
const widthBasis = minRowWidth / maxAspect
const squareSize = 250
const defaultImgSize = 100

const getContainerAspect = (aspect: number) => {
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

  const imageAspect = computed(() => imgWidth.value / imgHeight.value)
  const isPanorama = computed(() => imageAspect.value > panoramaAspect)

  /**
   * Returns the style declarations for container, figure and i padding.
   * For the square cell, the styles are empty.
   */
  const styles = computed(() => {
    const aspect = imageAspect.value

    if (isSquare.value)
      return {
        container: "",
        figure: "",
        iPadding: "",
      }

    const containerAspect = getContainerAspect(aspect)
    const containerWidth = containerAspect * widthBasis

    let imageWidth, imageLeft, imageTop

    if (aspect < maxAspect) {
      imageWidth = 100
      imageLeft = 0
    } else {
      imageWidth = (aspect / maxAspect) * 100
      imageLeft = ((aspect - maxAspect) / maxAspect) * -50
    }

    if (aspect > minAspect) {
      imageTop = 0
    } else {
      imageTop = ((minAspect - aspect) / (aspect * minAspect * minAspect)) * -50
    }

    return {
      container: `width: ${containerWidth}px;flex-grow: ${containerWidth}`,
      figure: `width: ${imageWidth}%; top: ${imageTop}%; left:${imageLeft}%;`,
      iPadding: `padding-bottom:${(1 / containerAspect) * 100}%`,
    }
  })

  return {
    imgHeight,
    imgWidth,
    isPanorama,
    styles,
  }
}
