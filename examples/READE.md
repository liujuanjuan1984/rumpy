# 案例大全


- [hellorum 你好 RUM](./hellorum)：新手友好，展示如何自动创建组，自动发布内容。
- [whosays 重点关注](./whosays)：想要重点关注某人或某些人在各个组的动态并把动态归拢到一起方便查阅？这个工具适合你。
- [leave groups 批量清理种子网络](./leave_groups)：不小心创建了大量测试组？想要清理同步失败的组？这个工具适合你。
- [search user 搜寻用户](./search_user)：在你加入的所有种子网络中搜寻当前和曾经的昵称包含某个片段的用户，返回它们所在的 group_id 和 pubkey。
- [search seeds 搜寻种子](./search_seeds)：根据你已经加入的种子网络，自动搜寻并加入更多公开的种子网络，还可以把这些种子进一步扩散出去。想要自动探索 Rum，这个工具适合你。
- [group statistics 种子网络数据概况](./group_statistics)：统计指定组的数据概况，并生成图文发布，或保存到文件中。
- [export data 批量数据导出](./export_data)：你所加入的 所有 groups 的数据其实已经保存在你的本地。这个工具帮你把数据导出为排版良好的 markdown 文件及图片。
- [bigfile 大文件上传和下载](./bigfile)：大文件上传及下载；展示了 电子书 epub、图片 jpeg、视频 mp4 文件三种类型。超出大小的文件，将拆分多个trx上链，并由包含 fileinfo trx 来描述这种拆分。客户端同步到 trxs 后，可以把这些文件块重新拼成文件，并渲染给用户查看。

其它案例：

- [coin price 币价](https://github.com/liujuanjuan1984/coin_price) bot: get price from coinmarketcap and post to quorum groups.
- [retweet 转发工具](https://github.com/liujuanjuan1984/retweet) bot: retweet weibo/twitter to rum groups
- [seedstore 种子商店](https://github.com/liujuanjuan1984/seedstore)：发现和分享更多种子~
- [sudoku 数独游戏](https://github.com/liujuanjuan1984/rum_sudoku)：玩数独游戏，把游戏结果推送到 rum group 上链存储。
- [todolist 待办清单](https://github.com/liujuanjuan1984/todolist)：只能把 Rum 当微博/博客用吗？Rum 的想象空间很大，待办清单这个雏形可以给你带来启发。

部分案例需安装 officy 以支持 JsonFile、Dir 等自定义方法：

- ```pip install officy```
- 源码 [https://github.com/liujuanjuan1984/officy](https://github.com/liujuanjuan1984/officy.git)