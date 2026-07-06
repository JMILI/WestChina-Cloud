const aiLesion = {
  state: {
    aiLesionOfPatCardId: '',
    pendingAiLesionId: null
  },
  mutations: {
    AI_LESION_OF_PAT_CARD_ID: (state, patCardId) => {
      state.aiLesionOfPatCardId = patCardId
    },
    SET_PENDING_AI_LESION_ID: (state, id) => {
      state.pendingAiLesionId = id
    }
  },
  actions: {
    aiLesionOfPatCardId({ commit }, patCardId) {
      commit('AI_LESION_OF_PAT_CARD_ID', patCardId)
    },
    setPendingAiLesionId({ commit }, id) {
      commit('SET_PENDING_AI_LESION_ID', id)
    }
  }
}

export default aiLesion
