package com.westChina.ct.service.impl;

import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.baomidou.dynamic.datasource.annotation.DS;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.westChina.common.core.domain.R;
import com.westChina.common.core.utils.ServletUtils;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.security.service.TokenService;
import com.westChina.ct.domain.CtDicom;
import com.westChina.ct.domain.DicomAiLesion;
import com.westChina.ct.mapper.DicomAiLesionMapper;
import com.westChina.ct.service.ICtDicomService;
import com.westChina.ct.service.IDicomAiLesionService;
import com.westChina.system.api.feign.RemoteFileService;
import com.westChina.system.api.model.LoginUser;
import com.westChina.tenant.api.feign.RemoteTenantService;
import static com.westChina.common.core.constant.TenantConstants.ISOLATE;

@Service
@DS(ISOLATE)
public class DicomAiLesionServiceImpl implements IDicomAiLesionService {

    private static final Logger log = LoggerFactory.getLogger(DicomAiLesionServiceImpl.class);

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Autowired
    private DicomAiLesionMapper dicomAiLesionMapper;

    @Autowired
    private ICtDicomService dicomService;

    @Autowired
    private RemoteFileService remoteFileService;

    @Autowired
    private RemoteTenantService remoteTenantService;

    @Autowired
    private TokenService tokenService;

    @Override
    public List<DicomAiLesion> selectDicomAiLesionList(DicomAiLesion dicomAiLesion) {
        return dicomAiLesionMapper.selectDicomAiLesionList(dicomAiLesion);
    }

    @Override
    public DicomAiLesion selectDicomAiLesionById(DicomAiLesion dicomAiLesion) {
        return dicomAiLesionMapper.selectDicomAiLesionById(dicomAiLesion);
    }

    @Override
    public List<DicomAiLesion> getDicomAiLesionByPatCardId(String patCardId) {
        DicomAiLesion query = new DicomAiLesion();
        query.setPatCardId(patCardId);
        return dicomAiLesionMapper.getDicomAiLesionByPatCardId(query);
    }

    @Override
    public DicomAiLesion saveLesionResult(Map<String, Object> request) {
        Long sourceDicomId = parseLong(request.get("sourceDicomId"));
        if (sourceDicomId == null) {
            throw new IllegalArgumentException("缺少 sourceDicomId");
        }

        CtDicom dicom = dicomService.selectDicomByDicomId(new CtDicom(sourceDicomId));
        if (dicom == null) {
            throw new IllegalArgumentException("未找到原始 DICOM 序列：" + sourceDicomId);
        }

        String bucketName = resolveBucketName();
        if (StringUtils.isEmpty(bucketName)) {
            throw new IllegalStateException("无法获取租户 MinIO 存储桶");
        }

        int imageCount = parseInt(request.get("imageCount"),
            dicom.getDicomCtCount() == null ? 0 : dicom.getDicomCtCount().intValue());
        String detectMode = firstNonEmpty(stringVal(request.get("detectMode")), "series");
        boolean singleSlice = "single".equalsIgnoreCase(detectMode);
        Integer sourceSliceIndex = parseNullableInt(request.get("sourceSliceIndex"));
        if (sourceSliceIndex == null) {
            Integer sliceIndex0 = parseNullableInt(request.get("sliceIndex"));
            if (sliceIndex0 != null && sliceIndex0 >= 0) {
                sourceSliceIndex = sliceIndex0 + 1;
            }
        }
        String instanceUid = stringVal(request.get("instanceUid"));

        if (!singleSlice && imageCount <= 0) {
            throw new IllegalArgumentException("序列切片数量为 0");
        }
        if (singleSlice && (sourceSliceIndex == null || sourceSliceIndex <= 0)) {
            throw new IllegalArgumentException("单层识别缺少有效的 sourceSliceIndex");
        }

        String sourcePath = dicom.getDicomCtPath();
        if (StringUtils.isEmpty(sourcePath) || !sourcePath.contains("/")) {
            throw new IllegalArgumentException("原始序列路径无效");
        }

        String sourceFolder = sourcePath.substring(0, sourcePath.lastIndexOf('/'));
        String patCardId = firstNonEmpty(stringVal(request.get("patCardId")), dicom.getPatCardId());
        long folderToken = System.currentTimeMillis();
        String destFolder = "ai-lesion/" + patCardId + "/" + folderToken;
        int storedImageCount = singleSlice ? 1 : imageCount;
        String aiSeriesPath = destFolder + "/" + storedImageCount + ".dcm";
        Integer copySliceIndex = singleSlice ? sourceSliceIndex : null;

        log.info("[CT-AI] copy series for save, mode={}, sourceFolder={}, destFolder={}, count={}, slice={}",
            detectMode, sourceFolder, destFolder, storedImageCount, copySliceIndex);

        R<Integer> copyResult = remoteFileService.copyDicomSeriesOfMinio(
            bucketName, sourceFolder, destFolder, storedImageCount, copySliceIndex);
        if (copyResult == null || copyResult.getData() == null || copyResult.getData() <= 0) {
            String msg = copyResult != null ? copyResult.getMsg() : "文件服务无响应";
            throw new IllegalStateException("复制 DICOM 序列失败：" + msg
                + "（请执行 deploymentServer/runlocal.sh start all 或确保 westChina-file:9300 已启动）");
        }
        if (!singleSlice && copyResult.getData() < imageCount) {
            log.warn("[CT-AI] partial copy: expected={}, copied={}", imageCount, copyResult.getData());
            storedImageCount = copyResult.getData();
            aiSeriesPath = destFolder + "/" + storedImageCount + ".dcm";
        }

        LoginUser loginUser = tokenService.getLoginUser(ServletUtils.getRequest());
        String doctor = loginUser != null && loginUser.getSysUser() != null
            ? loginUser.getSysUser().getUserName() : "";
        String enterpriseName = loginUser != null ? loginUser.getEnterpriseName() : "";

        Object lesionsObj = request.get("lesions");
        String lesionsJson;
        try {
            lesionsJson = objectMapper.writeValueAsString(
                lesionsObj == null ? Collections.emptyList() : lesionsObj);
        } catch (JsonProcessingException ex) {
            throw new IllegalArgumentException("病灶结果 JSON 序列化失败", ex);
        }

        int lesionCount = parseInt(request.get("lesionCount"), 0);
        if (lesionCount <= 0 && lesionsObj instanceof List) {
            lesionCount = ((List<?>) lesionsObj).size();
        }

        DicomAiLesion record = new DicomAiLesion();
        record.setSourceDicomId(sourceDicomId);
        record.setStudyUid(firstNonEmpty(stringVal(request.get("studyUid")), dicom.getDicomCtStudyUid()));
        record.setSeriesUid(firstNonEmpty(stringVal(request.get("seriesUid")), dicom.getDicomCtSeriesUid()));
        record.setStudyDate(firstNonEmpty(stringVal(request.get("studyDate")), dicom.getDicomCtTime()));
        record.setPatCardId(patCardId);
        record.setPatientName(firstNonEmpty(stringVal(request.get("patientName")), ""));
        record.setBodyPart(firstNonEmpty(stringVal(request.get("bodyPart")), dicom.getDicomCtBody()));
        record.setDetectDoctor(doctor);
        record.setDetectEnterpriseName(enterpriseName);
        record.setDetectTime(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
        record.setAiSeriesPath(aiSeriesPath);
        record.setImageCount(storedImageCount);
        record.setLesionCount(lesionCount);
        record.setLesionsJson(lesionsJson);
        record.setEngine(stringVal(request.get("engine")));
        record.setDisclaimer(stringVal(request.get("disclaimer")));
        record.setDescription(stringVal(request.get("description")));
        record.setDetectMode(detectMode);
        record.setInstanceUid(instanceUid);
        if (sourceSliceIndex != null && sourceSliceIndex > 0) {
            record.setSourceSliceIndex(sourceSliceIndex - 1);
        }
        record.setSort(0);

        dicomAiLesionMapper.insertDicomAiLesion(record);
        record.setDicomAiLesionId(record.getSnowflakeId());
        log.info("[CT-AI] saved lesion result, id={}, path={}, lesions={}",
            record.getDicomAiLesionId(), aiSeriesPath, lesionCount);
        return record;
    }

    @Override
    public int updateDicomAiLesion(DicomAiLesion dicomAiLesion) {
        return dicomAiLesionMapper.updateDicomAiLesion(dicomAiLesion);
    }

    @Override
    public int deleteDicomAiLesionByIds(DicomAiLesion dicomAiLesion) {
        return dicomAiLesionMapper.deleteDicomAiLesionByIds(dicomAiLesion);
    }

    private String resolveBucketName() {
        LoginUser loginUser = tokenService.getLoginUser(ServletUtils.getRequest());
        if (loginUser == null || StringUtils.isEmpty(loginUser.getEnterpriseName())) {
            return null;
        }
        R<String> bucketResult = remoteTenantService.getBucketNameByEnterpriseName(loginUser.getEnterpriseName());
        return bucketResult != null ? bucketResult.getData() : null;
    }

    private static String stringVal(Object value) {
        return value == null ? null : String.valueOf(value);
    }

    private static String firstNonEmpty(String first, String second) {
        if (StringUtils.isNotEmpty(first)) {
            return first;
        }
        return second;
    }

    private static Long parseLong(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Number) {
            return ((Number) value).longValue();
        }
        try {
            return Long.parseLong(String.valueOf(value));
        } catch (NumberFormatException ex) {
            return null;
        }
    }

    private static int parseInt(Object value, int defaultValue) {
        if (value == null) {
            return defaultValue;
        }
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        try {
            return Integer.parseInt(String.valueOf(value));
        } catch (NumberFormatException ex) {
            return defaultValue;
        }
    }

    private static Integer parseNullableInt(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        try {
            return Integer.parseInt(String.valueOf(value));
        } catch (NumberFormatException ex) {
            return null;
        }
    }
}
