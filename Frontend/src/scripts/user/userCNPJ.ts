const API_BANCO_DE_DADOS = 'http://localhost:5176/accounts'

export interface UserCNPJ {
  nome: string
  cnpj: string
  telefone: string
  email: string
  senha: string
  descrição: string
  imagem_perfil_link: string
  data_criação: string
  slot_anuncio_quantidade: number
  bairro_criacao: string
  bairro_id: number
}

export const registrarContaCNPJ = async (userData: UserCNPJ) => {
  console.log(userData)

   const payload = {
    Username: userData.nome,
    Hashed_password: userData.senha,
    Email: userData.email,
    District_id: userData.bairro_id,
    Business_Details: {
      CNPJ: userData.cnpj,
    },
  }

  try {

    const response = await fetch(API_BANCO_DE_DADOS, {
      method: 'POST',
      headers: { 'Content-type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(
        `Erro ao enviar conta registrada para o banco de dados: ${response.status} -${text}`,
      )
    }

    console.log(`Usuario registrado no sistema: ${payload.Username}`)

    return await response.json();
  } catch (e) {
    console.error('Erro ao tentar criar conta: ', e)
    throw e
  }
}
