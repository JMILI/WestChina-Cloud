package com.westChina.job.controller;

import com.westChina.common.core.constant.HttpConstants;
import com.westChina.common.core.constant.ScheduleConstants;
import com.westChina.common.core.exception.job.TaskException;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.core.utils.poi.ExcelUtil;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.common.log.annotation.Log;
import com.westChina.common.log.enums.BusinessType;
import com.westChina.common.security.annotation.RequiresPermissions;
import com.westChina.job.domain.SysJob;
import com.westChina.job.service.ISysJobService;
import com.westChina.job.util.CronUtils;
import com.westChina.job.util.ScheduleUtils;
import org.quartz.SchedulerException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;

/**
 * 调度任务信息操作处理
 *
 * @author westChina
 */
@RestController
@RequestMapping("/job")
public class SysJobController extends BaseController {

    @Autowired
    private ISysJobService jobService;

    /**
     * 查询定时任务列表
     */
    @RequiresPermissions("monitor:job:list")
    @GetMapping("/list")
    public AjaxResult list(SysJob sysJob) {
        startPage();
        List<SysJob> list = jobService.selectJobList(sysJob);
        return getDataTable(list);
    }

    /**
     * 导出定时任务列表
     */
    @RequiresPermissions("monitor:job:export")
    @Log(title = "定时任务", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, SysJob sysJob) throws IOException {
        List<SysJob> list = jobService.selectJobList(sysJob);
        ExcelUtil<SysJob> util = new ExcelUtil<SysJob>(SysJob.class);
        util.exportExcel(response, list, "定时任务");
    }

    /**
     * 获取定时任务详细信息
     */
    @RequiresPermissions("monitor:job:query")
    @GetMapping(value = "/{jobId}")
    public AjaxResult getInfo(@PathVariable("jobId") Long jobId) {
        return AjaxResult.success(jobService.selectJobById(jobId));
    }

    /**
     * 新增定时任务
     */
    @RequiresPermissions("monitor:job:add")
    @Log(title = "定时任务", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody SysJob job) throws SchedulerException, TaskException {
        if (!CronUtils.isValid(job.getCronExpression())) {
            return error("新增任务'" + job.getJobName() + "'失败，Cron表达式不正确");
        } else if (StringUtils.containsIgnoreCase(job.getInvokeTarget(), HttpConstants.Type.LOOKUP_RMI.getCode())) {
            return error("新增任务'" + job.getJobName() + "'失败，目标字符串不允许'rmi'调用");
        } else if (StringUtils.containsAnyIgnoreCase(job.getInvokeTarget(), new String[]{HttpConstants.Type.LOOKUP_LDAP.getCode(), HttpConstants.Type.LOOKUP_LDAPS.getCode()})) {
            return error("新增任务'" + job.getJobName() + "'失败，目标字符串不允许'ldap(s)'调用");
        } else if (StringUtils.containsAnyIgnoreCase(job.getInvokeTarget(), new String[]{HttpConstants.Type.HTTP.getCode(), HttpConstants.Type.HTTPS.getCode()})) {
            return error("新增任务'" + job.getJobName() + "'失败，目标字符串不允许'http(s)'调用");
        } else if (StringUtils.containsAnyIgnoreCase(job.getInvokeTarget(), ScheduleConstants.JOB_ERROR_STR)) {
            return error("新增任务'" + job.getJobName() + "'失败，目标字符串存在违规");
        } else if (!ScheduleUtils.whiteList(job.getInvokeTarget())) {
            return error("新增任务'" + job.getJobName() + "'失败，目标字符串不在白名单内");
        }
        return toAjax(jobService.insertJob(job));
    }

    /**
     * 修改定时任务
     */
    @RequiresPermissions("monitor:job:edit")
    @Log(title = "定时任务", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody SysJob job) throws SchedulerException, TaskException {
        if (!CronUtils.isValid(job.getCronExpression())) {
            return error("修改任务'" + job.getJobName() + "'失败，Cron表达式不正确");
        } else if (StringUtils.containsIgnoreCase(job.getInvokeTarget(), HttpConstants.Type.LOOKUP_RMI.getCode())) {
            return error("修改任务'" + job.getJobName() + "'失败，目标字符串不允许'rmi'调用");
        } else if (StringUtils.containsAnyIgnoreCase(job.getInvokeTarget(), new String[]{HttpConstants.Type.LOOKUP_LDAP.getCode(), HttpConstants.Type.LOOKUP_LDAPS.getCode()})) {
            return error("新增任务'" + job.getJobName() + "'失败，目标字符串不允许'ldap(s)'调用");
        } else if (StringUtils.containsAnyIgnoreCase(job.getInvokeTarget(), new String[]{HttpConstants.Type.HTTP.getCode(), HttpConstants.Type.HTTPS.getCode()})) {
            return error("修改任务'" + job.getJobName() + "'失败，目标字符串不允许'http(s)'调用");
        } else if (StringUtils.containsAnyIgnoreCase(job.getInvokeTarget(), ScheduleConstants.JOB_ERROR_STR)) {
            return error("修改任务'" + job.getJobName() + "'失败，目标字符串存在违规");
        } else if (!ScheduleUtils.whiteList(job.getInvokeTarget())) {
            return error("修改任务'" + job.getJobName() + "'失败，目标字符串不在白名单内");
        }
        return toAjax(jobService.updateJob(job));
    }

    /**
     * 定时任务状态修改
     */
    @RequiresPermissions("monitor:job:changeStatus")
    @Log(title = "定时任务", businessType = BusinessType.UPDATE)
    @PutMapping("/changeStatus")
    public AjaxResult changeStatus(@RequestBody SysJob job) throws SchedulerException {
        SysJob newJob = jobService.selectJobById(job.getJobId());
        newJob.setStatus(job.getStatus());
        return toAjax(jobService.changeStatus(newJob));
    }

    /**
     * 定时任务立即执行一次
     */
    @RequiresPermissions("monitor:job:changeStatus")
    @Log(title = "定时任务", businessType = BusinessType.UPDATE)
    @PutMapping("/run")
    public AjaxResult run(@RequestBody SysJob job) throws SchedulerException {
        jobService.run(job);
        return AjaxResult.success();
    }

    /**
     * 删除定时任务
     */
    @RequiresPermissions("monitor:job:remove")
    @Log(title = "定时任务", businessType = BusinessType.DELETE)
    @DeleteMapping("/{jobIds}")
    public AjaxResult remove(@PathVariable Long[] jobIds) throws SchedulerException, TaskException {
        jobService.deleteJobByIds(jobIds);
        return AjaxResult.success();
    }
}