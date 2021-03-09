<template>
  <b-container fluid>
    <h3>{{ stats.toto }}</h3>
    <b-row class="mb-4">
      <repartitioncharts> </repartitioncharts>
    </b-row>
  </b-container>
</template>

<script>
import repartitioncharts from '../../components/stats/repartitioncharts.vue'
export default {
  components: { repartitioncharts },
  name: 'Stats',
  async asyncData ({ app }) {
    const data = await app.$axios.$get('/stats/')
    return {
      stats: data
    }
  }
}
</script>

<style scoped>
</style>
