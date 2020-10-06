function doNotTrackEnabled() {
  //        Standard                     IE 9/10              IE11/MS Edge
  return navigator.doNotTrack || navigator.msDoNotTrack || window.doNotTrack
}

function isTrackingEnabled() {
  if (typeof window === 'undefined' || typeof navigator === 'undefined') {
    return false
  }

  const gaAvailable = window.ga !== null && window.ga !== undefined

  if (!gaAvailable) {
    console.warn('Google Analytics is unavailable. Unable to send any events.')
  }

  return gaAvailable && !doNotTrackEnabled()
}

function sendEvent(event) {
  window.ga('send', event)
}

function sendPageView() {
  sendEvent('pageview')
}

function set(field, params) {
  window.ga('set', field, params)
}

function setCurrentPage(to) {
  set('page', to.fullPath)
}

const GoogleAnalytics = () => {
  const enabled = isTrackingEnabled()
  return {
    sendPageView(to) {
      if (enabled) {
        setCurrentPage(to)
        sendPageView()
      }
    },
    sendEvent(event) {
      if (enabled) {
        sendEvent(event)
      }
    },
  }
}

export default GoogleAnalytics

export function Event(category, action, label = '', value = 0) {
  return {
    hitType: 'event',
    eventCategory: category,
    eventAction: action,
    eventLabel: label,
    eventValue: value,
  }
}
