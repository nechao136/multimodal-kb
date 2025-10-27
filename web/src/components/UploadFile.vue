<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'


@Component({})
export default class UploadFile extends Vue {

  private async handleUpload(option: any) {
    const formData = new FormData();
    formData.append('file', option.file);

    const res = await fetch('http://150.109.15.178:10090/upload', {
      method: 'POST',
      body: formData,
    })
    const data = await res.json()
    if (data?.status === 'ok') {
      this.$emit('uploaded', data)
      this.$message.success('上传成功')
    } else {
      this.$message.error('上传失败')
    }
  }

  private async beforeUpload(file: File) {
    const allowed = ['pdf', 'md', 'txt'];
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !allowed.includes(ext)) {
      this.$message.error('仅支持 PDF / MD / TXT');
      return false;
    }
    return true;
  }

}
</script>

<template>
  <div>
    <el-upload
      class="upload-demo"
      drag
      action=""
      :http-request="handleUpload"
      :show-file-list="false"
      :before-upload="beforeUpload"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      <div class="el-upload__tip" slot="tip">支持 PDF / MD / TXT</div>
    </el-upload>
  </div>
</template>

<style scoped lang="scss">

</style>
