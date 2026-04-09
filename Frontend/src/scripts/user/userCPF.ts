export interface UserCPF {
  nome: string
  cpf: string
  telefone: string
  email: string
  senha: string
  descrição: string
  imagem_perfil_link: string
  data_nascimento: string
  bairro_criacao: string
}

export const registrarContaCPF = async (userData: UserCPF) => {
  console.log(userData)

  try {
    console.log(`Usuario registrado no sistema: ${userData.nome}`)
  } catch (e) {
    console.error('Erro ao tentar criar conta: ', e)
  }
}
