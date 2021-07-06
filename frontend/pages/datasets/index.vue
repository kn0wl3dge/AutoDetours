<template>
  <b-container fluid>
    <h3>Datasets</h3>
    <b-row class="mb-4">
      <DatasetTable :datasets="datasets" />
    </b-row>
  </b-container>
</template>

<script>

export default {
  async asyncData ({ app }) {
    return {
      datasets: await app.$api.datasets.index()
    }
  },
  data () {
    return {
      datasets: []
    }
  }
}
</script>

<style scoped>
</style>
