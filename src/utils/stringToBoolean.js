function stringToBoolean(string) {
  // In case the string is already a boolean, bail and return the boolean.
  // This isn't *awesome*, but sometimes .env vars are auto-cast to booleans
  // and this will catch that.
  if (typeof string === 'boolean') return string

  if (string && typeof string === 'string') {
    switch (string.toLowerCase().trim()) {
      case 'true':
      case 'yes':
      case '1':
        return true
      case 'false':
      case 'no':
      case '0':
      case null:
        return false
      default:
        return Boolean(string)
    }
  } else return false
}

export default stringToBoolean
