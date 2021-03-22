<template>
  <b-container fluid>
    <h3> Dashboard </h3>
    <b-row class="mb-4">
      <b-col>
        <b-card-group deck>
          <b-card header="Total Malwares" class="text-center">
            <animated-number class="number" :value="stats.count.total_malwares" round="1" />
          </b-card>
          <b-card header="Analyzed Malwares" class="text-center">
            <animated-number class="number" :value="stats.count.total_malwares_analyzed" round="1" />
          </b-card>
          <b-card header="Labels Number" class="text-center">
            <animated-number class="number" :value="stats.count.distinct_labels_number" round="1" />
          </b-card>
          <b-card header="Workers Number" class="text-center">
            <animated-number class="number" :value="stats.count.workers_number" round="1" />
          </b-card>
        </b-card-group>
      </b-col>
    </b-row>
    <b-row class="mb-4">
      <b-col sm="4">
        <b-card header="Malwares States" class="text-center">
          <repartition-chart :stats="stats.malware" />
        </b-card>
      </b-col>
      <b-col sm="4">
        <b-card header="Most Seen Labels" class="text-center">
          <repartition-area-chart :stats="stats.worker" />
        </b-card>
      </b-col>
      <b-col sm="4">
        <b-card header="Workers States" class="text-center">
          <repartition-chart :stats="stats.worker" />
        </b-card>
      </b-col>
    </b-row>
    <b-row class="mb-4">
      <b-col>
        <b-card header="Analysis Load" class="text-center">
          <time-line-chart :stats="stats.worker" />
        </b-card>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import AnimatedNumber from 'animated-number-vue'
import RepartitionChart from '../components/stats/RepartitionChart'
import TimeLineChart from '../components/stats/TimeLineChart.vue'
import RepartitionAreaChart from '../components/stats/RepartitionAreaChart.vue'
export default {
  components: { RepartitionChart, TimeLineChart, AnimatedNumber, RepartitionAreaChart },
  async asyncData ({ app }) {
    const resp = await app.$axios.$get('/stats/')
    return {
      stats: {
        malware: {
          stateanalyze: resp.malwares_repartition,
          labels: ['Not Analyzed', 'Analyzing', 'Analyzed', 'Timed Out'],
          borderColors: ['##fff', '##fff', '##fff', '##fff'],
          colors: ['#e74c3c', '#fd7e14', '#00bc8c', '#375a7f']
        },
        worker: {
          stateanalyze: resp.workers_repartition,
          labels: ['Registered', 'Tasked', 'Finished'],
          borderColors: ['##fff', '##fff', '##fff'],
          colors: ['#00bc8c', '#fd7e14', '#e74c3c']
        },
        malware_import_timeline: resp.malware_import_timeline,
        count: resp.count
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

.number {
  font-size: 3rem;
}
</style>
