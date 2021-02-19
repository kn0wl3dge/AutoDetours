import createRepository from '@/api/api.js'

export default (ctx, inject) => {
  const repositoryWithAxios = createRepository(ctx.$axios)

  const repositories = {
    malware: repositoryWithAxios('malwares'),
    workers: repositoryWithAxios('workers')
  }

  inject('api', repositories)
}
