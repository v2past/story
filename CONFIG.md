# 🔧 火山方舟API配置指南

## 📋 配置步骤

### 1. 获取火山方舟API密钥

1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 注册/登录您的账号
3. 进入"火山方舟"产品页面
4. 申请API密钥（ARK_API_KEY）

### 2. 创建环境变量文件

在项目根目录下创建 `.env` 文件，内容如下：

```bash
# 火山方舟API密钥
ARK_API_KEY=your_ark_api_key_here
```

**注意：** 请将 `your_ark_api_key_here` 替换为您的实际API密钥

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行应用

```bash
streamlit run app.py
```

## 🔍 验证配置

如果配置正确，应用启动时会显示：
- ✅ 火山方舟客户端初始化成功
- 🎭 可以使用AI生成故事功能

如果配置有误，应用会：
- ⚠️ 显示警告信息
- 🔄 自动切换到本地模板生成模式

## 📚 支持的模型

应用默认使用以下火山方舟模型：
- **doubao-1.5-pro-32k-250115**: 豆包1.5 Pro模型，支持长文本生成
- **doubao-1.5-pro-256k-250115**: 豆包1.5 Pro模型，支持超长文本
- **doubao-1.5-lite-4k-250115**: 豆包1.5 Lite模型，轻量快速
- **doubao-1.5-lite-32k-250115**: 豆包1.5 Lite模型，支持长文本

您可以在代码中修改 `model` 参数来使用其他模型。完整模型列表请参考[火山方舟官方文档](https://www.volcengine.com/docs/82379/1319847)。

## 🛠️ 故障排除

### 常见问题

1. **API密钥无效**
   - 检查API密钥是否正确
   - 确认API密钥是否已激活

2. **网络连接问题**
   - 确保网络连接正常
   - 检查防火墙设置

3. **依赖包安装失败**
   - 尝试使用 `pip3` 而不是 `pip`
   - 检查Python版本（需要3.7+）

### 备用方案

如果火山方舟API不可用，应用会自动切换到本地模板生成模式，确保基本功能正常运行。

## 📞 技术支持

如有问题，请参考：
- [火山方舟官方文档](https://www.volcengine.com/docs/82379/1319847)
- [火山引擎开发者社区](https://developer.volcengine.com/) 