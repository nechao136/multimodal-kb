<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'


@Component({})
export default class SearchResult extends Vue {

  @Prop()
  private results!: any

  private getImageUrl(path: string) {
    if (path.startsWith('http')) {
      return path
    }
    return `http://150.109.15.178:10090/data/${path}`
  }

}
</script>

<template>
  <div class="search-result">
    <h3>文本检索结果</h3>
    <el-card v-for="(item, idx) in results.texts" :key="idx" style="margin-bottom: 10px;">
      <div><strong>score:</strong> {{item.score.toFixed(3)}}</div>
      <div><strong>source:</strong> {{item.payload.source}}</div>
      <div style="white-space: pre-wrap;">{{item.payload.text}}</div>
    </el-card>

    <h3 style="margin-top:20px;">图片检索结果</h3>
    <el-row :gutter="10">
      <el-col :span="6" v-for="(item, idx) in results.images" :key="idx">
        <el-card>
          <img alt="" :src="getImageUrl(item.payload.image_path)" style="width:100%;height:auto;" />
          <div><strong>score:</strong> {{item.score.toFixed(3)}}</div>
          <div style="font-size:12px; color:#666;">{{item.payload.source}}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
.search-result {
  margin-top: 30px;
}
</style>
