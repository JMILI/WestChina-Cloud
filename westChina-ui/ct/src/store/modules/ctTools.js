const ctTools = {
  state: {
    invert: false,
    hflip: false,
    vflip: false,
    pixelReplication: true,
    rotation: 0,


    isShowPatientInfo: true,
    isShowStudyInfo: false,
    isShowSeriesInfo: false,
    isShowInstancesInfo: false,
    isShowImageInfo: false,
    isShowEquipmentInfo: false,
    isShowUIDS: false,

    openStudy:true,

  },

  mutations: {
    SET_INVERT: (state) => {
      state.invert = !state.invert
    },

    SET_HFLIP: (state) => {
      state.hflip = !state.hflip
    },
    SET_VFLIP: (state) => {
      state.vflip = !state.vflip
    },
    SET_PIXEL_REPLICATION: (state) => {
      state.pixelReplication = !state.pixelReplication
    },
    // SET_ROTATION:(state)=>{
    //   state.rotation=!state.rotation
    // },


    //region dicom 信息展示开关
    SET_IS_SHOW_PATIENT_INFO: (state) => {
      state.isShowPatientInfo = !state.isShowPatientInfo
      state.isShowStudyInfo = false
      state.isShowSeriesInfo = false
      state.isShowInstancesInfo = false
      state.isShowImageInfo = false
      state.isShowEquipmentInfo = false
      state.isShowUIDS = false
    },
    SET_IS_SHOW_STUDY_INFO: (state) => {
      state.isShowStudyInfo = !state.isShowStudyInfo
      state.isShowPatientInfo = false
      state.isShowSeriesInfo = false
      state.isShowInstancesInfo = false
      state.isShowImageInfo = false
      state.isShowEquipmentInfo = false
      state.isShowUIDS = false
    },
    SET_IS_SHOW_SERIES_INFO: (state) => {
      state.isShowSeriesInfo = !state.isShowSeriesInfo
      state.isShowPatientInfo = false
      state.isShowStudyInfo = false
      state.isShowInstancesInfo = false
      state.isShowImageInfo = false
      state.isShowEquipmentInfo = false
      state.isShowUIDS = false
    },
    SET_IS_SHOW_INSTANCES_INFO: (state) => {
      state.isShowInstancesInfo = !state.isShowInstancesInfo
      state.isShowPatientInfo = false
      state.isShowStudyInfo = false
      state.isShowSeriesInfo = false
      state.isShowImageInfo = false
      state.isShowEquipmentInfo = false
      state.isShowUIDS = false
    },
    SET_IS_SHOW_IMAGE_INFO: (state) => {
      state.isShowImageInfo = !state.isShowImageInfo
      state.isShowPatientInfo = false
      state.isShowStudyInfo = false
      state.isShowSeriesInfo = false
      state.isShowInstancesInfo = false
      state.isShowEquipmentInfo = false
      state.isShowUIDS = false
    },
    SET_IS_SHOW_EQUIPMENT_INFO: (state) => {
      state.isShowEquipmentInfo = !state.isShowEquipmentInfo
      state.isShowPatientInfo = false
      state.isShowStudyInfo = false
      state.isShowSeriesInfo = false
      state.isShowInstancesInfo = false
      state.isShowImageInfo = false
      state.isShowUIDS = false
    },
    SET_IS_SHOW_UIDS_INFO: (state) => {
      state.isShowUIDS = !state.isShowUIDS
      state.isShowPatientInfo = false
      state.isShowStudyInfo = false
      state.isShowSeriesInfo = false
      state.isShowInstancesInfo = false
      state.isShowImageInfo = false
      state.isShowEquipmentInfo = false
    },
    //  endregion

    SET_OPEN_STUDY:(state)=>{
      state.openStudy = !state.openStudy
    },

    SET_DEFAULT_STUDY:(state)=>{
      state.openStudy = true
    }
  },
  actions: {
    changeViewPort({commit}, name) {
      commit(name.toString())
    },
    changeShowInfo({commit}, switchInfo) {
      commit(switchInfo.toString())
    },
    openStudy({commit}){
      commit('SET_OPEN_STUDY')
    },
    setDefaultStudy({commit}){
      commit('SET_DEFAULT_STUDY')
    }
  }
}

export default ctTools
