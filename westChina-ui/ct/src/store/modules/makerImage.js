const makerImage = {
  state: {
    makerOfPatCardId: '',
    makerImageList: [],
    makerImageInitInfo:'',
  },

  mutations: {
    MAKER_OF_PAT_CARD_ID: (state, makerOfPatCardId) => {
      state.makerOfPatCardId = makerOfPatCardId
    },
    UPDATE_MAKER_IMAGE: (state, makerImageList) => {
      state.makerImageList=[]
      state.makerImageList = makerImageList
    },
    MAKER_IMAGE_INIT_INFO: (state, makerImageInitInfo) => {
      state.makerImageInitInfo=makerImageInitInfo
    },

  },
  actions: {
    makerOfPatCardId({commit}, makerOfPatCardId) {
      commit('MAKER_OF_PAT_CARD_ID', makerOfPatCardId)
    },
    updateMakerImageList({commit}, makerImageList) {
      commit('UPDATE_MAKER_IMAGE', makerImageList)
    },
    makerImageInitInfo({commit}, makerImageInitInfo) {
      commit('MAKER_IMAGE_INIT_INFO', makerImageInitInfo)
    },

  }
}

export default makerImage
