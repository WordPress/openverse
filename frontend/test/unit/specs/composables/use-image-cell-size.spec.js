import { ref } from "@nuxtjs/composition-api"

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
    expect(styles.value).toEqual({ container: "", figure: "", iPadding: "" })
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
      container: "width: 450px;flex-grow: 450",
      figure: "width: 675%; top: 0%; left:-287.5%;",
      iPadding: "padding-bottom:56.25%",
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
      container: "width: 189.84375px;flex-grow: 189.84375",
      figure: "width: 100%; top: -711.1111111111111%; left:0%;",
      iPadding: "padding-bottom:133.33333333333331%",
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
      container: "width: 253.125px;flex-grow: 253.125",
      figure: "width: 100%; top: 0%; left:0%;",
      iPadding: "padding-bottom:100%",
    })
  })
})
