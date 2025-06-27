# QQ邮箱配置完整指南

## 📧 配置步骤

### 第一步：开启QQ邮箱SMTP服务

1. **登录QQ邮箱**
   - 访问：https://mail.qq.com
   - 使用您的QQ号和密码登录

2. **进入邮箱设置**
   - 点击邮箱页面右上角的"设置"
   - 选择"账户"选项卡

3. **开启SMTP服务**
   - 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
   - 开启"POP3/SMTP服务"或"IMAP/SMTP服务"
   - 按照提示发送短信到指定号码进行验证

4. **获取授权码**
   - 验证成功后，系统会显示一个16位的授权码
   - **重要：请务必保存好这个授权码，这就是您的邮箱密码！**
   - 授权码格式类似：`abcdefghijklmnop`

### 第二步：配置环境变量

1. **复制配置文件**
   ```bash
   # 将 env.qq.example 复制为 .env
   cp env.qq.example .env
   ```

2. **修改.env文件中的邮箱配置**
   ```env
   # QQ邮箱配置
   EMAIL_SMTP_SERVER=smtp.qq.com
   EMAIL_SMTP_PORT=587
   EMAIL_USERNAME=你的QQ号@qq.com
   EMAIL_PASSWORD=你的16位授权码
   EMAIL_FROM_NAME=生活管家AI
   ```

   **具体示例：**
   ```env
   EMAIL_SMTP_SERVER=smtp.qq.com
   EMAIL_SMTP_PORT=587
   EMAIL_USERNAME=1876146375@qq.com
   EMAIL_PASSWORD=abcdefghijklmnop
   EMAIL_FROM_NAME=生活管家AI
   ```

### 第三步：测试邮件功能

1. **使用测试脚本**
   ```bash
   python test_email_service.py
   ```

2. **或在Web界面测试**
   - 启动应用：`python start.py`
   - 打开浏览器访问：http://localhost:8000
   - 在提醒设置中输入您的邮箱地址
   - 点击"测试邮件服务"按钮

## ⚠️ 重要注意事项

### 1. 授权码 vs 密码
- **不能使用QQ密码**：邮件服务必须使用授权码，不能使用QQ登录密码
- **授权码是16位字符**：通常是小写字母，无特殊符号
- **授权码有效期**：长期有效，除非您主动重置

### 2. 常见错误及解决方案

**错误1：535 Login Fail**
- **原因**：未开启SMTP服务或使用了错误的密码
- **解决**：确保开启了SMTP服务并使用授权码

**错误2：554 DT:SPM**
- **原因**：邮件被识别为垃圾邮件
- **解决**：检查邮件内容，避免敏感词汇

**错误3：Connection timeout**
- **原因**：网络连接问题或端口被阻止
- **解决**：检查网络连接，尝试使用465端口（SSL）

### 3. 其他QQ邮箱相关配置

如果587端口不工作，可以尝试SSL配置：
```env
EMAIL_SMTP_SERVER=smtp.qq.com
EMAIL_SMTP_PORT=465
# 注意：使用465端口需要SSL连接
```

## 🔧 高级配置

### 企业QQ邮箱
如果您使用的是企业QQ邮箱：
```env
EMAIL_SMTP_SERVER=smtp.exmail.qq.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=你的企业邮箱@company.com
EMAIL_PASSWORD=你的企业邮箱授权码
```

### 安全建议
1. **不要在代码中硬编码邮箱密码**
2. **定期更换授权码**
3. **限制邮件发送频率**，避免被识别为垃圾邮件
4. **监控邮件发送日志**

## 📋 配置检查清单

- [ ] 已登录QQ邮箱并开启SMTP服务
- [ ] 已获取16位授权码
- [ ] 已创建.env文件
- [ ] 已正确填写EMAIL_USERNAME（完整邮箱地址）
- [ ] 已正确填写EMAIL_PASSWORD（授权码，不是QQ密码）
- [ ] 已设置EMAIL_SMTP_SERVER=smtp.qq.com
- [ ] 已设置EMAIL_SMTP_PORT=587
- [ ] 已测试邮件发送功能

## 🚀 快速验证

运行以下命令进行快速测试：
```bash
# 测试邮件服务
python test_email_service.py

# 或者启动应用进行Web测试
python start.py
```

如果一切配置正确，您应该能收到测试邮件！

## 📞 常见问题

**Q: 为什么收不到邮件？**
A: 检查垃圾邮件文件夹，QQ邮箱发送的邮件可能被其他邮箱服务商标记为垃圾邮件。

**Q: 授权码忘记了怎么办？**
A: 重新进入QQ邮箱设置，关闭SMTP服务再重新开启，会生成新的授权码。

**Q: 可以发送给非QQ邮箱吗？**
A: 可以，QQ邮箱可以向任何邮箱地址发送邮件。

**Q: 有发送频率限制吗？**
A: QQ邮箱有反垃圾邮件机制，建议不要短时间内大量发送邮件。 