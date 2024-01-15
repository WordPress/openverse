import { ref } from "vue"

import { useImageCellSize } from "~/composables/use-image-cell-size"

describe("useImageCellSize", () => {
  it("Should return correct values for square image", async () => {
    const { imgHeight, imgWidth, isPanorama, styles } = useImageCellSize({
      imageSize: {},
      isSquare: ref(true),
    })

    expect(imgHeight.value).toBe(250)
    expect(imgWidth.value).toBe(250)
    expect(isPanorama.value).toBe(false)
    expect(styles.value).toEqual({})
  })

  it("Should return correct values for intrinsic panorama image", async () => {
    const HEIGHT = 25
    const WIDTH = 300
    const { imgHeight, imgWidth, isPanorama, styles } = useImageCellSize({
      imageSize: { width: WIDTH, height: HEIGHT },
      isSquare: ref(false),
    })

    expect(imgHeight.value).toEqual(HEIGHT)
    expect(imgWidth.value).toEqual(WIDTH)
    expect(isPanorama.value).toBe(true)
    expect(styles.value).toEqual({
      "--container-grow": 250,
      "--container-width": "250px",
      "--img-aspect-ratio": 1.7777777777777777,
    })
  })

  it("Should return correct values for intrinsic tall image", async () => {
    const HEIGHT = 300
    const WIDTH = 25
    const { imgHeight, imgWidth, isPanorama, styles } = useImageCellSize({
      imageSize: { width: WIDTH, height: HEIGHT },
      isSquare: ref(false),
    })

    expect(imgHeight.value).toEqual(HEIGHT)
    expect(imgWidth.value).toEqual(WIDTH)
    expect(isPanorama.value).toBe(false)
    expect(styles.value).toEqual({
      "--container-grow": 105,
      "--container-width": "105px",
      "--img-aspect-ratio": 0.75,
    })
  })

  it("Should return correct values for intrinsic square image", async () => {
    const HEIGHT = 300
    const WIDTH = 300
    const { imgHeight, imgWidth, isPanorama, styles } = useImageCellSize({
      imageSize: { width: WIDTH, height: HEIGHT },
      isSquare: ref(false),
    })

    expect(imgHeight.value).toEqual(HEIGHT)
    expect(imgWidth.value).toEqual(WIDTH)
    expect(isPanorama.value).toBe(false)
    expect(styles.value).toEqual({
      "--container-grow": 141,
      "--container-width": "141px",
      "--img-aspect-ratio": 1,
    })
  })
})
