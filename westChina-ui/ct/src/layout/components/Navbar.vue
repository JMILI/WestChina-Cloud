<template>
  <div class="navbar">
    <hamburger id="hamburger-container" :is-active="!sidebar.opened" class="hamburger-container"
               @toggleClick="toggleSideBar"/>
    <el-button icon="el-icon-message"
               style="background-color:#282c34;border: 0px;margin-top: 7px;margin-bottom: 5px;padding-left: 5px;"
               @click="openStudySeries"
    ></el-button>
    <el-button icon="el-icon-success"
               style="background-color:#282c34;border: 0px;margin-top: 7px;margin-bottom: 5px;padding-left: 0px;"
               @click="routeReturn"
    ></el-button>
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
        <el-dropdown class="right-menu-item hover-effect">
          <span class="el-dropdown-link">
            布局<i class="el-icon-arrow-down el-icon--right"></i>
          </span>
          <el-dropdown-menu slot="dropdown">
<!--            <el-dropdown-item>-->
<!--              <router-link :to="{path:'ct2row'}"> 双列布局</router-link>-->
<!--            </el-dropdown-item>-->
             <el-dropdown-item @click.native="routerToCt2row">双列布局</el-dropdown-item>
<!--            &lt;!&ndash;            <el-dropdown-item divided>三列布局</el-dropdown-item>&ndash;&gt;-->
          </el-dropdown-menu>
        </el-dropdown>
        <!--      changeShowInfos方法传入需要调用的函数名  -->
        <div class="right-menu-item hover-effect" @click="changeShowInfos('SET_IS_SHOW_PATIENT_INFO')">病人信息</div>
        <div class="right-menu-item hover-effect" @click="changeShowInfos('SET_IS_SHOW_STUDY_INFO')">study信息</div>
        <div class="right-menu-item hover-effect" @click="changeShowInfos('SET_IS_SHOW_SERIES_INFO')">Series信息</div>
        <div class="right-menu-item hover-effect" @click="changeShowInfos('SET_IS_SHOW_INSTANCES_INFO')">instances信息
        </div>
        <div class="right-menu-item hover-effect" @click="changeShowInfos('SET_IS_SHOW_IMAGE_INFO')">图像信息</div>
        <div class="right-menu-item hover-effect" @click="changeShowInfos('SET_IS_SHOW_EQUIPMENT_INFO')">设备信息</div>
        <div class="right-menu-item hover-effect" @click="changeShowInfos('SET_IS_SHOW_UIDS_INFO')">UIDS信息</div>
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

export default {
  //jm start 顶部菜单
  data() {
    return {
      activeIndex: '1',
      activeIndex2: '1'
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
    Notice
  },
  computed: {
    ...mapGetters([
      'sidebar',
      'avatar',
      'device'
    ]),
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
    routerToCt2row(){
      this.$router.push({path: 'ct2row'})
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
          location.href = '/login'
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
    ...mapActions(['changeShowInfo', 'openStudy']),
    changeShowInfos(value) {
      console.log(value)
      this.changeShowInfo(value)
    },
    openStudySeries() {
      this.openStudy()
    },
    routeReturn(){
        this.$router.push({name: 'patients'})
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

  .hamburger-container {
    line-height: 46px;
    height: 100%;
    float: left;
    cursor: pointer;
    transition: background .3s;
    -webkit-tap-highlight-color: transparent;

    &:hover {
      background: rgba(45, 42, 42, 0.02)
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
      font-size: 18px;
      color: #ddd;
      vertical-align: text-bottom;

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

  .el-dropdown-link {
    cursor: pointer;
    color: #409EFF;
  }

  .el-icon-arrow-down {
    font-size: 12px;
  }
}
</style>
