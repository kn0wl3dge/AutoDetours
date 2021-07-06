<template>
  <line-chart v-if="loaded" :chartdata="chartdata" :options="options" />
</template>

<script>
import LineChart from './BaseCharts/LineChart'
export default {
  name: 'TimeLineChart',
  components: { LineChart },
  props: {
    stats: { type: Array, default: null }
  },
  data () {
    return {
      options: {
        responsive: true,
        maintainAspectRatio: false,
        title: {
          display: false
        },
        scales: {
          xAxes: [
            {
              type: 'time',
              distribution: 'linear',
              ticks: {
                maxTicksLimit: 10
              },
              scaleLabel: {
                display: true,
                labelString: 'Datetime'
              }
            }
          ],
          yAxes: [
            {
              type: 'linear',
              ticks: {
                maxTicksLimit: 11,
                min: 0,
                beginAtZero: true
              },
              scaleLabel: {
                display: true,
                labelString: 'Number of finished analysis'
              }
            }
          ]
        },
        legend: {
          display: false
        }
      },
      loaded: false,
      chartdata: null
    }
  },
  mounted () {
    this.loaded = true
    this.chartdata = {
      datasets: [
        {
          label: 'Analysis',
          data: this.stats,
          fill: true,
          borderColor: '#f39c12',
          lineTension: 0.3
        }
      ]
    }
  }
}
</script>

<style scoped></style>
