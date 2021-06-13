import createRepository from '@/api/api.js'

export default (ctx, inject) => {
  const repositoryWithAxios = createRepository(ctx.$axios)

  const repositories = {
    malwares: repositoryWithAxios('malwares'),
    jobs: repositoryWithAxios('jobs'),
    workers: repositoryWithAxios('workers'),
    settings: repositoryWithAxios('settings')
  }

  inject('api', repositories)
}
