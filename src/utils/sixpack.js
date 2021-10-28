import axios from 'axios'

export const participate = (
  { name, defaultCase, cases },
  {
    sessionId,
    traffic_fraction,
    force,
    base_url = process.env.apiUrl.replace('/v1/', '/sixpack'),
    timeout = 3000,
  }
) => {
  if (!name || !/^[a-z0-9][a-z0-9\-_ ]*$/.test(name)) {
    throw new Error('Bad experiment_name')
  }

  if (cases.length < 2 && this.ignore_alternates_warning !== true) {
    throw new Error('Must specify at least 2 alternatives')
  }

  for (let i = 0; i < cases.length; i += 1) {
    if (!/^[a-z0-9][a-z0-9\-_ ]*$/.test(cases[i])) {
      throw new Error('Bad alternative name: ' + cases[i])
    }
  }

  let params = {
    client_id: sessionId,
    experiment: name,
    alternatives: Object.values(cases),
    user_agent: window.navigator.userAgent,
  }

  if (typeof window !== 'undefined' && force == null) {
    let regex = new RegExp('[\\?&]sixpack-force-' + name + '=([^&#]*)')
    let results = regex.exec(window.location.search)
    if (results != null) {
      force = decodeURIComponent(results[1].replace(/\+/g, ' '))
    }
  }
  if (traffic_fraction !== null && !isNaN(traffic_fraction)) {
    params.traffic_fraction = traffic_fraction
  }

  if (force != null && cases.includes(force)) {
    return Promise.resolve({
      status: 'ok',
      alternative: { name: force },
      experiment: { version: 0, name },
      client_id: sessionId,
    })
  }

  // Result looks like this:
  // {
  //   status: 'ok',
  //   alternative: { name: 'donation_percentage' },
  //   experiment: { name: 'donation_language' },
  //   client_id: '13cd8214-8a99-4587-8e50-483fdedc69b0',
  // }
  return axios
    .get(base_url + '/participate', {
      params,
      paramsSerializer,
      timeout,
    })
    .then((res) => ({
      name,
      case: res.data.status === 'ok' ? res.data.alternative.name : defaultCase,
      session: sessionId,
    }))
    .catch((error) => {
      console.error(`Using default a/b case due to error: ${error.message}`)
      return {
        name,
        case: defaultCase,
        session: sessionId,
      }
    })
}

export const convert = (
  name,
  {
    kpi,
    sessionId,
    baseUrl = process.env.apiUrl.replace('/v1', '/sixpack'),
    timeout = 3000,
  }
) => {
  if (!name || !/^[a-z0-9][a-z0-9\-_ ]*$/.test(name)) {
    throw new Error('Bad experiment_name')
  }

  let params = {
    client_id: sessionId,
    experiment: name,
    user_agent: window.navigator.userAgent,
  }
  if (kpi) {
    params.kpi = kpi
  }

  return axios.get(baseUrl + '/convert', {
    params,
    paramsSerializer,
    timeout,
  })
}

// Needed to ensure array query params are in this format:
// {array: [1,2]} becomes "?array=1&array=2", axios defaults to "?array[]=1&array[]=2"
const paramsSerializer = (params) => {
  const keys = Object.keys(params)
  let options = ''

  keys.forEach((key) => {
    const isParamTypeObject = typeof params[key] === 'object'
    const isParamTypeArray = isParamTypeObject && params[key].length >= 0

    if (!isParamTypeObject) {
      options += `${key}=${params[key]}&`
    }

    if (isParamTypeObject && isParamTypeArray) {
      params[key].forEach((element) => {
        options += `${key}=${element}&`
      })
    }
  })

  return options ? options.slice(0, -1) : options
}
