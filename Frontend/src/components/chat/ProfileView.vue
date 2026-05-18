<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { authAccountStore } from '@/stores/auth'
import { mapBuildStore } from '@/stores/map'
import type { NeighborhoodInfo } from '@/scripts/maps/neighborhoodMap'
import { giveAccountInfo } from '@/scripts/user/authLogin'
import { editProfile } from '@/scripts/user/userGeneric'
import { registrarContaCNPJ } from '@/scripts/user/userCNPJ'
import { registrarContaCPF } from '@/scripts/user/userCPF'
import { storeToRefs } from 'pinia'

const authStore = authAccountStore()
const mapStore = mapBuildStore()

const { neighborhoodsList, detectLocation } = storeToRefs(mapStore)
const { currentUser } = storeToRefs(authStore)

const showLogin = ref(true)
const isEditing = ref(false)

const loginForm = ref({ nome: '', senha: '' })

const registerForm = ref({
  nome: '',
  razao_social: '',
  telefone: '',
  email: '',
  senha: '',
  data: '',
  bairro_criacao: '',
  bairro_id: 0,
})

const razaoSocial = ref<'CPF' | 'CNPJ'>('CPF')

const selectRegisterNeighborhood = ref(false)

const editForm = ref({
  nome: '',
  bairro_id: 0,
  bairro_criacao: '',
  descricao: '',
  trabalho_informal: false,
})

const filteredNeighborhoods = computed(() =>
  neighborhoodsList.value.filter((n) =>
    n.name.toLowerCase().includes(registerForm.value.bairro_criacao.toLowerCase()),
  ),
)

const verifyErrorRegister = ref({
  nome: false,
  razao_social: false,
  telefone: false,
  email: false,
  senha: false,
  data: false,
  bairro_criacao: false,
})

const nameRegex = /(?!.*(\S)\1\1)^\S+( \S+)+/
const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/

const InputFix = (field: string) => {
  const form = registerForm.value

  if (field === 'nome') verifyErrorRegister.value.nome = !nameRegex.test(form.nome)
  if (field === 'senha') verifyErrorRegister.value.senha = !passwordRegex.test(form.senha)
  if (field === 'email') verifyErrorRegister.value.email = !emailRegex.test(form.email)
  if (field === 'data') verifyErrorRegister.value.data = !form.data
  if (field === 'bairro_criacao') verifyErrorRegister.value.bairro_criacao = !form.bairro_criacao
  if (field === 'razao_social') {
    const len = form.razao_social.replace(/\D/g, '').length
    verifyErrorRegister.value.razao_social = razaoSocial.value === 'CPF' ? len !== 11 : len !== 14
  }
  if (field === 'telefone') {
    verifyErrorRegister.value.telefone = form.telefone.replace(/\D/g, '').length !== 11
  }
}

const handleInputDropdownClick = () => {
  registerForm.value.bairro_criacao = ''

  selectRegisterNeighborhood.value = !selectRegisterNeighborhood.value
}

const selectingRegisterNeighborhood = (neighborhood: NeighborhoodInfo) => {
  registerForm.value.bairro_criacao = neighborhood.name
  registerForm.value.bairro_id = neighborhood.id
  selectRegisterNeighborhood.value = false
  InputFix('bairro_criacao')
}

const allIsValidRegister = computed(() => {
  const errors = verifyErrorRegister.value
  const form = registerForm.value

  return (
    !Object.values(errors).some((v) => v === true) && Object.values(form).every((v) => v !== '')
  )
})

const handleLogin = async () => {
  try {

    console.log(
      `dados de loginForm: Nome -> ${loginForm.value.nome}| Senha -> ${loginForm.value.senha}`,
    )

    authStore.login(loginForm.value)
    showLogin.value = true
  } catch (e) {
    console.error('Erro ao tentar login: ', e)
  }
}

const handleRegistration = async () => {
  const baseData = {
    nome: registerForm.value.nome,
    telefone: registerForm.value.telefone,
    email: registerForm.value.email,
    senha: registerForm.value.senha,
    bairro_criacao: registerForm.value.bairro_criacao,
    bairro_id: registerForm.value.bairro_id,
    descricao: '',
    imagem_perfil_link: '',
  }

  try {
    if (razaoSocial.value === 'CPF') {
      await registrarContaCPF({
        ...baseData,
        accountType: 'PersonAccount',
        cpf: registerForm.value.razao_social,
        data_nascimento: registerForm.value.data,
      })
    } else {
      await registrarContaCNPJ({
        ...baseData,
        accountType: 'BusinessAccount',
        cnpj: registerForm.value.razao_social,
        data_criacao: registerForm.value.data,
        slot_anuncio_quantidade: 3,
      })
    }
    showLogin.value = true
  } catch (error) {
    console.error('Falha ao realizar registro:', error)
  }
}

const startEditing = () => {
  if (!currentUser.value) return

  const user = currentUser.value
  editForm.value = {
    nome: user.nome || '',
    bairro_id: user.bairro_id || 0,
    bairro_criacao: user.bairro_criacao || '',
    descricao: user.descricao || '',
    trabalho_informal: (user as any).trabalho_informal || false,
  }
  isEditing.value = true
}

const stopEditing = () => {
  isEditing.value = false
}

const showEditNeighborhoodDropdown = ref(false)

const toogleEditDropdown = () => {
  showEditNeighborhoodDropdown.value = !showEditNeighborhoodDropdown.value
}

const closeEditDropdown = () => {
  showEditNeighborhoodDropdown.value = false
}

const selectingEditNeighborhood = (neighborhoodName: NeighborhoodInfo) => {
  editForm.value.bairro_criacao = neighborhoodName.name
  editForm.value.bairro_id = neighborhoodName.id
  showEditNeighborhoodDropdown.value = false
}

const saveProfile = async () => {
  try {
    const token: string = localStorage.getItem('userToken')!

    const updatedUserData = {
      username: editForm.value.nome,
      email: currentUser.value?.email || '',
      description: editForm.value?.descricao || null,
      district_Id: editForm.value?.bairro_id,
    }

    let payload = {}

    if (currentUser.value?.accountType === 'PersonAccount') {
      payload = {
        person_Data: {
          ...updatedUserData,
          informal_Work: editForm.value.trabalho_informal ? 'SIM' : 'NÃO',
        },
        business_Data: null,
      }
    } else {
      payload = {
        person_Data: null,
        business_Data: updatedUserData,
      }
    }

    console.log('Enviando dados de edição:', updatedUserData)

    await editProfile(payload, token)

    if (currentUser.value) {
      Object.assign(currentUser.value, editForm.value)
    }

    isEditing.value = false
  } catch (e) {
    console.error('Erro ao atualizar perfil: ', e)
    throw e
  }
}

const handleLogout = () => {
  authStore.logout()
  isEditing.value = false
}

watch(
  () => detectLocation.value,
  (newNeighborhood) => {
    if (newNeighborhood && !registerForm.value.bairro_criacao) {
      registerForm.value.bairro_criacao = newNeighborhood
    }
  },
)
</script>

<template>
  <div class="box-chat-viewprofile">
    <div v-if="!authStore.isLoggedIn">
      <Transition name="slide" mode="out-in">
        <div v-if="showLogin" class="box-chat-loginform">
          <h3>Acessar a conta</h3>
          <input
            v-model="loginForm.nome"
            @keyup.enter="handleLogin"
            type="text"
            placeholder="Nome"
          />
          <input
            v-model="loginForm.senha"
            @keyup.enter="handleLogin"
            type="password"
            placeholder="Senha"
          />
          <button class="box-chat-loginform-button" @click="handleLogin">ENTRAR</button>
          <div class="box-chat-loginform-verifications">
            <span class="box-chat-loginform-not-registered" @click="showLogin = false"
              >Não possui registro?</span
            >
          </div>
        </div>
        <div v-else class="box-chat-registerform">
          <h3>Criar sua conta</h3>
          <div class="box-chat-registerform-typeaccount">
            <button :class="{ active: razaoSocial === 'CPF' }" @click="razaoSocial = 'CPF'">
              CPF
            </button>
            <button :class="{ active: razaoSocial === 'CNPJ' }" @click="razaoSocial = 'CNPJ'">
              CNPJ
            </button>
          </div>
          <div class="box-chat-registerform-inputgroup">
            <input
              v-model="registerForm.nome"
              type="text"
              :placeholder="razaoSocial === 'CPF' ? 'Nome Completo' : 'Razão Social'"
              @blur="InputFix('nome')"
              required
            />
            <span v-if="verifyErrorRegister.nome" class="box-chat-registerform-errormsg"
              >Insira seu nome completo</span
            >
          </div>
          <div class="box-chat-registerform-inputgroup">
            <input
              v-model="registerForm.email"
              type="text"
              @blur="InputFix('email')"
              placeholder="E-mail"
              required
            />
            <span v-if="verifyErrorRegister.email" class="box-chat-registerform-errormsg"
              >Insira seu email valido</span
            >
          </div>
          <div class="box-chat-registerform-inputgroup">
            <input
              v-model="registerForm.senha"
              type="password"
              @blur="InputFix('senha')"
              placeholder="Senha"
              required
            />
            <span v-if="verifyErrorRegister.senha" class="box-chat-registerform-errormsg"
              >Insira uma senha forte</span
            >
          </div>
          <div class="box-chat-registerform-inputgroup">
            <input
              v-model="registerForm.razao_social"
              type="text"
              :placeholder="
                razaoSocial === 'CPF' ? 'CPF(000.000.000-00)' : 'CNPJ(00.000.000/0000-00)'
              "
              @blur="InputFix('razao_social')"
              required
            />
            <span v-if="verifyErrorRegister.razao_social" class="box-chat-registerform-errormsg"
              >Insira seu numero de registro valido</span
            >
          </div>
          <div class="box-chat-registerform-inputgroup">
            <input
              v-model="registerForm.data"
              type="date"
              min="1926-01-01"
              max="2025-12-31"
              @blur="InputFix('data')"
              required
            />
            <span v-if="verifyErrorRegister.data" class="box-chat-registerform-errormsg"
              >Insira uma data</span
            >
          </div>
          <div class="box-chat-registerform-neighborhood" @click="handleInputDropdownClick">
            <input
              v-model="registerForm.bairro_criacao"
              type="text"
              placeholder="Seu bairro"
              @blur="InputFix('bairro_criacao')"
              @keydown.enter.prevent="handleInputDropdownClick"
              @keydown.space.prevent="handleInputDropdownClick"
              readonly
              required
              tabindex="0"
            />
            <ul
              v-if="selectRegisterNeighborhood && filteredNeighborhoods.length"
              class="box-chat-registerform-dropdown"
            >
              <li
                v-for="n in filteredNeighborhoods"
                :key="n.id"
                @mousedown.prevent="selectingRegisterNeighborhood(n)"
                @keydown.enter.prevent="selectingRegisterNeighborhood(n)"
                tabindex="0"
              >
                {{ n.name }}
              </li>
            </ul>
            <span v-if="verifyErrorRegister.bairro_criacao" class="box-chat-registerform-errormsg"
              >Insira o bairro de criação da conta</span
            >
          </div>
          <div class="box-chat-registerform-inputgroup">
            <input
              v-model="registerForm.telefone"
              type="tel"
              placeholder="Seu numero de celular"
              @blur="InputFix('telefone')"
              pattern="\(\d{2}\)\s\d{5}-\d{4}"
              required
            />
            <span v-if="verifyErrorRegister.telefone" class="box-chat-registerform-errormsg"
              >Insira um numero de telefone</span
            >
          </div>
          <button
            class="box-chat-registerform-btn"
            :disabled="!allIsValidRegister"
            @click="handleRegistration"
          >
            CADASTRAR
          </button>
          <div class="box-chat-loginform-verifications">
            <span class="box-chat-loginform-not-registered" @click="showLogin = true"
              >Já possui conta?</span
            >
          </div>
        </div>
      </Transition>
    </div>
    <div v-else class="box-chat-profile-table-container" :class="{ 'is-editing-mode': isEditing }">
      <template v-if="!isEditing">
        <div class="box-chat-profile-header">
          <div class="box-chat-profile-avatar">
            <img v-if="currentUser?.imagem_perfil_link" :src="currentUser.imagem_perfil_link" />
            <div v-else class="box-chat-profile-avatar-placeholder">
              <img src="../../assets/images/no-photo.svg"/>
            </div>
          </div>
          <div class="box-chat-profile-info">
            <h4 class="box-chat-profile-name">{{ currentUser?.nome }}</h4>
            <p class="box-chat-profile-neighborhood">{{ currentUser?.bairro_criacao }}</p>
          </div>
        </div>
        <div class="box-chat-profile-bio">
          <p class="box-chat-profile-bio-title">Descrição</p>
          <p class="box-chat-profile-bio-text">
            {{ currentUser?.descricao || 'Ainda sem nenhuma descrição.' }}
          </p>
        </div>
        <div
          v-if="currentUser?.accountType === 'BusinessAccount'"
          class="box-chat-profile-cnpj-ads"
        >
          <p class="box-chat-profile-cnpj-ads-label">
            Produtos anunciados (Disponiveis: {{ currentUser?.slot_anuncio_quantidade + 2 }})
          </p>
          <div class="box-chat-profile-cnpj-ads-album">
            <div v-for="i in 3" :key="i" class="box-chat-profile-cnpj-slots">
              <span>Placeholder</span>
            </div>
          </div>
        </div>
        <div class="box-chat-profile-buttons-container">
          <button class="box-chat-profile-editbutton" @click="startEditing">Editar conta</button>
          <button class="box-chat-profile-logoutbutton" @click="handleLogout">Sair da conta</button>
        </div>
      </template>
      <template v-else>
        <h3 class="box-chat-profile-edit-title">Editar perfil</h3>
        <div class="box-chat-profile-edit-fields">
          <label>Seu nome / Razão social</label>
          <input
            v-model="editForm.nome"
            type="text"
            placeholder="Digite seu nome/razão social..."
          />
        </div>
        <div class="box-chat-profile-edit-fields">
          <label>Bairro de Atuação</label>
          <div class="box-chat-profile-edit-neighborhood" @click="toogleEditDropdown">
            <input
              v-model="editForm.bairro_criacao"
              type="text"
              placeholder="Seu Bairro"
              readonly
              tabindex="0"
              @blur="closeEditDropdown"
              @keydown.enter.prevent="toogleEditDropdown"
              @keydown.space.prevent="toogleEditDropdown"
            />
            <ul
              v-if="showEditNeighborhoodDropdown && neighborhoodsList.length"
              class="box-chat-profile-edit-dropdown"
            >
              <li
                v-for="n in neighborhoodsList"
                :key="n.id"
                tabindex="0"
                @mousedown.prevent="selectingEditNeighborhood(n)"
                @keydown.enter.prevent="selectingEditNeighborhood(n)"
              >
                {{ n.name }}
              </li>
            </ul>
          </div>
        </div>
        <div class="box-chat-profile-edit-fields">
          <label>Trabalha de forma informal?</label>
          <div class="box-chat-profile-edit-toogle-group">
            <button
              :class="{ active: editForm.trabalho_informal === true }"
              @click="editForm.trabalho_informal = true"
            >
              SIM
            </button>
            <button
              :class="{ active: editForm.trabalho_informal === false }"
              @click="editForm.trabalho_informal = false"
            >
              NÃO
            </button>
          </div>
        </div>
        <div class="box-chat-profile-edit-fields">
          <label>Descrição</label>
          <textarea
            v-model="editForm.descricao"
            rows="3"
            placeholder="Insira a sua descrição..."
          ></textarea>
        </div>
        <div class="box-chat-profile-buttons-container">
          <button class="box-chat-profile-edit-btn-save" @click="saveProfile">Salvar</button>
          <button class="box-chat-profile-edit-btn-cancel" @click="stopEditing">Cancelar</button>
        </div>
      </template>
    </div>
  </div>
</template>
