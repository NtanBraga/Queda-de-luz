<script setup lang="ts">
defineProps<{
  users: Array<{ name: string; location: string; }>
}>()
</script>

<template>
  <div class="box-chat-viewonline">
    <div class="box-chat-viewonline-container">
      <table class="box-chat-viewonline-table">
        <thead>
          <tr>
            <th>Usuário</th>
            <th>Local</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.name">
            <td>{{ user.name }}</td>
            <td>{{ user.location }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
