<template>
  <div class="ct-container"
       :style="{
         width:divTempWidth,
       }"
  >
    <el-scrollbar>
      <div class="left" v-show="openStudySeries">
        <el-collapse v-model="activeNames" class="left-collapse">
          <el-collapse-item v-if="makerFlag" title="标记管理" name="1" class="left-label">
            <el-card v-for="item in makerInfoList"
                     :body-style="{ padding: '0px' }">
              <div class="left-label-item" @click="viewImage(item)">
                <div>图像id：{{ item.instanceUid }}</div>
                <div>拍摄CT时间：{{ item.studyDate }}</div>
                <div class="bottom clearfix">
                  <span class="time">标记日期:{{ item.makerTime }}</span>
                </div>
              </div>
            </el-card>
            <div v-if="isDisplaySave" class="left-label-item-save">

              <el-button class="uploader-btn" @click="submitUpload">保存</el-button>
              <br>
              <span class="noteOfMe"> 解释：点击保存按钮，系统将上传标记的图像!!!</span>

            </div>
          </el-collapse-item>


          <el-collapse-item title="病人study列表" name="2" class="left-study">

            <el-collapse v-model="activeNames" v-for="(index,key) in studySeriesList" :index="key"
                         class="left-study-collapse"

            >
              <!--              study-->
              <el-collapse-item :title="'studyID:'+key" class="left-study-collapse left-study-collapse-item" name="3">
                <!--                series-->
                <el-card v-for="(childrenIndex,childrenKey) in studySeriesList[key]"
                         :childrenIndex="studySeriesList[key][childrenKey].dicomId"
                         :body-style="{ padding: '0px' }"

                >
                  <div
                    :ref="studySeriesList[key][childrenKey].dicomId"
                    class="ct-image1"
                  >

                  </div>
                  <!--  <img src="https://shadow.elemecdn.com/app/element/hamburger.9cf7b091-55e9-11e9-a976-7f4d0b07eef6.png" class="image">-->
                  <div style="padding: 14px;" class="left-study-collapse-item"
                       @click="changeCurrentImagesIds(studySeriesList[key][childrenKey])"
                  >
                    <div>id：{{ studySeriesList[key][childrenKey].dicomId }}</div>
                    <div>研究id：{{ studySeriesList[key][childrenKey].dicomCtStudyUid }}</div>
                    <div>序列id：{{ studySeriesList[key][childrenKey].dicomCtSeriesUid }}</div>
                    <div>检查部位：{{ studySeriesList[key][childrenKey].dicomCtBody }}</div>
                    <div class="bottom clearfix">
                      <span class="time">日期:{{ studySeriesList[key][childrenKey].dicomCtTime }}</span>
                      <!--                      <el-button type="text" class="button" @click="ownData(studySeriesList[key][childrenKey])">操作按钮-->
                      <!--                      </el-button>-->
                    </div>
                  </div>
                </el-card>
              </el-collapse-item>

            </el-collapse>

          </el-collapse-item>


        </el-collapse>


      </div>
    </el-scrollbar>
    <div
      class="ct-father-Open1"
      :style="{
         width:divTempWidth1,
       }"
      oncontextmenu="return false"
      onmousedown="return false"
    >
      <div id="dicomImage1"
           data-id="1"
           ref="canvas1"
           class="ct-image"
           @mouseover="hoverOver(1)"
           @contextmenu="select(1,'dicomImage1')"
      >
      </div>
      <!--      region as-->
      <!--      病人信息-->
      <!--  病人信息    左上角-->
      <div id="topleft" v-show="isShowPatientInfo" class="overlay1"
           style="position:absolute;top:10px;left:10px;">
        sop Instance Uid: {{ patient1.sopInstanceUid }}
        <br>
        是否反转：{{ getInvert }}
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowPatientInfo" class="overlay1"
           style="position:absolute;top:10px;right:10px;">
        patient ID: {{ patient1.patientId }},
        <br>
        patient Name: {{ patient1.patientName }}
        <br>
      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowPatientInfo" class="overlay1"
           style="position:absolute;bottom:10px;left:10px;">
        Patient sex: {{ patient1.patientSex }}
        <br>
        Patient age: {{ patient1.patientAge }}
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowPatientInfo" class="overlay1"
           style="position:absolute;bottom:10px;right:10px;">
        Patient birth date: {{ patient1.patientBirthDate }}
        <br>
      </div>
      <!--study信息-->
      <!--study:isShowStudyInfo-->
      <div id="topleft" v-show="isShowStudyInfo" class="overlay1"
           style="position:absolute;top:10px;left:10px; ">
        study Description: {{ studyInfo1.studyDescription }}
        <br>
        protocol Name:{{ studyInfo1.protocolName }}
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowStudyInfo" class="overlay1"
           style="position:absolute;top:10px;right:10px;"
      >
        accession: {{ studyInfo1.accession }},
        <br>
        studyId: {{ studyInfo1.studyId }}
        <br>

      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowStudyInfo" class="overlay1"
           style="position:absolute;bottom:10px;left:10px;">
        study Date: {{ studyInfo1.studyDate }}
        <br>
        study Time: {{ studyInfo1.studyTime }}
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowStudyInfo" class="overlay1"
           style="position:absolute;bottom:10px;right:10px;">
      </div>

      <!--       序列信息-->
      <!-- study:isShowSeriesInfo -->
      <div id="topleft" v-show="isShowSeriesInfo" class="overlay1"
           style="position:absolute;top:10px;left:10px; ">
        series Description: {{ seriesInfo1.seriesDescription }}
        <br>
        series:{{ seriesInfo1.series }}
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowSeriesInfo" class="overlay1"
           style="position:absolute;top:10px;right:10px;"
      >
        modality: {{ seriesInfo1.modality }},
        <br>
        bodyPart: {{ seriesInfo1.bodyPart }}
        <br>

      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowSeriesInfo" class="overlay1"
           style="position:absolute;bottom:10px;left:10px;">
        series Date: {{ seriesInfo1.seriesDate }}
        <br>
        series Time: {{ seriesInfo1.seriesTime }}
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowSeriesInfo" class="overlay1"
           style="position:absolute;bottom:10px;right:10px;">
      </div>

      <!--      instances 信息-->
      <!--      -->
      <div id="topleft" v-show="isShowInstancesInfo" class="overlay1"
           style="position:absolute;top:10px;left:10px; ">
        instance: {{ instanceInfo1.instance }}
        <br>
        acquisition:{{ instanceInfo1.acquisition }}
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowInstancesInfo" class="overlay1"
           style="position:absolute;top:10px;right:10px;"
      >
        acquisition Date: {{ instanceInfo1.acquisitionDate }},
        <br>
        acquisition Time: {{ instanceInfo1.acquisitionTime }}
        <br>

      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowInstancesInfo" class="overlay1"
           style="position:absolute;bottom:10px;left:10px;">
        content Date: {{ instanceInfo1.contentDate }}
        <br>
        content Time: {{ instanceInfo1.contentTime }}
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowInstancesInfo" class="overlay1"
           style="position:absolute;bottom:10px;right:10px;">
      </div>


      <!--       image 信息-->
      <!--      -->
      <div id="topleft" v-show="isShowImageInfo" class="overlay1"
           style="position:absolute;top:10px;left:10px; ">
        rows: {{ imageInfo1.rows }}<br>
        columns:{{ imageInfo1.columns }}<br>
        photometric Interpretation:{{ imageInfo1.photometricInter }}<br>
        image Type:{{ imageInfo1.imageType }}<br>
        bits Allocated:{{ imageInfo1.bitsAllocated }}<br>
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowImageInfo" class="overlay1"
           style="position:absolute;top:10px;right:10px;"
      >
        bits Stored:{{ imageInfo1.bitsStored }}<br>
        pixel Representation:{{ imageInfo1.pixelRepre }}<br>
        high Bit:{{ imageInfo1.highBit }}<br>
      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowImageInfo" class="overlay1"
           style="position:absolute;bottom:10px;left:10px;">
        rescale Slope:{{ imageInfo1.rescaleSlope }}<br>
        rescale Intercept:{{ imageInfo1.rescaleIntercept }}<br>
        image Position Patient:{{ imageInfo1.imagePositionPatient }}<br>
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowImageInfo" class="overlay1"
           style="position:absolute;bottom:10px;right:10px;">
        image Orientation Patient:{{ imageInfo1.imageOrientationPatient }}<br>
        pixel Spacing:{{ imageInfo1.pixelSpacing }}<br>
        samples Per Pixel:{{ imageInfo1.samplesPerPixel }}<br>
      </div>

      <!--     equipmentInfo   设备信息-->
      <!--      -->
      <div id="topleft" v-show="isShowEquipmentInfo" class="overlay1"
           style="position:absolute;top:10px;left:10px; ">
        manufacturer:{{ equipmentInfo1.manufacturer }}<br>
        model:{{ equipmentInfo1.model }}<br>
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowEquipmentInfo" class="overlay1"
           style="position:absolute;top:10px;right:10px;"
      >
        station Name:{{ equipmentInfo1.stationName }}<br>
        AE Title:{{ equipmentInfo1.AETitle }}<br>
      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowEquipmentInfo" class="overlay1"
           style="position:absolute;bottom:10px;left:10px;">
        institution Name:{{ equipmentInfo1.institutionName }}<br>
        software Version:{{ equipmentInfo1.softwareVersion }}<br>
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowEquipmentInfo" class="overlay1"
           style="position:absolute;bottom:10px;right:10px;">
        implementation Version Name:{{ equipmentInfo1.implementationVersionName }}<br>
      </div>
      <!--     UIDS   uid信息-->
      <!--      -->
      <div id="topleft" v-show="isShowUIDS" class="overlay1"
           style="position:absolute;top:10px;left:10px; ">
        study UID:{{ UIDS1.studyUID }}<br>
        series UID:{{ UIDS1.seriesUID }}<br>
        instance UID:{{ UIDS1.instanceUID }}<br>
        SOP Class UID:{{ UIDS1.SOPClassUID }}<br>
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowUIDS" class="overlay1"
           style="position:absolute;top:10px;right:10px;"
      >

      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowUIDS" class="overlay1"
           style="position:absolute;bottom:10px;left:10px;">
        transfer Syntax UID:{{ UIDS1.transferSyntaxUID }}<br>
        frame Of Reference UID:{{ UIDS1.frameOfReferenceUID }}<br>
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowUIDS" class="overlay1"
           style="position:absolute;bottom:10px;right:10px;">
      </div>
      <!--endregion-->
    </div>
    <div
      class="ct-father-Open2"
      :style="{
         width:divTempWidth2,
       }"
      oncontextmenu="return false"
      onmousedown="return false"
    >
      <div
        id="dicomImage2"
        ref="canvas2"
        class="ct-image"
        @mouseover="hoverOver(2)"
        @contextmenu="select(2,'dicomImage2')"
      >
      </div>
      <!--      region as-->
      <!--      病人信息-->
      <!--  病人信息    左上角-->
      <div id="topleft" v-show="isShowPatientInfo" class="overlay2"
           style="position:absolute;top:10px;left:10px;">
        sop Instance Uid: {{ patient2.sopInstanceUid }}
        <br>
        是否反转：{{ getInvert }}
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowPatientInfo" class="overlay2"
           style="position:absolute;top:10px;right:10px;">
        patient ID: {{ patient2.patientId }},
        <br>
        patient Name: {{ patient2.patientName }}
        <br>
      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowPatientInfo" class="overlay2"
           style="position:absolute;bottom:10px;left:10px;">
        Patient sex: {{ patient2.patientSex }}
        <br>
        Patient age: {{ patient2.patientAge }}
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowPatientInfo" class="overlay2"
           style="position:absolute;bottom:10px;right:10px;">
        Patient birth date: {{ patient2.patientBirthDate }}
        <br>
      </div>
      <!--study信息-->
      <!--study:isShowStudyInfo-->
      <div id="topleft" v-show="isShowStudyInfo" class="overlay2"
           style="position:absolute;top:10px;left:10px; ">
        study Description: {{ studyInfo2.studyDescription }}
        <br>
        protocol Name:{{ studyInfo2.protocolName }}
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowStudyInfo" class="overlay2"
           style="position:absolute;top:10px;right:10px;"
      >
        accession: {{ studyInfo2.accession }},
        <br>
        studyId: {{ studyInfo2.studyId }}
        <br>

      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowStudyInfo" class="overlay2"
           style="position:absolute;bottom:10px;left:10px;">
        study Date: {{ studyInfo2.studyDate }}
        <br>
        study Time: {{ studyInfo2.studyTime }}
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowStudyInfo" class="overlay2"
           style="position:absolute;bottom:10px;right:10px;">
      </div>

      <!--       序列信息-->
      <!-- study:isShowSeriesInfo -->
      <div id="topleft" v-show="isShowSeriesInfo" class="overlay2"
           style="position:absolute;top:10px;left:10px; ">
        series Description: {{ seriesInfo2.seriesDescription }}
        <br>
        series:{{ seriesInfo2.series }}
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowSeriesInfo" class="overlay2"
           style="position:absolute;top:10px;right:10px;"
      >
        modality: {{ seriesInfo2.modality }},
        <br>
        bodyPart: {{ seriesInfo2.bodyPart }}
        <br>

      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowSeriesInfo" class="overlay2"
           style="position:absolute;bottom:10px;left:10px;">
        series Date: {{ seriesInfo2.seriesDate }}
        <br>
        series Time: {{ seriesInfo2.seriesTime }}
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowSeriesInfo" class="overlay2"
           style="position:absolute;bottom:10px;right:10px;">
      </div>

      <!--      instances 信息-->
      <!--      -->
      <div id="topleft" v-show="isShowInstancesInfo" class="overlay2"
           style="position:absolute;top:10px;left:10px; ">
        instance: {{ instanceInfo2.instance }}
        <br>
        acquisition:{{ instanceInfo2.acquisition }}
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowInstancesInfo" class="overlay2"
           style="position:absolute;top:10px;right:10px;"
      >
        acquisition Date: {{ instanceInfo2.acquisitionDate }},
        <br>
        acquisition Time: {{ instanceInfo2.acquisitionTime }}
        <br>

      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowInstancesInfo" class="overlay2"
           style="position:absolute;bottom:10px;left:10px;">
        content Date: {{ instanceInfo2.contentDate }}
        <br>
        content Time: {{ instanceInfo2.contentTime }}
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowInstancesInfo" class="overlay2"
           style="position:absolute;bottom:10px;right:10px;">
      </div>


      <!--       image 信息-->
      <!--      -->
      <div id="topleft" v-show="isShowImageInfo" class="overlay2"
           style="position:absolute;top:10px;left:10px; ">
        rows: {{ imageInfo2.rows }}<br>
        columns:{{ imageInfo2.columns }}<br>
        photometric Interpretation:{{ imageInfo2.photometricInter }}<br>
        image Type:{{ imageInfo2.imageType }}<br>
        bits Allocated:{{ imageInfo2.bitsAllocated }}<br>
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowImageInfo" class="overlay2"
           style="position:absolute;top:10px;right:10px;"
      >
        bits Stored:{{ imageInfo2.bitsStored }}<br>
        pixel Representation:{{ imageInfo2.pixelRepre }}<br>
        high Bit:{{ imageInfo2.highBit }}<br>
      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowImageInfo" class="overlay2"
           style="position:absolute;bottom:10px;left:10px;">
        rescale Slope:{{ imageInfo2.rescaleSlope }}<br>
        rescale Intercept:{{ imageInfo2.rescaleIntercept }}<br>
        image Position Patient:{{ imageInfo2.imagePositionPatient }}<br>
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowImageInfo" class="overlay2"
           style="position:absolute;bottom:10px;right:10px;">
        image Orientation Patient:{{ imageInfo2.imageOrientationPatient }}<br>
        pixel Spacing:{{ imageInfo2.pixelSpacing }}<br>
        samples Per Pixel:{{ imageInfo2.samplesPerPixel }}<br>
      </div>

      <!--     equipmentInfo   设备信息-->
      <!--      -->
      <div id="topleft" v-show="isShowEquipmentInfo" class="overlay2"
           style="position:absolute;top:10px;left:10px; ">
        manufacturer:{{ equipmentInfo2.manufacturer }}<br>
        model:{{ equipmentInfo2.model }}<br>
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowEquipmentInfo" class="overlay2"
           style="position:absolute;top:10px;right:10px;"
      >
        station Name:{{ equipmentInfo2.stationName }}<br>
        AE Title:{{ equipmentInfo2.AETitle }}<br>
      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowEquipmentInfo" class="overlay2"
           style="position:absolute;bottom:10px;left:10px;">
        institution Name:{{ equipmentInfo2.institutionName }}<br>
        software Version:{{ equipmentInfo2.softwareVersion }}<br>
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowEquipmentInfo" class="overlay2"
           style="position:absolute;bottom:10px;right:10px;">
        implementation Version Name:{{ equipmentInfo2.implementationVersionName }}<br>
      </div>
      <!--     UIDS   uid信息-->
      <!--      -->
      <div id="topleft" v-show="isShowUIDS" class="overlay2"
           style="position:absolute;top:10px;left:10px; ">
        study UID:{{ UIDS2.studyUID }}<br>
        series UID:{{ UIDS2.seriesUID }}<br>
        instance UID:{{ UIDS2.instanceUID }}<br>
        SOP Class UID:{{ UIDS2.SOPClassUID }}<br>
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowUIDS" class="overlay2"
           style="position:absolute;top:10px;right:10px;"
      >

      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowUIDS" class="overlay2"
           style="position:absolute;bottom:10px;left:10px;">
        transfer Syntax UID:{{ UIDS2.transferSyntaxUID }}<br>
        frame Of Reference UID:{{ UIDS2.frameOfReferenceUID }}<br>
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowUIDS" class="overlay2"
           style="position:absolute;bottom:10px;right:10px;">
      </div>
      <!--endregion-->
    </div>
  </div>


</template>

<script>


//region 包引入
import {mapActions} from "vuex"
import * as cornerstone from 'cornerstone-core'
import * as dicomParser from 'dicom-parser'

import * as cornerstoneWebImageLoader from 'cornerstone-web-image-loader'
import * as cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader'
import Hammer from 'hammerjs'
import * as cornerstoneMath from 'cornerstone-math'
import * as cornerstoneTools from '@cornerstoneTools'
import {ctFile} from "../../api/ct/ctFileUpload";
import cornerstoneFileImageLoader from "cornerstone-file-image-loader/src";
import {addMaker} from "../../api/ct/maker";

cornerstoneTools.external.cornerstone = cornerstone
cornerstoneTools.external.cornerstoneMath = cornerstoneMath
cornerstoneTools.external.Hammer = Hammer
//指定要注册加载程序的基石实例
cornerstoneWADOImageLoader.external.cornerstone = cornerstone
cornerstoneWADOImageLoader.external.dicomParser = dicomParser
cornerstoneWADOImageLoader.external.cornerstoneMath = cornerstoneMath
//如果是从服务器端请求png,jpeg文件，使用这个文件
cornerstoneWebImageLoader.external.cornerstone = cornerstone
//如果是直接从前端上传的png,jpeg文件，使用这个加载图像
cornerstoneFileImageLoader.external.cornerstone = cornerstone
//endregion
export default {
  name: 'ct2row',
  data() {
    return {
      activeNames: ['1', '2', '3'],
      fileList: [],
      //region 展示图像的第一列：id="dicomImage1"  各个部分信息
      patient1: {
        patientId: '',
        patientName: '',
        patientBirthDate: '',
        patientSex: '',
        patientAge: '',
        sopInstanceUid: ''
      },
      studyInfo1: {
        studyDescription: '',
        protocolName: '',
        accession: '',
        studyId: '',
        studyDate: '',
        studyTime: ''
      },
      seriesInfo1: {
        seriesDescription: '',
        series: '',
        modality: '',
        bodyPart: '',
        seriesDate: '',
        seriesTime: ''
      },
      instanceInfo1: {
        instance: '',
        acquisition: '',
        acquisitionDate: '',
        acquisitionTime: '',
        contentDate: '',
        contentTime: ''
      },
      imageInfo1: {
        rows: '',
        columns: '',
        photometricInter: '',
        imageType: '',
        bitsAllocated: '',
        bitsStored: '',
        pixelRepre: '',
        highBit: '',
        rescaleSlope: '',
        rescaleIntercept: '',
        imagePositionPatient: '',
        imageOrientationPatient: '',
        pixelSpacing: '',
        samplesPerPixel: ''
      },
      equipmentInfo1: {
        manufacturer: '',
        model: '',
        stationName: '',
        AETitle: '',
        institutionName: '',
        softwareVersion: '',
        implementationVersionName: ''
      },
      UIDS1: {
        studyUID: '',
        seriesUID: '',
        instanceUID: '',
        SOPClassUID: '',
        transferSyntaxUID: '',
        frameOfReferenceUID: ''
      },
      //endregion
      //region 展示图像的第二列：id="dicomImage1"  各个部分信息
      patient2: {
        patientId: '',
        patientName: '',
        patientBirthDate: '',
        patientSex: '',
        patientAge: '',
        sopInstanceUid: ''
      },
      studyInfo2: {
        studyDescription: '',
        protocolName: '',
        accession: '',
        studyId: '',
        studyDate: '',
        studyTime: ''
      },
      seriesInfo2: {
        seriesDescription: '',
        series: '',
        modality: '',
        bodyPart: '',
        seriesDate: '',
        seriesTime: ''
      },
      instanceInfo2: {
        instance: '',
        acquisition: '',
        acquisitionDate: '',
        acquisitionTime: '',
        contentDate: '',
        contentTime: ''
      },
      imageInfo2: {
        rows: '',
        columns: '',
        photometricInter: '',
        imageType: '',
        bitsAllocated: '',
        bitsStored: '',
        pixelRepre: '',
        highBit: '',
        rescaleSlope: '',
        rescaleIntercept: '',
        imagePositionPatient: '',
        imageOrientationPatient: '',
        pixelSpacing: '',
        samplesPerPixel: ''
      },
      equipmentInfo2: {
        manufacturer: '',
        model: '',
        stationName: '',
        AETitle: '',
        institutionName: '',
        softwareVersion: '',
        implementationVersionName: ''
      },
      UIDS2: {
        studyUID: '',
        seriesUID: '',
        instanceUID: '',
        SOPClassUID: '',
        transferSyntaxUID: '',
        frameOfReferenceUID: ''
      },
      //endregion
      //region 图像展示cavas信息
      canvasStack1: {
        currentImageIdIndex: 0,
        isUPOrDown: 0,
        isInvertAboutUpAndDown: 0,
        currentImageId: '',
        imageIds: []
      },
      canvasStack2: {
        currentImageIdIndex: 0,
        isUPOrDown: 0,
        isInvertAboutUpAndDown: 0,
        currentImageId: '',
        imageIds: [],
      },
      inEffectCanvas: 1,
      inEffectImageId: '',
      inEffectWheelCanvas: 1,
      //endregion


      divTempWidth: 'calc(100vw - 200px)',
      divTempWidth1: 'calc(40vw - 100px)',
      divTempWidth2: 'calc(40vw - 100px)',
      studyCanvasList: {},

      makerInfoList: {},
      makerFlag: true,
      isDisplaySave: false,
      scaleOfMe: 1,

      beforeUnload: 0,
      Handler: 0,
    }
  },

  created() {
    let that = this
    //这里可以拿到数据
    let studyList = that.$store.getters.studySeriesList
    for (let studyListKey in studyList) {
      for (let studyListKeyKey in studyList[studyListKey]) {
        that.studyCanvasList[studyList[studyListKey][studyListKeyKey].dicomId] = studyList[studyListKey][studyListKeyKey].imageIds[0]
      }
    }
  },
  destroyed() {
    // window.removeEventListener('beforeunload', e => this.beforeunloadHandler(e))
    // window.removeEventListener('unload', e => this.unloadHandler(e))
  },
  mounted() {
    const that = this
    //页面刷新事件监听
    // window.addEventListener('beforeunload', e => this.beforeunloadHandler(e))
    // window.addEventListener('unload', e => this.unloadHandler(e))
    window.addEventListener("load", () => {
      //写入你想要执行的代码
      that.$store.dispatch('app/setDefaultOpenedOfMe')
      that.setDefaultStudy()
    });
    //图像操作事件监听
    let element1 = this.$refs.canvas1
    let element2 = this.$refs.canvas2
    //加载初始化
    //监听滚动事件:mounted是vue已经渲染好了最终模板，
    // 也就是可以拿到页面的元素了，或者监听页面2021年12月28日22:23:52
    element1.addEventListener(cornerstoneTools.EVENTS.MOUSE_WHEEL, this.handleScroll, false)
    element2.addEventListener(cornerstoneTools.EVENTS.MOUSE_WHEEL, this.handleScroll, false)

    // 用户用操作用具标注图像完成之后，触发这个监听事件MEASUREMENT_COMPLETED。用来保存图像png/jpeg
    element1.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_COMPLETED, function (params) {
      let waitChangInEffectCanvas = new Promise((resolve, reject) => {
        that.select(1, 'dicomImage1')
         resolve()
      })
      waitChangInEffectCanvas.then(() => {
        that.makerImageDeal()
      })
    });
    element2.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_COMPLETED, function (params) {
      let waitChangInEffectCanvas = new Promise((resolve, reject) => {
        that.select(2, 'dicomImage2')
         resolve()
      })
      waitChangInEffectCanvas.then(() => {
        that.makerImageDeal()
      })
    });
    // // 使用橡皮擦修改图像后，重新保存图像
    element1.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_REMOVED, function (params) {
      let waitChangInEffectCanvas = new Promise((resolve, reject) => {
        that.select(1, 'dicomImage1')
         resolve()
      })
      waitChangInEffectCanvas.then(() => {
        that.makerImageDeal()
      })
    });
    element2.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_REMOVED, function (params) {
      let waitChangInEffectCanvas = new Promise((resolve, reject) => {
        that.select(2, 'dicomImage2')
         resolve()
      })
      waitChangInEffectCanvas.then(() => {
        that.makerImageDeal()
      })
    });
    that.initListCanvas()
    that.initTwoCanvas()
  },
  methods: {
    ...mapActions(['updateMakerNeed','setDefaultStudy']),
    // beforeunloadHandler(){
    //   this.beforeUnload=new Date().getTime();
    // },
    // unloadHandler(e){
    //   this.Handler=new Date().getTime()-this.beforeUnload;
    //   //判断是窗口关闭还是刷新
    //   if(this.Handler<=5){
    //     console.log('为所欲为');
    //   }
    // },
    viewImage(row) {
      if (this.inEffectCanvas == 1) {
        let element1 = this.$refs.canvas1
        cornerstone.displayImage(element1, row.makerImage.imageSave)
      } else if (this.inEffectCanvas == 2) {
        let element2 = this.$refs.canvas2
        cornerstone.displayImage(element2, row.makerImage.imageSave)
      }

    },
    makerImageDeal() {
      let that = this
      let canvas = null
      if (that.inEffectCanvas == 1) {
        canvas = this.$refs.canvas1
      } else if (that.inEffectCanvas == 2) {
        canvas = this.$refs.canvas2
      }
      let cachedImagesList = cornerstone.imageCache.cachedImages
      let imageSave = null
      for (const item of cachedImagesList) {
        if (item.imageId === that.inEffectImageId) {
          imageSave = item.image
        }
      }
      //解析图像信息
      const byteArray = imageSave.data.byteArray
      const dataSet = dicomParser.parseDicom(byteArray)
      let makerInfo = {}
      let instanceUid = dataSet.string('x00080018')
      makerInfo.instanceUid = dataSet.string('x00080018')
      makerInfo.studyUid = dataSet.string('x0020000d')
      makerInfo.seriesUid = dataSet.string('x0020000e')
      makerInfo.studyDate = dataSet.string('x00080020')
      //获取病人信息
      makerInfo.patCardId = that.$store.getters.patCardId
      makerInfo.patientName = that.$store.getters.patName
      //获取医生信息和企业信息
      makerInfo.makerDoctor = that.$store.getters.name
      makerInfo.makerEnterpriseName = that.$store.getters.enterpriseName
      //图像信息
      makerInfo.makerColumns = that.$store.getters.makerNeed.columnsOfMe
      makerInfo.makerRows = that.$store.getters.makerNeed.rowsOfMe
      makerInfo.makerColumnPixelSpacing = that.$store.getters.makerNeed.columnPixelSpacingOfMe
      makerInfo.makerRowPixelSpacing = that.$store.getters.makerNeed.rowPixelSpacingOfMe
      makerInfo.makerSlope = that.$store.getters.makerNeed.slopeOfMe
      makerInfo.makerIntercept = that.$store.getters.makerNeed.interceptOfMe
      makerInfo.makerWindowCenter = that.$store.getters.makerNeed.windowCenterOfMe
      makerInfo.makerWindowWidth = that.$store.getters.makerNeed.windowWidthOfMe
      makerInfo.makerScale = that.$store.getters.makerNeed.scaleOfMe
      makerInfo.makerIsDicom = 0

      //设置标记图像时间
      makerInfo.makerTime = new Date().toLocaleString()
      //存储图像在服务器上的地址
      makerInfo.makerImageAddress = ""
      makerInfo.makerDescription = ''
      //canvas类型图像信息，方便后面上传，数据库表中没有该字段
      //生成png照片
      const viewport = cornerstone.getViewport(canvas)
      const zoom = viewport.scale.toFixed(2)
      const cols = imageSave.columns * zoom
      const rows = imageSave.rows * zoom
      let myCanvas = document.createElement('canvas')
      let canvasTemp = canvas.firstElementChild
      // console.log("打印",canvasTemp)
      myCanvas = that.cropCanvas(
        canvasTemp,
        Math.round(canvasTemp.width / 2 - cols / 2),
        Math.round(canvasTemp.height / 2 - rows / 2),
        cols, rows)
      //canvas转base64
      // let image = new Image();
      // canvas.toDataURL 返回的是一串Base64编码的URL，当然,浏览器自己肯定支持
      // 指定格式 PNG
      let base64Image = myCanvas.toDataURL("image/png");
      // console.log(base64Image)
      let datetime = new Date().getTime()
      let fileName = makerInfo.instanceUid + "_" + datetime + ".png"
      let fileOfImage = that.dataURLtoFile(base64Image, fileName)
      //记录信息
      //canvas类型图像信息，方便后面上传，数据库表中没有该字段，临时存储起来,
      // fileOfImage:需要保存的图像，png类型文件
      //imageSave：存放可以直接通过：displayImage(imageSave)展示该图像
      let makerImage = {}
      makerImage.fileOfImage = fileOfImage
      makerImage.imageSave = imageSave
      makerInfo.makerImage = makerImage
      // //将此次标记图像和信息存储到页面中
      that.makerInfoList[instanceUid] = makerInfo
      that.makerFlag = false
      that.$nextTick(() => {
        that.makerFlag = true
        that.isDisplaySave = true
      });
    },
    submitUpload() {
      let that = this
      that.$modal.loading("正在上传数据中");
      const upload = new Promise((resolve, reject) => {
        for (let makerInfoListKey in that.makerInfoList) {
          //上传前处理
          let tempDicomMaker = that.makerInfoList[makerInfoListKey]
          const uploadImage = new Promise((resolve, reject) => {
            let formDateOfMakerImage = new FormData(); //创建form对象
            formDateOfMakerImage.append('file', tempDicomMaker.makerImage.fileOfImage, tempDicomMaker.makerImage.fileOfImage.name);//通过append向form对象添加数据
            resolve(formDateOfMakerImage)
          })
          //  上传
          uploadImage.then(formDateOfMakerImage => {
            return new Promise((resolve, reject) => {
              ctFile(formDateOfMakerImage).then(res => {
                if (res.url !== '') {
                  //  封装对象
                  let dicomMaker = {}
                  dicomMaker = tempDicomMaker
                  dicomMaker.makerImage = ""
                  dicomMaker.makerImageAddress = res.url
                  resolve(dicomMaker)
                } else {
                  reject("上传失败，请检查网络")
                }
              })
            })
          }).then((dicomMaker) => {
            addMaker(dicomMaker).then(res => {
              // console.log(res)
            })
            resolve()
          })
        }
      })

      //上传完之后，清空列表
      upload.then((resolve, reject) => {
        that.$nextTick(() => {
          that.makerInfoList = {}
          that.makerFlag = true
          that.isDisplaySave = false
          setTimeout(() => {
            that.$modal.closeLoading();
          }, 500)
        });
      })
    },
    dataURLtoFile(base64Image, fileName) {//将base64转换为文件，dataurl为base64字符串，filename为文件名（必须带后缀名，如.jpg,.png）
      const dataArr = base64Image.split(",");
      let opType = base64Image.split(";base64")[0].slice(5);

      const byteString = atob(dataArr[1]);
      const options = {
        type: opType,
        endings: "native"
      }
      const u8Arr = new Uint8Array(byteString.length);
      for (let i = 0; i < byteString.length; i++) {
        u8Arr[i] = byteString.charCodeAt(i);
      }
      // console.log(u8Arr)
      return new File([u8Arr], fileName, options);
    },
    saveImages() {
      let that = this
      let tempSize = that.canvasStack1.imageIds.length
      const canvas1 = document.getElementById('dicomImage1')
      const viewport = cornerstone.getViewport(canvas1)
      for (let i = 0; i < 1; i++) {
        cornerstone.loadImage(that.canvasStack1.imageIds[i]).then(function (image) {
          //toFixed,小数点后几位进位，例如123.7654 toFixed(3)是123.765
          const zoom = viewport.scale.toFixed(2)
          const cols = image.columns * zoom
          const rows = image.rows * zoom
          //创建一个canvas元素
          let myCanvas = document.createElement('canvas')
          let canvasTemp = canvas.firstElementChild
          myCanvas = that.cropCanvas(
            canvasTemp,
            Math.round(canvasTemp.width / 2 - cols / 2),
            Math.round(canvasTemp.height / 2 - rows / 2),
            cols, rows)
          //创建一个a标签
          let a = document.createElement("a")
          // let imagemy = myCanvas.toDataURL(`image/jpeg`)
          a.href = myCanvas.toDataURL(`image/jpeg`)
          // a.href = myCanvas.toDataURL(`image/${type}`)
          a.download = `test.png`
          document.body.appendChild(a) // Required for this to work in FireFox为使其在FireFox中工作，这是必要的
          a.click()
          // debugger
          // debugger
          // const temp = cornerstoneTools.SaveAs(element1, `test.png`, `image/png`)
          // const canvas = document.getElementsByClassName('dicomImage1')[this.props.activeDcmIndex]
          // cornerstone.getActiveLayer(element1)
          // const layers = cornerstone.getLayers(element1)
          // const aa = cornerstone.getDisplayedArea(image)
          // let temp = cornerstone.imageCache
          // cornerstone.getImage(element1)
          // // cornerstone.getElementData(element1,multiple)
          // const bb = cornerstone.getEnabledElementsByImageId(that.canvasStack1.imageIds[i])
          // // cornerstone.getEnabledElements()
          // debugger
          // that.fileList.push(image)
          // ctFile(image).then(function (result) {
          //   console.log(result)
          //   debugger
          // })
        })
      }
    },
    /**
     * 重新绘制图像并返回
     * @param canvas 原来canvas图像
     * @param x
     * @param y
     * @param width
     * @param height
     * @returns {HTMLCanvasElement}
     */
    cropCanvas(canvas, x, y, width, height) {
      // create a temp canvas创建一个临时的画布
      const newCanvas = document.createElement('canvas')
      // set its dimensions
      newCanvas.width = width
      newCanvas.height = height
      // draw the canvas in the new resized temp canvas
      newCanvas.getContext('2d').drawImage(canvas, x, y, width, height, 0, 0, width, height)
      return newCanvas
    },
    //  region
    // upload() {
    //   console.log('wenjian:', this.fileList[0])
    //   var reader = new FileReader()
    //
    //   var file = this.fileList[0]
    //   //将上传的文件给cornerstoneWADOImageLoader
    //   const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(file);
    //   const canvas2 = this.$refs.canvas
    //   cornerstone.loadImage(imageId).then(function (image) {
    //     var viewport = cornerstone.getDefaultViewportForImage(
    //       canvas2,
    //       image
    //     )
    //     cornerstone.displayImage(canvas2, image, viewport)
    //   })
    //   reader.readAsArrayBuffer(file)
    //   reader.onload = function (file) {
    //     var arrayBuffer = reader.result;
    //     debugger
    //     console.log("file", file)
    //     var byteArray = new Uint8Array(arrayBuffer)
    //     let dataSet = dicomParser.parseDicom(byteArray)
    //
    //     let patientName = dataSet.string('x00100010')
    //     let patientId = dataSet.string('x00100020')
    //     let patientDob = dataSet.string('x00100030')
    //     let patientSex = dataSet.string('x00100040')
    //
    //     let scanOpt = dataSet.string('x00180022')
    //     let encodingOpt = dataSet.string('x00080102')
    //
    //     // renderData(patientName, patientId, patientDob, patientSex);
    //
    //     console.log('Patient Name          = ' + patientName)
    //     console.log('Patient ID            = ' + patientId)
    //     console.log('Patient Date of Birth = ' + patientDob)
    //     console.log('Patient Gender        = ' + patientSex)
    //     console.log('Scan optionss         = ' + scanOpt)
    //     console.log('Encoding type         = ' + encodingOpt)
    //   }
    //   //
    //
    // },
    // deleteMinioFile(index = 0) {
    //   // this.fileList.splice(index,1)
    //
    // },
    // getFileName() {
    //   let inputDOM = this.$refs.minIoFile
    //   console.log("minIoFile", this.$refs.minIoFile)
    //   inputDOM.click()
    //   console.log("minIoFile2")
    // },
    // getFile(event) {
    //   console.log("minIoFile3")
    //   console.log(document.getElementById('minIoFile').files)
    //   let files = document.getElementById('minIoFile').files
    //   let arr = []
    //   //
    //   let fileSwitch = true
    //   if (files.length > 0) {
    //     for (let i = 0; i < files.length; i++) {
    //       //文件大小限制
    //       if ((files[i].size / 1024 / 1024).toFixed(2) > 64) {
    //         this.$message({
    //           message: `${item.name}超过文件的最大长度`,
    //           type: 'warning'
    //         })
    //         fileSwitch = false
    //       }
    //     }
    //     if (fileSwitch) {
    //       for (let i = 0; i < files.length; i++) {
    //         console.log("files[i][File]", files[i][File])
    //         this.fileList.push(files[i])
    //       }
    //     }
    //   }
    // },
    //上传文件到minio
    // uploadMinIo(fileObj, index) {
    //   let vm = this
    //   // const files = fileObj;
    //   if (fileObj) {
    //     let file = fileObj
    //     //判断是否选择了文件
    //     if (file == undefined) {
    //       //未选择
    //       console.log('请上传文件')
    //     } else {
    //       //选择
    //       //获取文件类型及大小
    //       const fileName = file.name
    //       const mineType = file.type
    //       const fileSize = file.size
    //
    //       //参数
    //       let metadata = {
    //         'content-type': mineType,
    //         'content-length': fileSize
    //       }
    //       //判断储存桶是否存在
    //       minioClient.bucketExists('testfile', function (err) {
    //         if (err) {
    //           if (err.code == 'NoSuchBucket') return console.log('bucket does not exist.')
    //           return console.log(err)
    //         }
    //         //存在
    //         console.log('Bucket exists.')
    //         //准备上传
    //         let reader = new FileReader()
    //         reader.readAsDataURL(file)
    //         reader.onloadend = function (e) {
    //           const dataurl = e.target.result
    //           //base64转blob
    //           const blob = vm.toBlob(dataurl)
    //           //blob转arrayBuffer
    //           let reader2 = new FileReader()
    //           reader2.readAsArrayBuffer(blob)
    //
    //           reader2.onload = function (ex) {
    //             //定义流
    //             let bufferStream = new stream.PassThrough()
    //             //将buffer写入
    //             bufferStream.end(new Buffer(ex.target.result))
    //             //上传
    //             minioClient.putObject('testfile', fileName, bufferStream, fileSize, metadata, function (err, etag) {
    //               if (err == null) {
    //                 minioClient.presignedGetObject('testfile', fileName, 24 * 60 * 60, function (err, presignedUrl) {
    //                   if (err) return console.log(err)
    //                   //输出url
    //                   console.log(presignedUrl)
    //                   // this.$notify({
    //                   //   title: '标题名称',
    //                   //   message: h('i', { style: 'color: teal'}, '这是提示文案这是提示文案这是提示文案这是提示文案这是提示文案这是提示文案这是提示文案这是提示文案')
    //                   // });
    //                 })
    //               }
    //               //return console.log(err, etag)
    //             })
    //           }
    //         }
    //       })
    //     }
    //
    //   }
    // },
    // //base64转blob
    // toBlob(base64Data) {
    //   let byteString = base64Data
    //   if (base64Data.split(',')[0].indexOf('base64') >= 0) {
    //     byteString = atob(base64Data.split(',')[1]) // base64 解码
    //   } else {
    //     byteString = unescape(base64Data.split(',')[1])
    //   }
    //   // 获取文件类型
    //   let mimeString = base64Data.split(';')[0].split(':')[1] // mime类型
    //
    //   // ArrayBuffer 对象用来表示通用的、固定长度的原始二进制数据缓冲区
    //   // let arrayBuffer = new ArrayBuffer(byteString.length) // 创建缓冲数组
    //   // let uintArr = new Uint8Array(arrayBuffer) // 创建视图
    //
    //   let uintArr = new Uint8Array(byteString.length) // 创建视图
    //
    //   for (let i = 0; i < byteString.length; i++) {
    //     uintArr[i] = byteString.charCodeAt(i)
    //   }
    //   // 生成blob
    //   const blob = new Blob([uintArr], {
    //     type: mimeString
    //   })
    //   // 使用 Blob 创建一个指向类型化数组的URL, URL.createObjectURL是new Blob文件的方法,可以生成一个普通的url,可以直接使用,比如用在img.src上
    //   return blob
    // },
    //  endregion

    initListCanvas() {
      let that = this
      setTimeout(()=>{
        for (const temp in that.studyCanvasList) {
          let tempCanvas = that.$refs[temp][0]
          let address = that.studyCanvasList[temp]
          cornerstone.enable(tempCanvas)
          cornerstone.loadImage(address).then(function (image) {
            cornerstone.displayImage(tempCanvas, image)
          })
        }
      },300)
    },
    changeCurrentImagesIds(row) {
      // console.log(row.imageIds)
      if (this.inEffectCanvas == 1) {
        this.canvasStack1.imageIds = row.imageIds
        this.canvasStack1.currentImageIdIndex = 0
        this.canvasStack1.currentImageId = row.imageIds[0]
        // console.log(row.imageIds[0])
        this.inEffectImageId =  row.imageIds[0]
        this.displayCanvas()
      } else if (this.inEffectCanvas == 2) {
        this.canvasStack2.imageIds = row.imageIds
        this.canvasStack2.currentImageIdIndex = 0
        this.canvasStack2.currentImageId = row.imageIds[0]
        // console.log(row.imageIds[0])
        this.inEffectImageId =  row.imageIds[0]
        this.displayCanvas()
      }

    },
    initTwoCanvas() {
      let that = this
      //初始化工具
      cornerstoneTools.init()
      const canvas1 = this.$refs.canvas1
      const canvas2 = this.$refs.canvas2
      //初始化tools,方法包含是否开启触摸监听，鼠标监听，等
      // 在 DOM 中将 canvas 元素注册到 cornerstone
      cornerstone.enable(canvas1)
      cornerstone.enable(canvas2)
      //初始化自己的工具设置
      this.initTools()
    },
    initTools() {
      //stack滚动工具
      let that = this
      const canvas1 = this.$refs.canvas1
      const canvas2 = this.$refs.canvas2
      // console.log("设置默认工具")
      const StackScrollMouseWheelTool = cornerstoneTools.StackScrollMouseWheelTool
      cornerstoneTools.addTool(StackScrollMouseWheelTool)
      cornerstoneTools.setToolActive('StackScrollMouseWheel', {})
      that.styleOfCanvas()
    },
    styleOfCanvas() {
      //可以设置激活工具的颜色，也就是鼠标覆盖在上面的颜色
      cornerstoneTools.toolColors.setActiveColor('rgb(255, 255, 0)');
      //Set color for inactive tools
      cornerstoneTools.toolColors.setToolColor('rgb(0, 255, 0)');
      // Set the tool width
      cornerstoneTools.toolStyle.setToolWidth(2);
      // Set the tool font and font size
      const fontFamily =
        'Work Sans, Roboto, OpenSans, HelveticaNeue-Light, Helvetica Neue Light, Helvetica Neue, Helvetica, Arial, Lucida Grande, sans-serif';
      cornerstoneTools.textStyle.setFont(`16px ${fontFamily}`);
    },


    /**
     * 1.加载图像，2.处理图像信息，3，显示图像，4.保存图像
     */
    displayCanvas1() {
      let that = this
      const canvas1 = this.$refs.canvas1
      let tempIndex = that.canvasStack1.currentImageIdIndex
      cornerstone.loadAndCacheImage(that.canvasStack1.imageIds[tempIndex])
        .then(function (image) {
          let dealImageInfo = new Promise((resolve, reject) => {
            // 图像信息显示
            // console.log(image)
            that.canvasStack1.currentImageId = image.imageId
            that.imageInfos1(image)
            that.saveMakerNeed(image)
            resolve()
          })
          dealImageInfo.then(() => {
            //设置视口
            let viewport = {}
            viewport.scale = that.scaleOfMe
            viewport.invert = that.getInvert
            viewport.hflip = that.getHflip
            viewport.vflip = that.getVflip
            cornerstone.displayImage(canvas1, image, viewport)
          })
        })

      cornerstoneTools.addStackStateManager(canvas1, ['stack'])
      cornerstoneTools.addToolState(canvas1, 'stack', that.canvasStack1)

    },
    /**
     * 1.加载图像，2.处理图像信息，3，显示图像，4.保存图像
     */
    displayCanvas2() {
      let that = this
      const canvas2 = this.$refs.canvas2
      let tempIndex = that.canvasStack2.currentImageIdIndex
      cornerstone.loadAndCacheImage(that.canvasStack2.imageIds[tempIndex])
        .then(function (image) {
          let dealImageInfo = new Promise((resolve, reject) => {
            // 图像信息显示
            that.canvasStack2.currentImageId = image.imageId
            that.imageInfos2(image)
            that.saveMakerNeed(image)
            resolve()
            // if (that.imageInfos2(image) && that.saveMakerNeed(image)) {
            //   resolve()
            // } else {
            //   reject()
            // }
          })
          dealImageInfo.then(() => {
            //设置视口
            let viewport = {}
            viewport.scale = that.scaleOfMe
            viewport.invert = that.getInvert
            viewport.hflip = that.getHflip
            viewport.vflip = that.getVflip
            cornerstone.displayImage(canvas2, image, viewport)
          })
        })
      cornerstoneTools.addStackStateManager(canvas2, ['stack'])
      cornerstoneTools.addToolState(canvas2, 'stack', that.canvasStack2)
    },
    saveMakerNeed(image) {
      //  当前图像的一些信息，有利于标记工具的使用
      let makerNeed = {
        columnPixelSpacingOfMe: image.columnPixelSpacing,
        columnsOfMe: image.columns,
        interceptOfMe: image.intercept,
        rowsOfMe: image.rows,
        rowPixelSpacingOfMe: image.rowPixelSpacing,
        slopeOfMe: image.slope,
        windowCenterOfMe: image.windowCenter,
        windowWidthOfMe: image.windowWidth,
        scaleOfMe: this.scaleOfMe,
        isDicomOfMe: 1,
      }
      this.updateMakerNeed(makerNeed)
      return true
    },
    /**
     * 图像信息处理
     * @param image
     */
    imageInfos1(image) {
      let that = this
      //region dicom 信息解析映射
      // console.log('image.data.byteArray', image.data.byteArray)
      const byteArray = image.data.byteArray
      const dataSet = dicomParser.parseDicom(byteArray)

      that.patient1.patientId = dataSet.string('x00100020')
      that.patient1.patientName = dataSet.string("x00100010")
      that.patient1.patientBirthDate = dataSet.string('x00100030')
      that.patient1.patientSex = dataSet.string('x00100040')
      that.patient1.patientAge = dataSet.string('x00101010')
      that.patient1.sopInstanceUid = dataSet.string('x00080018')
      // console.log(that.patient.sopInstanceUid)
      that.studyInfo1.studyDescription = dataSet.string('x00081030')
      that.studyInfo1.protocolName = dataSet.string('x00181030')
      that.studyInfo1.accession = dataSet.string('x00080050')
      that.studyInfo1.studyId = dataSet.string('x00200010')
      that.studyInfo1.studyDate = dataSet.string('x00080020')
      that.studyInfo1.studyTime = dataSet.string('x00080030')

      that.seriesInfo1.seriesDescription = dataSet.string('x0008103e')
      that.seriesInfo1.series = dataSet.string('x00200011')
      that.seriesInfo1.modality = dataSet.string('x00080060')
      that.seriesInfo1.bodyPart = dataSet.string('x00180015')
      that.seriesInfo1.seriesDate = dataSet.string('x00080021')
      that.seriesInfo1.seriesTime = dataSet.string('x00080031')

      that.instanceInfo1.instance = dataSet.string('x00200013')
      that.instanceInfo1.acquisition = dataSet.string('x00200012')
      that.instanceInfo1.acquisitionDate = dataSet.string('x00080022')
      that.instanceInfo1.acquisitionTime = dataSet.string('x00080032')
      that.instanceInfo1.contentDate = dataSet.string('x00080023')
      that.instanceInfo1.contentTime = dataSet.string('x00080033')

      that.imageInfo1.rows = dataSet.string('x00280010')
      that.imageInfo1.columns = dataSet.string('x00280011')
      that.imageInfo1.photometricInter = dataSet.string('x00280004')
      that.imageInfo1.imageType = dataSet.string('x00080008')
      that.imageInfo1.bitsAllocated = dataSet.string('x00280100')
      that.imageInfo1.bitsStored = dataSet.string('x00280101')
      that.imageInfo1.highBit = dataSet.string('x00280102')
      that.imageInfo1.pixelRepre = dataSet.string('x00280103')
      that.imageInfo1.rescaleSlope = dataSet.string('x00281053')
      that.imageInfo1.rescaleIntercept = dataSet.string('x00281052')
      that.imageInfo1.imagePositionPatient = dataSet.string('x00200032')
      that.imageInfo1.imageOrientationPatient = dataSet.string('x00200037')
      that.imageInfo1.pixelSpacing = dataSet.string('x00280030')
      that.imageInfo1.samplesPerPixel = dataSet.string('x00280002')

      that.equipmentInfo1.manufacturer = dataSet.string('x00080070')
      that.equipmentInfo1.model = dataSet.string('x00081090')
      that.equipmentInfo1.stationName = dataSet.string('x00081010')
      that.equipmentInfo1.AETitle = dataSet.string('x00020016')
      that.equipmentInfo1.institutionName = dataSet.string('x00080080')
      that.equipmentInfo1.softwareVersion = dataSet.string('x00181020')
      that.equipmentInfo1.implementationVersionName = dataSet.string('x00020013')

      that.UIDS1.studyUID = dataSet.string('x0020000d')
      that.UIDS1.seriesUID = dataSet.string('x0020000e')
      that.UIDS1.instanceUID = dataSet.string('x00080018')
      that.UIDS1.SOPClassUID = dataSet.string('x00080016')
      that.UIDS1.transferSyntaxUID = dataSet.string('x00020010')
      that.UIDS1.frameOfReferenceUID = dataSet.string('x00200052')
      //endregion
      return true

    },
    /**
     * 图像信息处理
     * @param image
     */
    imageInfos2(image) {
      let that = this
      //region dicom 信息解析映射
      // console.log('image.data.byteArray', image.data.byteArray)
      const byteArray = image.data.byteArray
      const dataSet = dicomParser.parseDicom(byteArray)

      that.patient2.patientId = dataSet.string('x00100020')
      that.patient2.patientName = dataSet.string("x00100010")
      that.patient2.patientBirthDate = dataSet.string('x00100030')
      that.patient2.patientSex = dataSet.string('x00100040')
      that.patient2.patientAge = dataSet.string('x00101010')
      that.patient2.sopInstanceUid = dataSet.string('x00080018')
      // console.log(that.patient.sopInstanceUid)
      that.studyInfo2.studyDescription = dataSet.string('x00081030')
      that.studyInfo2.protocolName = dataSet.string('x00181030')
      that.studyInfo2.accession = dataSet.string('x00080050')
      that.studyInfo2.studyId = dataSet.string('x00200010')
      that.studyInfo2.studyDate = dataSet.string('x00080020')
      that.studyInfo2.studyTime = dataSet.string('x00080030')

      that.seriesInfo2.seriesDescription = dataSet.string('x0008103e')
      that.seriesInfo2.series = dataSet.string('x00200011')
      that.seriesInfo2.modality = dataSet.string('x00080060')
      that.seriesInfo2.bodyPart = dataSet.string('x00180015')
      that.seriesInfo2.seriesDate = dataSet.string('x00080021')
      that.seriesInfo2.seriesTime = dataSet.string('x00080031')

      that.instanceInfo2.instance = dataSet.string('x00200013')
      that.instanceInfo2.acquisition = dataSet.string('x00200012')
      that.instanceInfo2.acquisitionDate = dataSet.string('x00080022')
      that.instanceInfo2.acquisitionTime = dataSet.string('x00080032')
      that.instanceInfo2.contentDate = dataSet.string('x00080023')
      that.instanceInfo2.contentTime = dataSet.string('x00080033')

      that.imageInfo2.rows = dataSet.string('x00280010')
      that.imageInfo2.columns = dataSet.string('x00280011')
      that.imageInfo2.photometricInter = dataSet.string('x00280004')
      that.imageInfo2.imageType = dataSet.string('x00080008')
      that.imageInfo2.bitsAllocated = dataSet.string('x00280100')
      that.imageInfo2.bitsStored = dataSet.string('x00280101')
      that.imageInfo2.highBit = dataSet.string('x00280102')
      that.imageInfo2.pixelRepre = dataSet.string('x00280103')
      that.imageInfo2.rescaleSlope = dataSet.string('x00281053')
      that.imageInfo2.rescaleIntercept = dataSet.string('x00281052')
      that.imageInfo2.imagePositionPatient = dataSet.string('x00200032')
      that.imageInfo2.imageOrientationPatient = dataSet.string('x00200037')
      that.imageInfo2.pixelSpacing = dataSet.string('x00280030')
      that.imageInfo2.samplesPerPixel = dataSet.string('x00280002')

      that.equipmentInfo2.manufacturer = dataSet.string('x00080070')
      that.equipmentInfo2.model = dataSet.string('x00081090')
      that.equipmentInfo2.stationName = dataSet.string('x00081010')
      that.equipmentInfo2.AETitle = dataSet.string('x00020016')
      that.equipmentInfo2.institutionName = dataSet.string('x00080080')
      that.equipmentInfo2.softwareVersion = dataSet.string('x00181020')
      that.equipmentInfo2.implementationVersionName = dataSet.string('x00020013')

      that.UIDS2.studyUID = dataSet.string('x0020000d')
      that.UIDS2.seriesUID = dataSet.string('x0020000e')
      that.UIDS2.instanceUID = dataSet.string('x00080018')
      that.UIDS2.SOPClassUID = dataSet.string('x00080016')
      that.UIDS2.transferSyntaxUID = dataSet.string('x00020010')
      that.UIDS2.frameOfReferenceUID = dataSet.string('x00200052')
      //endregion
    },
    /**
     * 鼠标覆盖时，设置当前inEffectWheelCanvas参数
     * @param e
     */
    hoverOver(e) {
      // console.log(e)
      this.inEffectWheelCanvas = e
    },
    /**
     * 点击，选中所选element
     * @param id
     * @param classId
     */
    select(id, classId) {
      // console.log('select', classId)
      let that = this
      //改变当前正在作用的canavs对象id
      that.inEffectCanvas = id
      //改变颜色
      let boxs1 = document.getElementsByClassName("overlay1");
      let boxs2 = document.getElementsByClassName("overlay2")
      if (id == 1) {
        //改变当前正在作用的图像地址
        // console.log("that.inEffectImageId",that.inEffectImageId)
        that.inEffectImageId = that.canvasStack1.currentImageId
        for (let i = 0; i < boxs1.length; i++) {
          boxs1[i].style.color = "#eeff11"
          boxs2[i].style.color = "#fff"
        }
      } else if (id == 2) {
        that.inEffectImageId = that.canvasStack2.currentImageId
        // console.log("that.inEffectImageId",that.inEffectImageId)
        for (let i = 0; i < boxs2.length; i++) {
          boxs1[i].style.color = "#fff"
          boxs2[i].style.color = "#eeff11"
        }
      }
    },

    /**
     * 滚动处理
     * @param e
     */
    handleScroll(e) {
      //滚动 展示一个图像
      let up = -1
      let down = 1
      let upOrDown = e.detail.direction
      // 滚动，展示当前选中的视图下一张图像。
      if (this.inEffectCanvas === 1) {
        let isUPOrDown = this.canvasStack1.isUPOrDown
        let currentIndex = this.canvasStack1.currentImageIdIndex
        if (isUPOrDown === 0 && upOrDown === up) {
          //想要看上一张，发现isUPOrDown===0，也就是，初始化状态，之前没有使用鼠标滚轮，还是展示第一张
        } else if (isUPOrDown === 0 && upOrDown === down) {
          //想要看下一张，发现isUPOrDown===0，也就是，初始化状态，之前没有使用鼠标滚轮，展示下一张
          this.canvasStack1.isUPOrDown = down
          this.canvasStack1.currentImageIdIndex = currentIndex + down
        } else if (isUPOrDown === down && upOrDown === up) {
          //想要看上一张，发现isUPOrDown===1，也就是上次也是鼠标滚轮下移操作，，展示上一张
          this.canvasStack1.isUPOrDown = up
          this.canvasStack1.currentImageIdIndex = currentIndex + up + up
        } else if (isUPOrDown === down && upOrDown === down) {

        } else if (isUPOrDown === up && upOrDown === up) {

        } else if (isUPOrDown === up && upOrDown === down) {
          this.canvasStack1.isUPOrDown = down
          this.canvasStack1.currentImageIdIndex = currentIndex + down
        }
        this.displayCanvas1()
        //设置，翻转，像素翻转的标志变量
        this.canvasStack1.isInvertAboutUpAndDown = this.canvasStack1.isUPOrDown
      } else if (this.inEffectCanvas === 2) {
        let isUPOrDown = this.canvasStack2.isUPOrDown
        let currentIndex = this.canvasStack2.currentImageIdIndex
        if (isUPOrDown === 0 && upOrDown === up) {
          //想要看上一张，发现isUPOrDown===0，也就是，初始化状态，之前没有使用鼠标滚轮，还是展示第一张
        } else if (isUPOrDown === 0 && upOrDown === down) {
          //想要看下一张，发现isUPOrDown===0，也就是，初始化状态，之前没有使用鼠标滚轮，展示下一张
          this.canvasStack2.isUPOrDown = down
          this.canvasStack2.currentImageIdIndex = currentIndex + down
        } else if (isUPOrDown === down && upOrDown === up) {
          //想要看上一张，发现isUPOrDown===1，也就是上次也是鼠标滚轮下移操作，，展示上一张
          this.canvasStack2.isUPOrDown = up
          this.canvasStack2.currentImageIdIndex = currentIndex + up + up
        } else if (isUPOrDown === down && upOrDown === down) {

        } else if (isUPOrDown === up && upOrDown === up) {

        } else if (isUPOrDown === up && upOrDown === down) {
          this.canvasStack2.isUPOrDown = down
          this.canvasStack2.currentImageIdIndex = currentIndex + down
        }
        this.displayCanvas2()
        //设置，翻转，像素翻转的标志变量
        this.canvasStack2.isInvertAboutUpAndDown = this.canvasStack2.isUPOrDown
      }
    },
    //提供下面的监视变量的使用，getInvert，getHflip，getVflip，getPixelReplication
    watchAssist(isChangeWidth) {
      console.log("asdasd")
      if(isChangeWidth){
        if (this.inEffectCanvas === 1) {
          this.canvasStack1.currentImageIdIndex = this.canvasStack1.currentImageIdIndex - this.canvasStack1.isInvertAboutUpAndDown
          this.displayCanvas1();
          this.canvasStack1.isInvertAboutUpAndDown = 0
        }else if(this.inEffectCanvas === 2){
          this.canvasStack2.currentImageIdIndex = this.canvasStack2.currentImageIdIndex - this.canvasStack2.isInvertAboutUpAndDown
          this.displayCanvas2();
          this.canvasStack2.isInvertAboutUpAndDown = 0
        }
      }else{
        console.log("wide")
        if(this.canvasStack1.imageIds.length>0){
          this.canvasStack1.currentImageIdIndex = this.canvasStack1.currentImageIdIndex - this.canvasStack1.isInvertAboutUpAndDown
          this.displayCanvas1();
          this.canvasStack1.isInvertAboutUpAndDown = 0
        }else if(this.canvasStack2.imageIds.length>0){
          this.canvasStack2.currentImageIdIndex = this.canvasStack2.currentImageIdIndex - this.canvasStack2.isInvertAboutUpAndDown
          this.displayCanvas2();
          this.canvasStack2.isInvertAboutUpAndDown = 0
        }
      }


    },
    /**
     * 鼠标点击时，
     */
    displayCanvas() {

      if (this.inEffectCanvas === 1) {
        this.displayCanvas1()
      } else if (this.inEffectCanvas === 2) {
        this.displayCanvas2()
      }
    },
    //region 备用
    // /*
    //    * Window Resize
    //    *
    //    */
    // listenForWindowResize() {
    //   this.$nextTick(function () {
    //     window.addEventListener(
    //       "resize",
    //       this.debounce(this.onWindowResize, 100)
    //     );
    //   });
    // },
    // onWindowResize() {
    //   let canvas1 = this.$refs.canvas
    //   let canvas2 = this.$refs.canvas2
    //   canvas1.style.width = "100%"
    //   canvas1.style.height = "100%"
    //   canvas2.style.width = "100%"
    //   canvas2.style.height = "100%"
    //   cornerstone.resize(canvas1);
    //   cornerstone.resize(canvas2);
    // },
    //
// endregion

    changeWidth() {
      // console.log(this.isOpen, this.openStudySeries)
      if (this.isOpen === true && this.openStudySeries === true) {
        this.divTempWidth = 'calc(100vw - 200px)'
        this.divTempWidth1 = 'calc(40vw - 100px)'
        this.divTempWidth2 = 'calc(40vw - 100px)'
      } else if (this.isOpen === false && this.openStudySeries === true) {
        this.divTempWidth = 'calc(100vw - 54px)'
        this.divTempWidth1 = 'calc(40vw - 27px)'
        this.divTempWidth2 = 'calc(40vw - 27px)'
      } else if (this.isOpen === false && this.openStudySeries === false) {
        this.divTempWidth = 'calc(100vw - 54px)'
        this.divTempWidth1 = 'calc(50vw - 27px)'
        this.divTempWidth2 = 'calc(50vw - 27px)'
      } else {
        //true flase
        this.divTempWidth = 'calc(100vw - 200px)'
        this.divTempWidth1 = 'calc(50vw - 100px)'
        this.divTempWidth2 = 'calc(50vw - 100px)'
      }
    },


  },

  beforeUpdate() {
    //对需要修改的数据进行处理，此时数据还没有在页面更新，就是在页面更新之前的操作
  },
  updated() {
    //只要有数据更新就会执行。
    // this.displayCanvas()
  },

  computed: {
    //region viewport监视设置
    getInvert() {
      return this.$store.getters.invert
    },
    getHflip() {
      return this.$store.getters.hflip
    },
    getVflip() {
      return this.$store.getters.vflip
    },
    getPixelReplication() {
      return this.$store.getters.pixelReplication
    },
    //endregion

    //region dicom 信息展示开关
    isShowPatientInfo() {
      return this.$store.getters.isShowPatientInfo
    },
    isShowStudyInfo() {
      return this.$store.getters.isShowStudyInfo
    },
    isShowSeriesInfo() {
      return this.$store.getters.isShowSeriesInfo
    },
    isShowInstancesInfo() {
      return this.$store.getters.isShowInstancesInfo
    },
    isShowImageInfo() {
      return this.$store.getters.isShowImageInfo
    },
    isShowEquipmentInfo() {
      return this.$store.getters.isShowEquipmentInfo
    },
    isShowUIDS() {
      return this.$store.getters.isShowUIDS
    },

    //  endregion
    //region 窗口变化监视
    openStudySeries() {
      return this.$store.getters.openStudy
    },
    isOpen() {
      return this.$store.getters.sidebar.opened
    },
    //  endregion
    studySeriesList() {
      return this.$store.getters.studySeriesList
    }
  },
  watch: {
    //region viewpost 监视设置 逻辑操作
    getInvert: function (value) {
      this.watchAssist(true)
    },
    getHflip: function () {
      this.watchAssist(true)
    },
    getVflip: function () {
      this.watchAssist(true)
    },
    getPixelReplication: function () {
      this.watchAssist(true)
    },
    //  endregion
    //region 窗口变化监视
    openStudySeries: function () {
      this.changeWidth()
      this.watchAssist(false)
    },
    isOpen: function () {
      this.changeWidth()
      this.watchAssist(false)
    },
    //  endregion
  },
  components: {}
}

</script>

<style lang="scss" scoped>
@import "~@assets/styles/mixin.scss";
@import "~@assets/styles/variables.scss";

.overlay1 {
  /* prevent text selection on overlay */
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  /* ignore pointer event on overlay */
  pointer-events: none;
  color: #f1fa8c;
  font-size: 10px;
}

.overlay2 {
  /* prevent text selection on overlay */
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  /* ignore pointer event on overlay */
  pointer-events: none;
  font-size: 10px;
}

.ct-container {

  height: calc(100vh - 84px);
  background-color: #282c34;
  display: flex;
  flex-direction: row;
  //设置 滚动条，x轴隐藏
  ::v-deep .el-scrollbar__wrap {
    overflow-x: hidden;
  }


  .left {
    padding-left: 5px;
    width: 20vw;
    height: 100vh;
    background-color: #282c34 !important;
    //字体颜色
    color: white !important;

    .left-collapse {
      //width: 100%;
      //height: 100%;
      background-color: #282c34 !important;
      display: block;

      ::v-deep .el-collapse-item__header {
        background-color: #282c34 !important;
        color: #e3a5a5 !important;
        border-bottom-color: #f8f6f6;
        font-size: 10px;
      }

      ::v-deep .el-collapse-item__wrap {
        background-color: #17191c !important;
        color: white !important;
        //border-color: white !important;
      }

      ::v-deep .el-collapse-item__content {
        padding-bottom: 0px;
      }

      ::v-deep .el-card {
        border-radius: 28px;
        border: 3px solid #e6ebf5;
        background-color: #FFFFFF;
        overflow: hidden;
        color: #303133;
        -webkit-transition: 0.3s;
        transition: 0.3s;
        margin-top: 5px;
        margin-bottom: 5px;
        margin-right: 5px;
      }

      .left-label {
        .left-label-item {
          background-color: #282c34 !important;
          color: white !important;
          font-size: 10px;
          width: 20vw;
          padding: 14px;
        }

        .left-label-item-save {
          background-color: #282c34 !important;
          color: #e3a5a5 !important;
          font-size: 10px;
          width: 20vw;
          height: auto;

          ::v-deep.uploader-btn {
            margin: 3% 23.6%;
          }

          ::v-deep .el-button--medium {
            width: 50%;
            font-size: 14px;
            border-radius: 22px;
            background-color: #343536;
            border: none;
            color: white;
          }

          .noteOfMe {
            margin-bottom: 1%;
          }

        }
      }

      .left-study {
        display: block;

        .left-study-collapse {
          background-color: #282c34 !important;
          color: white !important;
          display: block;

          .left-study-collapse-item {

            .ct-image1 {
              width: 20vw;
              height: 35vh;
              display: block;
              pointer-events: none;
              background-color: #000 !important;
            }

            background-color: #282c34 !important;
            font-size: 10px;
            color: white;
            display: block;
          }
        }
      }
    }


  }

  .ct-father-Open1 {

    height: 100%;
    width: 100%;
    position: relative;
    color: white;

    .ct-image {
      width: 100%;
      height: 100%;
      background-color: #000000;
    }
  }

  .ct-father-Open2 {
    height: 100%;
    width: 100%;
    position: relative;
    color: white;

    .ct-image {
      width: 100%;
      height: 100%;
      background-color: #000000;
    }
  }

}


</style>

