export const isDev: boolean = process.env.NODE_ENV === "development"
export const isTest: boolean = process.env.NODE_ENV === "test"
export const isProd: boolean = process.env.NODE_ENV === "production"
export const isServer: boolean = process.server ?? false
export const isClient: boolean = process.client ?? false
