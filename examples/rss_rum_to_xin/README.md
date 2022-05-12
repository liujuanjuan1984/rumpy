# signin_reward

## rss 订阅种子网络动态

rss bot 是一个基于 mixin messenger 的 bot

其功能是：

1、用户在 mixin mesenger 上与 bot 对话交互，发出订阅指令 [[source code]](./do_rss_blaze.py)

2、bot 从 rum 网络获取待转发的数据并转换为动态，根据用户的订阅要求，转发给用户 [[source code]](./do_rss.py)

3、bot 可以根据一定条件向用户空投 token [[source code]](./do_airdrop.py)

## airdrop 活跃奖励（空投 token）

想要实现的效果是：

每天（北京时间）在指定种子网络中至少有 x 条trx（发内容，点赞，回复，改头像，每个动作都算作一条trx），那么将收到至少 y 个 某 token 的空投。

如果是不同的账号绑定了同一个钱包地址，那么只会得到一次空投。

想要获得空投奖励，需要去 rum app 中点击头像编辑，绑定 mixin 钱包地址。

该服务的逻辑分两部分：  [[source code]](./rumit.py)

- 在 Rum 指定种子网络获取所有 pubkey 已绑定的 wallet 信息，指定日期每个 pubkey 的 trx 条数，筛选出有资格获得奖励的 wallet 名单
- 调用 mixin sdk，给这些有资格的 wallet 投放 token 奖励