import axios1 from 'axios';
//
// axios.defaults.timeout = 50000;
// // 第一个代理基础路径配置
// axios.defaults.baseURL = '/api/xxxx/';
// axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8';


// 第二个代理基础路径配置
export const instance = axios1.create({
  baseURL:'http://tune01:8080',
});
instance.defaults.timeout = 50000;
instance.defaults.headers["Content-Type"] = "application/json;charset=utf-8"
// instance.defaults.baseURL='http://tune01:8080'
instance.interceptors.request.use(function(config){
  //在请求发出之前进行一些操作
  // return config;
  console.log(config)
},function(err){
  //Do something with request error
  return Promise.reject(error);
});



export default axios1;

