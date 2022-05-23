# 贡献代码指南

rumpy 欢迎任何人提交 issue 和 Pull Requests 贡献代码，在您创建 Pull Requests 之前，请注意以下事项。

## 开发环境搭建

tbd

## lint

tbd

## 静态类型检查

tbd

## 代码格式化

rumpy 使用 `isort` 及 [black](https://github.com/psf/black/) 自动格式化 Python 代码并在 CI 上进行代码格式检查，请在提交 PR 前进行代码格式化：

Install:

```bash
pip install black
pip install isort
```

Format:

```bash
isort .
black -l 80 -t py37 -t py38 -t py39 -t py310 .
black -l 120 -t py37 -t py38 -t py39 -t py310 .

```

## 自动化测试

在您完成对代码的改进和完善之后，请进行自动化测试，确保全部测试通过。

```bash
pytest tests
```

如果出现测试失败，请检查您修改过的代码或者检查测试用例的代码是否需要更新。

## Pull Requests

在您完成上述所有步骤后，您可以在 [rumpy](https://github.com/liujuanjuan1984/rumpy) 项目上提交您的 Pull Requests.

在所有环节完成之后，rumpy 项目成员会尽快 review 您的 Pull Requests，予以合并或和您进行进一步的讨论。

Thanks.

## 发布新版本

使用 [`bumpversion`](https://github.com/peritus/bumpversion)自动更新和维护项目版本号，配置文件见根目录 `.bumpversion.cfg` 文件。

对于主要版本：

1. 对于 bugfix 版本：`bumpversion patch`
2. 对于小 feature 版本：`bumpversion minor`
3. 大的 breaking change 版本：`bumpversion major`

大部分情况下使用 `bumpversion patch` 即可。

完成后将 master 分支代码改动和 `bumpversion` 自动产生的 tag 一起 push 到 GitHub 仓库中, 如:

```bash
git push origin master --tags
```
