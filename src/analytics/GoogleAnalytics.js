function doNotTrackEnabled() {
  //        Standard                     IE 9/10              IE11/MS Edge
  return navigator.doNotTrack || navigator.msDoNotTrack || window.doNotTrack;
}

function isTrackingEnabled() {
  const gaAvailable = window.ga !== null && window.ga !== undefined;

  if (!gaAvailable) {
    console.warn('Google Analytics is unavailable. Unable to send any events.');
  }

  return gaAvailable && !doNotTrackEnabled();
}

function sendEvent(event) {
  window.ga('send', event);
}

function sendPageView() {
  sendEvent('pageview');
}

function set(field, params) {
  window.ga('set', field, params);
}

function setCurrentPage(page) {
  set('page', page);
}

const GoogleAnalytics = () => {
  const enabled = isTrackingEnabled();
  return {
    anonymizeIpAddress() {
      if (enabled) {
        set('anonymizeIp', true);
      }
    },
    updatePageView(location) {
      if (enabled) {
        setCurrentPage(location);
        sendPageView();
      }
    },
    sendEvent(event) {
      if (enabled) {
        sendEvent(event);
      }
    },
  };
};

export default GoogleAnalytics;

export function Event(category, action, label = '', value = 0) {
  return {
    hitType: 'event',
    eventCategory: category,
    eventAction: action,
    eventLabel: label,
    eventValue: value,
  };
}
