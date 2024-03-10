

const getters = {
  sidebar: state => state.app.sidebar,
  size: state => state.app.size,
  device: state => state.app.device,

  visitedViews: state => state.tagsView.visitedViews,
  cachedViews: state => state.tagsView.cachedViews,

  token: state => state.user.token,
  avatar: state => state.user.avatar,
  enterpriseName: state => state.user.enterpriseName,
  enterpriseSystemName: state => state.user.enterpriseSystemName,
  isLessor: state => state.user.isLessor,
  logo: state => state.user.logo,
  name: state => state.user.name,
  introduction: state => state.user.introduction,
  roles: state => state.user.roles,
  permissions: state => state.user.permissions,
  bucketName: state => state.user.bucketName,

  permission_routes: state => state.permission.routes,
  topbarRouters: state => state.permission.topbarRouters,
  defaultRoutes: state => state.permission.defaultRoutes,
  sidebarRouters: state => state.permission.sidebarRouters,


  invert: state => state.ctTools.invert,
  hflip: state => state.ctTools.hflip,
  vflip: state => state.ctTools.vflip,
  pixelReplication: state => state.ctTools.pixelReplication,
  rotation: state => state.ctTools.rotation,

  isShowPatientInfo: state => state.ctTools.isShowPatientInfo,
  isShowStudyInfo: state => state.ctTools.isShowStudyInfo,
  isShowSeriesInfo: state => state.ctTools.isShowSeriesInfo,
  isShowInstancesInfo: state => state.ctTools.isShowInstancesInfo,
  isShowImageInfo: state => state.ctTools.isShowImageInfo,
  isShowEquipmentInfo: state => state.ctTools.isShowEquipmentInfo,
  isShowUIDS: state => state.ctTools.isShowUIDS,

  openStudy: state => state.ctTools.openStudy,

  patCardId: state => state.ctPatientInfo.patCardId,
  patName: state => state.ctPatientInfo.patName,
  patPhone: state => state.ctPatientInfo.patPhone,
  studySeriesList: state => state.ctPatientInfo.studySeriesList,

  dicomOfPatCardId: state => state.dicom.dicomOfPatCardId,

  makerOfPatCardId: state => state.makerImage.makerOfPatCardId,
  makerImageList: state => state.makerImage.makerImageList,
  makerImageInitInfo: state => state.makerImage.makerImageInitInfo,

  // columnPixelSpacingOfMe: state => state.makerToolsOfMe.columnPixelSpacingOfMe,
  // columnsOfMe: state => state.makerToolsOfMe.columnsOfMe,
  // interceptOfMe: state => state.makerToolsOfMe.interceptOfMe,
  // rowsOfMe: state => state.makerToolsOfMe.rowsOfMe,
  // rowPixelSpacingOfMe: state => state.makerToolsOfMe.rowPixelSpacingOfMe,
  // slopeOfMe: state => state.makerToolsOfMe.slopeOfMe,
  // windowCenterOfMe: state => state.makerToolsOfMe.windowCenterOfMe,
  // windowWidthOfMe: state => state.makerToolsOfMe.windowWidthOfMe,
  // scaleOfMe: state => state.makerToolsOfMe.scaleOfMe,

  makerNeed:state=>state.makerToolsOfMe.makerNeed,
}
export default getters
