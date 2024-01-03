import { isProd } from "~/utils/node-env"

export const cookieOptions = {
  path: "/",
  sameSite: "strict",
  maxAge: 60 * 60 * 24 * 60, // 60 days; Makes the cookie persistent.
  secure: isProd,
}
