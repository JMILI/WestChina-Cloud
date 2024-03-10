const makerToolsOfMe = {
  state: {
    makerNeed:{
      columnPixelSpacingOfMe: null,
      columnsOfMe: null,
      interceptOfMe: null,
      rowsOfMe: null,
      rowPixelSpacingOfMe: null,
      slopeOfMe: null,
      windowCenterOfMe: null,
      windowWidthOfMe: null,
      scaleOfMe: null,
      isDicomOfMe:false,
    },

  },

  mutations: {
    UPDATE_MAKER_NEED: (state, makerNeed) => {
      state.makerNeed.columnPixelSpacingOfMe = makerNeed.columnPixelSpacingOfMe
      state.makerNeed.columnsOfMe = makerNeed.columnsOfMe
      state.makerNeed.interceptOfMe = makerNeed.interceptOfMe
      state.makerNeed.rowsOfMe = makerNeed.rowsOfMe
      state.makerNeed.rowPixelSpacingOfMe = makerNeed.rowPixelSpacingOfMe
      state.makerNeed.slopeOfMe = makerNeed.slopeOfMe
      state.makerNeed.windowCenterOfMe = makerNeed.windowCenterOfMe
      state.makerNeed.windowWidthOfMe = makerNeed.windowWidthOfMe
      state.makerNeed.scaleOfMe = makerNeed.scaleOfMe
      state.makerNeed.isDicomOfMe = makerNeed.isDicomOfMe
    },

  },
  actions: {
    updateMakerNeed({commit}, makerNeed) {
      commit('UPDATE_MAKER_NEED', makerNeed)
    },
  }
}

export default makerToolsOfMe
