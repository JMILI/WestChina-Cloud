package com.westChina.tenant.controller;

import com.westChina.common.core.domain.R;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.core.utils.poi.ExcelUtil;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.common.log.annotation.Log;
import com.westChina.common.log.enums.BusinessType;
import com.westChina.common.security.annotation.RequiresPermissions;
import com.westChina.system.api.feign.RemoteFileService;
import com.westChina.tenant.domain.Bucket;
import com.westChina.tenant.service.IBucketService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletResponse;
import java.util.List;

/**
 * 对象存储，存储租户的桶信息 业务处理
 *
 * @author jm
 */
@RestController
@RequestMapping("/bucket")
public class BucketController extends BaseController {

    @Autowired
    private IBucketService bucketService;
    @Autowired
    private RemoteFileService remoteFileService;

    /**
     * 查询对象存储，存储租户的桶信息列表
     */
    @RequiresPermissions("tenant:bucket:list")
    @GetMapping("/list")
    public AjaxResult list(Bucket bucket) {
        startPage();
        List<Bucket> list = bucketService.selectBucketList(bucket);
        return getDataTable(list);
    }

    /**
     * 导出对象存储，存储租户的桶信息列表
     */
    @RequiresPermissions("tenant:bucket:export")
    @Log(title = "对象存储，存储租户的桶信息", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Bucket bucket) {
        List<Bucket> list = bucketService.selectBucketList(bucket);
        ExcelUtil<Bucket> util = new ExcelUtil<Bucket>(Bucket.class);
        util.exportExcel(response, list, "对象存储，存储租户的桶信息数据");
    }

    /**
     * 获取对象存储，存储租户的桶信息详细信息
     */
    @RequiresPermissions("tenant:bucket:query")
    @GetMapping(value = "/byId")
    public AjaxResult getInfo(Bucket bucket) {
        return AjaxResult.success(bucketService.selectBucketByBucketId(bucket));
    }

    /**
     * 根据enterpriseName企业账号查询企业的minio桶
     * @param enterpriseName 企业账号
     * @return
     */
    @GetMapping(value = "/getBucketNameByEnterpriseName")
    public AjaxResult getBucketNameByEnterpriseName(String enterpriseName) {
        Bucket bucket = bucketService.getBucketNameByEnterpriseName(enterpriseName);
        String msg = "";
        msg = "贵企业的对象存储不能用，请联系管理员";
        //有桶被停用了
        if (StringUtils.isNotNull(bucket) && 1 == Integer.parseInt(bucket.getStatus())) {
            return AjaxResult.error(msg);
        }
        //有桶
        else if (StringUtils.isNotNull(bucket) && 0 == Integer.parseInt(bucket.getStatus())) {
            return AjaxResult.success("成功", bucket.getBucketName());
        }
        //没有查询到该用户的桶信息
        else {
            msg = "该企业没有对象存储空间，不同上传文件";
            //这里默认返回的AjaxResult对象的data属性为null,msg这里设置了提示信息
            return AjaxResult.error(msg);
        }
    }

    /**
     * 新增对象存储，存储租户的桶信息
     */
    @RequiresPermissions("tenant:bucket:add")
    @Log(title = "对象存储，存储租户的桶信息", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Bucket bucket) {
        boolean flag = true;
        String msg = "";
        //1.查询该用户是否有minio的桶，如果有，则返回失败
        Bucket bucketTemp = bucketService.selectBucketByBucketTenantId(bucket);
        if (StringUtils.isNotNull(bucketTemp)) {
            //del_flag=0
            if (Integer.parseInt(bucketTemp.getStatus()) == 1) {
                flag = false;
                msg = "该用户有桶，只是被停用了";
            }
            // 该用户有桶，状态为0，使用中
            else {
                flag = false;
                msg = "该用户有桶，桶正在使用";
            }
        }
        //没有该用户的情况下
        else {
            //2.新增minio桶，返回为false,则名为bucketName的桶已经存在了
            //桶存在，新增成功了,应该是，“桶存在提示，桶已经存在了”
            R<Boolean> notExist = remoteFileService.makeMinioBucket(bucket.getBucketName());
            if (!notExist.getData()) {
                msg = "该名称的桶已经存在！";
                flag = false;
            }
        }
        //上述操作没问题
        if (flag) {
            //新增桶成功，数据库记录数据
            return AjaxResult.success(msg, bucketService.insertBucket(bucket));
        } else {
            return AjaxResult.error(msg);
        }

    }

    /**
     * 修改对象存储，存储租户的桶信息
     */
    @RequiresPermissions("tenant:bucket:edit")
    @Log(title = "对象存储，存储租户的桶信息", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Bucket bucket) {
        return toAjax(bucketService.updateBucket(bucket));
    }

    /**
     * 修改对象存储，存储租户的桶信息排序
     */
    @RequiresPermissions("tenant:bucket:edit")
    @Log(title = "对象存储，存储租户的桶信息", businessType = BusinessType.UPDATE)
    @PutMapping(value = "/sort")
    public AjaxResult updateSort(@RequestBody Bucket bucket) {
        return toAjax(bucketService.updateBucketSort(bucket));
    }

    /**
     * 删除对象存储，存储租户的桶信息
     */
    @RequiresPermissions("tenant:bucket:remove")
    @Log(title = "对象存储，存储租户的桶信息", businessType = BusinessType.DELETE)
    @DeleteMapping
    public AjaxResult remove(@RequestBody Bucket bucket) {
        return toAjax(bucketService.deleteBucketByBucketIds(bucket));
    }
}