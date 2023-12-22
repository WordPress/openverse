import { isProd } from "~/utils/node-env"
import { useCookie } from "#imports"

export const cookieOptions: Parameters<typeof useCookie>[1] = {
  path: "/",
  sameSite: "strict",
  maxAge: 60 * 60 * 24 * 60, // 60 days; Makes the cookie persistent.
  secure: isProd,
}
