/**
 * DICOM 信息模型说明
 * 主要依据：DICOM PS3.3 Chapter A (Composite IOD E-R Model)、
 *          PS3.4 C.3 Patient Root Q/R Model、PS3.4 C.6 Study Root Q/R Model
 * 临床场景参考：TCIA / 常见 CT 工作流（定位像、轴位、重建序列）
 */

/** 标准四层 + 关联信息实体 */
export const DICOM_HIERARCHY = [
  {
    id: 'patient',
    title: '病人 Patient',
    subtitle: 'Patient IE · 模态无关 · 人口统计学',
    color: '#5b9cf5',
    icon: '👤',
    rules: [
      '标识“接受检查的是谁”，与 CT/MR/US 等模态无关',
      '一个 Patient 可对应多次 Study（复诊、随访、不同日期检查）',
      '核心索引：Patient ID (0010,0020)，机构内唯一'
    ],
    uid: '通常无独立 Patient UID；以 Patient ID 在科室/院内关联',
    scenario: '李四，女，39岁，Patient ID=02291083 —— HIS 登记后进入 PACS 的病人主索引。'
  },
  {
    id: 'study',
    title: '检查 Study',
    subtitle: 'Study IE · 一次完整影像检查过程',
    color: '#67c23a',
    icon: '📋',
    rules: [
      '一次检查预约/登记产生的全部影像数据集合（逻辑上服务于同一次诊断）',
      '必须属于唯一 Patient；一个 Study 包含一个或多个 Series',
      '核心 UID：Study Instance UID (0020,000D)，全球唯一，PACS 归档主键',
      '与 RIS/HIS 对接时常用 Accession Number (0008,0050) 关联申请单'
    ],
    uid: 'Study Instance UID (0020,000D)',
    scenario: '2024-06-21 胸部 CT 平扫 —— 对应一张放射申请单、一次到检记录。'
  },
  {
    id: 'series',
    title: '序列 Series',
    subtitle: 'Series IE · 同条件采集或重建的一组实例',
    color: '#e6a23c',
    icon: '📚',
    rules: [
      '同一 Study 内，按采集协议、重建方式或扫描动作划分',
      '同一 Series 内：Modality 相同、通常由同一 Equipment 产生',
      '可关联 Frame of Reference，使各层图像处于同一空间坐标系（便于 MPR/3D）',
      '核心 UID：Series Instance UID (0020,000E)'
    ],
    uid: 'Series Instance UID (0020,000E)',
    scenario: 'CT 常见：定位像(Topogram)、轴位平扫(Axial)、冠状/矢状重建各为独立 Series。'
  },
  {
    id: 'instance',
    title: '实例 Instance',
    subtitle: 'SOP Instance · 单个 DICOM 文件对象',
    color: '#f56c6c',
    icon: '🖼',
    rules: [
      '最小存储与传输单元；每个 .dcm 文件对应一个 Instance',
      'CT/MR 中每一层断面通常是一个 Instance（Instance Number 递增）',
      '核心 UID：SOP Instance UID (0008,0018)；SOP Class UID 声明对象类型',
      '文件头中自带完整层级标签，故单文件可独立解析'
    ],
    uid: 'SOP Instance UID (0008,0018)',
    scenario: '胸部 CT 轴位序列第 37 层 —— 一张 512×512 的断层图像文件。'
  }
]

/** 与 Series 关联的其他信息实体（DICOM E-R 模型） */
export const DICOM_RELATED_IE = [
  {
    title: '设备 Equipment',
    color: '#b37feb',
    desc: '记录产生该 Series 的扫描仪/工作站。同一 Series 内设备信息一致。'
  },
  {
    title: '参考坐标 Frame of Reference',
    color: '#36cfc9',
    desc: '定义患者空间坐标系。同 UID 的 Series 可进行空间配准与三维重建。'
  },
  {
    title: '像素数据 Pixel Data',
    color: '#909399',
    desc: 'Instance 内的整数矩阵 + Rescale 参数；先换算成 HU，再经窗宽窗位映射为屏幕灰度。'
  }
]

/** 临床场景示例（用于结构图） */
export const DICOM_CLINICAL_SCENARIO = {
  title: '临床场景：胸部 CT 检查',
  patient: { name: '李四', id: '02291083', sex: 'F', age: '39Y' },
  study: { desc: '胸部 CT 平扫', date: '20240621', accession: 'ACC20240621001' },
  seriesList: [
    { num: 1, desc: 'Topogram 定位像', modality: 'CT', instances: 1 },
    { num: 2, desc: 'Axial 1.25mm 平扫', modality: 'CT', instances: 280 },
    { num: 3, desc: 'Coronal 冠状重建', modality: 'CT', instances: 120 }
  ]
}

export const DICOM_INFO_SECTIONS = [
  {
    key: 'SET_IS_SHOW_PATIENT_INFO',
    label: '病人信息',
    summary: 'Patient IE（DICOM PS3.3 A.1.2.1）：描述受检者身份与人口统计学属性，与成像模态无关。',
    fields: [
      { name: 'Patient ID', tag: '(0010,0020)', meaning: '机构内患者标识，RIS/HIS/PACS 对接的关键字段；非全球 UID。' },
      { name: 'Patient Name', tag: '(0010,0010)', meaning: '患者姓名，DICOM PN 类型，可含姓、名分量（如 ZHANG^SAN）。' },
      { name: 'Patient Birth Date', tag: '(0010,0030)', meaning: '出生日期，格式 YYYYMMDD。' },
      { name: 'Patient Sex', tag: '(0010,0040)', meaning: '性别：M 男、F 女、O 其他；影响剂量报告等场景。' },
      { name: 'Patient Age', tag: '(0010,1010)', meaning: '检查时的年龄字符串，如 039Y（39岁）、003M（3个月）。' },
      { name: 'SOP Instance UID', tag: '(0008,0018)', meaning: '【实例级】当前所阅 DICOM 文件的全局唯一标识；属 Instance 层级，本系统叠加在病人信息区便于查看。' }
    ]
  },
  {
    key: 'SET_IS_SHOW_STUDY_INFO',
    label: 'study信息',
    summary: 'Study IE（PS3.3 A.1.2.2）：一次医学检查过程；包含为诊断该患者而逻辑相关的一组 Series。',
    fields: [
      { name: 'Study Description', tag: '(0008,1030)', meaning: '检查描述，自由文本，如“Chest CT w/o contrast”。' },
      { name: 'Protocol Name', tag: '(0018,1030)', meaning: '采集协议名，反映扫描程序（常与设备预设方案对应）。' },
      { name: 'Accession Number', tag: '(0008,0050)', meaning: '申请/登记号，放射科工作流核心索引，关联 RIS 医嘱。' },
      { name: 'Study ID', tag: '(0020,0010)', meaning: '机构分配的检查编号，可与 Accession Number 不同。' },
      { name: 'Study Date', tag: '(0008,0020)', meaning: '检查日期 YYYYMMDD。' },
      { name: 'Study Time', tag: '(0008,0030)', meaning: '检查开始时间 HHMMSS.FFFFFF。' },
      { name: 'Study Instance UID', tag: '(0020,000D)', meaning: '检查级全球唯一 UID；同一检查下所有 Series/Instance 共享。' }
    ]
  },
  {
    key: 'SET_IS_SHOW_SERIES_INFO',
    label: 'Series信息',
    summary: 'Series IE（PS3.3 A.1.2.3）：将 Instance 分组；同组内 Modality 相同、设备一致、Series 标签相同。',
    fields: [
      { name: 'Series Description', tag: '(0008,103E)', meaning: '序列描述，如“1.25mm std”“Bone”“Lung”等。' },
      { name: 'Series Number', tag: '(0020,0011)', meaning: '检查内序列序号，用于排序显示。' },
      { name: 'Modality', tag: '(0008,0060)', meaning: '模态代码：CT、MR、US、CR、DX、PT、NM 等（DICOM 标准字典）。' },
      { name: 'Body Part Examined', tag: '(0018,0015)', meaning: '检查部位：CHEST、BRAIN、ABDOMEN、EXTREMITY 等。' },
      { name: 'Series Date', tag: '(0008,0021)', meaning: '该序列采集日期。' },
      { name: 'Series Time', tag: '(0008,0031)', meaning: '该序列采集时间。' },
      { name: 'Series Instance UID', tag: '(0020,000E)', meaning: '序列级全球唯一 UID；同序列所有 Instance 共享。' }
    ]
  },
  {
    key: 'SET_IS_SHOW_INSTANCES_INFO',
    label: 'instances信息',
    summary: 'Instance 层（Composite Object Instance）：单张图像/对象在序列中的序号与采集时刻。',
    fields: [
      { name: 'Instance Number', tag: '(0020,0013)', meaning: '实例序号；CT 断层从 1 递增，决定堆栈顺序。' },
      { name: 'Acquisition Number', tag: '(0020,0012)', meaning: '采集编号；增强扫描多期相时区分动脉期/静脉期等。' },
      { name: 'Acquisition Date', tag: '(0008,0022)', meaning: '本实例数据采集日期。' },
      { name: 'Acquisition Time', tag: '(0008,0032)', meaning: '本实例数据采集时间。' },
      { name: 'Content Date', tag: '(0008,0023)', meaning: 'DICOM 对象创建/写入日期（可能与采集时间不同，如离线重建）。' },
      { name: 'Content Time', tag: '(0008,0033)', meaning: 'DICOM 对象创建/写入时间。' },
      { name: 'SOP Instance UID', tag: '(0008,0018)', meaning: '本 .dcm 文件全球唯一标识，不可重复。' }
    ]
  },
  {
    key: 'SET_IS_SHOW_IMAGE_INFO',
    label: '图像信息',
    summary: 'Image Pixel Module 等：像素矩阵存的是原始整数；CT 用 Rescale 换成 HU；窗宽窗位只影响显示器上的灰度映射。',
    fields: [
      { name: 'Rows / Columns', tag: '(0028,0010)/(0028,0011)', meaning: '图像矩阵行、列数（像素），如 512×512。' },
      { name: 'Photometric Interpretation', tag: '(0028,0004)', meaning: '光度解释：CT 多为 MONOCHROME2（灰度，0=黑）。' },
      { name: 'Image Type', tag: '(0008,0008)', meaning: '多值字段，如 ORIGINAL\\PRIMARY\\AXIAL 表示原始轴位主图像。' },
      { name: 'Bits Allocated / Stored', tag: '(0028,0100)/(0028,0101)', meaning: '每像素分配位数 / 实际有效位数（CT 常见 16 bit）。' },
      { name: 'Pixel Representation', tag: '(0028,0103)', meaning: '0=无符号整数，1=有符号整数。' },
      { name: 'High Bit', tag: '(0028,0102)', meaning: '最高有效位位置。' },
      { name: 'Rescale Slope / Intercept', tag: '(0028,1053)/(0028,1052)', meaning: 'CT 亨氏单位换算：HU = 存储值 × Slope + Intercept；胸部 CT 常见 1 与 -1024。' },
      { name: 'Window Center / Width', tag: '(0028,1050)/(0028,1051)', meaning: '窗位/窗宽：把 HU 映射到 0~255 供人眼观看；调窗不改变文件内 HU，也不改变 AI 读取的密度值。' },
      { name: 'Pixel Spacing', tag: '(0028,0030)', meaning: '行、列方向像素物理间距 (mm)，影响测量与面积计算。' },
      { name: 'Samples Per Pixel', tag: '(0028,0002)', meaning: '每像素采样数，CT 通常为 1。' },
      { name: 'Image Position Patient', tag: '(0020,0032)', meaning: '图像左上角第一个像素在患者坐标系中的位置 (x,y,z) mm。' },
      { name: 'Image Orientation Patient', tag: '(0020,0037)', meaning: '行、列方向在患者坐标系中的方向余弦，用于 MPR/3D。' }
    ]
  },
  {
    key: 'SET_IS_SHOW_EQUIPMENT_INFO',
    label: '设备信息',
    summary: 'Equipment IE：与 Series 关联，记录采集设备与机构（同 Series 内一致）。',
    fields: [
      { name: 'Manufacturer', tag: '(0008,0070)', meaning: '设备制造商，如 SIEMENS、GE MEDICAL SYSTEMS、Philips。' },
      { name: 'Manufacturer Model', tag: '(0008,1090)', meaning: '设备型号名称。' },
      { name: 'Station Name', tag: '(0008,1010)', meaning: '采集站点/扫描仪名称（机构内命名）。' },
      { name: 'Institution Name', tag: '(0008,0080)', meaning: '医疗机构名称。' },
      { name: 'Software Version', tag: '(0018,1020)', meaning: '设备或重建软件版本。' },
      { name: 'Source AE Title', tag: '(0002,0016)', meaning: '【文件元信息】发送该对象的 DICOM 应用实体标题（本系统标注为 AE Title）。' }
    ]
  },
  {
    key: 'SET_IS_SHOW_UIDS_INFO',
    label: 'UIDS信息',
    summary: 'UID（Unique Identifier）：DICOM 全球唯一标识体系，PACS 检索、归档、C-MOVE/C-GET 的核心键。',
    fields: [
      { name: 'Study Instance UID', tag: '(0020,000D)', meaning: '标识一次 Study；检索“整次检查”时使用。' },
      { name: 'Series Instance UID', tag: '(0020,000E)', meaning: '标识一个 Series；检索“整个序列”时使用。' },
      { name: 'SOP Instance UID', tag: '(0008,0018)', meaning: '标识单个对象；传输时以 Instance 为最小单位。' },
      { name: 'SOP Class UID', tag: '(0008,0016)', meaning: '对象类型，如 1.2.840.10008.5.1.4.1.1.2 = CT Image Storage。' },
      { name: 'Transfer Syntax UID', tag: '(0002,0010)', meaning: '【文件头】编码方式：未压缩、JPEG、JPEG-LS、RLE 等。' },
      { name: 'Frame of Reference UID', tag: '(0020,0052)', meaning: '空间参考系 UID；相同者可联合重建、配准。' }
    ]
  }
]

export const DICOM_RELATION_SUMMARY =
  '标准 Patient-Root 模型：Patient 1→N Study → Study 1→N Series → Series 1→N Instance。' +
  '同一 Study 内所有 Instance 共享 Patient/Study 标签；同一 Series 内共享 Series/Equipment 标签；' +
  '每个 Instance 拥有唯一 SOP Instance UID 及像素数据。C-MOVE/C-GET 传输始终以 Instance 为最小单元。'

export function getDicomSectionByKey(key) {
  return DICOM_INFO_SECTIONS.find(s => s.key === key)
}
