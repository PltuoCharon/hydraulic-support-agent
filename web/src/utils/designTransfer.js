const KEY = "hs.designTransfer.v1"

const ALLOWED = new Set([
  "selected_support",
  "calculated_requirement",
])

const storage = () =>
  typeof window !== "undefined"
    ? window.sessionStorage
    : null

const valid = (payload) => {
  if (payload == null || payload.version !== 1) return false
  if (ALLOWED.has(payload.source_type) === false) return false

  const resistance = Number(
    payload?.target?.resistance_kn,
  )

  return Number.isFinite(resistance) && resistance > 0
}

export const writeDesignTransfer = (payload) => {
  if (valid(payload) === false) {
    throw new Error("invalid design transfer payload")
  }

  storage()?.setItem(KEY, JSON.stringify(payload))
  return payload
}

export const readDesignTransfer = () => {
  const s = storage()
  const raw = s?.getItem(KEY)

  if (raw == null) return null

  try {
    const payload = JSON.parse(raw)

    if (valid(payload) === false) {
      s.removeItem(KEY)
      return null
    }

    return payload
  } catch {
    s.removeItem(KEY)
    return null
  }
}

export const clearDesignTransfer = () => {
  storage()?.removeItem(KEY)
}
