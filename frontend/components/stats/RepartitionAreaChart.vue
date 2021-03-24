<template>
  <polar-area-chart v-if="loaded" :chartdata="chartdata" :options="options" />
</template>
<script>
import PolarAreaChart from './BaseCharts/PolarAreaChart'
export default {
  name: 'RepartitionAreaChart',
  components: { PolarAreaChart },
  props: {
    stats: {
      type: Object,
      default () {
        return {
          stateanalyse: [0, 0, 0],
          labels: ['', '', '']
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
        data: this.stats.stateanalyze,
        backgroundColor: this.stats.colors,
        borderColor: this.stats.borderColors
      }],
      labels: this.stats.labels
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
