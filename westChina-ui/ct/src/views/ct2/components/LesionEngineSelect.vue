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
    <template v-if="engine === 'scheme-b' && subEngineOptions.length > 0">
      <span class="lesion-engine-select__sep">·</span>
      <el-radio-group
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
      <span v-if="subEngineHint" class="lesion-engine-select__hint">{{ subEngineHint }}</span>
    </template>
    <el-button
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
  fetchLesionEngines,
  getEngineDescription,
  getSubEngines,
  readStoredEngine,
  writeStoredEngine
} from '@/utils/lesionEngines'
import AlgorithmExplainDialog from './AlgorithmExplainDialog'

export default {
  name: 'LesionEngineSelect',
  components: { AlgorithmExplainDialog },
  props: {
    compact: { type: Boolean, default: false },
    showLabel: { type: Boolean, default: true },
    placeholder: { type: String, default: '选择识别算法' }
  },
  data() {
    return {
      engineOptions: [...DEFAULT_LESION_ENGINES],
      showExplain: false
    }
  },
  computed: {
    ...mapGetters(['lesionDetectEngine', 'lesionDetectSubEngine', 'lesionEngineCatalog']),
    engine: {
      get() {
        return this.lesionDetectEngine || 'scheme-a'
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
      const opt = this.engineOptions.find((o) => o.id === this.engine)
      if (opt && !opt.available) {
        const fallback = this.engineOptions.find((o) => o.available)
        this.engine = fallback ? fallback.id : 'scheme-a'
      }
    },
    onChange(val) {
      const opt = this.engineOptions.find((o) => o.id === val)
      if (opt && !opt.available) {
        this.$message.warning(opt.unavailableReason || opt.installHint || '该识别算法暂不可用')
        const fallback = this.engineOptions.find((o) => o.available)
        this.engine = fallback ? fallback.id : 'scheme-a'
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
  gap: 8px;

  &.compact {
    gap: 6px;

    .lesion-engine-select__label {
      font-size: 12px;
    }

    .lesion-engine-select__control {
      width: 168px;
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
