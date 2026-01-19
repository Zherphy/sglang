# GitHub Packages 解决方案指南

## 问题分析

在测试 GitHub Packages 功能时，遇到了以下问题：

1. **404 Not Found 错误**：尝试上传 Python 包到 GitHub Packages 时返回 404 错误
2. **URL 格式问题**：使用了不正确的 URL 格式
3. **权限问题**：fork 仓库中的权限配置可能不正确

## 根本原因

经过分析，发现问题的根本原因是：

1. **错误的 URL 格式**：使用了 `github.event.repository.name` 变量，该变量在某些情况下可能不正确
2. **GitHub Packages 仓库不存在**：首次上传时，GitHub Packages 仓库需要被创建
3. **权限配置**：需要正确的 `packages: write` 权限

## 解决方案

### 1. 正确的 URL 格式

**Python 包上传 URL**：
```
https://upload.pkg.github.com/OWNER/REPO
```

**Python 包安装 URL**：
```
https://pkg.github.com/OWNER/REPO/simple
```

**Docker 镜像上传 URL**：
```
ghcr.io/OWNER/REPO:tag
```

### 2. 修复的工作流文件

已修复以下工作流文件：

1. **`.github/workflows/release-pypi-with-ghpkg.yml`**：
   - 修复了 URL 格式，使用正确的仓库名称提取
   - 添加了详细的日志输出

2. **`.github/workflows/test-fork-packages.yml`**：
   - 修复了 URL 格式
   - 改进了错误处理和日志

3. **新增测试工作流**：
   - `.github/workflows/simple-ghpkg-test.yml`：简单的 GitHub Packages 测试
   - `.github/workflows/test-ghpkg-url.yml`：URL 格式测试

### 3. 替代方案

如果 GitHub Packages 仍然无法正常工作，可以考虑以下替代方案：

#### 方案 A：使用 GitHub Container Registry (GHCR) 替代

对于 Python 包，可以使用 GHCR 作为替代方案：

```yaml
# 在 workflow 中使用
- name: Upload to GHCR as OCI artifact
  run: |
    # 将 Python 包打包为 OCI 镜像
    crane push dist/*.whl ghcr.io/${{ github.repository }}/sglang:latest
```

#### 方案 B：使用 TestPyPI 进行测试

在 fork 仓库中，可以使用 TestPyPI 进行测试：

```yaml
- name: Upload to TestPyPI
  run: |
    twine upload \
      --repository-url https://test.pypi.org/legacy/ \
      dist/* \
      --username __token__ \
      --password $TEST_PYPI_TOKEN
```

#### 方案 C：使用 GitHub Releases 作为包存储

将构建的包作为 GitHub Releases 的附件：

```yaml
- name: Upload to GitHub Releases
  uses: softprops/action-gh-release@v1
  with:
    files: python/dist/*
    tag_name: test-${{ github.run_id }}
```

### 4. 分步配置指南

#### 步骤 1：检查仓库设置

1. 进入仓库 Settings → Actions → General
2. 确保 "Workflow permissions" 设置为 "Read and write permissions"
3. 勾选 "Allow GitHub Actions to create and approve pull requests"

#### 步骤 2：测试配置

1. 运行 `.github/workflows/simple-ghpkg-test.yml` 工作流
2. 选择 `test_upload: false` 进行 dry-run 测试
3. 检查日志中的 URL 格式是否正确

#### 步骤 3：实际测试

1. 运行 `.github/workflows/test-fork-packages.yml` 工作流
2. 选择 `test_mode: dry-run` 查看上传命令
3. 如果一切正常，选择 `test_mode: actual-upload` 进行实际上传

#### 步骤 4：验证上传结果

1. 访问 `https://github.com/USERNAME?tab=packages` 查看上传的包
2. 尝试安装测试包：
   ```bash
   pip install --index-url https://pkg.github.com/USERNAME/REPO/simple test-sglang-pkg
   ```

### 5. 故障排除

#### 问题 1：404 Not Found

**原因**：包仓库不存在或 URL 格式错误
**解决方案**：
1. 检查 URL 格式是否正确
2. 首次上传会自动创建包仓库
3. 确保有 `packages: write` 权限

#### 问题 2：403 Forbidden

**原因**：权限不足
**解决方案**：
1. 检查工作流权限设置
2. 确保 GITHUB_TOKEN 有 packages:write 权限
3. 检查仓库是否启用了 GitHub Packages

#### 问题 3：405 Method Not Allowed

**原因**：使用了错误的 URL（如将 Python 包上传到 ghcr.io）
**解决方案**：
1. Python 包使用 `upload.pkg.github.com`
2. Docker 镜像使用 `ghcr.io`

### 6. 最佳实践

1. **使用环境变量**：在敏感操作中使用环境变量
2. **添加条件判断**：根据仓库类型和触发方式决定是否上传
3. **详细的日志**：添加详细的日志输出以便调试
4. **测试模式**：提供测试模式，避免意外上传
5. **权限最小化**：只授予必要的权限

### 7. 示例配置

#### 完整的 Python 包发布工作流

```yaml
name: Release Python Package

on:
  push:
    tags:
      - 'v[0-9]+.*'

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
      
      - name: Build package
        run: |
          cd python
          python -m build
      
      - name: Upload to PyPI
        env:
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: |
          cd python
          twine upload dist/* -u __token__ -p $PYPI_TOKEN
      
      - name: Upload to GitHub Packages
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          cd python
          REPO_NAME="${GITHUB_REPOSITORY##*/}"
          twine upload \
            --repository-url "https://upload.pkg.github.com/${{ github.repository_owner }}/$REPO_NAME" \
            dist/* \
            --username "${{ github.actor }}" \
            --password "$GITHUB_TOKEN"
```

### 8. 总结

通过以上解决方案，你应该能够：

1. ✅ 正确配置 GitHub Packages 工作流
2. ✅ 修复 URL 格式问题
3. ✅ 解决权限配置问题
4. ✅ 在 fork 仓库中测试包发布功能
5. ✅ 了解替代方案和故障排除方法

如果仍然遇到问题，请检查工作流日志中的详细错误信息，并根据错误信息调整配置。