<template>
  <b-container fluid>
    <h3> Dashboard </h3>
    <b-row class="mb-4">
      <b-col>
        <b-card header="Malwares States" class="text-center">
          <repartition-chart :stats="stats" />
        </b-card>
      </b-col>
      <b-col>
        <b-card header="Workers States" class="text-center">
          <repartition-chart />
        </b-card>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import RepartitionChart from '../components/stats/RepartitionChart'
export default {
  components: { RepartitionChart },
  async asyncData ({ app }) {
    const stats = await app.$axios.$get('/stats/')
    return {
      stats: {
        malware: {
          stateanalyze: stats.datafrommalware,
          labels: ['Not Analyzed', 'Analyzing', 'Analyzed']
        },
        worker: {
          workersup: stats.infoworker,
          labels: ['REGISTERED', 'TASKED', 'FINISHED']
        }
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
