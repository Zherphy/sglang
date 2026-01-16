# 在 Fork 仓库中测试 GitHub Packages 发布指南

本文档指导您在 `Zherphy/sglang` fork 仓库中测试 GitHub Packages 发布功能。

## 准备工作

### 1. 检查仓库设置
1. 访问 `https://github.com/Zherphy/sglang/settings/actions`
2. 确保 "Workflow permissions" 设置为：
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**
3. 点击 "Save" 保存设置

### 2. 了解可用的工作流
已为您创建了以下测试工作流：

| 工作流文件 | 用途 | 推荐测试顺序 |
|-----------|------|-------------|
| `test-packages-config.yml` | 配置检查，不执行构建 | 第一步 |
| `test-fork-packages.yml` | 完整的构建和上传测试 | 第二步 |
| `release-pypi-with-ghpkg.yml` | 实际发布工作流（修改版） | 第三步 |

## 测试步骤

### 第一步：配置检查
**工作流**: `Test GitHub Packages Configuration`

1. 访问 `https://github.com/Zherphy/sglang/actions`
2. 在左侧找到 "Test GitHub Packages Configuration"
3. 点击 "Run workflow"
4. 选择参数：
   - `package_type`: `all` (测试所有类型)
   - `dry_run`: `true` (默认，只检查不执行)
5. 点击 "Run workflow"

**预期结果**：
- 工作流成功运行
- 输出显示权限检查通过
- 显示可用的包配置信息

### 第二步：构建测试
**工作流**: `Test Package Publishing in Fork Repository`

1. 在 Actions 页面找到 "Test Package Publishing in Fork Repository"
2. 点击 "Run workflow"
3. 选择参数：
   - `package_type`: `python` (先测试 Python 包)
   - `test_mode`: `build-only` (只构建，不上传)
4. 点击 "Run workflow"

**预期结果**：
- Python 包构建成功
- 显示构建的 `.whl` 和 `.tar.gz` 文件
- 不执行上传操作

### 第三步：模拟上传测试
1. 再次运行 "Test Package Publishing in Fork Repository"
2. 选择参数：
   - `package_type`: `python`
   - `test_mode`: `dry-run` (显示上传命令)
3. 点击 "Run workflow"

**预期结果**：
- 显示 PyPI 上传命令
- 显示 GitHub Packages 上传命令
- 验证配置正确性

### 第四步：实际发布测试（可选）
**注意**: 这会在您的 GitHub Packages 中创建实际的包

1. 确保您有足够的权限（个人账户通常有）
2. 运行 "Test Package Publishing in Fork Repository"
3. 选择参数：
   - `package_type`: `python`
   - `test_mode`: `actual-upload`
4. 点击 "Run workflow"

**预期结果**：
- 包实际上传到 `https://ghcr.io/Zherphy/sglang/python`
- 可以在 GitHub Packages 页面查看
- 可以测试安装

## 验证发布结果

### 1. 检查 GitHub Packages
1. 访问 `https://github.com/Zherphy/sglang/packages`
2. 应该能看到上传的 Python 包
3. 包名称为 `sglang`，版本为构建时的版本

### 2. 测试安装
```bash
# 从您的 GitHub Packages 安装
pip install --index-url https://ghcr.io/Zherphy/sglang/python sglang

# 或临时测试
pip install --index-url https://ghcr.io/Zherphy/sglang/python --extra-index-url https://pypi.org/simple sglang
```

### 3. 检查 Docker 镜像（如果测试了 Docker）
```bash
# 查看可用的镜像标签
curl -H "Authorization: Bearer $(echo -n $GITHUB_TOKEN | base64)" \
  https://ghcr.io/v2/Zherphy/sglang/tags/list

# 拉取测试镜像
docker pull ghcr.io/Zherphy/sglang:test-{run_id}
```

## 故障排除

### 问题 1: 权限不足
```
Error: Resource not accessible by integration
```
**解决方案**：
1. 检查仓库 Settings → Actions → General
2. 确保 "Workflow permissions" 设置为 "Read and write permissions"
3. 重新运行工作流

### 问题 2: 包构建失败
```
Error: No module named 'build'
```
**解决方案**：
- 工作流会自动安装构建工具
- 检查 Python 目录结构是否正确
- 确保 `python/` 目录存在且包含 `pyproject.toml`

### 问题 3: 上传失败
```
Error: 401 Unauthorized
```
**解决方案**：
1. 确保 `GITHUB_TOKEN` 有 `packages:write` 权限
2. 检查仓库是否启用了 GitHub Packages
3. 个人账户通常有权限，组织账户可能需要额外配置

### 问题 4: 找不到工作流
工作流文件不存在或未显示在 Actions 页面
**解决方案**：
1. 确保文件已提交到 `.github/workflows/` 目录
2. 推送到仓库后等待几分钟
3. 刷新 Actions 页面

## 实际应用

### 1. 修改现有发布工作流
当测试通过后，可以修改现有的发布工作流：

**修改 `release-pypi.yml`**：
```yaml
# 添加 permissions
permissions:
  contents: read
  packages: write

# 在现有上传步骤后添加 GitHub Packages 上传
- name: Upload to GitHub Packages
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    cd python
    pip install twine
    python -m twine upload \
      --repository-url https://ghcr.io/${{ github.repository }}/python \
      dist/* \
      --verbose \
      --username ${{ github.actor }} \
      --password $GITHUB_TOKEN
```

### 2. 创建标签触发发布
测试完成后，可以通过创建标签触发完整发布：

```bash
# 创建测试标签
git tag v0.0.1-test
git push origin v0.0.1-test
```

### 3. 监控发布结果
1. 访问 Actions 页面查看工作流运行状态
2. 检查 GitHub Packages 页面确认包已发布
3. 测试从不同环境安装包

## 清理测试数据

### 1. 删除测试包
1. 访问 `https://github.com/Zherphy/sglang/packages`
2. 找到测试包
3. 点击包名称 → Package settings → Delete this package

### 2. 删除测试标签
```bash
# 本地删除
git tag -d v0.0.1-test

# 远程删除
git push origin --delete v0.0.1-test
```

### 3. 清理工作流文件
测试完成后，可以删除测试专用的工作流文件：
- `test-fork-packages.yml`
- `test-packages-config.yml`
- `example-packages.yml`

## 下一步计划

1. **完成测试**：按照上述步骤完成所有测试
2. **集成到主工作流**：将 GitHub Packages 支持添加到现有发布工作流
3. **文档更新**：更新项目 README 说明新的安装方式
4. **自动化优化**：优化工作流，提高发布效率

## 获取帮助

如果遇到问题：
1. 查看工作流运行日志获取详细错误信息
2. 参考 GitHub Packages 文档：https://docs.github.com/en/packages
3. 检查 GitHub Actions 文档：https://docs.github.com/en/actions
4. 在项目 Issues 中提出问题

---

*最后更新：2026-01-16*
*文档版本：1.0*
