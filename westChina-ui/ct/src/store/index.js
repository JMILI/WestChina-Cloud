import Vue from 'vue'
import Vuex from 'vuex'
import app from './modules/app'
import user from './modules/user'
import tagsView from './modules/tagsView'
import permission from './modules/permission'
import settings from './modules/settings'
import getters from './getters'
import ctTools from "./modules/ctTools";
import ctPatientInfo from "./modules/ctPatientInfo"
import dicom from "./modules/dicom";
import makerImage from "./modules/makerImage";
import makerToolsOfMe from "./modules/makerToolsOfMe"
import aiLesion from "./modules/aiLesion"

import { createPersistPlugin } from '@/utils/vuexPersist'

Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    app,
    user,
    tagsView,
    permission,
    settings,
    ctTools,
    ctPatientInfo,
    dicom,
    makerImage,
    makerToolsOfMe,
    aiLesion,
  },
  getters,
  plugins: [createPersistPlugin()],

})

export default store
