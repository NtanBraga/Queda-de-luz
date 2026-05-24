//Requisição client-side para APIs de terceiros como Nominatim e Overpass
//Evitar bloqueio 'Too many attempts' em host-side caso haja muitas requisições
let lastRequest = 0

const rateLimit = async (): Promise<void> => {
  const interval = 1100
  const date = Date.now()
  const timeSinceLastRequest = date - lastRequest

  if (timeSinceLastRequest < interval) {
    const waitTime = interval - timeSinceLastRequest
    await new Promise((resolve) => setTimeout(resolve, waitTime))
  }
  lastRequest = Date.now()
}

export const safeFetch = async (url: string, timeout = 25000, retries = 3): Promise<Response> => {
  if (url.includes('nominatim.openstreetmap.org')) await rateLimit()

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeout)

  try {
    const response = await fetch(url, {
      signal: controller.signal,
    })

    if (!response.ok) {
      throw new Error(`Erro na requisição da API: ${response.status}: ${response.statusText}`)
    }

    clearTimeout(timer)
    return response
  } catch (error: any) {
    clearTimeout(timer)

    if (retries > 0) {
      console.warn(`Falha na requisição. Tentando novamente. ${retries} tentativas faltando...`)

      if (url.includes('overpass')) {
        await new Promise((resolve) => setTimeout(resolve, 1000))
      }

      return safeFetch(url, timeout, retries - 1)
    }

    if (error.name === 'AbortError') {
      throw new Error('A requisição demorou demmais: Timeout')
    }
    throw error
  }
}
