<template>
  <section class="app-main">
    <transition name="fade-transform" mode="out-in">
      <keep-alive >
        <router-view :key="key" v-if="$route.meta.keepAlive"/>
        <router-view :key="key" v-if="!$route.meta.keepAlive"/>
      </keep-alive>

    </transition>
  </section>
</template>

<script>
export default {
  name: 'AppMain',
  computed: {
    key() {
      return this.$route.path
    }
  }
}
</script>

<style lang="scss" scoped>
.app-main {
  /* 50= navbar  50  */
  //min-height: calc(100vh - 50px);
  background: #000;
  //width: calc(100vh - 84px);
  position: relative;
  overflow: hidden;
}

.fixed-header+.app-main {
  //padding-top: 50px;
}

.hasTagsView {
  .app-main {
    /* 84 = navbar + tags-view = 50 + 34 */
    min-height: calc(100vh - 84px);
    background: #000;
  }

  .fixed-header+.app-main {
    padding-top: 84px;
    background: #000;
  }
}
</style>

<style lang="scss">
// fix css style bug in open el-dialog
.el-popup-parent--hidden {
  .fixed-header {
    padding-right: 17px;
    background: #000;
  }
}
</style>
