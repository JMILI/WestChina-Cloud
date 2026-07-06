package com.westChina.ct.service;

import java.util.List;
import java.util.Map;
import com.westChina.ct.domain.DicomAiLesion;

/**
 * AI识别病灶结果 业务层
 */
public interface IDicomAiLesionService {

    List<DicomAiLesion> selectDicomAiLesionList(DicomAiLesion dicomAiLesion);

    DicomAiLesion selectDicomAiLesionById(DicomAiLesion dicomAiLesion);

    List<DicomAiLesion> getDicomAiLesionByPatCardId(String patCardId);

    DicomAiLesion saveLesionResult(Map<String, Object> request);

    int updateDicomAiLesion(DicomAiLesion dicomAiLesion);

    int deleteDicomAiLesionByIds(DicomAiLesion dicomAiLesion);
}
