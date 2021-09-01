import { downsampleArray, upsampleArray } from '~/utils/resampling'

describe('upsampleArray', () => {
  const baseArray = [0, 10, 30, 20]

  it('should scale up array by filling points between elements', () => {
    expect(upsampleArray(baseArray, 7)).toEqual([0, 5, 10, 20, 30, 25, 20])
  })

  it('should scale up array even when not exactly divisible', () => {
    const upsampledArray = upsampleArray(baseArray, 8)
    expect(upsampledArray[0]).toEqual(0)
    expect(upsampledArray[1]).toBeCloseTo(4.285, 2)
    expect(upsampledArray[2]).toBeCloseTo(8.571, 2)
    expect(upsampledArray[3]).toBeCloseTo(15.714, 2)
    expect(upsampledArray[4]).toBeCloseTo(24.285, 2)
    expect(upsampledArray[5]).toBeCloseTo(28.571, 2)
    expect(upsampledArray[6]).toBeCloseTo(24.285, 2)
    expect(upsampledArray[7]).toEqual(20)
  })
})

describe('downsampleArray', () => {
  const baseArray = [5, 10, 15, 10, 5, 0, 5]

  it('should scale down array by dropping points between elements', () => {
    expect(downsampleArray(baseArray, 4)).toEqual([5, 15, 0, 5])
  })

  it('should scale down array even when not exactly divisible', () => {
    expect(downsampleArray(baseArray, 3)).toEqual([5, 15, 5])
  })
})
