<template>
  <b-container fluid>
    <b-row class="mb-2">
      <h3>Workers</h3>
    </b-row>
    <b-row>
      <worker-card
        v-for="w in workers"
        :key="w.id"
        :worker="w"
      />
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
  .card {
    width: 480px;
  }
</style>
