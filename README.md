# rumpy

[QuoRum](https://github.com/rumsystem/quorum) 第三方 Python SDK。

个人水平有限，欢迎参与代码贡献。持续开发迭代中。

官方教程： https://github.com/rumsystem/quorum/blob/main/Tutorial.md

官网 API文档：https://github.com/rumsystem/quorum 

## 安装使用

目前 `rumpy` 没有采用 pip 等发布，所以不支持 `pip install rumpy`。

如果您有需要，可以 clone 到本地，比如，在 `/work-space>` 下执行 ```git clone https://github.com/liujuanjuan1984/rumpy.git```。

完成后，`cd rumpy` 后所在目录/路径，请添加到 `PYTHONPATH` 环境变量中。

### 检查是否设置成功

检查 rumpy 的本地路径是否在下述输出结果中。

```py
import sys
print(sys.path)
```

### 导入方式：

```py

from rumpy import RumClient

```

## 安装依赖

#### rumpy 的依赖

```sh
pip install -r requirements.txt
```

#### examples 的依赖

```sh
pip install -r requirements_examples.txt
```

以及，安装 officepy 以支持 JsonFile、Dir 等自定义方法：

- `officepy` : [https://github.com/liujuanjuan1984/officepy](https://github.com/liujuanjuan1984/officepy.git)


## 一些案例

- [hellorum 你好 RUM](./examples/hellorum)：新手友好，展示如何自动创建组，自动发布内容。
- [whosays 重点关注](./examples/whosays)：想要重点关注某人或某些人在各个组的动态并把动态归拢到一起方便查阅？这个工具适合你。
- [leave groups 批量清理种子网络](./examples/leave_groups)：不小心创建了大量测试组？想要清理同步失败的组？这个工具适合你。
- [search user 搜寻用户](./examples/search_user)：在你加入的所有种子网络中搜寻当前和曾经的昵称包含某个片段的用户，返回它们所在的 group_id 和 pubkey。
- [search seeds 搜寻种子](./examples/search_seeds)：根据你已经加入的种子网络，自动搜寻并加入更多公开的种子网络，还可以把这些种子进一步扩散出去。想要自动探索 Rum，这个工具适合你。
- [group statistics 种子网络数据概况](./examples/group_statistics)：统计指定组的数据概况，并生成图文发布，或保存到文件中。
- [export data 批量数据导出](./examples/export_data)：你所加入的 所有 groups 的数据其实已经保存在你的本地。这个工具帮你把数据导出为排版良好的 markdown 文件及图片。

其它案例：

- [coin price 币价](https://github.com/liujuanjuan1984/coin_price) bot: get price from coinmarketcap and post to quorum groups.
- [retweet 转发工具](https://github.com/liujuanjuan1984/retweet) bot: retweet weibo/twitter to rum groups
- [seedstore 种子商店](https://github.com/liujuanjuan1984/seedstore)：发现和分享更多种子~
- [sudoku 数独游戏](https://github.com/liujuanjuan1984/rum_sudoku)：玩数独游戏，把游戏结果推送到 rum group 上链存储。
- [todolist 待办清单](https://github.com/liujuanjuan1984/todolist)：只能把 Rum 当微博/博客用吗？Rum 的想象空间很大，待办清单这个雏形可以给你带来启发。

## 问题反馈/需求建议/开发计划

前往 [GitHub issues](https://github.com/liujuanjuan1984/rumpy/issues)

## License

This work is released under the `GPL3.0` license. A copy of the license is provided in the [LICENSE](./LICENSE) file.
