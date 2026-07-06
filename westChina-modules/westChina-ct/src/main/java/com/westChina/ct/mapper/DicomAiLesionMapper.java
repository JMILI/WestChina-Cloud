package com.westChina.ct.mapper;

import java.util.List;
import com.westChina.common.datascope.annotation.DataScope;
import com.westChina.ct.domain.DicomAiLesion;

/**
 * AI识别病灶结果 数据层
 */
public interface DicomAiLesionMapper {

    @DataScope(eAlias = "e")
    List<DicomAiLesion> selectDicomAiLesionList(DicomAiLesion dicomAiLesion);

    @DataScope(eAlias = "e")
    DicomAiLesion selectDicomAiLesionById(DicomAiLesion dicomAiLesion);

    @DataScope(ueAlias = "empty")
    int insertDicomAiLesion(DicomAiLesion dicomAiLesion);

    @DataScope(ueAlias = "empty")
    int updateDicomAiLesion(DicomAiLesion dicomAiLesion);

    @DataScope(ueAlias = "empty")
    int deleteDicomAiLesionById(DicomAiLesion dicomAiLesion);

    @DataScope(ueAlias = "empty")
    int deleteDicomAiLesionByIds(DicomAiLesion dicomAiLesion);

    @DataScope(eAlias = "e")
    List<DicomAiLesion> getDicomAiLesionByPatCardId(DicomAiLesion dicomAiLesion);
}
