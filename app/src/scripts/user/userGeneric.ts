import { GetLoginDataByToken } from './authLogin'

export interface UserGeneric {
  nome: string
  telefone: string
  email: string
  senha: string
  descricao: string
  imagem_perfil_link: string
  bairro_criacao: string
  bairro_id: number
}

export interface UserCPF extends UserGeneric {
  accountType: 'PersonAccount'
  cpf: string
  data_nascimento: string
}
export interface UserCNPJ extends UserGeneric {
  accountType: 'BusinessAccount'
  cnpj: string
  data_criacao: string
  slot_anuncio_quantidade: number
}

export type UserAccount = UserCPF | UserCNPJ

export type UserLogin = Pick<UserGeneric, 'nome' | 'senha'>

export const editProfile = async (userData: any, token: string) => {
  const API_BANCO_DE_DADOS = `http://localhost:5176/accounts`

  const token_id = await GetLoginDataByToken(token)

  const response = await fetch(`${API_BANCO_DE_DADOS}/${token_id.account_Id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(userData),
  })
  if (!response.ok) {
    throw new Error(`Falha ao atualizar informações no servidor: ${response.status}`)
  }

  const responseText = await response.text()

  const data = responseText ? JSON.parse(responseText) : { updated: true }

  console.log('Dados de edição enviados para o banco de dados:', data)

  return data
}
