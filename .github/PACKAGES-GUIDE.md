# SGLang 项目 GitHub Packages 配置指南

本文档提供了针对 sglang 项目的 GitHub Actions 和 Packages 配置指南，帮助您实现包发布到 GitHub Packages。

## 目录

1. [项目现状分析](#项目现状分析)
2. [GitHub Packages 简介](#github-packages-简介)
3. [配置步骤](#配置步骤)
4. [Docker 镜像发布配置](#docker-镜像发布配置)
5. [Python 包发布配置](#python-包发布配置)
6. [测试和验证](#测试和验证)
7. [故障排除](#故障排除)
8. [最佳实践](#最佳实践)

## 项目现状分析

### 现有工作流
sglang 项目已有完善的工作流系统，包括：

- **Docker 镜像发布**：`release-docker.yml` - 发布到 Docker Hub (lmsysorg/sglang)
- **Python 包发布**：`release-pypi.yml` - 发布到 PyPI
- **测试工作流**：多平台测试（AMD、Intel、NPU、NVIDIA）
- **自动化工作流**：代码格式化、版本管理、文档发布

### 当前包发布目标
- Docker Hub: `lmsysorg/sglang`
- PyPI: `sglang` Python 包

### 需要添加的目标
- GitHub Container Registry: `ghcr.io/sgl-project/sglang`
- GitHub Packages: Python 包仓库

## GitHub Packages 简介

GitHub Packages 是 GitHub 提供的包托管服务，支持：

1. **GitHub Container Registry (ghcr.io)** - Docker/OCI 容器镜像
2. **Python 包仓库** - Python 包 (PyPI 兼容)
3. **npm 包仓库** - Node.js 包
4. **其他**：Maven、NuGet、RubyGems 等

### 优势
- 与 GitHub 仓库深度集成
- 使用相同的权限和访问控制
- 无需额外认证（使用 `GITHUB_TOKEN`）
- 与 GitHub Actions 无缝协作

## 配置步骤

### 1. 仓库设置检查

确保以下设置已正确配置：

1. **GitHub Packages 功能**：默认启用，无需额外配置
2. **工作流权限**：
   - 进入仓库 Settings → Actions → General
   - 设置 "Workflow permissions" 为 "Read and write permissions"
   - 勾选 "Allow GitHub Actions to create and approve pull requests"
3. **环境配置**（可选）：
   - 在 Settings → Environments 中创建 "production" 环境
   - 配置部署保护规则

### 2. 工作流文件修改

有两种方式实现：

**方式 A：修改现有工作流**（推荐）
- 在现有 `release-docker.yml` 和 `release-pypi.yml` 中添加 GitHub Packages 支持
- 保持现有功能不变，增加新目标

**方式 B：创建新工作流**
- 创建专门用于 GitHub Packages 的新工作流文件
- 避免影响现有发布流程

## Docker 镜像发布配置

### 修改 `release-docker.yml`

#### 1. 添加权限配置
在每个作业的顶部添加：
```yaml
permissions:
  contents: read
  packages: write  # 关键：允许写入 packages
```

#### 2. 添加 GitHub Container Registry 登录
在 "Login to Docker Hub" 步骤后添加：
```yaml
- name: Login to GitHub Container Registry
  uses: docker/login-action@v2
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

#### 3. 修改构建命令添加 ghcr.io 标签
在现有的 `docker buildx build` 命令中，添加额外的 `-t` 参数：
```bash
-t ghcr.io/sgl-project/sglang:${tag}
```

示例：
```bash
docker buildx build \
  --target framework \
  --platform linux/amd64 \
  --push \
  -f docker/Dockerfile \
  --build-arg CUDA_VERSION=${{ matrix.variant.cuda_version }} \
  --build-arg BUILD_TYPE=${{ matrix.variant.build_type }} \
  --build-arg GRACE_BLACKWELL=${{ matrix.variant.grace_blackwell }} \
  --build-arg INSTALL_FLASHINFER_JIT_CACHE=1 \
  --build-arg SGL_VERSION=${version} \
  -t lmsysorg/sglang:${tag} \
  -t ghcr.io/sgl-project/sglang:${tag} \  # 新增
  --no-cache \
  .
```

#### 4. 添加 ghcr.io 的多架构清单
在 `create-manifests` 作业中，添加 ghcr.io 的清单创建命令。

### 参考文件
已创建完整示例：`release-docker-with-ghcr.yml`

## Python 包发布配置

### 修改 `release-pypi.yml`

#### 1. 添加权限配置
在作业顶部添加：
```yaml
permissions:
  contents: read
  packages: write
```

#### 2. 添加发布到 GitHub Packages 的步骤
在现有的 "Upload to pypi" 步骤后添加：
```yaml
- name: Publish to GitHub Packages
  env:
    TWINE_USERNAME: ${{ github.actor }}
    TWINE_PASSWORD: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python3 -m twine upload \
      --repository-url https://ghcr.io/${{ github.repository }}/python \
      dist/* \
      --verbose
```

#### 3. 完整示例步骤
```yaml
- name: Upload to pypi
  run: |
    cd python
    cp ../README.md ../LICENSE .
    pip install build wheel setuptools setuptools-scm
    python3 -m build
    pip install twine
    # 发布到 PyPI
    python3 -m twine upload dist/* -u __token__ -p ${{ secrets.PYPI_TOKEN }}
    # 发布到 GitHub Packages
    python3 -m twine upload \
      --repository-url https://ghcr.io/${{ github.repository }}/python \
      dist/* \
      --verbose
```

## 测试和验证

### 1. 测试工作流
1. 提交修改到仓库
2. 在 GitHub 仓库页面进入 "Actions" 标签页
3. 选择对应的工作流
4. 点击 "Run workflow" 手动触发
5. 监控执行状态和日志

### 2. 验证发布结果

#### Docker 镜像验证
```bash
# 查看可用标签
curl -H "Authorization: Bearer $(echo -n $GITHUB_TOKEN | base64)" \
  https://ghcr.io/v2/sgl-project/sglang/tags/list

# 拉取测试
docker pull ghcr.io/sgl-project/sglang:latest
```

#### Python 包验证
```bash
# 查看包信息
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/users/sgl-project/packages/pypi/sglang

# 安装测试
pip install --index-url https://ghcr.io/sgl-project/sglang/python sglang
```

### 3. 网页验证
- Docker 镜像：访问 `https://ghcr.io/sgl-project/sglang`
- Python 包：访问 `https://github.com/sgl-project/sglang/packages`

## 故障排除

### 常见问题 1：权限不足
```
Error: denied: permission_denied
```
**解决方案**：
- 检查工作流中的 `permissions:` 设置
- 确保包含 `packages: write`
- 验证仓库的 Actions 设置允许写入权限

### 常见问题 2：认证失败
```
Error: 401 Unauthorized
```
**解决方案**：
- 确保使用 `secrets.GITHUB_TOKEN` 而非个人访问令牌
- 验证令牌具有 `write:packages` 权限
- 检查仓库是否属于组织，需要组织级权限

### 常见问题 3：包不存在
```
Error: 404 Not Found
```
**解决方案**：
- 确认包名称和路径正确
- 检查包是否已成功发布
- 验证仓库名称大小写（GitHub 区分大小写）

### 常见问题 4：构建失败
```
Error: Docker build failed
```
**解决方案**：
- 检查 Dockerfile 路径是否正确
- 验证构建参数是否完整
- 查看详细构建日志

## 最佳实践

### 1. 渐进式实施
- 先测试单个包类型（如 Docker）
- 验证通过后再添加其他包类型
- 使用 `workflow_dispatch` 手动测试

### 2. 版本管理
- 使用语义化版本标签触发发布
- 保持 Docker 镜像和 Python 包版本同步
- 为预发布版本使用 `-rc`、`-dev` 后缀

### 3. 安全考虑
- 使用最小权限原则
- 定期轮换访问令牌
- 启用环境保护规则
- 审核工作流运行记录

### 4. 监控和维护
- 设置工作流失败通知
- 定期清理旧版本包
- 监控包下载和使用统计
- 更新文档说明包使用方式

### 5. 文档更新
更新项目文档，添加 GitHub Packages 使用说明：

#### README.md 添加：
```markdown
## 安装方式

### Docker 镜像
```bash
# 从 Docker Hub 安装
docker pull lmsysorg/sglang:latest

# 从 GitHub Container Registry 安装
docker pull ghcr.io/sgl-project/sglang:latest
```

### Python 包
```bash
# 从 PyPI 安装
pip install sglang

# 从 GitHub Packages 安装
pip install --index-url https://ghcr.io/sgl-project/sglang/python sglang
```
```

## 下一步计划

1. **立即实施**：
   - 修改 `release-docker.yml` 添加 ghcr.io 支持
   - 测试 Docker 镜像发布到 GitHub Container Registry

2. **中期计划**：
   - 修改 `release-pypi.yml` 添加 GitHub Packages 支持
   - 测试 Python 包发布到 GitHub Packages

3. **长期优化**：
   - 创建统一的多注册表发布工作流
   - 添加自动化测试和验证
   - 优化包管理和版本控制

## 参考资源

1. [GitHub Packages 官方文档](https://docs.github.com/en/packages)
2. [GitHub Container Registry 文档](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
3. [GitHub Actions 工作流语法](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
4. [Docker Buildx 多架构构建](https://docs.docker.com/build/building/multi-platform/)

## 支持与反馈

如有问题或需要进一步协助，请：
1. 查看工作流运行日志
2. 参考 GitHub Actions 文档
3. 在项目 Issues 中提出问题
4. 联系项目维护团队

---

*最后更新：2026-01-15*
*文档版本：1.0*