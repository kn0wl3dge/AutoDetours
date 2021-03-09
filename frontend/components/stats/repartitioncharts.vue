<template>
  <doughnut-chart v-if="loaded" :chartdata="chartdata" :options="options" />
</template>
<script>
import DoughnutChart from './doughnutchart'
export default {
  name: 'repartitionchart',
  components: { DoughnutChart },
  // props: {
  //  top5: { type: Array, default () { return [] } }
  // },
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
        data: [2, 5, 3], // data.toto,
        backgroundColor: ['#E74C3C', '#fd7e14', '#18BC9C']
      }],
      labels: ['Analyzed', 'Test', 'Passed']
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
