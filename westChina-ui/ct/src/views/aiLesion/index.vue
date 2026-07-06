<template>
  <div class="app-container">
    <div class="table-container">
      <el-row :gutter="10" class="mb8">
        <el-col :span="1.5">
          <el-button type="info" plain icon="el-icon-back" size="mini" @click="returnRoute">返回</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="danger"
            plain
            icon="el-icon-delete"
            size="mini"
            :disabled="multiple"
            @click="handleDelete"
          >删除</el-button>
        </el-col>
        <right-toolbar :showSearch.sync="showSearch" @queryTable="getList" :columns="columns"/>
      </el-row>

      <el-table v-loading="loading" :data="aiLesionList" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center"/>
        <el-table-column label="序号" align="center" min-width="60">
          <template slot-scope="scope">
            <span>{{ queryParams.pageSize * (queryParams.pageNum - 1) + scope.$index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="身份证号" align="center" prop="patCardId" min-width="140" v-if="columns[0].visible"/>
        <el-table-column label="病人姓名" align="center" prop="patientName" min-width="90" v-if="columns[1].visible"/>
        <el-table-column label="检查部位" align="center" prop="bodyPart" min-width="90" v-if="columns[2].visible"/>
        <el-table-column label="切片数" align="center" prop="imageCount" min-width="70" v-if="columns[3].visible"/>
        <el-table-column label="病灶数" align="center" prop="lesionCount" min-width="70" v-if="columns[4].visible"/>
        <el-table-column label="识别医生" align="center" prop="detectDoctor" min-width="90" v-if="columns[5].visible"/>
        <el-table-column label="识别时间" align="center" prop="detectTime" min-width="140" v-if="columns[6].visible"/>
        <el-table-column label="序列路径" align="center" prop="aiSeriesPath" min-width="180" show-overflow-tooltip v-if="columns[7].visible"/>
        <el-table-column label="操作" align="center" min-width="160" class-name="small-padding fixed-width">
          <template slot-scope="scope">
            <el-button size="mini" type="text" icon="el-icon-view" @click="viewAiLesion(scope.row)">阅片</el-button>
            <el-button size="mini" type="text" icon="el-icon-delete" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <pagination
        :total="total"
        :page.sync="queryParams.pageNum"
        :limit.sync="queryParams.pageSize"
        :page-sizes="[5, 10, 20, 30]"
        layout="prev, pager, next, jumper,->,sizes,total"
        @pagination="getList"
      />
    </div>
  </div>
</template>

<script>
import { listAiLesion } from '@/api/ct/aiLesion'
import { getStudyListByPatCardId } from '@/api/ct/dicom'
import { minioUrl } from '@/settings'
import { mapActions } from 'vuex'
import { delAiLesionAndImages } from './aiLesion'

export default {
  name: 'aiLesionManage',
  data() {
    return {
      loading: true,
      ids: [],
      aiSeriesPaths: [],
      single: true,
      multiple: true,
      showSearch: true,
      total: 0,
      aiLesionList: [],
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        patCardId: null
      },
      columns: [
        { key: 0, label: '身份证号', visible: true },
        { key: 1, label: '病人姓名', visible: true },
        { key: 2, label: '检查部位', visible: true },
        { key: 3, label: '切片数', visible: true },
        { key: 4, label: '病灶数', visible: true },
        { key: 5, label: '识别医生', visible: true },
        { key: 6, label: '识别时间', visible: true },
        { key: 7, label: '序列路径', visible: false }
      ]
    }
  },
  created() {
    this.getList()
  },
  activated() {
    this.getList()
  },
  methods: {
    ...mapActions([
      'changePatientInfo',
      'updatePatientsStudySeries',
      'dicomOfPatCardId',
      'makerOfPatCardId',
      'aiLesionOfPatCardId',
      'setPendingAiLesionId'
    ]),
    getList() {
      this.loading = true
      this.queryParams.patCardId = this.$store.getters.aiLesionOfPatCardId
      listAiLesion(this.queryParams).then((response) => {
        this.aiLesionList = response.data.items || []
        this.total = response.data.total || 0
        this.loading = false
      })
    },
    handleSelectionChange(selection) {
      this.ids = selection.map((item) => item.dicomAiLesionId)
      this.aiSeriesPaths = selection.map((item) => item.aiSeriesPath)
      this.single = selection.length !== 1
      this.multiple = !selection.length
    },
    handleDelete(row) {
      const ids = row.dicomAiLesionId || this.ids
      const paths = row.aiSeriesPath ? [row.aiSeriesPath] : this.aiSeriesPaths
      this.$modal.confirm('是否确认删除选中的 AI 识别病灶结果？').then(() => {
        const payload = this.updateParamIds(Array.isArray(ids) ? ids : [ids])
        return delAiLesionAndImages(payload, paths)
      }).then(() => {
        this.getList()
        this.$modal.msgSuccess('删除成功')
      }).catch(() => {})
    },
    viewAiLesion(row) {
      const patCardId = row.patCardId
      const patient = {
        patCardId: row.patCardId,
        patName: row.patientName,
        patPhone: ''
      }
      this.changePatientInfo(patient)
      this.dicomOfPatCardId(patCardId)
      this.makerOfPatCardId(patCardId)
      this.aiLesionOfPatCardId(patCardId)
      this.setPendingAiLesionId(row.dicomAiLesionId)

      getStudyListByPatCardId({ patCardId }).then((result) => {
        const studySeriesList = {}
        const items = result.data || []
        if (!items.length) {
          this.$modal.alertWarning('该病人没有 CT 影像，无法阅片')
          return
        }
        const bucketName = this.$store.getters.bucketName
        const dicomPrefix = 'wadouri:'
        items.forEach((item) => {
          if (!studySeriesList[item.dicomCtStudyUid]) {
            studySeriesList[item.dicomCtStudyUid] = {}
          }
          studySeriesList[item.dicomCtStudyUid][item.dicomCtSeriesUid] = item
          item.imageIds = []
          const path = item.dicomCtPath.substring(0, item.dicomCtPath.lastIndexOf('/'))
          for (let i = 1; i <= item.dicomCtCount; i++) {
            item.imageIds.push(`${dicomPrefix}${minioUrl}${bucketName}/${path}/${i}.dcm`)
          }
        })
        this.updatePatientsStudySeries(studySeriesList)
        this.$router.push({ name: 'ct2' })
      })
    },
    returnRoute() {
      this.$router.back()
    }
  }
}
</script>
