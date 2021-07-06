import createRepository from '@/api/api.js'

export default (ctx, inject) => {
  const repositoryWithAxios = createRepository(ctx.$axios)

  const repositories = {
    datasets: repositoryWithAxios('datasets'),
    jobs: repositoryWithAxios('jobs'),
    malwares: repositoryWithAxios('malwares'),
    settings: repositoryWithAxios('settings'),
    workers: repositoryWithAxios('workers')
  }

  inject('api', repositories)
}
