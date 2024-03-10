import * as cornerstoneTools from '@cornerstoneTools'


const BaseAnnotationTool = cornerstoneTools.import('base/BaseAnnotationTool');

// const renderToolData = cornerstoneTools.import('bidirectionalTool/renderToolData')
// const addNewMeasurement = cornerstoneTools.import('bidirectionalTool/addNewMeasurement')
import renderToolData from './BidirectionalUtils/renderToolData'
import addNewMeasurement from './BidirectionalUtils/addNewMeasurement'

const createNewMeasurement = cornerstoneTools.import('bidirectionalTool/createNewMeasurement')
const calculateLongestAndShortestDiameters = cornerstoneTools.import('calculateLongestAndShortestDiameters')
const pointNearTool = cornerstoneTools.import('bidirectionalTool/pointNearTool')
const _moveCallback = cornerstoneTools.import('bidirectionalTool/mouseMoveCallback')
const handleSelectedCallback = cornerstoneTools.import('bidirectionalTool/handleSelectedCallback')
const handleSelectedMouseCallback = cornerstoneTools.import('bidirectionalTool/handleSelectedMouseCallback')
const handleSelectedTouchCallback = cornerstoneTools.import('bidirectionalTool/handleSelectedTouchCallback')

//cursors
const bidirectionalCursor = cornerstoneTools.import('tools/cursors')
// Util,下面的没有
const getPixelSpacing = cornerstoneTools.importInternal('util/getPixelSpacing')
const throttle = cornerstoneTools.importInternal('util/throttle')


//引入vuex
import myStore from './../../store'

const makerNeed = myStore.getters.makerNeed


const emptyLocationCallback = (measurementData, eventData, doneCallback) =>
  doneCallback();

/**
 * @public
 * @class BidirectionalTool
 * @memberof Tools.Annotation
 * @classdesc Create and position an annotation that measures the
 * length and width of a region.
 * @extends Tools.Base.BaseAnnotationTool
 */

export default class BidirectionalToolOfMe extends BaseAnnotationTool {
  constructor(props) {
    const defaultProps = {
      name: 'BidirectionalOfMe',
      supportedInteractionTypes: ['Mouse', 'Touch'],
      configuration: {
        changeMeasurementLocationCallback: emptyLocationCallback,
        getMeasurementLocationCallback: emptyLocationCallback,
        textBox: '',
        shadow: '',
        drawHandles: true,
        drawHandlesOnHover: true,
        hideHandlesIfMoving: false,
        renderDashed: false,
        additionalData: [],
      },
      svgCursor: bidirectionalCursor,
    };

    super(props, defaultProps);
    // console.log("props",props)
    // console.log("defaultProps",defaultProps)
    this.throttledUpdateCachedStats = throttle(this.updateCachedStats, 110);

    this.createNewMeasurement = createNewMeasurement.bind(this);
    this.pointNearTool = pointNearTool.bind(this);

    this.renderToolData = renderToolData.bind(this);
    this.addNewMeasurement = addNewMeasurement.bind(this);

    this._moveCallback = _moveCallback.bind(this);

    this.handleSelectedCallback = handleSelectedCallback.bind(this);
    this.handleSelectedMouseCallback = handleSelectedMouseCallback.bind(this);
    this.handleSelectedTouchCallback = handleSelectedTouchCallback.bind(this);
  }

  updateCachedStats(image, element, data) {
    // console.log("-----------updateCachedStats-------------------",image, element, data)
    // Prevent updating other tools' data
    if (data.toolName !== this.name) {
      return;
    }

    const pixelSpacing = getPixelSpacing(image);
    //自己改进，当标记的是png图像时，修改像素间距，
    // 原因是，标记png时，这里获取不到数据，colPixelSpacing默认为1，所以需要修改
    if (makerNeed.isDicomOfMe === "0") {
      pixelSpacing.rowPixelSpacing = makerNeed.rowPixelSpacingOfMe
      pixelSpacing.colPixelSpacing = makerNeed.columnPixelSpacingOfMe
    }
    //end
    const {
      longestDiameter,
      shortestDiameter,
    } = calculateLongestAndShortestDiameters(data, pixelSpacing);


    // Set measurement text to show lesion table
    data.longestDiameter = longestDiameter;
    data.shortestDiameter = shortestDiameter;
    data.invalidated = false;
  }
}
