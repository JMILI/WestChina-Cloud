import * as cornerstoneTools from '@cornerstoneTools'

const external = cornerstoneTools.external
const EVENTS = cornerstoneTools.EVENTS
// State
const addToolState = cornerstoneTools.addToolState
const removeToolState = cornerstoneTools.removeToolState
const triggerEvent = cornerstoneTools.import('util/triggerEvent')
const  moveNewHandle = cornerstoneTools.import('manipulators/moveNewHandle')

const  anyHandlesOutsideImage = cornerstoneTools.import('manipulators/anyHandlesOutsideImage')
const  getActiveTool = cornerstoneTools.import('util/getActiveTool')

import BidirectionalTool from '../BidirectionalToolOfMe';
import updatePerpendicularLineHandles from './updatePerpendicularLineHandles.js';



//引入vuex
import myStore from './../../../store'

const makerNeed = myStore.getters.makerNeed



export default function(evt, interactionType) {
  const eventData = evt.detail;
  console.log("eve",evt.detail)
  const { element, image, buttons } = eventData;

  const config = this.configuration;

  if (checkPixelSpacing(image)) {
    return;
  }

  const measurementData = this.createNewMeasurement(eventData);

  const doneCallback = () => {
    measurementData.active = false;
    external.cornerstone.updateImage(element);
  };

  // Associate this data with this imageId so we can render it and manipulate it
  addToolState(element, this.name, measurementData);
  external.cornerstone.updateImage(element);

  const timestamp = new Date().getTime();
  const { end, perpendicularStart } = measurementData.handles;

  moveNewHandle(
    eventData,
    this.name,
    measurementData,
    end,
    {},
    interactionType,
    success => {
      if (!success) {
        removeToolState(element, this.name, measurementData);

        return;
      }
      const { handles, longestDiameter, shortestDiameter } = measurementData;
      const hasHandlesOutside = anyHandlesOutsideImage(eventData, handles);
      const longestDiameterSize = parseFloat(longestDiameter) || 0;
      const shortestDiameterSize = parseFloat(shortestDiameter) || 0;
      const isTooSmal = longestDiameterSize < 1 || shortestDiameterSize < 1;
      const isTooFast = new Date().getTime() - timestamp < 150;

      if (hasHandlesOutside || isTooSmal || isTooFast) {
        // Delete the measurement
        measurementData.cancelled = true;
        removeToolState(element, this.name, measurementData);
      } else {
        // Set lesionMeasurementData Session
        config.getMeasurementLocationCallback(
          measurementData,
          eventData,
          doneCallback
        );
      }

      // Update perpendicular line and disconnect it from the long-line
      updatePerpendicularLineHandles(eventData, measurementData);
      perpendicularStart.locked = false;

      measurementData.invalidated = true;

      external.cornerstone.updateImage(element);

      const activeTool = getActiveTool(element, buttons, interactionType);

      if (activeTool instanceof BidirectionalTool) {
        activeTool.updateCachedStats(image, element, measurementData);
      }

      const modifiedEventData = {
        toolName: this.name,
        toolType: this.name, // Deprecation notice: toolType will be replaced by toolName
        element,
        measurementData,
      };

      triggerEvent(element, EVENTS.MEASUREMENT_MODIFIED, modifiedEventData);
      triggerEvent(element, EVENTS.MEASUREMENT_COMPLETED, modifiedEventData);
    }
  );
}

const checkPixelSpacing = image => {
  const imagePlane = external.cornerstone.metaData.get(
    'imagePlaneModule',
    image.imageId
  );
  let rowPixelSpacing = image.rowPixelSpacing;
  let colPixelSpacing = image.columnPixelSpacing;

  //自己改进，当标记的是png图像时，修改像素间距，
  // 原因是，标记png时，这里获取不到数据，colPixelSpacing默认为1，所以需要修改
  if (makerNeed.isDicomOfMe === "0") {
    rowPixelSpacing = makerNeed.rowPixelSpacingOfMe
    colPixelSpacing = makerNeed.columnPixelSpacingOfMe
  }
  //end

  if (imagePlane) {
    rowPixelSpacing =
      imagePlane.rowPixelSpacing || imagePlane.rowImagePixelSpacing;
    colPixelSpacing =
      imagePlane.columnPixelSpacing || imagePlane.colImagePixelSpacing;
  }

  // LT-29 Disable Target Measurements when pixel spacing is not available
  return !rowPixelSpacing || !colPixelSpacing;
};
