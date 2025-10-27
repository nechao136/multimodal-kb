<template>
  <div id="app" style="padding: 20px;">
    <el-row :gutter="20">
      <el-col :span="12">
        <upload-file @uploaded="onUploaded"/>
      </el-col>
      <el-col :span="12">
        <el-input v-model="query" placeholder="请输入查询内容" @keyup.enter.native="onSearch" clearable />
        <el-button type="primary" @click="onSearch" style="margin-top: 10px;">搜索</el-button>
      </el-col>
    </el-row>

    <search-result :results="results" />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import UploadFile from './components/UploadFile.vue';
import SearchResult from './components/SearchResult.vue';

@Component({
  components: {
    SearchResult,
    UploadFile,
  },
})
export default class App extends Vue {

  private query: string = ''
  private results: any = null

  onUploaded(fileInfo: any) {
    this.$message.success(`上传成功，插入 ${fileInfo.chunks} 个 chunks`);
  }

  async onSearch() {
    if (!this.query) {
      this.$message.warning('请输入查询内容')
      return
    }
    const res = await fetch(`http://150.109.15.178:10090/search?q=${encodeURIComponent(this.query)}`)
    this.results = await res.json()
  }

}
</script>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
