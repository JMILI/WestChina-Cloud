const ctPatientInfo = {
  state: {
    patCardId: '',
    patName: '',
    patPhone: '',
    studySeriesList:{},
  },

  mutations: {
    CHANGE_PATIENT_INFO: (state, patient) => {
      state.patName = patient.patName
      state.patCardId=patient.patCardId
      state.patPhone = patient.patPhone
      //这种方式解析之后，给state加不了值
      // state={...patient}
    },
    STUDY_SERIES_LIST:(state,studySeriesList)=>{
      state.studySeriesList={}
      state.studySeriesList=studySeriesList
    }
  },
  actions: {
    changePatientInfo({commit}, patient) {
      commit('CHANGE_PATIENT_INFO', patient)
    },
    updatePatientsStudySeries({commit}, studySeriesList) {
      commit('STUDY_SERIES_LIST', studySeriesList)
    },
  }
}

export default ctPatientInfo
