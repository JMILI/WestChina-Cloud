import * as cornerstoneTools from '@cornerstoneTools'
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

const getPixelSpacing = cornerstoneTools.import('util/getPixelSpacing')

const getModule = cornerstoneTools.getModule
import updatePerpendicularLineHandles from './updatePerpendicularLineHandles.js';
const numbersWithCommas = cornerstoneTools.import('util/numbersWithCommas')
//引入vuex
import myStore from './../../../store'

const makerNeed = myStore.getters.makerNeed


export default function (evt) {
  const eventData = evt.detail;
  const {element, canvasContext, image} = eventData;
  const {
    handleRadius,
    drawHandlesOnHover,
    hideHandlesIfMoving,
    renderDashed,
  } = this.configuration;

  const lineDash = getModule('globalConfiguration').configuration.lineDash;

  // If we have no toolData for this element, return immediately as there is nothing to do
  const toolData = getToolState(element, this.name);

  if (!toolData) {
    return;
  }

  let {rowPixelSpacing, colPixelSpacing} = getPixelSpacing(image);


  //自己改进，当标记的是png图像时，修改像素间距，
  // 原因是，标记png时，这里获取不到数据，colPixelSpacing默认为1，所以需要修改
  if (makerNeed.isDicomOfMe === "0") {
    rowPixelSpacing = makerNeed.rowPixelSpacingOfMe
    colPixelSpacing = makerNeed.columnPixelSpacingOfMe
  }
  //end

  // LT-29 Disable Target Measurements when pixel spacing is not available
  if (!rowPixelSpacing || !colPixelSpacing) {
    return;
  }

  // We have tool data for this element - iterate over each one and draw it
  const context = getNewContext(canvasContext.canvas);

  let color;
  const lineWidth = toolStyle.getToolWidth();

  for (let i = 0; i < toolData.data.length; i++) {
    const data = toolData.data[i];

    if (data.visible === false) {
      continue;
    }

    color = toolColors.getColorIfActive(data);

    // Calculate the data measurements
    if (data.invalidated === true) {
      if (data.longestDiameter && data.shortestDiameter) {
        this.throttledUpdateCachedStats(image, element, data);
      } else {
        this.updateCachedStats(image, element, data);
      }
    }

    draw(context, context => {
      // Configurable shadow
      setShadow(context, this.configuration);

      const {
        start,
        end,
        perpendicularStart,
        perpendicularEnd,
        textBox,
      } = data.handles;

      const lineOptions = {color};
      const perpendicularLineOptions = {color};

      if (renderDashed) {
        lineOptions.lineDash = lineDash;
        perpendicularLineOptions.lineDash = lineDash;
      }

      // Draw the measurement line
      drawLine(context, element, start, end, lineOptions);

      // Draw perpendicular line
      // const strokeWidth = lineWidth;

      updatePerpendicularLineHandles(eventData, data);

      drawLine(
        context,
        element,
        perpendicularStart,
        perpendicularEnd,
        perpendicularLineOptions
      );

      // Draw the handles
      const handleOptions = {
        color,
        handleRadius,
        drawHandlesIfActive: drawHandlesOnHover,
        hideHandlesIfMoving,
      };

      // Draw the handles
      if (this.configuration.drawHandles) {
        drawHandles(context, eventData, data.handles, handleOptions);
      }

      // Draw the textbox
      // Move the textbox slightly to the right and upwards
      // So that it sits beside the length tool handle
      const xOffset = 10;
      const textBoxAnchorPoints = handles => [
        handles.start,
        handles.end,
        handles.perpendicularStart,
        handles.perpendicularEnd,
      ];
      const textLines = getTextBoxText(data, rowPixelSpacing, colPixelSpacing);

      drawLinkedTextBox(
        context,
        element,
        textBox,
        textLines,
        data.handles,
        textBoxAnchorPoints,
        color,
        lineWidth,
        xOffset,
        true
      );
    });
  }
}

const getTextBoxText = (data, rowPixelSpacing, colPixelSpacing) => {
  let suffix = ' mm';

  if (!rowPixelSpacing || !colPixelSpacing) {
    suffix = ' pixels';
  }
  //自己改进，当标记的是png图像时，修改像素间距，
  // 原因是，标记png时，这里获取不到数据，colPixelSpacing默认为1，所以需要修改
  let tempLong=data.longestDiameter
  let tempShort=data.shortestDiameter
  if (makerNeed.isDicomOfMe === "0") {
    tempLong=tempLong/makerNeed.scaleOfMe
    tempShort=tempShort/makerNeed.scaleOfMe
  }
  //end
  const lengthText = ` Length: ${numbersWithCommas(tempLong)}${suffix}`;
  const widthText = ` Width: ${numbersWithCommas(tempShort)}${suffix}`;

  const {labels} = data;

  if (labels && Array.isArray(labels)) {
    return [...labels, lengthText, widthText];
  }

  return [lengthText, widthText];
};
