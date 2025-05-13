<template>
  <div class="app-container">
    <!-- 左侧边栏 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h2>Explorer</h2>
        <button v-if="zipBlob" @click="downloadZip">Download ZIP</button>
      </div>
      <div class="sidebar-content">
        <TreeNode v-for="node in sidebarFiles" :key="node.path" :node="node" @open="openFile" />
      </div>
    </div>

    <!-- 中间内容区 -->
    <div class="main-content">
      <div class="editor-container">
        <pre style="white-space: pre-wrap;">{{ centerContent }}</pre>
      </div>
    </div>

    <!-- 右侧对话框 -->
    <div class="chat-panel">
      <div class="chat-header">
        <h2>Chat</h2>
      </div>
      <div class="chat-content" >
        <!-- 聊天消息列表 -->
        <div v-for="(item, idx) in chatList" :key="idx" class="chat-message">
          <div>{{ item.text }}</div>
          <div v-if="item.response">
            <span>{{ item.response }}</span>
            <span v-if="item.streaming" class="cursor">|</span>
          </div>
          <div v-if="item.files && item.files.length">
            <div v-for="(file, fidx) in item.files" :key="fidx" class="chat-file">
              <a :href="file.url" target="_blank">{{ file.name }}</a>
            </div>
          </div>
        </div>
      </div>
      <div class="chat-input">
        <div class="input-container">
          <input
            type="text"
            v-model="message"
            placeholder="Type your message..."
            @keyup.enter="sendMessage"
          />
          <div class="button-group">
            <label class="upload-button">
              <input
                type="file"
                @change="handleFileUpload"
                multiple
                style="display: none"
              />
              📎
            </label>
            <button class="send-button" @click="sendMessage">Send</button>
          </div>
        </div>
        <!-- 显示已选文件（在输入框下方） -->
        <div v-if="uploadedFiles.length" class="file-list">
          <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">({{ formatFileSize(file.size) }})</span>
            <button class="remove-file" @click="removeFile(index)">×</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted,watch, nextTick ,onBeforeUnmount,markRaw  } from 'vue'
import axios from 'axios'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import TreeNode from './TreeNode.vue'
const message = ref('')
const uploadedFiles = ref<File[]>([])
const chatList = ref<any[]>([])
const sidebarFiles = ref<any[]>([]) // zip结构树
const centerContent = ref('') // 中间内容区
const zipBlob = ref<Blob | null>(null)
const zipUrl = ref('')

let streamingIdx: number | null = null
let eventSource: EventSource | null = null




//
// const chatContentRef = ref<HTMLElement | null>(null)
//
// // 滚动到底部函数
// const scrollToBottom = () => {
//   nextTick(() => {
//     if (chatContentRef.value) {
//       chatContentRef.value.scrollTop = chatContentRef.value.scrollHeight
//     }
//   })
// }
//
// // 监听聊天列表变更时自动滚动到底部
// watch(chatList, scrollToBottom, { deep: true })
// 处理文件上传
const handleFileUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files) {
    const newFiles = Array.from(input.files)
    uploadedFiles.value = [...uploadedFiles.value, ...newFiles]
    // 在输入框里自动插入文件名
    const fileNames = newFiles.map(f => f.name).join(', ')
    message.value = message.value
      ? message.value + ' [upload files: ' + fileNames + ']'
      : '[upload files: ' + fileNames + ']'
  }
}

// 移除文件
const removeFile = (index: number) => {
  uploadedFiles.value.splice(index, 1)
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 发送消息和文件
const sendMessage = async () => {
  if (!message.value && uploadedFiles.value.length === 0) return

  try {
    const formData = new FormData()
    if (message.value) formData.append('message', message.value)
    uploadedFiles.value.forEach(file => formData.append('file', file))

    // 假设后端返回文件的可访问url
    const response = await axios.post('http://localhost:9876/submit-requirement-files', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    // 假设后端返回 { files: [{name, url}, ...] }
    const files = response.data.files || []

    // 添加到聊天列表
    chatList.value.push({
      text: message.value,
      files
    })
    // chatList.value = chatList.value.slice(-20)

    // 清空输入框和文件
    message.value = ''
    uploadedFiles.value = []

    // 新增：触发流式推送
    startStream()
  } catch (error) {
    console.error('Upload failed:', error)
  }
}
let syncTimer: ReturnType<typeof setTimeout> | null = null
let rawResponse = ''
function startStream() {

  if (eventSource) {
    eventSource.close()
  }

  eventSource = new EventSource('http://localhost:9876/view-result')

  streamingIdx = null

  eventSource.onmessage = async (event) => {
    console.log('[STREAM LOG]', event.data)
    if (event.data.startsWith('[ZIP]')) {
      zipUrl.value = event.data.replace('[ZIP]', '')
      const resp = await fetch(zipUrl.value)
      const blob = await resp.blob()
      zipBlob.value = blob
      const zip = await JSZip.loadAsync(blob)
      sidebarFiles.value = zipTree(zip)
      chatList.value.push({
        text: 'ZIP文件已生成',
        files: [{ name: '下载ZIP', url: zipUrl.value }]
      })
      // chatList.value = chatList.value.slice(-20)
      return
    }
    if (event.data === '[DONE]') {
      if (streamingIdx !== null) chatList.value[streamingIdx].streaming = false
      streamingIdx = null
      eventSource?.close()
      return
    }
    // if (streamingIdx === null) {
    //   chatList.value.push({
    //     text: '[SmartCoder]',
    //     files: [],
    //     streaming: true,
    //     response: ''
    //   })
    //   // const item = markRaw({
    //   //   text: '[SmartCoder]',
    //   //   response: '',       // 这里不会被 Vue 追踪
    //   //   streaming: true,
    //   //   files: []
    //   // })
    //   //
    //   // chatList.value.push(item)
    //   // chatList.value = chatList.value.slice(-20)
    //   streamingIdx = chatList.value.length - 1
    // }
    // chatList.value[streamingIdx].response += event.data
    if (streamingIdx === null) {
      rawResponse = ''
      const item = markRaw({
        text: '[SmartCoder]',
        response: '',
        streaming: true,
        files: []
      })
      chatList.value.push(item)
      streamingIdx = chatList.value.length - 1
    }

    // 缓存文本，不立刻更新 Vue 响应式
    rawResponse += event.data

    // 每 100ms 手动同步到响应式（节流）
    if (!syncTimer) {
      syncTimer = setTimeout(() => {
        if (streamingIdx !== null) {
          chatList.value[streamingIdx].response = rawResponse
        }
        syncTimer = null
      }, 100)
    }
  }



}

onBeforeUnmount(() => {
  if (eventSource) eventSource.close()
})

// 递归生成zip树结构
function zipTree(zip: JSZip) {
  const root: any[] = []

  Object.keys(zip.files).forEach((path) => {
    const fileObj = zip.files[path]
    const parts = path.split('/').filter(Boolean)
    let current = root

    parts.forEach((part, idx) => {
      let node = current.find((n: any) => n.name === part)
      const isLast = idx === parts.length - 1

      if (!node) {
        node = {
          name: part,
          isDir: !isLast || fileObj.dir,
          children: [],
          path: parts.slice(0, idx + 1).join('/'),
          expanded: false
        }
        // 只在目录时添加，或者在最后一级且不是目录且没有同名目录时添加
        if (
          node.isDir ||
          (
            !fileObj.dir &&
            isLast &&
            !current.find(n => n.isDir && n.name === part)
          )
        ) {
          current.push(node)
        }
      }

      if (node.isDir) {
        current = node.children
      }
    })
  })

  return root
}

// 侧边栏文件树递归渲染


// 双击文件，读取内容
async function openFile(node: any) {
  if (!zipBlob.value) return
  const zip = await JSZip.loadAsync(zipBlob.value)
  const file = zip.file(node.path)
  if (file) {
    const content = await file.async('string')
    centerContent.value = content
  }
}

// 下载zip
function downloadZip() {
  if (zipBlob.value) saveAs(zipBlob.value, 'result.zip')
}
</script>

<style scoped>
/* 保留原有样式 */
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  background-color: #f5f5f5;
  color: #333;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
}

.main-content {
  flex: 1;
  background-color: #ffffff;
  color: #333;
  display: flex;
  flex-direction: column;
}

.editor-container {
  flex: 1;
  padding: 1rem;
}

.chat-panel {
  width: 600px;
  background-color: #f5f5f5;
  color: #333;
  border-left: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.chat-content {
  overflow-x: hidden;
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

/* 新增样式 */
.input-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-input {
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
}

.chat-input input {
  width: 100%;
  padding: 0.5rem;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  color: #333;
  border-radius: 4px;
}

.button-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.upload-button {
  cursor: pointer;
  padding: 4px 8px;
  background-color: #f0f0f0;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 1.2rem;
}

.upload-button:hover {
  background-color: #e0e0e0;
}

.send-button {
  padding: 4px 12px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.send-button:hover {
  background-color: #1976d2;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: #666;
  font-size: 0.9em;
}

.remove-file {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 0 4px;
}

.remove-file:hover {
  color: #f44336;
}

.chat-message {
  margin-bottom: 1em;
  padding-bottom: 0.5em;
  border-bottom: 1px solid #eee;
}
.chat-file a {
  color: #2196f3;
  text-decoration: underline;
  margin-right: 8px;
}
</style>