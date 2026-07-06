<template>
  <div class="navbar">
    <div class="toolbar-left">
      <el-tooltip content="影像工具栏" placement="bottom" :open-delay="300">
        <button
          type="button"
          class="toolbar-btn"
          :class="{ 'is-active': sidebar.opened }"
          @click="toggleSideBar"
        >
          <i :class="sidebar.opened ? 'el-icon-s-fold' : 'el-icon-s-unfold'"></i>
        </button>
      </el-tooltip>
      <el-tooltip content="检查序列列表" placement="bottom" :open-delay="300">
        <button
          type="button"
          class="toolbar-btn"
          :class="{ 'is-active': isStudyPanelOpen }"
          @click="toggleStudyPanel"
        >
          <i class="el-icon-files"></i>
        </button>
      </el-tooltip>
      <el-tooltip content="返回病人列表" placement="bottom" :open-delay="300">
        <button type="button" class="toolbar-btn" @click="routeReturn">
          <i class="el-icon-back"></i>
        </button>
      </el-tooltip>
    </div>
    <!--    <div style="text-align: center;color: white;font-size:15px; float: left;">病人图像</div>-->
    <top-nav id="topmenu-container" class="topmenu-container" v-if="topNav"/>
    <!--    <hamburger id="hamburger-container"  class="hamburger-container"-->
    <!--               />-->
    <div class="right-menu">
      <template v-if="device!=='mobile'">
        <!--        这里放顶部的菜单工具 start jm-->
        <!--        <el-dropdown class="right-menu-item hover-effect">-->
        <!--&lt;!&ndash;          <span class="el-dropdown-link">&ndash;&gt;-->
        <!--&lt;!&ndash;            上传文件<i class="el-icon-arrow-down el-icon&#45;&#45;right"></i>&ndash;&gt;-->
        <!--&lt;!&ndash;          </span>&ndash;&gt;-->
        <!--          <el-dropdown-menu slot="dropdown">-->
        <!--            &lt;!&ndash;        <el-dropdown-item disabled>双皮奶</el-dropdown-item>&ndash;&gt;-->
        <!--            <el-dropdown-item>单文件dicom</el-dropdown-item>-->
        <!--            <el-dropdown-item divided>文件夹</el-dropdown-item>-->
        <!--          </el-dropdown-menu>-->
        <!--        </el-dropdown>-->
        <div v-if="isCtViewerRoute" class="right-menu-item ai-engine-menu">
          <lesion-engine-select compact :show-label="true" />
        </div>
        <el-tooltip
          v-if="isCtViewerRoute"
          :content="singleSliceTooltip"
          placement="bottom"
          :open-delay="350"
        >
          <div
            class="right-menu-item hover-effect ai-lesion-btn ai-lesion-slice-btn"
            :class="{ 'is-loading': lesionDetectLoading, 'is-disabled': !canDetectCurrentSlice }"
            @click.stop="triggerLesionDetectCurrentSlice"
          >
            <i :class="lesionDetectLoading ? 'el-icon-loading' : 'el-icon-picture-outline'"></i>
            当前层识别
          </div>
        </el-tooltip>
        <el-tooltip
          v-if="isCtViewerRoute"
          :content="seriesDetectTooltip"
          placement="bottom"
          :open-delay="350"
        >
          <div
            class="right-menu-item hover-effect ai-lesion-btn"
            :class="{ 'is-loading': lesionDetectLoading, 'is-disabled': !canDetectSeries }"
            @click.stop="triggerLesionDetect"
          >
            <i :class="lesionDetectLoading ? 'el-icon-loading' : 'el-icon-aim'"></i>
            识别病灶
          </div>
        </el-tooltip>
        <div
          class="right-menu-item hover-effect dicom-guide-btn"
          @click="showDicomDialog = true"
        >
          <i class="el-icon-info"></i>
          DICOM结构解释
        </div>
        <el-dropdown class="right-menu-item hover-effect layout-dropdown" trigger="click">
          <span class="el-dropdown-link layout-trigger">
            <i class="el-icon-s-grid"></i>
            布局
            <i class="el-icon-arrow-down el-icon--right"></i>
          </span>
          <el-dropdown-menu slot="dropdown" class="layout-menu">
            <el-dropdown-item
              :class="{ 'is-selected': layoutMode === 'single' }"
              @click.native="switchLayout('single')"
            >
              <i class="el-icon-full-screen"></i>
              单列布局
              <i v-if="layoutMode === 'single'" class="el-icon-check layout-check"></i>
            </el-dropdown-item>
            <el-dropdown-item
              :class="{ 'is-selected': layoutMode === 'double' }"
              @click.native="switchLayout('double')"
            >
              <i class="el-icon-c-scale-to-original"></i>
              双列布局
              <i v-if="layoutMode === 'double'" class="el-icon-check layout-check"></i>
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
        <!--      changeShowInfos方法传入需要调用的函数名  -->
        <el-tooltip
          v-for="section in dicomInfoSections"
          :key="section.key"
          placement="bottom"
          :open-delay="350"
          popper-class="dicom-nav-tooltip"
        >
          <div slot="content" class="dicom-tooltip-inner">
            <div class="tt-title">{{ section.label }}</div>
            <div class="tt-summary">{{ section.summary }}</div>
            <div v-for="field in section.fields" :key="field.tag" class="tt-field">
              <div class="tt-field-head">
                <span class="tt-name">{{ field.name }}</span>
                <span class="tt-tag">{{ field.tag }}</span>
              </div>
              <div class="tt-meaning">{{ field.meaning }}</div>
            </div>
          </div>
          <div
            class="right-menu-item hover-effect info-menu-item"
            @click="changeShowInfos(section.key)"
          >{{ section.label }}</div>
        </el-tooltip>
        <!--end-->

        <!--TODO 全屏工具 可以研究研究-->
        <!--        <screenfull id="screenfull" class="right-menu-item hover-effect"/>-->
        <!--主题设置-->
        <!--        <div class="right-menu-item hover-effect" @click.stop="setting = true">-->
        <!--          <SvgIcon iconClass="xy_renovation"/>-->
        <!--        </div>-->

        <!--        <el-tooltip content="布局大小" effect="dark" placement="bottom">-->
        <!--          <size-select id="size-select" class="right-menu-item hover-effect"/>-->
        <!--        </el-tooltip>-->
      </template>

      <el-dropdown class="avatar-container right-menu-item hover-effect">
        <div class="avatar-wrapper">
          <img :src="avatar" class="user-avatar">
        </div>
        <el-dropdown-menu slot="dropdown">
          <el-dropdown-item @click.native="jumpBaseSystem('1')">个人中心</el-dropdown-item>
          <el-dropdown-item @click.native="jumpBaseSystem('2')">企业中心</el-dropdown-item>
          <!--          <el-dropdown-item @click.native="setting = true">-->
          <!--            <span>布局设置</span>-->
          <!--          </el-dropdown-item>-->
          <el-dropdown-item divided @click.native="logout">
            <span>退出登录</span>
          </el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>

    </div>
    <dicom-structure-dialog :visible.sync="showDicomDialog" />
    <lesion-series-dialog
      v-if="isCtViewerRoute"
      :visible.sync="lesionSeriesDialogVisible"
      :study-series-list="studySeriesList"
      :lesion-results-by-dicom-id="lesionResultsByDicomId"
      @detect="onLesionDetectSeries"
    />
  </div>
</template>

<script>
import {mapGetters, mapActions} from 'vuex'
import Breadcrumb from '@basicsComponents/Breadcrumb'
import TopNav from '@basicsComponents/TopNav'
import Hamburger from '@basicsComponents/Hamburger'
import SvgIcon from '@basicsComponents/SvgIcon'
import Screenfull from '@basicsComponents/Screenfull'
import SizeSelect from '@basicsComponents/SizeSelect'
import Search from '@basicsComponents/HeaderSearch'
import Notice from '@customComponents/Notice'
import DicomStructureDialog from './DicomStructureDialog'
import LesionSeriesDialog from '@/views/ct2/components/LesionSeriesDialog'
import LesionEngineSelect from '@/views/ct2/components/LesionEngineSelect'
import { engineSupportsMode } from '@/utils/lesionEngines'
import { DICOM_INFO_SECTIONS } from '@/constants/dicomStructure'

export default {
  //jm start 顶部菜单
  data() {
    return {
      activeIndex: '1',
      activeIndex2: '1',
      showDicomDialog: false,
      dicomInfoSections: DICOM_INFO_SECTIONS
    };
  },
  //end
  components: {
    Breadcrumb,
    TopNav,
    Hamburger,
    SvgIcon,
    Screenfull,
    SizeSelect,
    Search,
    Notice,
    DicomStructureDialog,
    LesionSeriesDialog,
    LesionEngineSelect
  },
  computed: {
    ...mapGetters([
      'sidebar',
      'avatar',
      'device',
      'openStudy',
      'studySeriesList',
      'lesionResultsByDicomId',
      'lesionDetectEngine',
      'lesionEngineCatalog'
    ]),
    isStudyPanelOpen() {
      return this.openStudy
    },
    layoutMode() {
      return this.$route.name === 'ct2row' ? 'double' : 'single'
    },
    isCtViewerRoute() {
      return this.$route.name === 'ct2' || this.$route.name === 'ct2row'
    },
    lesionDetectLoading() {
      return this.$store.getters.lesionDetectLoading
    },
    canDetectCurrentSlice() {
      const engine = this.lesionDetectEngine || 'scheme-a'
      return engineSupportsMode(engine, 'single', this.lesionEngineCatalog)
    },
    canDetectSeries() {
      const engine = this.lesionDetectEngine || 'scheme-a'
      return engineSupportsMode(engine, 'series', this.lesionEngineCatalog)
    },
    singleSliceTooltip() {
      if (!this.canDetectCurrentSlice) {
        return '当前算法仅支持全序列识别（如融合精准分析）'
      }
      return '对当前显示的 DICOM 层进行 AI 识别并标记'
    },
    seriesDetectTooltip() {
      if (!this.canDetectSeries) {
        return '当前算法仅支持当前层识别（如单层异常倾向）'
      }
      return '选择序列进行 AI 病灶识别（全序列）'
    },
    lesionSeriesDialogVisible: {
      get() {
        return this.$store.getters.lesionSeriesDialogVisible
      },
      set(val) {
        this.$store.commit('SET_LESION_SERIES_DIALOG', val)
      }
    },
    setting: {
      get() {
        return this.$store.state.settings.showSettings
      },
      set(val) {
        this.$store.dispatch('settings/changeSetting', {
          key: 'showSettings',
          value: val
        })
      }
    },
    topNav: {
      get() {
        return this.$store.state.settings.topNav
      }
    }
  },
  methods: {
    //jm start 顶部菜单
    switchLayout(mode) {
      const target = mode === 'double' ? 'ct2row' : 'ct2'
      if (this.$route.name === target) {
        return
      }
      this.$router.push({ name: target })
    },

    handleSelect(key, keyPath) {
      console.log(key, keyPath);
    },
    //end
    toggleSideBar() {
      this.$store.dispatch('app/toggleSideBar')
    },
    async logout() {
      this.$modal.confirm('确定注销并退出系统吗？', '提示').then(() => {
        this.$store.dispatch('LogOut').then(() => {
          location.href = this.$router.options.base + 'login'
        })
      }).catch(() => {
      })
    },
    jumpBaseSystem(type) {
      let url
      if (type === '1') {//跳转个人中心
        url = this.$store.state.settings.baseSystemUrl + '/user/profile'
      } else if (type === '2') {//跳转主系统企业中心
        url = this.$store.state.settings.baseSystemUrl
      }
      // window.open(url, '_blank') // 在新窗口打开外链接
      window.location.href = url  //在本页面打开外部链接
    },
    //病人信息展示状态改变
    ...mapActions({
      changeShowInfo: 'changeShowInfo'
    }),
    changeShowInfos(value) {
      console.log(value)
      this.changeShowInfo(value)
    },
    toggleStudyPanel() {
      this.$store.dispatch('openStudy')
    },
    routeReturn(){
        this.$router.push({name: 'patients'})
    },
    triggerLesionDetect() {
      if (this.lesionDetectLoading || !this.canDetectSeries) {
        if (!this.canDetectSeries) {
          this.$message.warning(this.seriesDetectTooltip)
        }
        return
      }
      this.$store.dispatch('requestLesionDetect')
    },
    triggerLesionDetectCurrentSlice() {
      if (this.lesionDetectLoading || !this.canDetectCurrentSlice) {
        if (!this.canDetectCurrentSlice) {
          this.$message.warning(this.singleSliceTooltip)
        }
        return
      }
      this.$store.dispatch('requestLesionDetectCurrentSlice')
    },
    onLesionDetectSeries(row) {
      this.$store.dispatch('startLesionDetectForSeries', row)
    }
  }
}
</script>

<style lang="scss" scoped>
.navbar {
  height: 50px;
  overflow: hidden;
  position: relative;
  background: #282c34;
  box-shadow: 0 1px 4px rgba(0, 233, 233, .08);

  .toolbar-left {
    float: left;
    display: flex;
    align-items: center;
    height: 100%;
    gap: 2px;
    padding-left: 4px;
  }

  .toolbar-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    margin: 0;
    padding: 0;
    border: none;
    border-radius: 6px;
    background: transparent;
    color: #b8bcc6;
    font-size: 18px;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
    -webkit-tap-highlight-color: transparent;

    &:hover {
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
    }

    &.is-active {
      background: rgba(91, 156, 245, 0.18);
      color: #7eb8ff;
    }
  }

  .hamburger-container {
    line-height: 36px;
    height: 36px;
    width: 36px;
    cursor: pointer;
    transition: background .3s;
    -webkit-tap-highlight-color: transparent;

    &:hover {
      background: rgba(255, 255, 255, 0.08);
    }
  }

  .breadcrumb-container {
    float: left;
  }

  .topmenu-container {
    position: absolute;
    left: 50px;
  }

  .errLog-container {
    display: inline-block;
    vertical-align: top;
  }

  .right-menu {
    float: right;
    height: 100%;
    line-height: 50px;

    &:focus {
      outline: none;
    }

    .right-menu-item {
      display: inline-block;
      padding: 0 8px;
      height: 100%;
      font-size: 14px;
      color: #ddd;
      vertical-align: text-bottom;

      &.info-menu-item {
        font-size: 13px;
      }

      &.dicom-guide-btn {
        font-size: 13px;
        color: #7eb8ff;

        i {
          margin-right: 3px;
        }

        &:hover {
          color: #a8d0ff;
        }
      }

      &.ai-lesion-btn {
        font-size: 13px;
        color: #f0a96e;

        i {
          margin-right: 3px;
        }

        &:hover {
          color: #ffc89a;
        }

        &.is-loading {
          opacity: 0.75;
          pointer-events: none;
        }

        &.is-disabled {
          opacity: 0.45;
          cursor: not-allowed;
          color: #8b93a7;

          &:hover {
            color: #8b93a7;
          }
        }
      }

      &.ai-engine-menu {
        padding: 0 10px;
        cursor: default;

        &:hover {
          background: transparent !important;
        }

        ::v-deep .lesion-engine-select__label {
          color: #b8bcc6;
        }

        ::v-deep .el-input__inner {
          background: rgba(255, 255, 255, 0.06);
          border-color: rgba(255, 255, 255, 0.12);
          color: #e8eaed;
          height: 28px;
          line-height: 28px;
        }

        ::v-deep .el-input__suffix {
          color: #b8bcc6;
        }
      }

      &.hover-effect {
        cursor: pointer;
        transition: background .3s;

        &:hover {
          background: rgba(0, 0, 0, .025)
        }
      }
    }

    .avatar-container {
      margin-right: 10px;

      .avatar-wrapper {
        margin-top: 5px;
        position: relative;

        .user-avatar {
          cursor: pointer;
          width: 40px;
          height: 40px;
          border-radius: 10px;
        }

        .el-icon-caret-bottom {
          cursor: pointer;
          position: absolute;
          right: -20px;
          top: 25px;
          font-size: 12px;
        }
      }
    }

  }

  .layout-trigger {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    cursor: pointer;
    color: #c5cad3;
    font-size: 13px;

    i.el-icon-s-grid {
      color: #5b9cf5;
    }
  }

  .el-dropdown-link {
    cursor: pointer;
    color: #409EFF;
  }

  .el-icon-arrow-down {
    font-size: 12px;
  }
}

::v-deep .layout-menu {
  .el-dropdown-menu__item {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 140px;
    font-size: 13px;

    i:first-child {
      color: #8b93a7;
    }

    &.is-selected {
      color: #409eff;
      background: rgba(64, 158, 255, 0.08);

      i:first-child {
        color: #409eff;
      }
    }
  }

  .layout-check {
    margin-left: auto;
    color: #67c23a;
    font-weight: bold;
  }
}

.dicom-nav-tooltip {
  max-width: 420px !important;
  padding: 0 !important;
  background: #23272f !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45) !important;

  .popper__arrow::after {
    border-bottom-color: #23272f !important;
  }
}

.dicom-tooltip-inner {
  padding: 10px 12px 8px;
  max-height: 360px;
  overflow-y: auto;

  .tt-title {
    font-size: 14px;
    font-weight: 600;
    color: #e3a5a5;
    margin-bottom: 4px;
  }

  .tt-summary {
    font-size: 12px;
    color: #8b93a7;
    margin-bottom: 8px;
    line-height: 1.4;
  }

  .tt-field {
    padding: 5px 0;
    border-top: 1px solid rgba(255, 255, 255, 0.05);

    &:first-of-type {
      border-top: none;
    }
  }

  .tt-field-head {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 2px;
  }

  .tt-name {
    font-size: 12px;
    color: #7eb8ff;
    font-weight: 500;
  }

  .tt-tag {
    font-size: 10px;
    color: #6b7280;
    font-family: monospace;
  }

  .tt-meaning {
    font-size: 11px;
    color: #c5cad3;
    line-height: 1.45;
  }
}
</style>
