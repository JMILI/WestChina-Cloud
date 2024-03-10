
// 删除病人标记过的dicom图像
import {delMaker} from "../../api/ct/maker";
import {delFile} from "../../api/ct/ctFileUpload";

export function delMakerAndImage(ids, imageAddresses) {
  // console.log(ids)
  console.log(imageAddresses)
  let delImage = new Promise((resolve, reject)=>{
    delFile(imageAddresses)
    resolve()
  })
  // //删除图像信息
  delImage.then(()=>{
    return delMaker(ids)
  }).catch((err)=>{
    console.log("删除失败！")
    return "删除失败！"
  })
}
