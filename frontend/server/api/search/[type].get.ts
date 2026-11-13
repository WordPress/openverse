import { defineEventHandler } from "h3"
import { proxyApiRequest } from "~~/server/utils/proxy"

export default defineEventHandler((event) => proxyApiRequest(event, "search"))
