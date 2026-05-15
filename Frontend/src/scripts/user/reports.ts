const API_BANCO_DE_DADOS = 'http://localhost:5176/homepage/cities/1'

export const postReport = async (district_id: number, token: string | null) => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  try {
    const response = await fetch(`${API_BANCO_DE_DADOS}/districts/${district_id}/reports`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        Is_Fixed: false,
        Problem_Category_id: 1,
      }),
    })

    if (!response.ok) {
      throw new Error(`Erro ao tentar processar requisição: ${response.status}`)
    }

    return await response.json()
  } catch (e) {
    console.error('Erro ao receber reporte: ', e)
    throw e
  }
}

export const getReports = async () => {
  try {
    const response = await fetch(`${API_BANCO_DE_DADOS}/statistics`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`Erro ao tentar processar requisição: ${response.status}`)
    }

    return await response.json()
  } catch (e) {
    console.error('Erro ao pegar reportes: ', e)
    throw e
  }
}

export const resolveReport = async(district_id: number, token: string) => {
  try{
    const response = await fetch(`${API_BANCO_DE_DADOS}/districts/${district_id}/reports`,{
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        Is_Fixed: true,
        Problem_Category_id: 1,
      }),
    })

    if(!response.ok) {
      throw new Error(`Erro ao enviar resolveReport para banco de dados: ${response.status}`)
    }

    return await response.json()
  }catch(e) {
    console.error("Falha ao enviar requisição de resolveReport: ", e)
    throw e
  }
}