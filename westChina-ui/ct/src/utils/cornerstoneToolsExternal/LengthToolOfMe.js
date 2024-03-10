// import BaseAnnotationTool from '../base/BaseAnnotationTool.js';
import * as cornerstoneTools from '@cornerstoneTools'


const BaseAnnotationTool = cornerstoneTools.importInternal('base/BaseAnnotationTool');

// State
const getToolState = cornerstoneTools.getToolState
const toolStyle = cornerstoneTools.toolStyle
const toolColors = cornerstoneTools.toolColors

const getNewContext = cornerstoneTools.import('drawing/getNewContext')
const draw = cornerstoneTools.import('drawing/draw')
const setShadow = cornerstoneTools.import('drawing/setShadow')
const drawLine = cornerstoneTools.import('drawing/drawLine')
const drawLinkedTextBox = cornerstoneTools.import('drawing/drawLinkedTextBox')
const drawHandles = cornerstoneTools.import('drawing/drawHandles')

const lineSegDistance = cornerstoneTools.import('util/lineSegDistance')
const getPixelSpacing = cornerstoneTools.import('util/getPixelSpacing')
const throttle = cornerstoneTools.import('util/throttle')

const getLogger = cornerstoneTools.enableLogger


const lengthCursor = cornerstoneTools.import('tools/cursors')
const getModule = cornerstoneTools.getModule

//二次开发，需要的变量
import myStore from './../../store'
const makerNeed = myStore.getters.makerNeed


// const logger = getLogger('tools:annotation:LengthToolOfMe');

/**
 * @public
 * @class LengthTool
 * @memberof Tools.Annotation
 * @classdesc Tool for measuring distances.
 * @extends Tools.Base.BaseAnnotationTool
 */
export default class LengthToolOfMe extends BaseAnnotationTool {

  constructor(props = {}) {
    const defaultProps = {
      name: 'LengthOfMe',
      supportedInteractionTypes: ['Mouse', 'Touch'],
      svgCursor: lengthCursor,
      configuration: {
        drawHandles: true,
        drawHandlesOnHover: false,
        hideHandlesIfMoving: false,
        renderDashed: false,
        digits: 2,
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

    const {x, y} = eventData.currentPoints.image;

    return {
      visible: true,
      active: true,
      color: undefined,
      invalidated: true,
      handles: {
        start: {
          x,
          y,
          highlight: true,
          active: false,
        },
        end: {
          x,
          y,
          highlight: true,
          active: true,
        },
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

  /**
   *
   *
   * @param {*} element
   * @param {*} data
   * @param {*} coords
   * @returns {Boolean}
   */
  pointNearTool(element, data, coords) {
    const hasStartAndEndHandles =
      data && data.handles && data.handles.start && data.handles.end;
    const validParameters = hasStartAndEndHandles;

    if (!validParameters) {
      logger.warn(
        `invalid parameters supplied to tool ${this.name}'s pointNearTool`
      );

      return false;
    }

    if (data.visible === false) {
      return false;
    }

    return (
      lineSegDistance(element, data.handles.start, data.handles.end, coords) <
      25
    );
  }

  //计算长度
  updateCachedStats(image, element, data) {
    let {rowPixelSpacing, colPixelSpacing} = getPixelSpacing(image);
    //自己改进，当标记的是png图像时，修改像素间距，
    // 原因是，标记png时，这里获取不到数据，colPixelSpacing默认为1，所以需要修改
    if (makerNeed.isDicomOfMe === "0") {
      rowPixelSpacing = makerNeed.rowPixelSpacingOfMe
      colPixelSpacing = makerNeed.columnPixelSpacingOfMe
    }
    //end

    // Set rowPixelSpacing and columnPixelSpacing to 1 if they are undefined (or zero)
    // 如果rowPixelSpacing和columnPixelSpacing未定义(或为零)，则将它们设置为1
    const dx =
      (data.handles.end.x - data.handles.start.x) * (colPixelSpacing || 1);
    const dy =
      (data.handles.end.y - data.handles.start.y) * (rowPixelSpacing || 1);

    // Calculate the length, and create the text variable with the millimeters or pixels suffix
    //计算长度，并创建带有毫米或像素后缀的文本变量
    let length = Math.sqrt(dx * dx + dy * dy);

    // Store the length inside the tool for outside access 将长度存储在工具内部以供外部访问
    data.length = length;
    data.invalidated = false;
  }

  renderToolData(evt) {
    const eventData = evt.detail;
    const {
      handleRadius,
      drawHandlesOnHover,
      hideHandlesIfMoving,
      renderDashed,
      digits,
    } = this.configuration;
    const toolData = getToolState(evt.currentTarget, this.name);

    if (!toolData) {
      return;
    }

    // We have tool data for this element - iterate over each one and draw it
    const context = getNewContext(eventData.canvasContext.canvas);
    const {image, element} = eventData;

    let {rowPixelSpacing, colPixelSpacing} = getPixelSpacing(image);
    //自己改进，当标记的是png图像时，修改像素间距，
    // 原因是，标记png时，这里获取不到数据，colPixelSpacing默认为1，所以需要修改
    if (makerNeed.isDicomOfMe === "0") {
      rowPixelSpacing = makerNeed.rowPixelSpacingOfMe
      colPixelSpacing = makerNeed.columnPixelSpacingOfMe
    }
    //end
    const lineWidth = toolStyle.getToolWidth();
    const lineDash = getModule('globalConfiguration').configuration.lineDash;

    for (let i = 0; i < toolData.data.length; i++) {
      const data = toolData.data[i];

      if (data.visible === false) {
        continue;
      }

      draw(context, context => {
        // Configurable shadow
        setShadow(context, this.configuration);

        const color = toolColors.getColorIfActive(data);

        const lineOptions = {color};

        if (renderDashed) {
          lineOptions.lineDash = lineDash;
        }

        // Draw the measurement line
        drawLine(
          context,
          element,
          data.handles.start,
          data.handles.end,
          lineOptions
        );

        // Draw the handles
        const handleOptions = {
          color,
          handleRadius,
          drawHandlesIfActive: drawHandlesOnHover,
          hideHandlesIfMoving,
        };

        if (this.configuration.drawHandles) {
          drawHandles(context, eventData, data.handles, handleOptions);
        }

        if (!data.handles.textBox.hasMoved) {
          const coords = {
            x: Math.max(data.handles.start.x, data.handles.end.x),
          };

          // Depending on which handle has the largest x-value,
          // Set the y-value for the text box
          //取决于哪个句柄的x值最大
          //设置文本框的y值
          if (coords.x === data.handles.start.x) {
            coords.y = data.handles.start.y;
          } else {
            coords.y = data.handles.end.y;
          }

          data.handles.textBox.x = coords.x;
          data.handles.textBox.y = coords.y;
        }

        // Move the textbox slightly to the right and upwards
        // So that it sits beside the length tool handle
        const xOffset = 10;

        // Update textbox stats
        if (data.invalidated === true) {
          if (data.length) {
            this.throttledUpdateCachedStats(image, element, data);
          } else {
            this.updateCachedStats(image, element, data);
          }
        }
        const text = textBoxText(data, rowPixelSpacing, colPixelSpacing);

        drawLinkedTextBox(
          context,
          element,
          data.handles.textBox,
          text,
          data.handles,
          textBoxAnchorPoints,
          color,
          lineWidth,
          xOffset,
          true,
        );
      });
    }

    // - SideEffect: Updates annotation 'suffix'
    function textBoxText(annotation, rowPixelSpacing, colPixelSpacing) {
      const measuredValue = _sanitizeMeasuredValue(annotation.length);

      // Measured value is not defined, return empty string
      if (!measuredValue) {
        return '';
      }

      // Set the length text suffix depending on whether or not pixelSpacing is available
      let suffix = 'mm';

      if (!rowPixelSpacing || !colPixelSpacing) {
        suffix = 'pixels';
      }

      annotation.unit = suffix;
      //自己写
      let temp =measuredValue
      if(makerNeed.isDicomOfMe===false){
        temp = temp/makerNeed.scaleOfMe
      }
      //end
      return `${temp.toFixed(digits)}${suffix}`;
    }

    function textBoxAnchorPoints(handles) {
      const midpoint = {
        x: (handles.start.x + handles.end.x) / 2,
        y: (handles.start.y + handles.end.y) / 2,
      };

      return [handles.start, midpoint, handles.end];
    }
  }
}

/**
 * Attempts to sanitize a value by casting as a number; if unable to cast,
 * we return `undefined`
 *
 * @param {*} value
 * @returns a number or undefined
 */
function _sanitizeMeasuredValue(value) {
  const parsedValue = Number(value);
  const isNumber = !isNaN(parsedValue);

  return isNumber ? parsedValue : undefined;
}
