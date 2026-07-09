<template>
  <div class="lesion-engine-select" :class="{ compact: compact }">
    <span v-if="showLabel" class="lesion-engine-select__label">识别算法</span>
    <el-tooltip
      :content="selectedDesc"
      placement="bottom"
      :open-delay="400"
      :disabled="!selectedDesc"
      popper-class="lesion-engine-tooltip"
    >
      <el-select
        v-model="engine"
        :size="compact ? 'mini' : 'small'"
        :placeholder="placeholder"
        class="lesion-engine-select__control"
        popper-class="lesion-engine-dropdown"
        @change="onChange"
      >
        <el-option
          v-for="opt in engineOptions"
          :key="opt.id"
          :label="opt.label"
          :value="opt.id"
          :disabled="!opt.available"
        >
          <span>{{ opt.label }}</span>
          <span v-if="!opt.available" class="engine-unavailable">（不可用）</span>
        </el-option>
      </el-select>
    </el-tooltip>
    <!-- 方案 B 子引擎选择 -->
    <template v-if="engine === 'scheme-b' && subEngineOptions.length > 0 && subEngineDisplay !== 'none'">
      <span v-if="subEngineDisplay === 'radio'" class="lesion-engine-select__sep">·</span>
      <el-radio-group
        v-if="subEngineDisplay === 'radio'"
        v-model="subEngine"
        size="mini"
        class="lesion-engine-select__sub"
        @change="onSubChange"
      >
        <el-radio-button
          v-for="sopt in subEngineOptions"
          :key="sopt.id"
          :label="sopt.id"
          :disabled="!sopt.available"
        >
          {{ sopt.label }}
        </el-radio-button>
      </el-radio-group>
      <el-select
        v-else-if="subEngineDisplay === 'select'"
        v-model="subEngine"
        size="mini"
        class="lesion-engine-select__sub-select"
        popper-class="lesion-engine-dropdown"
        @change="onSubChange"
      >
        <el-option
          v-for="sopt in subEngineOptions"
          :key="sopt.id"
          :label="sopt.label"
          :value="sopt.id"
          :disabled="!sopt.available"
        />
      </el-select>
      <span v-if="subEngineHint && subEngineDisplay === 'radio'" class="lesion-engine-select__hint">{{ subEngineHint }}</span>
    </template>
    <el-button
      v-if="showHelp"
      type="text"
      :size="compact ? 'mini' : 'small'"
      class="lesion-engine-select__help"
      @click="showExplain = true"
    >
      <i class="el-icon-question"></i>
    </el-button>
    <algorithm-explain-dialog :visible.sync="showExplain" :scheme="engine" />
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import {
  DEFAULT_LESION_ENGINES,
  DEFAULT_ACTIVE_LESION_ENGINE,
  fetchLesionEngines,
  filterVisibleEngines,
  getEngineDescription,
  getSubEngines,
  normalizeActiveEngine
} from '@/utils/lesionEngines'
import AlgorithmExplainDialog from './AlgorithmExplainDialog'

export default {
  name: 'LesionEngineSelect',
  components: { AlgorithmExplainDialog },
  props: {
    compact: { type: Boolean, default: false },
    showLabel: { type: Boolean, default: true },
    showHelp: { type: Boolean, default: true },
    /** radio | select | none — 子引擎展示方式 */
    subEngineDisplay: { type: String, default: 'radio' },
    placeholder: { type: String, default: '选择识别算法' }
  },
  data() {
    return {
      engineOptions: filterVisibleEngines([...DEFAULT_LESION_ENGINES]),
      showExplain: false
    }
  },
  computed: {
    ...mapGetters(['lesionDetectEngine', 'lesionDetectSubEngine', 'lesionEngineCatalog']),
    engine: {
      get() {
        return this.lesionDetectEngine || DEFAULT_ACTIVE_LESION_ENGINE
      },
      set(val) {
        this.setLesionDetectEngine(val)
      }
    },
    selectedDesc() {
      const catalog = this.lesionEngineCatalog.length
        ? this.lesionEngineCatalog
        : this.engineOptions
      return getEngineDescription(this.engine, catalog)
    },
    subEngineOptions() {
      const catalog = this.lesionEngineCatalog.length
        ? this.lesionEngineCatalog
        : this.engineOptions
      return getSubEngines(this.engine, catalog) || []
    },
    subEngine: {
      get() {
        return this.lesionDetectSubEngine || 'auto'
      },
      set(val) {
        this.setLesionDetectSubEngine(val)
      }
    },
    subEngineHint() {
      const opt = this.subEngineOptions.find(o => o.id === this.subEngine)
      if (opt && !opt.available && opt.unavailableReason) {
        return opt.unavailableReason
      }
      return ''
    }
  },
  mounted() {
    this.loadEngines()
  },
  methods: {
    ...mapActions(['setLesionDetectEngine', 'setLesionDetectSubEngine', 'loadLesionEngineCatalog']),
    loadEngines() {
      fetchLesionEngines().then((list) => {
        this.engineOptions = list
        this.loadLesionEngineCatalog(list)
        this.ensureEngineAvailable()
      })
    },
    ensureEngineAvailable() {
      const next = normalizeActiveEngine(this.engine, this.engineOptions)
      if (next !== this.engine) {
        this.engine = next
      }
    },
    onChange(val) {
      const opt = this.engineOptions.find((o) => o.id === val)
      if (opt && !opt.available) {
        this.$message.warning(opt.unavailableReason || opt.installHint || '该识别算法暂不可用')
        this.engine = normalizeActiveEngine(this.engine, this.engineOptions)
        return
      }
      this.$emit('change', val)
    },
    onSubChange(val) {
      const opt = this.subEngineOptions.find(o => o.id === val)
      if (opt && !opt.available) {
        this.$message.warning(opt.unavailableReason || '该子引擎暂不可用')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.lesion-engine-select {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  max-width: 100%;

  &.compact {
    gap: 6px;
    flex-wrap: nowrap;

    .lesion-engine-select__label {
      font-size: 12px;
    }

    .lesion-engine-select__control {
      width: 132px;
      min-width: 108px;
    }

    .lesion-engine-select__sub-select {
      width: 148px;
      min-width: 120px;
    }
  }

  &__label {
    font-size: 13px;
    color: #b8bcc6;
    white-space: nowrap;
  }

  &__control {
    width: 220px;
  }

  &__sep {
    color: #4a5568;
    font-size: 14px;
    margin: 0 2px;
  }

  &__sub {
    flex-shrink: 0;

    ::v-deep .el-radio-button__inner {
      padding: 4px 10px;
      font-size: 11px;
      border-radius: 0;
    }

    ::v-deep .el-radio-button:first-child .el-radio-button__inner {
      border-radius: 3px 0 0 3px;
    }

    ::v-deep .el-radio-button:last-child .el-radio-button__inner {
      border-radius: 0 3px 3px 0;
    }
  }

  &__sub-select {
    width: 168px;
    flex-shrink: 0;
  }

  &__hint {
    font-size: 11px;
    color: #e6a23c;
    max-width: 180px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &__help {
    color: #7eb8ff;
    padding: 0 4px;
  }
}

.engine-unavailable {
  margin-left: 6px;
  color: #c0c4cc;
  font-size: 12px;
}
</style>

<style lang="scss">
.lesion-engine-tooltip {
  max-width: 360px;
  line-height: 1.5;
  white-space: normal;
}

.lesion-engine-dropdown {
  z-index: 3000 !important;
}
</style>
