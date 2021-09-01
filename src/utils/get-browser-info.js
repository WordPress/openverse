const exportBrowserInfo = () => {
  let browserInfo = ''
  if (!navigator) {
    browserInfo = 'Not available'
  } else {
    browserInfo = `Browser CodeName: ${navigator.appCodeName}\n`
    browserInfo += `Browser Name: ${navigator.appName}\n`
    browserInfo += `Browser Version: ${navigator.appVersion}\n`
    browserInfo += `Platform: ${navigator.platform}\n`
    browserInfo += `User-agent header: ${navigator.userAgent}\n`
  }

  return browserInfo
}

export const screenWidth = () => {
  if (typeof window === 'undefined') {
    return NaN
  }
  return window.innerWidth
}

export default exportBrowserInfo
