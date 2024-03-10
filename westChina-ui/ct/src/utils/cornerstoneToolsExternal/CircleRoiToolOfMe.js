//region import
import * as cornerstoneTools from '@cornerstoneTools'

const BaseAnnotationTool = cornerstoneTools.importInternal('base/BaseAnnotationTool');
const external = cornerstoneTools.external
// State
const getToolState = cornerstoneTools.getToolState
const toolStyle = cornerstoneTools.toolStyle
const toolColors = cornerstoneTools.toolColors
const getModule = cornerstoneTools.getModule
// Drawing
const getHandleNearImagePoint = cornerstoneTools.import('manipulators/getHandleNearImagePoint')

const getNewContext = cornerstoneTools.import('drawing/getNewContext')
const draw = cornerstoneTools.import('drawing/draw')
const setShadow = cornerstoneTools.import('drawing/setShadow')
const drawLinkedTextBox = cornerstoneTools.import('drawing/drawLinkedTextBox')
const drawHandles = cornerstoneTools.import('drawing/drawHandles')
const drawCircle = cornerstoneTools.import('drawing/drawCircle')
// Util
const getCircleCoords = cornerstoneTools.import('util/getCircleCoords')
const calculateEllipseStatistics = cornerstoneTools.import('calculateEllipseStatistics')
//cursors
const circleRoiCursor = cornerstoneTools.import('tools/cursors')
const getROITextBoxCoords = cornerstoneTools.import('util/getROITextBoxCoords')
const calculateSUV = cornerstoneTools.import('util/calculateSUV')
const throttle = cornerstoneTools.import('util/throttle')
const getPixelSpacing = cornerstoneTools.import('util/getPixelSpacing')
const numbersWithCommas = cornerstoneTools.import('util/numbersWithCommas')
//endregion

//二次开发，需要的变量
//引入vuex
import myStore from './../../store'

const makerNeed = myStore.getters.makerNeed

// const getLogger = cornerstoneTools.enableLogger
// const logger = getLogger('tools:annotation:CircleRoiTool');

/**
 * @public
 * @class CircleRoiTool
 * @memberof Tools.Annotation
 * @classdesc Tool for drawing circular regions of interest, and measuring
 * the statistics of the enclosed pixels.
 * @extends Tools.Base.BaseAnnotationTool
 */
export default class CircleRoiToolOfMe extends BaseAnnotationTool {
  constructor(props = {}) {
    const defaultProps = {
      name: 'CircleRoiOfMe',
      supportedInteractionTypes: ['Mouse', 'Touch'],
      svgCursor: circleRoiCursor,
      configuration: {
        showMinMax: true,
        showHounsfieldUnits: true,
        centerPointRadius: 0,
        renderDashed: false,
        // drawHandles: false,
        hideHandlesIfMoving:true,
        drawHandlesOnHover: true,
      },
    };

    super(props, defaultProps);

    this.throttledUpdateCachedStats = throttle(this.updateCachedStats, 110);
  }

  createNewMeasurement(eventData) {
    const goodEventData =
      eventData && eventData.currentPoints && eventData.currentPoints.image;

    if (!goodEventData) {
      logger.error(
        `required eventData not supplied to tool ${this.name}'s createNewMeasurement`
      );

      return;
    }

    return {
      visible: true,
      active: true,
      color: undefined,
      invalidated: true,
      handles: {
        start: {
          x: eventData.currentPoints.image.x,
          y: eventData.currentPoints.image.y,
          highlight: true,
          active: false,
        },
        end: {
          x: eventData.currentPoints.image.x,
          y: eventData.currentPoints.image.y,
          highlight: true,
          active: true,
        },
        initialRotation: eventData.viewport.rotation,
        textBox: {
          active: false,
          hasMoved: false,
          movesIndependently: false,
          drawnIndependently: true,
          allowedOutsideImage: true,
          hasBoundingBox: true,
        },
      },
    };
  }

  pointNearTool(element, data, coords, interactionType) {
    const hasStartAndEndHandles =
      data && data.handles && data.handles.start && data.handles.end;

    const getDistance = external.cornerstoneMath.point.distance;

    if (!hasStartAndEndHandles) {
      logger.warn(
        `invalid parameters supplied to tool ${this.name}'s pointNearTool`
      );
    }
    const handleNearImagePoint = getHandleNearImagePoint(
      element,
      data.handles,
      coords,
      6
    );

    if (handleNearImagePoint) {
      return true;
    }
    if (!hasStartAndEndHandles || data.visible === false) {
      return false;
    }

    const distance = interactionType === 'mouse' ? 15 : 25;

    const startCanvas = external.cornerstone.pixelToCanvas(
      element,
      data.handles.start
    );

    const endCanvas = external.cornerstone.pixelToCanvas(
      element,
      data.handles.end
    );

    // StartCanvas is the center of the circle
    // StartCanvas是圆心
    const distanceFromCenter = getDistance(startCanvas, coords);

    // Getting radius of circle annotation in canvas
    // 在画布中获取圆注释的半径
    const radius = getDistance(startCanvas, endCanvas);

    // Checking if point is near the tool by comparing its distance from the center of the circle
    // 通过比较点到圆心的距离来检查点是否在工具附近
    return (
      distanceFromCenter > radius - distance / 2 &&
      distanceFromCenter < radius + distance / 2
    );
  }

  updateCachedStats(image, element, data) {
    // console.log("-----------updateCachedStats-------------------",image, element, data)
    const seriesModule =
      external.cornerstone.metaData.get('generalSeriesModule', image.imageId) ||
      {};
    const modality = seriesModule.modality;
    // console.log("------------------modality----------------------------",modality)
    let pixelSpacing = getPixelSpacing(image);

    // debugger
    //自己改进，当标记的是png图像时，修改像素间距，
    // 原因是，标记png时，这里获取不到数据，colPixelSpacing默认为1，所以需要修改
    if (makerNeed.isDicomOfMe === "0") {
      pixelSpacing.rowPixelSpacing = makerNeed.rowPixelSpacingOfMe
      pixelSpacing.colPixelSpacing = makerNeed.columnPixelSpacingOfMe
    }
    //end

    const stats = _calculateStats(
      image,
      element,
      data.handles,
      modality,
      pixelSpacing
    );

    data.cachedStats = stats;
    data.invalidated = false;
  }

  renderToolData(evt) {
    const toolData = getToolState(evt.currentTarget, this.name);

    if (!toolData) {
      return;
    }

    const getDistance = external.cornerstoneMath.point.distance;

    const eventData = evt.detail;
    const {image, element, canvasContext} = eventData;
    const lineWidth = toolStyle.getToolWidth();
    const {
      handleRadius,
      drawHandlesOnHover,
      hideHandlesIfMoving,
      renderDashed,
      centerPointRadius,
    } = this.configuration;
    const newContext = getNewContext(canvasContext.canvas);
    let {rowPixelSpacing, colPixelSpacing} = getPixelSpacing(image);

    //自己改进，当标记的是png图像时，修改像素间距，
    // 原因是，标记png时，这里获取不到数据，colPixelSpacing默认为1，所以需要修改
    if (makerNeed.isDicomOfMe === "0") {
      rowPixelSpacing = makerNeed.rowPixelSpacingOfMe
      colPixelSpacing = makerNeed.columnPixelSpacingOfMe
    }
    //end

    const lineDash = getModule('globalConfiguration').configuration.lineDash;

    // Meta
    const seriesModule =
      external.cornerstone.metaData.get('generalSeriesModule', image.imageId) ||
      {};

    // Pixel Spacing
    const modality = seriesModule.modality;
    const hasPixelSpacing = rowPixelSpacing && colPixelSpacing;

    draw(newContext, context => {
      // If we have tool data for this element, iterate over each set and draw it
      //如果我们有这个元素的工具数据，遍历每个集合并绘制它
      for (let i = 0; i < toolData.data.length; i++) {
        const data = toolData.data[i];

        if (data.visible === false) {
          continue;
        }

        // Configure
        const color = toolColors.getColorIfActive(data);
        const handleOptions = {
          color,
          handleRadius,
          drawHandlesIfActive: drawHandlesOnHover,
          hideHandlesIfMoving,
        };

        setShadow(context, this.configuration);

        const startCanvas = external.cornerstone.pixelToCanvas(
          element,
          data.handles.start
        );

        const endCanvas = external.cornerstone.pixelToCanvas(
          element,
          data.handles.end
        );

        // Calculating the radius where startCanvas is the center of the circle to be drawn
        // 计算startCanvas作为要绘制的圆心的半径
        const radius = getDistance(startCanvas, endCanvas);

        const circleOptions = {color};

        if (renderDashed) {
          circleOptions.lineDash = lineDash;
        }

        // Draw Circle
        drawCircle(
          context,
          element,
          data.handles.start,
          radius,
          circleOptions,
          'pixel',
          data.handles.initialRotation
        );


        if (centerPointRadius && radius > 3 * centerPointRadius) {
          drawCircle(
            context,
            element,
            data.handles.start,
            centerPointRadius,
            circleOptions,
            'pixel',
            data.handles.initialRotation
          );
        }

        // if (data.handles) {
        //   data.handles.start.drawnIndependently = false;
        //   data.handles.end.drawnIndependently = false;
        // }



        drawHandles(context, eventData, data.handles, handleOptions);

        // Update textbox stats
        // 更新文本框统计信息
        if (data.invalidated === true) {
          if (data.cachedStats) {
            this.throttledUpdateCachedStats(image, element, data);
          } else {
            this.updateCachedStats(image, element, data);
          }
        }

        // Default to textbox on right side of ROI
        //默认为ROI右侧的文本框
        if (!data.handles.textBox.hasMoved) {
          const defaultCoords = getROITextBoxCoords(
            eventData.viewport,
            data.handles
          );

          Object.assign(data.handles.textBox, defaultCoords);
        }

        const textBoxAnchorPoints = handles =>
          _findTextBoxAnchorPoints(handles.start, handles.end);

        const textBoxContent = _createTextBoxContent(
          context,
          image.color,
          data.cachedStats,
          modality,
          hasPixelSpacing,
          this.configuration,
        );

        data.unit = _getUnit(modality, this.configuration.showHounsfieldUnits);

        drawLinkedTextBox(
          context,
          element,
          data.handles.textBox,
          textBoxContent,
          data.handles,
          textBoxAnchorPoints,
          color,
          lineWidth,
          10,
          true
        );
      }
    });
  }
}


/**
 *
 *
 * @param {*} startHandle
 * @param {*} endHandle
 * @returns {Array.<{x: number, y: number}>}
 */
function _findTextBoxAnchorPoints(startHandle, endHandle) {
  const {left, top, width, height} = getCircleCoords(startHandle, endHandle);

  return [
    {
      // Top middle point of ellipse
      x: left + width / 2,
      y: top,
    },
    {
      // Left middle point of ellipse
      x: left,
      y: top + height / 2,
    },
    {
      // Bottom middle point of ellipse
      x: left + width / 2,
      y: top + height,
    },
    {
      // Right middle point of ellipse
      x: left + width,
      y: top + height / 2,
    },
  ];
}

function _getUnit(modality, showHounsfieldUnits) {
  return modality === 'CT' && showHounsfieldUnits !== false ? 'HU' : '';
}

/**
 *
 *
 * @param {*} context
 * @param {*} isColorImage
 * @param {*} { area, mean, stdDev, min, max, meanStdDevSUV }
 * @param {*} modality
 * @param {*} hasPixelSpacing
 * @param {*} [options={}] - { showMinMax, showHounsfieldUnits }
 * @returns {string[]}
 */
function _createTextBoxContent(
  context,
  isColorImage,
  {
    area = 0,
    radius = 0,
    perimeter = 0,
    mean = 0,
    stdDev = 0,
    min = 0,
    max = 0,
    meanStdDevSUV = 0,
  } = {},
  modality,
  hasPixelSpacing,
  options = {}
) {
  const showMinMax = options.showMinMax || false;
  const textLines = [];

  // Don't display mean/standardDev for color images
  //不要为彩色图像显示mean/standardDev
  const otherLines = [];

  if (!isColorImage) {
    const hasStandardUptakeValues = meanStdDevSUV && meanStdDevSUV.mean !== 0;
    const unit = _getUnit(modality, options.showHounsfieldUnits);
    //这两个属性都有
    let meanString = `Mean: ${numbersWithCommas(mean.toFixed(2))} ${unit}`;
    const stdDevString = `Std Dev: ${numbersWithCommas(
      stdDev.toFixed(2)
    )} ${unit}`;

    // If this image has SUV values to display, concatenate them to the text line
    //如果此图像有SUV值要显示，则将它们连接到文本行
    if (hasStandardUptakeValues) {
      const SUVtext = ' SUV: ';

      const meanSuvString = `${SUVtext}${numbersWithCommas(
        meanStdDevSUV.mean.toFixed(2)
      )}`;
      const stdDevSuvString = `${SUVtext}${numbersWithCommas(
        meanStdDevSUV.stdDev.toFixed(2)
      )}`;

      const targetStringLength = Math.floor(
        context.measureText(`${stdDevString}     `).width
      );

      while (context.measureText(meanString).width < targetStringLength) {
        meanString += ' ';
      }

      otherLines.push(`${meanString}${meanSuvString}`);
      otherLines.push(`${stdDevString}     ${stdDevSuvString}`);
    } else {
      otherLines.push(`${meanString}     ${stdDevString}`);
    }


    //是否展示最大值和最小值
    if (showMinMax) {
      let minString = `Min: ${min} ${unit}`;
      let maxString = `Max: ${max} ${unit}`;
      const targetStringLength = hasStandardUptakeValues
        ? Math.floor(context.measureText(`${stdDevString}     `).width)
        : Math.floor(context.measureText(`${meanString}     `).width);

      while (context.measureText(minString).width < targetStringLength) {
        minString += ' ';
      }

      otherLines.push(`${minString}${maxString}`);
    }
  }

  textLines.push(_formatArea(area, hasPixelSpacing));
  if (radius) {
    textLines.push(_formatLength(radius, 'Radius', hasPixelSpacing));
  }
  if (perimeter) {
    textLines.push(_formatLength(perimeter, 'Perimeter', hasPixelSpacing));
  }
  otherLines.forEach(x => textLines.push(x));

  return textLines;
}

/**
 *
 *
 * @param {*} area
 * @param {*} hasPixelSpacing
 * @returns {string} The formatted label for showing area 用于显示区域的格式化标签
 */
function _formatArea(area, hasPixelSpacing) {
  // This uses Char code 178 for a superscript 2
  const suffix = hasPixelSpacing
    ? ` mm${String.fromCharCode(178)}`
    : ` px${String.fromCharCode(178)}`;

  //自己改进，当标记的是png图像时，修改像素间距，
  // 原因是，标记png时，这里获取不到数据，colPixelSpacing默认为1，所以需要修改
  let temp = area
  if (makerNeed.isDicomOfMe === "0") {
    temp = (temp / makerNeed.scaleOfMe) / makerNeed.scaleOfMe
  }
  //end

  return `Area: ${numbersWithCommas(temp.toFixed(2))}${suffix}`;
}

function _formatLength(value, name, hasPixelSpacing) {
  if (!value) {
    return '';
  }
  const suffix = hasPixelSpacing ? ' mm' : ' px';

  //自己改进，当标记的是png图像时，修改像素间距，
  // 原因是，标记png时，这里获取不到数据，colPixelSpacing默认为1，所以需要修改
  let temp = value
  if (makerNeed.isDicomOfMe === "0") {
    temp = temp  / makerNeed.scaleOfMe
  }
  //end

  return `${name}: ${numbersWithCommas(temp.toFixed(2))}${suffix}`;
}

/**
 *
 *
 * @param {*} image
 * @param {*} element
 * @param {*} handles
 * @param {*} modality
 * @param {*} pixelSpacing
 * @returns {Object} The Stats object
 */
function _calculateStats(image, element, handles, modality, pixelSpacing) {
  // Retrieve the bounds of the ellipse in image coordinates
  //在图像坐标中检索椭圆的边界
  const circleCoordinates = getCircleCoords(handles.start, handles.end);

  // Retrieve the array of pixels that the ellipse bounds cover
  //检索椭圆边界所覆盖的像素数组
  const pixels = external.cornerstone.getPixels(
    element,
    circleCoordinates.left,
    circleCoordinates.top,
    circleCoordinates.width,
    circleCoordinates.height
  );

  // Calculate the mean & standard deviation from the pixels and the ellipse details.
  // 计算像素和椭圆细节的平均值和标准偏差。
  const ellipseMeanStdDev = calculateEllipseStatistics(
    pixels,
    circleCoordinates
  );

  let meanStdDevSUV;

  if (modality === 'PT') {
    meanStdDevSUV = {
      mean: calculateSUV(image, ellipseMeanStdDev.mean, true) || 0,
      stdDev: calculateSUV(image, ellipseMeanStdDev.stdDev, true) || 0,
    };
  }

  const radius =
    (circleCoordinates.width *
      ((pixelSpacing && pixelSpacing.colPixelSpacing) || 1)) /
    2;
  const perimeter = 2 * Math.PI * radius;

  const area =
    Math.PI *
    ((circleCoordinates.width * (pixelSpacing.colPixelSpacing || 1)) / 2) *
    ((circleCoordinates.height * (pixelSpacing.rowPixelSpacing || 1)) / 2);

  return {
    area: area || 0,
    radius: radius || 0,
    perimeter: perimeter || 0,
    count: ellipseMeanStdDev.count || 0,
    mean: ellipseMeanStdDev.mean || 0,
    variance: ellipseMeanStdDev.variance || 0,
    stdDev: ellipseMeanStdDev.stdDev || 0,
    min: ellipseMeanStdDev.min || 0,
    max: ellipseMeanStdDev.max || 0,
    meanStdDevSUV,
  };
}
