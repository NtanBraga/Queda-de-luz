const requestHeader = {
  Accept: 'application/json',
  'X-Requested-With': 'XMLHttpRequest',
  'User-Agent': 'OutageMap/0.1',
}

export const safeFetch = async (url: string, timeout = 25000) => {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort, timeout)

  try {
    const response = await fetch(url, {
      headers: requestHeader,
      signal: controller.signal,
    })

    if (!response.ok) {
      throw new Error(`Erro na requisição da API: ${response.status}: ${response.statusText}`)
    }

    clearTimeout(timer)
    return response
  } catch (error: any) {
    clearTimeout(timer)
    if (error.name === 'AbortError') {
      throw new Error('A requisição demorou demmais: Timeout')
    }
    throw error
  }
}
