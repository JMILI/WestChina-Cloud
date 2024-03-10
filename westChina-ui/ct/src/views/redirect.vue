<script>
export default {
  created() {
    //没必要给重定向页面定义模板，因为不用加载，就需要跳到下一个页面了。
    // created是最早能拿到vue实例中的数据和方法
    //有些页面可能有参数，首先拿到参数，params类型的参数，query类型的参数
    const { params, query } = this.$route
    //拿到路径
    const { path } = params
    this.$router.replace({ path: '/' + path, query })
  },
  render: function(h) {
    return h() // avoid warning message
  }
}
</script>
