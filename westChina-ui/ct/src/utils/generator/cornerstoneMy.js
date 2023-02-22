import * as cornerstone from 'cornerstone-core'
import * as dicomParser from 'dicom-parser'

// 不建议 npm 安装 cornerstoneWADOImageLoader 如果你做了 会很头疼
// import * as cornerstoneWADOImageLoader from "../../../static/cornerstoneWADOImageLoader.js";
import * as cornerstoneWebImageLoader from 'cornerstone-web-image-loader'
import * as cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader'
// Cornerstone 工具外部依赖
import Hammer from 'hammerjs'
import * as cornerstoneMath from 'cornerstone-math'
import * as cornerstoneTools from 'cornerstone-tools'
// import {getModule} from "cornerstone-tools"
const BaseTool = cornerstoneTools.importInternal('base/BaseTool')
const cornerstoneStore = cornerstoneTools.importInternal('store')
// Specify external dependencies 指定外部依赖，什么意思？为什么指定
cornerstoneTools.external.cornerstone = cornerstone
cornerstoneTools.external.cornerstoneMath = cornerstoneMath
cornerstoneTools.external.Hammer = Hammer
//指定要注册加载程序的基石实例
cornerstoneWADOImageLoader.external.cornerstone = cornerstone
cornerstoneWADOImageLoader.external.dicomParser = dicomParser
cornerstoneWADOImageLoader.external.cornerstoneMath = cornerstoneMath
cornerstoneWebImageLoader.external.cornerstone = cornerstone
