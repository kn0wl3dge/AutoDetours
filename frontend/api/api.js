export default $axios => resource => ({
  index () {
    return $axios.$get(`/${resource}/`)
  },

  create (payload, config = {}) {
    return $axios.$post(`/${resource}/`, payload, config)
  },

  show (id) {
    return $axios.$get(`/${resource}/${id}/`)
  },

  update (payload, id) {
    return $axios.$put(`/${resource}/${id}/`, payload)
  },

  delete (id) {
    return $axios.$delete(`/${resource}/${id}/`)
  }

})
