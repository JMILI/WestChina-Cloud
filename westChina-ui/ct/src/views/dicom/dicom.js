
// 删除病人标记过的dicom图像
import {delDicom} from "../../api/ct/dicom";
import {delFolderFiles} from "../../api/ct/ctFileUpload";

export function delDicomAndImage(ids, dicomImageList) {
  console.log(dicomImageList)
  //删除minio中存储图像
  let delImage = new Promise((resolve, reject)=>{
    delFolderFiles(dicomImageList)
    resolve()
  })
  // //删除图像信息
  delImage.then(()=>{
    return delDicom(ids)
  }).catch((err)=>{
    console.log("删除失败！")
    return "删除失败！"
  })

}
