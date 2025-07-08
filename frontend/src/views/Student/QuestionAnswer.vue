<template>
    <div class="chat-wrapper">
      <h1 class="title">学习问答助手</h1>
      <!-- 聊天记录区域 -->
      <el-scrollbar class="chat-box" ref="chatBox">
        <div class="message-list">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', msg.type === 'user' ? 'user' : 'bot']"
          >
            <div class="bubble">
              <div 
                v-if="msg.type === 'bot'" 
                class="markdown-content"
                v-html="renderMarkdown(msg.text)"
              ></div>
              <span v-else>{{ msg.text }}</span>
              <span v-if="msg.type === 'bot' && msg.streaming" class="cursor">|</span>
            </div>
          </div>
        </div>
      </el-scrollbar>
      <!-- 底部输入区域 -->
      <div class="input-area">
        <el-input
          v-model="question"
          placeholder="请输入您的问题"
          clearable
          class="question-input"
          @keyup.enter="submitQuestion"
          :disabled="loading"
        />
        <el-button
          type="primary"
          @click="submitQuestion"
          :loading="loading"
          class="submit-btn"
        >
          发送
        </el-button>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    name: "QuestionAnswer",
    data() {
      return {
        question: "",
        loading: false,
        messages: [],
        streamingInterval: null, // 用于存储定时器引用
      };
    },
    methods: {
      async submitQuestion() {
        const q = this.question.trim();
        if (!q) {
          this.$message.error("请输入问题！");
          return;
        }
        
        // 添加用户消息
        this.messages.push({ type: "user", text: q });
        this.question = "";
        this.loading = true;
        this.scrollToBottom();
        
        try {
          const res = await axios.post("/api/fastapi/v1/student/qa", {
            question: q,
          });
          const answerText = res.data.answer || "抱歉，未能获取回答。";
          
          // 添加空的 bot 消息用于流式填充
          const botMsgIndex = this.messages.length;
          this.messages.push({ 
            type: "bot", 
            text: "", 
            streaming: true 
          });
          this.scrollToBottom();
          
          // 开始流式输出
          await this.startStreamingText(answerText, botMsgIndex);
          
        } catch (error) {
          console.error("API调用失败:", error);
          this.$message.error("获取答案失败，请稍后重试！");
          this.messages.push({
            type: "bot",
            text: "获取答案失败，请稍后重试！",
            streaming: false
          });
          this.loading = false;
          this.scrollToBottom();
        }
      },
      
      async startStreamingText(text, messageIndex) {
        return new Promise((resolve) => {
          let i = 0;
          const streamText = () => {
            if (i < text.length) {
              // 直接修改消息对象的text属性
              this.messages[messageIndex].text += text[i];
              i++;
              this.scrollToBottom();
              this.streamingInterval = setTimeout(streamText, 50);
            } else {
              // 流式输出完成
              this.messages[messageIndex].streaming = false;
              this.loading = false;
              resolve();
            }
          };
          streamText();
        });
      },
      
      scrollToBottom() {
        this.$nextTick(() => {
          const scrollbar = this.$refs.chatBox;
          if (scrollbar && scrollbar.wrap) {
            scrollbar.wrap.scrollTop = scrollbar.wrap.scrollHeight;
          }
        });
      },
  
      renderMarkdown(text) {
        if (!text) return '';
        
        let html = text;
        
        // 代码块渲染 (```代码```)
        html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
          const language = lang || 'text';
          return `<div class="code-block">
            <div class="code-header">
              <span class="language">${language}</span>
              <button class="copy-btn" onclick="copyCode(this)">复制</button>
            </div>
            <pre><code class="language-${language}">${this.escapeHtml(code.trim())}</code></pre>
          </div>`;
        });
        
        // 行内代码渲染 (`代码`)
        html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
        
        // 加粗文本 (**文本** 或 __文本__)
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');
        
        // 斜体文本 (*文本* 或 _文本_)
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        html = html.replace(/_(.*?)_/g, '<em>$1</em>');
        
        // 删除线文本 (~~文本~~)
        html = html.replace(/~~(.*?)~~/g, '<del>$1</del>');
        
        // 链接渲染 [文本](链接)
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="markdown-link">$1</a>');
        
        // 标题渲染 (# ## ### #### ##### ######)
        html = html.replace(/^### (.*$)/gm, '<h3 class="markdown-h3">$1</h3>');
        html = html.replace(/^## (.*$)/gm, '<h2 class="markdown-h2">$1</h2>');
        html = html.replace(/^# (.*$)/gm, '<h1 class="markdown-h1">$1</h1>');
        html = html.replace(/^#### (.*$)/gm, '<h4 class="markdown-h4">$1</h4>');
        html = html.replace(/^##### (.*$)/gm, '<h5 class="markdown-h5">$1</h5>');
        html = html.replace(/^###### (.*$)/gm, '<h6 class="markdown-h6">$1</h6>');
        
        // 无序列表渲染 (- 或 * 或 +)
        html = html.replace(/^[\s]*[-\*\+]\s+(.*)$/gm, '<li class="markdown-li">$1</li>');
        html = html.replace(/(<li class="markdown-li">.*<\/li>)/gs, '<ul class="markdown-ul">$1</ul>');
        
        // 有序列表渲染 (1. 2. 3.)
        html = html.replace(/^[\s]*\d+\.\s+(.*)$/gm, '<li class="markdown-oli">$1</li>');
        html = html.replace(/(<li class="markdown-oli">.*<\/li>)/gs, '<ol class="markdown-ol">$1</ol>');
        
        // 引用块渲染 (>)
        html = html.replace(/^>\s+(.*)$/gm, '<blockquote class="markdown-blockquote">$1</blockquote>');
        
        // 水平分割线渲染 (--- 或 ***)
        html = html.replace(/^(---|\*\*\*)$/gm, '<hr class="markdown-hr">');
        
        // 换行处理
        html = html.replace(/\n/g, '<br>');
        
        return html;
      },
      
      escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
      },
    },
    
    beforeDestroy() {
      // 清理定时器
      if (this.streamingInterval) {
        clearTimeout(this.streamingInterval);
      }
    },
  
    mounted() {
      // 全局复制代码功能
      window.copyCode = (btn) => {
        const codeBlock = btn.closest('.code-block');
        const code = codeBlock.querySelector('code').textContent;
        
        if (navigator.clipboard) {
          navigator.clipboard.writeText(code).then(() => {
            btn.textContent = '已复制';
            setTimeout(() => {
              btn.textContent = '复制';
            }, 2000);
          });
        } else {
          // 降级方案
          const textarea = document.createElement('textarea');
          textarea.value = code;
          document.body.appendChild(textarea);
          textarea.select();
          document.execCommand('copy');
          document.body.removeChild(textarea);
          
          btn.textContent = '已复制';
          setTimeout(() => {
            btn.textContent = '复制';
          }, 2000);
        }
      };
    }
  };
  </script>
  
  <style scoped>
  .chat-wrapper {
    max-width: 720px;
    height: 90vh;
    margin: 0 auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8f8f8;
    border-radius: 10px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  }
  
  .title {
    text-align: center;
    color: #222;
    font-size: 24px;
    margin-bottom: 15px;
    font-weight: 600;
  }
  
  .chat-box {
    flex: 1;
    overflow-y: auto;
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #eee;
  }
  
  .message-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .message {
    display: flex;
    animation: messageSlideIn 0.3s ease-out;
  }
  
  .message.user {
    justify-content: flex-end;
  }
  
  .message.bot {
    justify-content: flex-start;
  }
  
  .bubble {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 16px;
    font-size: 16px;
    line-height: 1.6;
    word-break: break-word;
    transition: all 0.2s ease;
    position: relative;
    text-align: left; /* 添加左对齐 */
  }
  
  .message.user .bubble {
    background-color: #3f51b5;
    color: #fff;
    border-bottom-right-radius: 4px;
  }
  
  .message.bot .bubble {
    background-color: #f1f1f1;
    color: #333;
    border-bottom-left-radius: 4px;
  }
  
  .cursor {
    color: #3f51b5;
    font-weight: bold;
    animation: blink 1s infinite;
    margin-left: 2px;
  }
  
  .input-area {
    display: flex;
    margin-top: 20px;
    gap: 10px;
  }
  
  .question-input {
    flex: 1;
  }
  
  .submit-btn {
    padding: 10px 20px;
    min-width: 80px;
  }
  
  /* 动画效果 */
  @keyframes messageSlideIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }
  
  /* 响应式设计 */
  @media (max-width: 768px) {
    .chat-wrapper {
      height: 100vh;
      margin: 0;
      padding: 10px;
      border-radius: 0;
    }
    
    .bubble {
      max-width: 90%;
      font-size: 14px;
    }
    
    .title {
      font-size: 20px;
      margin-bottom: 10px;
    }
    
    .input-area {
      flex-direction: column;
      gap: 8px;
    }
    
    .submit-btn {
      align-self: stretch;
    }
  }
  
  /* Element UI 样式覆盖 */
  .question-input >>> .el-input__inner {
    border-radius: 20px;
    padding: 12px 16px;
    border: 1px solid #ddd;
    transition: border-color 0.3s ease;
  }
  
  .question-input >>> .el-input__inner:focus {
    border-color: #3f51b5;
    box-shadow: 0 0 0 2px rgba(63, 81, 181, 0.1);
  }
  
  .submit-btn {
    border-radius: 20px;
    background-color: #3f51b5;
    border-color: #3f51b5;
  }
  
  .submit-btn:hover {
    background-color: #303f9f;
    border-color: #303f9f;
  }
  
  /* Markdown 渲染样式 */
  .markdown-content {
    line-height: 1.6;
    color: #333;
    text-align: left; /* 确保 Markdown 内容左对齐 */
  }
  
  .markdown-content h1, .markdown-h1 {
    font-size: 1.8em;
    font-weight: 600;
    margin: 16px 0 12px 0;
    color: #222;
    border-bottom: 2px solid #3f51b5;
    padding-bottom: 8px;
    text-align: left; /* 标题左对齐 */
  }
  
  .markdown-content h2, .markdown-h2 {
    font-size: 1.5em;
    font-weight: 600;
    margin: 14px 0 10px 0;
    color: #222;
    border-bottom: 1px solid #ddd;
    padding-bottom: 6px;
    text-align: left; /* 标题左对齐 */
  }
  
  .markdown-content h3, .markdown-h3 {
    font-size: 1.3em;
    font-weight: 600;
    margin: 12px 0 8px 0;
    color: #333;
    text-align: left; /* 标题左对齐 */
  }
  
  .markdown-content h4, .markdown-h4 {
    font-size: 1.1em;
    font-weight: 600;
    margin: 10px 0 6px 0;
    color: #333;
    text-align: left; /* 标题左对齐 */
  }
  
  .markdown-content h5, .markdown-h5,
  .markdown-content h6, .markdown-h6 {
    font-size: 1em;
    font-weight: 600;
    margin: 8px 0 4px 0;
    color: #333;
    text-align: left; /* 标题左对齐 */
  }
  
  .markdown-content strong {
    font-weight: 600;
    color: #222;
  }
  
  .markdown-content em {
    font-style: italic;
    color: #555;
  }
  
  .markdown-content del {
    text-decoration: line-through;
    color: #999;
  }
  
  .markdown-content code, .inline-code {
    background-color: #f5f5f5;
    border: 1px solid #e1e1e1;
    border-radius: 3px;
    padding: 2px 6px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 0.9em;
    color: #d73a49;
  }
  
  .code-block {
    background-color: #f8f8f8;
    border: 1px solid #e1e1e1;
    border-radius: 8px;
    margin: 12px 0;
    overflow: hidden;
    text-align: left; /* 代码块左对齐 */
  }
  
  .code-header {
    background-color: #f0f0f0;
    padding: 8px 12px;
    border-bottom: 1px solid #e1e1e1;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .language {
    font-size: 0.8em;
    color: #666;
    font-weight: 500;
  }
  
  .copy-btn {
    background-color: #3f51b5;
    color: white;
    border: none;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8em;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .copy-btn:hover {
    background-color: #303f9f;
  }
  
  .code-block pre {
    margin: 0;
    padding: 12px;
    background-color: #f8f8f8;
    overflow-x: auto;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 0.9em;
    line-height: 1.4;
    text-align: left; /* 代码内容左对齐 */
  }
  
  .code-block code {
    background: none;
    border: none;
    padding: 0;
    color: #333;
    font-size: inherit;
  }
  
  .markdown-ul, .markdown-ol {
    margin: 8px 0;
    padding-left: 20px;
    text-align: left; /* 列表左对齐 */
  }
  
  .markdown-li, .markdown-oli {
    margin: 4px 0;
    line-height: 1.5;
    text-align: left; /* 列表项左对齐 */
  }
  
  .markdown-ul {
    list-style-type: disc;
  }
  
  .markdown-ol {
    list-style-type: decimal;
  }
  
  .markdown-blockquote {
    background-color: #f9f9f9;
    border-left: 4px solid #3f51b5;
    margin: 12px 0;
    padding: 12px 16px;
    color: #555;
    font-style: italic;
    text-align: left; /* 引用块左对齐 */
  }
  
  .markdown-hr {
    border: none;
    height: 1px;
    background-color: #ddd;
    margin: 16px 0;
  }
  
  .markdown-link {
    color: #3f51b5;
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: border-bottom 0.2s;
  }
  
  .markdown-link:hover {
    border-bottom: 1px solid #3f51b5;
  }
  
  /* 针对bot消息的特殊处理 */
  .message.bot .markdown-content {
    color: #333;
    text-align: left; /* 确保机器人消息左对齐 */
  }
  
  .message.bot .markdown-content h1,
  .message.bot .markdown-content h2,
  .message.bot .markdown-content h3,
  .message.bot .markdown-content h4,
  .message.bot .markdown-content h5,
  .message.bot .markdown-content h6 {
    color: #222;
    text-align: left; /* 机器人消息中的标题左对齐 */
  }
  
  .message.bot .code-block {
    background-color: #ffffff;
    border: 1px solid #e1e1e1;
    text-align: left; /* 机器人消息中的代码块左对齐 */
  }
  
  .message.bot .code-header {
    background-color: #f8f8f8;
  }
  
  .message.bot .code-block pre {
    background-color: #ffffff;
    text-align: left; /* 机器人消息中的代码内容左对齐 */
  }
  
  /* 移动端适配 */
  @media (max-width: 768px) {
    .markdown-content h1, .markdown-h1 {
      font-size: 1.5em;
    }
    
    .markdown-content h2, .markdown-h2 {
      font-size: 1.3em;
    }
    
    .markdown-content h3, .markdown-h3 {
      font-size: 1.2em;
    }
    
    .code-block pre {
      font-size: 0.8em;
    }
    
    .code-header {
      padding: 6px 10px;
    }
    
    .copy-btn {
      padding: 3px 6px;
      font-size: 0.75em;
    }
  }
  </style>