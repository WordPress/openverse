import stringToBoolean from '~/utils/string-to-boolean'

describe('stringToBoolean', () => {
  it('returns true', () => {
    expect(stringToBoolean('true')).toBe(true)
    expect(stringToBoolean('yes')).toBe(true)
    expect(stringToBoolean('1')).toBe(true)
  })

  it('returns false', () => {
    expect(stringToBoolean('false')).toBe(false)
    expect(stringToBoolean('no')).toBe(false)
    expect(stringToBoolean('0')).toBe(false)
  })
})
