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
