<template>
  <b-container fluid>
    <h3>Workers</h3>
    <b-row class="mb-4">
      <ul>
        <li v-for="w in workers" :key="w.id">
          {{ w.id }}
        </li>
      </ul>
    </b-row>
  </b-container>
</template>

<script>
export default {
  async asyncData ({ app }) {
    return {
      workers: await app.$api.workers.index()
    }
  },
  data () {
    return {
      workers: []
    }
  }
}
</script>

<style scoped>
</style>
