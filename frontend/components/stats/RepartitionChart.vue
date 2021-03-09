<template>
  <doughnut-chart v-if="loaded" :chartdata="chartdata" :options="options" />
</template>
<script>
import DoughnutChart from './DoughnutChart'
export default {
  name: 'RepartitionChart',
  components: { DoughnutChart },
  props: {
    stats: {
      type: Object,
      default () {
        return {
          malware: {
            stateanalyse: [0, 0, 0],
            labels: ['', '', '']
          },
          worker: {
            stateanalyse: [0, 0, 0],
            labels: ['', '', '']
          }
        }
      }
    }
  },
  data () {
    return {
      chartdata: null,
      options: null,
      loaded: false
    }
  },
  mounted () {
    this.chartdata = {
      datasets: [{
        data: this.stats.malware.stateanalyze,
        backgroundColor: ['#e74c3c', '#fd7e14', '#00bc8c'],
        borderColor: ['##fff', '##fff', '##fff']
      }],
      labels: this.stats.malware.labels
    }
    this.options = {
      responsive: true,
      maintainAspectRatio: false,
      title: {
        display: true
      },
      legend: {
        position: 'bottom'
      }
    }
    this.loaded = true
  }
}
</script>
<style scoped>
</style>
