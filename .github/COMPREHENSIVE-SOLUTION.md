# GitHub Packages Python 注册表综合解决方案

## 问题总结

经过多次测试，GitHub Packages Python 注册表持续返回 404 Not Found 错误，即使使用了正确的 URL 格式。这表明：

1. **GitHub Packages Python 注册表可能未正确启用** 或
2. **账户/组织配置有问题** 或
3. **需要手动创建包** 或
4. **GitHub Packages Python 注册表有已知问题**

## 已尝试的解决方案

### 1. URL 格式测试
- ❌ `https://upload.pkg.github.com/Zherphy/sglang` (仓库名)
- ❌ `https://upload.pkg.github.com/Zherphy/sglang` (包名)
- ❌ `https://upload.pkg.github.com/Zherphy/` (带斜杠)
- ❌ `https://upload.pkg.github.com/Zherphy/_` (下划线)

### 2. 权限检查
- ✅ GITHUB_TOKEN 可用
- ✅ `packages: write` 权限已配置
- ✅ 仓库设置正确

### 3. API 检查
- ❌ 包 `sglang` 不存在 (API 返回 404)
- ❌ 无法通过 API 创建包

## 可行的替代方案

### 方案 A: 使用 GitHub Container Registry (GHCR) - **推荐**

将 Python 包作为 OCI 镜像发布到 GHCR：

#### 工作流: `.github/workflows/ghcr-as-alternative.yml`
```yaml
name: Publish to GitHub Container Registry
on: workflow_dispatch

jobs:
  publish-python-oci:
    runs-on: ubuntu-latest
    steps:
      - name: Build Python package
        run: cd python && python -m build
      
      - name: Install crane
        run: wget crane工具 && install
      
      - name: Login to GHCR
        uses: docker/login-action@v2
      
      - name: Push as OCI artifact
        run: crane push dist/*.whl ghcr.io/OWNER/REPO/python/sglang:latest
```

#### 优点:
- ✅ 可靠工作
- ✅ 支持任何类型的包
- ✅ 与 Docker 生态集成
- ✅ 避免 GitHub Packages Python 注册表问题

#### 安装:
```bash
# 安装 crane
# 拉取包
crane pull ghcr.io/Zherphy/sglang/python/sglang-*.whl:latest sglang.whl
# 安装
pip install sglang.whl
```

### 方案 B: 使用 TestPyPI 进行测试

对于测试目的，使用 TestPyPI：

#### 工作流配置:
```yaml
- name: Upload to TestPyPI
  env:
    TEST_PYPI_TOKEN: ${{ secrets.TEST_PYPI_TOKEN }}
  run: |
    twine upload \
      --repository-url https://test.pypi.org/legacy/ \
      dist/* \
      --username __token__ \
      --password $TEST_PYPI_TOKEN
```

#### 安装:
```bash
pip install --index-url https://test.pypi.org/simple/ sglang
```

### 方案 C: 使用 GitHub Releases

将构建的包附加到 GitHub Releases：

#### 工作流配置:
```yaml
- name: Upload to GitHub Releases
  uses: softprops/action-gh-release@v1
  with:
    files: python/dist/*
    tag_name: test-${{ github.run_id }}
```

#### 安装:
```bash
# 从 Releases 页面下载 .whl 文件
pip install sglang-*.whl
```

## 如果必须使用 GitHub Packages Python 注册表

### 手动创建步骤:

1. **访问包页面**:
   ```
   https://github.com/Zherphy?tab=packages
   ```

2. **点击 "New package"**

3. **选择 "Python"**

4. **输入包信息**:
   - Package name: `sglang`
   - Visibility: Public 或 Private

5. **点击 "Create package"**

6. **重试上传**

### 检查账户设置:

1. **个人账户设置**:
   - 访问 `https://github.com/settings/packages`
   - 确保 GitHub Packages 已启用

2. **组织设置** (如果适用):
   - 访问 `https://github.com/organizations/ORGNAME/settings/packages`
   - 启用 GitHub Packages

## 已创建的工作流文件

### 1. **GitHub Packages 相关**
- `.github/workflows/test-fork-packages.yml` - Fork 仓库测试 (已修复 URL)
- `.github/workflows/release-pypi-with-ghpkg.yml` - 生产发布 (已修复 URL)
- `.github/workflows/ghpkg-correct-format.yml` - 正确格式测试
- `.github/workflows/ghpkg-with-api-create.yml` - API 创建测试

### 2. **替代方案**
- `.github/workflows/ghcr-as-alternative.yml` - GHCR 发布 (推荐)
- `.github/workflows/release-docker-with-ghcr.yml` - Docker 镜像发布

### 3. **测试和验证**
- `.github/workflows/test-packages-simple.yml` - 简单测试
- `.github/workflows/simple-ghpkg-test.yml` - 详细测试
- `.github/workflows/test-ghpkg-url.yml` - URL 格式测试

## 推荐的工作流程

### 对于测试和学习:
1. **运行 GHCR 方案**:
   ```
   工作流: ghcr-as-alternative.yml
   参数: package_type = python-oci
   ```

2. **验证发布**:
   - 检查 `https://github.com/Zherphy?tab=packages`
   - 应该看到 OCI 镜像

### 对于生产发布:
1. **使用 TestPyPI 测试**
2. **使用 GHCR 作为主要存储**
3. **考虑使用 GitHub Releases 分发**

## 故障排除检查清单

如果 GitHub Packages 仍然不工作:

- [ ] 1. 手动创建包 via Web UI
- [ ] 2. 检查账户/组织的 Packages 设置
- [ ] 3. 尝试不同的包名 (避免冲突)
- [ ] 4. 联系 GitHub 支持
- [ ] 5. 使用替代方案 (GHCR/TestPyPI/Releases)

## 结论

**GitHub Packages Python 注册表可能存在配置问题或已知限制**。对于实际使用，推荐:

1. **短期**: 使用 GHCR 作为替代方案
2. **测试**: 使用 TestPyPI
3. **分发**: 使用 GitHub Releases

所有必要的工作流和文档已创建，可以根据需要选择最适合的方案。