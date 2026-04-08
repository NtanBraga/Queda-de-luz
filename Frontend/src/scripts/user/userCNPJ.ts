export interface UserCNPJ {
  nome: string
  cnpj: string
  telefone: string
  email: string
  descrição: string
  imagem_perfil_link: string
  data_criação: string
  slot_anuncio_quantidade: number
  bairro_criacao: string
}

export const registrarContaCNPJ = async (userData: UserCNPJ) => {
  try {
    console.log(`Usuario registrado no sistema: ${userData.nome}`)
  } catch (e) {
    console.error('Erro ao tentar criar conta: ', e)
  }
}
