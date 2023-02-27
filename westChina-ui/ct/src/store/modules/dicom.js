const   dicom = {
  state: {
    dicomOfPatCardId: '',
  },

  mutations: {
    DICOM_OF_PAT_CARD_ID: (state, dicomOfPatCardId) => {
      state.dicomOfPatCardId=dicomOfPatCardId
    },
  },
  actions: {
    dicomOfPatCardId({commit}, dicomOfPatCardId) {
      commit('DICOM_OF_PAT_CARD_ID', dicomOfPatCardId)
    },
  }
}

export default dicom
