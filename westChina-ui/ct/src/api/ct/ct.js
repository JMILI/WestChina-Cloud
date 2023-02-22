import instance from './ctSwiftConfig'
 import ctRequest from "common/src/utils/ctRequest";
import axios1 from 'axios';


// 清空调度日志
export function getAuth() {
  console.log("getAuth")
  return ctRequest({
    url: '/auth/v1.0',
    method: 'get',
    headers: {
      'X-Storage-User': 'test:tester',
      'X-Storage-Pass': 'testing'
    }
  })
}
