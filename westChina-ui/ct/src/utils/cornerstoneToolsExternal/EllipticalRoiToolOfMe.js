import * as cornerstoneTools from '@cornerstoneTools'
const BaseAnnotationTool = cornerstoneTools.importInternal('base/BaseAnnotationTool');
const external = cornerstoneTools.external
// State
const getToolState = cornerstoneTools.getToolState
const toolStyle = cornerstoneTools.toolStyle
const toolColors = cornerstoneTools.toolColors
const getModule = cornerstoneTools.getModule
const getHandleNearImagePoint = cornerstoneTools.import('manipulators/getHandleNearImagePoint')
// Drawing
const getNewContext = cornerstoneTools.import('drawing/getNewContext')
const draw = cornerstoneTools.import('drawing/draw')
const setShadow = cornerstoneTools.import('drawing/setShadow')
const drawLinkedTextBox = cornerstoneTools.import('drawing/drawLinkedTextBox')
const drawHandles = cornerstoneTools.import('drawing/drawHandles')
const drawEllipse = cornerstoneTools.import('drawing/drawEllipse')
// Util
const getPixelSpacing = cornerstoneTools.import('util/getPixelSpacing')
const throttle = cornerstoneTools.import('util/throttle')
const calculateSUV = cornerstoneTools.import('util/calculateSUV')
const getROITextBoxCoords = cornerstoneTools.import('util/getROITextBoxCoords')
const numbersWithCommas = cornerstoneTools.import('util/numbersWithCommas')
// const getLogger = cornerstoneTools.enableLogger
const pointInEllipse = cornerstoneTools.import('pointInEllipse')
const calculateEllipseStatistics = cornerstoneTools.import('calculateEllipseStatistics')
const  ellipticalRoiCursor  = cornerstoneTools.import('tools/cursors')




// const logger = getLogger('tools:annotation:EllipticalRoiTool');


import myStore from './../../store'

//二次开发，需要的变量
const makerNeed = myStore.getters.makerNeed


/**
 * @public
 * @class EllipticalRoiTool
 * @memberof Tools.Annotation
 * @classdesc Tool for drawing elliptical regions of interest, and measuring
 * the statistics of the enclosed pixels.
 * @extends Tools.Base.BaseAnnotationTool
 */
export default class EllipticalRoiToolOfMe extends BaseAnnotationTool {
  constructor(props = {}) {
    const defaultProps = {
      name: 'EllipticalRoiOfMe',
      supportedInteractionTypes: ['Mouse', 'Touch'],
      configuration: {
        showMinMax: true,
        showHounsfieldUnits: true,
        drawHandles: true,
        drawHandlesOnHover: false,
        hideHandlesIfMoving: false,
        renderDashed: false,
      },
      svgCursor: ellipticalRoiCursor,
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

    const validParameters = hasStartAndEndHandles;

    if (!validParameters) {
      logger.warn(
        `invalid parameters supplied to tool ${this.name}'s pointNearTool`
      );
    }

    if (!validParameters || data.visible === false) {
      return false;
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

    const distance = interactionType === 'mouse' ? 15 : 25;
    const startCanvas = external.cornerstone.pixelToCanvas(
      element,
      data.handles.start
    );
    const endCanvas = external.cornerstone.pixelToCanvas(
      element,
      data.handles.end
    );

    const minorEllipse = {
      left: Math.min(startCanvas.x, endCanvas.x) + distance / 2,
      top: Math.min(startCanvas.y, endCanvas.y) + distance / 2,
      width: Math.abs(startCanvas.x - endCanvas.x) - distance,
      height: Math.abs(startCanvas.y - endCanvas.y) - distance,
    };

    const majorEllipse = {
      left: Math.min(startCanvas.x, endCanvas.x) - distance / 2,
      top: Math.min(startCanvas.y, endCanvas.y) - distance / 2,
      width: Math.abs(startCanvas.x - endCanvas.x) + distance,
      height: Math.abs(startCanvas.y - endCanvas.y) + distance,
    };

    const pointInMinorEllipse = pointInEllipse(minorEllipse, coords);
    const pointInMajorEllipse = pointInEllipse(majorEllipse, coords);

    if (pointInMajorEllipse && !pointInMinorEllipse) {
      return true;
    }

    return false;
  }

  updateCachedStats(image, element, data) {
    const seriesModule =
      external.cornerstone.metaData.get('generalSeriesModule', image.imageId) ||
      {};
    const modality = seriesModule.modality;
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

    const eventData = evt.detail;
    const { image, element } = eventData;
    const lineWidth = toolStyle.getToolWidth();
    const lineDash = getModule('globalConfiguration').configuration.lineDash;
    const {
      handleRadius,
      drawHandlesOnHover,
      hideHandlesIfMoving,
      renderDashed,
    } = this.configuration;
    const context = getNewContext(eventData.canvasContext.canvas);
    let { rowPixelSpacing, colPixelSpacing } = getPixelSpacing(image);
    //自己改进，当标记的是png图像时，修改像素间距，
    // 原因是，标记png时，这里获取不到数据，colPixelSpacing默认为1，所以需要修改
    if (makerNeed.isDicomOfMe === "0") {
      rowPixelSpacing = makerNeed.rowPixelSpacingOfMe
      colPixelSpacing = makerNeed.columnPixelSpacingOfMe
    }
    //end


    // Meta
    const seriesModule =
      external.cornerstone.metaData.get('generalSeriesModule', image.imageId) ||
      {};

    // Pixel Spacing
    const modality = seriesModule.modality;
    const hasPixelSpacing = rowPixelSpacing && colPixelSpacing;

    draw(context, context => {
      // If we have tool data for this element - iterate over each set and draw it
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

        const ellipseOptions = { color };

        if (renderDashed) {
          ellipseOptions.lineDash = lineDash;
        }

        // Draw
        drawEllipse(
          context,
          element,
          data.handles.start,
          data.handles.end,
          ellipseOptions,
          'pixel',
          data.handles.initialRotation
        );
        drawHandles(context, eventData, data.handles, handleOptions);

        // Update textbox stats
        if (data.invalidated === true) {
          if (data.cachedStats) {
            this.throttledUpdateCachedStats(image, element, data);
          } else {
            this.updateCachedStats(image, element, data);
          }
        }

        // Default to textbox on right side of ROI
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
          this.configuration
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
  const { left, top, width, height } = _getEllipseImageCoordinates(
    startHandle,
    endHandle
  );

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
  const otherLines = [];

  if (!isColorImage) {
    const hasStandardUptakeValues = meanStdDevSUV && meanStdDevSUV.mean !== 0;
    const unit = _getUnit(modality, options.showHounsfieldUnits);

    let meanString = `Mean: ${numbersWithCommas(mean.toFixed(2))} ${unit}`;
    const stdDevString = `Std Dev: ${numbersWithCommas(
      stdDev.toFixed(2)
    )} ${unit}`;

    // If this image has SUV values to display, concatenate them to the text line
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
      otherLines.push(`${meanString}`);
      otherLines.push(`${stdDevString}`);
    }

    if (showMinMax) {
      let minString = `Min: ${min} ${unit}`;
      const maxString = `Max: ${max} ${unit}`;
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
  otherLines.forEach(x => textLines.push(x));

  return textLines;
}

/**
 *
 *
 * @param {*} area
 * @param {*} hasPixelSpacing
 * @returns {string} The formatted label for showing area
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
  const ellipseCoordinates = _getEllipseImageCoordinates(
    handles.start,
    handles.end
  );

  // Retrieve the array of pixels that the ellipse bounds cover
  const pixels = external.cornerstone.getPixels(
    element,
    ellipseCoordinates.left,
    ellipseCoordinates.top,
    ellipseCoordinates.width,
    ellipseCoordinates.height
  );

  // Calculate the mean & standard deviation from the pixels and the ellipse details.
  const ellipseMeanStdDev = calculateEllipseStatistics(
    pixels,
    ellipseCoordinates
  );

  let meanStdDevSUV;

  if (modality === 'PT') {
    meanStdDevSUV = {
      mean: calculateSUV(image, ellipseMeanStdDev.mean, true) || 0,
      stdDev: calculateSUV(image, ellipseMeanStdDev.stdDev, true) || 0,
    };
  }

  // Calculate the image area from the ellipse dimensions and pixel spacing
  const area =
    Math.PI *
    ((ellipseCoordinates.width * (pixelSpacing.colPixelSpacing || 1)) / 2) *
    ((ellipseCoordinates.height * (pixelSpacing.rowPixelSpacing || 1)) / 2);

  return {
    area: area || 0,
    count: ellipseMeanStdDev.count || 0,
    mean: ellipseMeanStdDev.mean || 0,
    variance: ellipseMeanStdDev.variance || 0,
    stdDev: ellipseMeanStdDev.stdDev || 0,
    min: ellipseMeanStdDev.min || 0,
    max: ellipseMeanStdDev.max || 0,
    meanStdDevSUV,
  };
}

/**
 * Retrieve the bounds of the ellipse in image coordinates
 *
 * @param {*} startHandle
 * @param {*} endHandle
 * @returns {{ left: number, top: number, width: number, height: number }}
 */
function _getEllipseImageCoordinates(startHandle, endHandle) {
  return {
    left: Math.round(Math.min(startHandle.x, endHandle.x)),
    top: Math.round(Math.min(startHandle.y, endHandle.y)),
    width: Math.round(Math.abs(startHandle.x - endHandle.x)),
    height: Math.round(Math.abs(startHandle.y - endHandle.y)),
  };
}
