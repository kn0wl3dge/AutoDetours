<template>
  <b-container fluid>
    <h3> Dashboard </h3>
    <b-row class="mb-4">
      <repartitioncharts :datafrommalware="stats"> </repartitioncharts>
    </b-row>
  </b-container>
</template>

<script>
import repartitioncharts from '../components/stats/repartitioncharts.vue'
export default {
  components: { repartitioncharts },
  name: 'Dashoard',
  async asyncData ({ app }) {
    const datafrommalware = await app.$axios.$get('/stats/')
    return {
      stats: {
        stateanalyze: datafrommalware.status,
        labels: ['Not Analyzed', 'Analyzing', 'Analyzed']
      }
    }
  }
}
</script>

<style>
.container {
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.title {
  font-family:
    'Quicksand',
    'Source Sans Pro',
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    'Helvetica Neue',
    Arial,
    sans-serif;
  display: block;
  font-weight: 300;
  font-size: 100px;
  color: #35495e;
  letter-spacing: 1px;
}

.subtitle {
  font-weight: 300;
  font-size: 42px;
  color: #526488;
  word-spacing: 5px;
  padding-bottom: 15px;
}

.links {
  padding-top: 15px;
}
</style>
