import { ref } from "vue"

import { useImageCellSize } from "~/composables/use-image-cell-size"

describe("useImageCellSize", () => {
  it("Should return correct values for square image", () => {
    const { imgHeight, imgWidth, isPanorama, styles } = useImageCellSize({
      imageSize: {},
      isSquare: ref(true),
    })

    expect(imgHeight.value).toEqual(250)
    expect(imgWidth.value).toEqual(250)
    expect(isPanorama.value).toEqual(false)
    expect(styles.value).toEqual({})
  })

  it("Should return correct values for intrinsic panorama image", () => {
    const HEIGHT = 25
    const WIDTH = 300
    const { imgHeight, imgWidth, isPanorama, styles } = useImageCellSize({
      imageSize: { width: WIDTH, height: HEIGHT },
      isSquare: ref(false),
    })

    expect(imgHeight.value).toEqual(HEIGHT)
    expect(imgWidth.value).toEqual(WIDTH)
    expect(isPanorama.value).toEqual(true)
    expect(styles.value).toEqual({
      "--container-grow": 250,
      "--container-width": "250px",
      "--img-aspect-ratio": 1.7777777777777777,
    })
  })

  it("Should return correct values for intrinsic tall image", () => {
    const HEIGHT = 300
    const WIDTH = 25
    const { imgHeight, imgWidth, isPanorama, styles } = useImageCellSize({
      imageSize: { width: WIDTH, height: HEIGHT },
      isSquare: ref(false),
    })

    expect(imgHeight.value).toEqual(HEIGHT)
    expect(imgWidth.value).toEqual(WIDTH)
    expect(isPanorama.value).toEqual(false)
    expect(styles.value).toEqual({
      "--container-grow": 105,
      "--container-width": "105px",
      "--img-aspect-ratio": 0.75,
    })
  })

  it("Should return correct values for intrinsic square image", () => {
    const HEIGHT = 300
    const WIDTH = 300
    const { imgHeight, imgWidth, isPanorama, styles } = useImageCellSize({
      imageSize: { width: WIDTH, height: HEIGHT },
      isSquare: ref(false),
    })

    expect(imgHeight.value).toEqual(HEIGHT)
    expect(imgWidth.value).toEqual(WIDTH)
    expect(isPanorama.value).toEqual(false)
    expect(styles.value).toEqual({
      "--container-grow": 141,
      "--container-width": "141px",
      "--img-aspect-ratio": 1,
    })
  })
})
