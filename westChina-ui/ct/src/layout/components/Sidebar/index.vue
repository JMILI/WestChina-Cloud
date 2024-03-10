<template xmlns="">
  <div :class="{'has-logo':showLogo}">
    :style="{ backgroundColor: settings.sideTheme === 'theme-dark' ? variables.menuBackground :
    variables.menuLightBackground }">
    <!--    logo-->
    <logo v-if="showLogo" :collapse="isCollapse"/>
    <!--    标题-->
    <el-scrollbar :class="settings.sideTheme" wrap-class="scrollbar-wrapper">


      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :background-color="settings.sideTheme === 'theme-dark' ? variables.menuBackground : variables.menuLightBackground"
        :text-color="settings.sideTheme === 'theme-dark' ? variables.menuColor : variables.menuLightColor"
        :unique-opened="true"
        :active-text-color="settings.sideTheme === 'theme-dark' ? variables.menuTextColorActive : variables.menuLightColorActive"
        :collapse-transition="true"
        mode="vertical"
      >
        <el-submenu index="1">
          <template slot="title"><i class="el-icon-edit"></i>标注</template>
          <el-menu-item
            v-for="item of labelTools" :key="item.index"
            @click="resetTools2(item.toolName)"
          >
            <i class="el-icon-menu"></i>
            <span slot="title">{{ item.name }}</span>
          </el-menu-item>
        </el-submenu>
        <el-submenu index="2">
          <template slot="title"><i class="el-icon-message"></i>平移翻转旋转</template>
          <el-menu-item
            v-for="item of spinTools" :key="item.index"
            @click="resetTools2(item.toolName)"
          >
            <i class="el-icon-menu"></i>
            <span slot="title">{{ item.name }}</span>
          </el-menu-item>
          <el-menu-item @click="changeViewPorts('SET_HFLIP')">
            <i class="el-icon-menu"></i>
            <span slot="title">水平翻转</span>
          </el-menu-item>
          <el-menu-item @click="changeViewPorts('SET_VFLIP')">
            <i class="el-icon-menu"></i>
            <span slot="title">垂直翻转</span>
          </el-menu-item>
          <el-menu-item @click="changeViewPorts('SET_INVERT')">
            <i class="el-icon-menu"></i>
            <span slot="title">像素反转</span>
          </el-menu-item>
        </el-submenu>
        <el-menu-item
          v-for="item of tools" :key="item.index"
          @click="resetTools2(item.toolName)"
        >
          <i class="el-icon-menu"></i>
          <span slot="title">{{ item.name }}</span>
        </el-menu-item>


      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script>
import {mapGetters, mapState, mapMutations, mapActions} from "vuex"
import Logo from "./Logo"
import SidebarItem from "./SidebarItem"
import variables from "@assets/styles/variables.scss"

import * as cornerstoneTools from '@cornerstoneTools'

import LengthToolOfMe from '../../../utils/cornerstoneToolsExternal/LengthToolOfMe.js'
import BidirectionalToolOfMe from '../../../utils/cornerstoneToolsExternal/BidirectionalToolOfMe.js'
import CircleRoiToolOfMe from '../../../utils/cornerstoneToolsExternal/CircleRoiToolOfMe.js'
import EllipticalRoiToolOfMe from '../../../utils/cornerstoneToolsExternal/EllipticalRoiToolOfMe.js'
import FreehandRoiToolOfMe from '../../../utils/cornerstoneToolsExternal/FreehandRoiToolOfMe.js'
import ProbeToolOfMe from '../../../utils/cornerstoneToolsExternal/ProbeToolOfMe.js'


export default {
  components: {SidebarItem, Logo},
  data() {
    return {

      isInit: false,
      labelTools: [
        {
          toolName: 'Angle',
          name: '角度测量',
        },
        {
          toolName: 'ArrowAnnotate',
          name: '箭头标记',
        },


        {
          toolName: 'BidirectionalOfMe',
          name: '十字测量',
        },
        {
          toolName: 'CircleRoiOfMe',
          name: '圆',
        },
        {
          toolName: 'EllipticalRoiOfMe',
          name: '椭圆',
        },
        {
          toolName: 'FreehandRoiOfMe',
          name: '自由绘制',
        },
        // 原始的
        // {
        //   toolName: 'Length',
        //   name: '长度测量',
        // },
        {
          toolName: 'LengthOfMe',
          name: '长度测量',
        },
        {
          toolName: 'ProbeOfMe',
          name: '探针标记',
        },
        {
          toolName: 'DragProbe',
          name: '探针',
        },
      ],
      spinTools:[
        {
          toolName: 'Pan',
          name: '平移图像',
        },
        {
          toolName: 'Rotate',
          name: '旋转',
        },
      ],
      tools: [
        // {
        //   toolName: 'Angle',
        //   name: '角度测量',
        // },
        // {
        //   toolName: 'CobbAngle',
        //   name: 'Cobb角度测量',
        // },
        // {
        //   toolName: 'ArrowAnnotate',
        //   name: '箭头标记',
        // },
        // {
        //   toolName: 'Bidirectional',
        //   name: '位置注释',
        // },
        // {
        //   toolName: 'CircleRoi',
        //   name: '圆',
        // },
        // {
        //   toolName: 'EllipticalRoi',
        //   name: '椭圆',
        // },
        // {
        //   toolName: 'FreehandRoi',
        //   name: '自由绘制',
        // },
        // {
        //   toolName: 'Length',
        //   name: '长度测量',
        // },
        // {
        //   toolName: 'Probe',
        //   name: '探针标记',
        // },
        // {
        //   toolName: 'RectangleRoi',
        //   name: '矩阵',
        // },
        // {
        //   toolName: 'TextMarker',
        //   name: '文本标记',
        // },
        // {
        //   toolName: 'DoubleTapFitToWindow',
        //   name: 'fit',
        // },
        // {
        //   toolName: 'DragProbe',
        //   name: '探针',
        // },
        {
          toolName: 'Eraser',
          name: '橡皮擦',
        },
        // {
        //   toolName: 'FreehandRoiSculptor',
        //   name: '修改',
        // },
        {
          toolName: 'Magnify',
          name: '放大镜',
        },
        {
          toolName: 'OrientationMarkers',
          name: '方向标记',
        },
        // {
        //   toolName: 'Overlay',
        //   name: '比例',
        // },
        // {
        //   toolName: 'Pan',
        //   name: '平移图像',
        // },
        // {
        //   toolName: 'ReferenceLines',
        //   name: '参考线',
        // },
        // {
        //   toolName: 'Rotate',
        //   name: '旋转',
        // },
        // {
        //   toolName: 'ScaleOverlay',
        //   name: 'ScaleOverlay',
        // },
        // {
        //   toolName: 'Brush',
        //   name: '分割图像',
        // },
        // {
        //   toolName: 'CircleScissors',
        //   name: '圆形剪刀',
        // },
        // {
        //   toolName: 'CorrectionScissors',
        //   name: '纠正剪刀',
        // },
        // {
        //   toolName: 'FreehandScissors',
        //   name: '自由剪刀',
        // },
        // {
        //   toolName: 'RectangleScissors',
        //   name: '矩阵剪刀',
        // },
        {
          toolName: 'Zoom',
          name: '局部放大Zoom',
        },
        {
          toolName: 'Wwwc',
          name: '窗位窗宽Wwwc',
        },

      ]
    }
  },
  computed: {
    ...mapState(["settings"]),
    //sidebarRouter中存放动态路由组件jm
    // ...mapGetters(["sidebarRouters", "sidebar"]),
    ...mapGetters(["sidebar"]),

    activeMenu() {
      const route = this.$route
      const {meta, path} = route
      // if set path, the sidebar will highlight the path you set
      if (meta.activeMenu) {
        return meta.activeMenu
      }
      return path
    },
    showLogo() {
      return this.$store.state.settings.sidebarLogo
    },
    variables() {
      return variables
    },
    isCollapse() {
      return !this.sidebar.opened
    },


  },
  mounted() {
  },
  methods: {
    //引入vuex方法
    ...mapActions(['changeViewPort']),
    changeViewPorts(name) {
      this.changeViewPort(name)
    },
    resetTools2(tool) {
      if (!this.isInit) {
        cornerstoneTools.init()
        const AngleTool = cornerstoneTools.AngleTool;
        const CobbAngleTool = cornerstoneTools.CobbAngleTool;
        const ArrowAnnotateTool = cornerstoneTools.ArrowAnnotateTool;
        const BidirectionalTool = cornerstoneTools.BidirectionalTool;
        const CircleRoiTool = cornerstoneTools.CircleRoiTool;
        const EllipticalRoiTool = cornerstoneTools.EllipticalRoiTool;
        const FreehandRoiTool = cornerstoneTools.FreehandRoiTool;
        const LengthTool = cornerstoneTools.LengthTool;

        const ProbeTool = cornerstoneTools.ProbeTool;

        const RectangleRoiTool = cornerstoneTools.RectangleRoiTool;
        const TextMarkerTool = cornerstoneTools.TextMarkerTool;
        const DoubleTapFitToWindowTool = cornerstoneTools.DoubleTapFitToWindowTool;
        const DragProbeTool = cornerstoneTools.DragProbeTool;
        const EraserTool = cornerstoneTools.EraserTool;
        const FreehandRoiSculptorTool = cornerstoneTools.FreehandRoiSculptorTool;
        const MagnifyTool = cornerstoneTools.MagnifyTool;
        const OrientationMarkersTool = cornerstoneTools.OrientationMarkersTool;
        const OverlayTool = cornerstoneTools.OverlayTool;
        const PanTool = cornerstoneTools.PanTool;
        const ReferenceLinesTool = cornerstoneTools.ReferenceLinesTool;
        const RotateTool = cornerstoneTools.RotateTool;
        const ScaleOverlayTool = cornerstoneTools.ScaleOverlayTool;
        const BrushTool = cornerstoneTools.BrushTool;
        const CircleScissorsTool = cornerstoneTools.CircleScissorsTool;
        const CorrectionScissorsTool = cornerstoneTools.CorrectionScissorsTool;
        const FreehandScissorsTool = cornerstoneTools.FreehandScissorsTool;
        const RectangleScissorsTool = cornerstoneTools.RectangleScissorsTool;
        const ZoomTool = cornerstoneTools.ZoomTool;
        const WwwcTool = cornerstoneTools.WwwcTool;


        const StackScrollMouseWheelTool = cornerstoneTools.StackScrollMouseWheelTool;

        cornerstoneTools.addTool(AngleTool);
        cornerstoneTools.addTool(CobbAngleTool);
        cornerstoneTools.addTool(ArrowAnnotateTool);
        cornerstoneTools.addTool(BidirectionalTool);
        cornerstoneTools.addTool(CircleRoiTool);
        cornerstoneTools.addTool(EllipticalRoiTool);
        cornerstoneTools.addTool(FreehandRoiTool);
        cornerstoneTools.addTool(LengthTool);
        cornerstoneTools.addTool(ProbeTool);
        cornerstoneTools.addTool(RectangleRoiTool);
        cornerstoneTools.addTool(TextMarkerTool);
        cornerstoneTools.addTool(DoubleTapFitToWindowTool);
        cornerstoneTools.addTool(DragProbeTool);
        cornerstoneTools.addTool(EraserTool);
        cornerstoneTools.addTool(FreehandRoiSculptorTool);
        cornerstoneTools.addTool(MagnifyTool);
        cornerstoneTools.addTool(OrientationMarkersTool);
        cornerstoneTools.addTool(OverlayTool);
        cornerstoneTools.addTool(PanTool);
        cornerstoneTools.addTool(ReferenceLinesTool);
        cornerstoneTools.addTool(RotateTool);
        cornerstoneTools.addTool(ScaleOverlayTool);
        cornerstoneTools.addTool(BrushTool);
        cornerstoneTools.addTool(CircleScissorsTool);
        cornerstoneTools.addTool(CorrectionScissorsTool);
        cornerstoneTools.addTool(FreehandScissorsTool);
        cornerstoneTools.addTool(RectangleScissorsTool);
        cornerstoneTools.addTool(ZoomTool);
        cornerstoneTools.addTool(WwwcTool);
        //二次开发工具，长度工具
        cornerstoneTools.addTool(LengthToolOfMe);

        cornerstoneTools.addTool(BidirectionalToolOfMe);
        cornerstoneTools.addTool(CircleRoiToolOfMe);
        cornerstoneTools.addTool(EllipticalRoiToolOfMe);
        cornerstoneTools.addTool(FreehandRoiToolOfMe);
        cornerstoneTools.addTool(ProbeToolOfMe);

        cornerstoneTools.addTool(StackScrollMouseWheelTool);

        cornerstoneTools.setToolActive('ZoomTool', 1);
        cornerstoneTools.setToolActive('StackScrollMouseWheel', {});
      }
      //不必设置取消键,若设置取消则之前的那一层可能会被取消掉
      console.log("tools:", tool)
      cornerstoneTools.setToolActive(tool, {mouseButtonMask: 1})

    },

  }
}
</script>
