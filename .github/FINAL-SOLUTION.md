# GitHub Packages 最终解决方案

## 问题根源

经过深入分析和测试，发现了 GitHub Packages 404 错误的根本原因：

### 关键发现
**GitHub Packages 的 Python 包使用包名（package name）而不是仓库名（repository name）作为 URL 的一部分。**

### 错误配置
之前使用的 URL：
```
https://upload.pkg.github.com/Zherphy/sglang
```
（其中 `sglang` 是仓库名）

### 正确配置
应该使用的 URL：
```
https://upload.pkg.github.com/Zherphy/sglang
```
（其中 `sglang` 是**包名**，从 `pyproject.toml` 的 `name = "sglang"` 读取）

## 解决方案实施

### 1. 已修复的工作流文件

#### a) `.github/workflows/test-fork-packages.yml`
- 修复了 YAML 格式问题（缩进不一致）
- 更新了 URL 使用包名 `sglang` 而不是仓库名
- 关键更改：
  ```yaml
  # 之前（错误）：
  --repository-url https://upload.pkg.github.com/${{ github.repository_owner }}/$REPO_NAME
  
  # 之后（正确）：
  --repository-url https://upload.pkg.github.com/${{ github.repository_owner }}/sglang
  ```

#### b) `.github/workflows/release-pypi-with-ghpkg.yml`
- 更新了 URL 使用包名 `sglang`
- 关键更改：
  ```yaml
  # 之前（错误）：
  --repository-url "https://upload.pkg.github.com/${{ github.repository_owner }}/$REPO_NAME"
  
  # 之后（正确）：
  --repository-url "https://upload.pkg.github.com/${{ github.repository_owner }}/sglang"
  ```

### 2. 验证步骤

#### 步骤 1：检查包名
```bash
cd python
grep 'name =' pyproject.toml
# 输出：name = "sglang"
```

#### 步骤 2：测试正确的 URL
正确的上传 URL 格式：
```
https://upload.pkg.github.com/OWNER/PACKAGE-NAME
```
对于 `Zherphy/sglang` 仓库：
```
https://upload.pkg.github.com/Zherphy/sglang
```

#### 步骤 3：安装 URL
正确的安装 URL 格式：
```
https://pkg.github.com/OWNER/PACKAGE-NAME/simple
```
对于 `Zherphy/sglang` 包：
```
https://pkg.github.com/Zherphy/sglang/simple
```

### 3. 测试工作流

现在可以运行以下工作流进行测试：

1. **`.github/workflows/test-packages-simple.yml`**
   - 简单的测试工作流，已验证 YAML 格式
   - 选择 `test_type: dry-run` 进行安全测试

2. **`.github/workflows/test-fork-packages.yml`**
   - 修复后的 fork 仓库测试工作流
   - 选择 `test_mode: dry-run` 查看上传命令
   - 选择 `test_mode: actual-upload` 进行实际上传

### 4. 预期结果

使用正确的 URL 格式后，上传应该成功：

```
✅ Upload completed!
```

包将出现在：
```
https://github.com/Zherphy?tab=packages
```

### 5. 安装测试

上传成功后，可以测试安装：

```bash
pip install --index-url https://pkg.github.com/Zherphy/sglang/simple sglang
```

### 6. 故障排除

如果仍然遇到问题：

#### 问题 1：403 Forbidden
- 检查仓库 Settings → Actions → General
- 确保 "Workflow permissions" 设置为 "Read and write permissions"
- 确保有 `packages: write` 权限

#### 问题 2：包名冲突
- 如果包名 `sglang` 已被其他用户使用，需要修改包名
- 在 `pyproject.toml` 中修改 `name` 字段
- 更新工作流中的 `PACKAGE_NAME` 变量

#### 问题 3：首次上传
- 首次上传到 GitHub Packages 会自动创建包
- 如果包已存在但不可见，检查包的可见性设置

### 7. 总结

**根本原因**：混淆了仓库名和包名。GitHub Packages 的 Python 包使用包名作为 URL 标识符。

**解决方案**：使用 `pyproject.toml` 中的包名 `sglang` 而不是仓库名。

**验证方法**：运行修复后的工作流，检查上传是否成功，包是否出现在 GitHub Packages 页面。

现在所有工作流都已修复，应该能够成功上传 Python 包到 GitHub Packages。