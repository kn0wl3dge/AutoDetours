<template>
  <doughnut-chart v-if="loaded" :chartdata="chartdata" :options="options" />
</template>
<script>
import DoughnutChart from './doughnutchart'
export default {
  name: 'repartitionchart',
  components: { DoughnutChart },
  props: {
    datafrommalware: {
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
        data: this.datafrommalware.stateanalyze,
        backgroundColor: ['#E74C3C', '#fd7e14', '#18BC9C'],
        borderColor: ['##fff', '##fff', '##fff']
      }],
      labels: this.datafrommalware.labels
    }
    this.options = {
      responsive: true,
      maintainAspectRatio: false,
      title: {
        display: true
      }
    }
    this.loaded = true
  }
}
</script>
<style scoped>
</style>
