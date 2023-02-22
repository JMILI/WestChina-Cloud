<template>
  <div id="tags-view-container" class="tags-view-container">
    <span>病人姓名：{{ patName }} 身份证号： {{ patCardId }} 手机号：{{ patPhone }}</span>
  </div>
</template>

<script>


import eventBus from "@/eventBus";

export default {
  components: {},
  data() {
    return {
    }
  },
  create() {
    // eventBus.$on('patient',(patient)=>{
    //   //一些操作，message就是从top组件传过来的值
    //   console.log(patient)
    // })
  },
  computed: {
    patPhone(){
      return this.$store.getters.patPhone
    },
    patName(){
      return this.$store.getters.patName
    },
    patCardId(){
      return this.$store.getters.patCardId
    }
  },
  watch: {},
  mounted() {
    // eventBus.$on('patient', (patient) => {
    //   //一些操作，message就是从top组件传过来的值
    //   this.patient = patient
    //   console.log(patient)
    // })
  },
  methods: {}
}
</script>

<style lang="scss" scoped>
.tags-view-container {
  height: 34px;
  width: 100%;
  background: #282c34;
  //border-bottom: 1px solid #d8dce5;
  //box-shadow: 0 1px 3px 0 rgba(0, 0, 0, .12), 0 0 3px 0 rgba(0, 0, 0, .04);
}

span {
  text-align: center;
  margin-left: 50px;
  display: block;
  line-height: 34px;
  font-size: 15px;
  color: #ddd;
}


</style>

