function stringToBoolean(string) {
  if (string) {
    switch (string.toLowerCase().trim()) {
      case 'true': case 'yes': case '1': return true;
      case 'false': case 'no': case '0': case null: return false;
      default: return Boolean(string);
    }
  }
  else return false;
}

const flags = {
  watermark: stringToBoolean(process.env.WATERMARK),
  socialSharing: stringToBoolean(process.env.SOCIAL_SHARING),
};

export default flags;
