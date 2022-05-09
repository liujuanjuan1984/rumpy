# signin_reward

签到奖励（空投 token）

想要实现的效果是：

每天（北京时间）在指定种子网络中至少有 x 条trx（发内容，点赞，回复，改头像，每个动作都算作一条trx），那么将收到至少 y 个 某 token 的空投。

如果是不同的账号绑定了同一个钱包地址，那么只会得到一次空投。

想要获得空投奖励，需要去 rum app 中点击头像编辑，绑定 mixin 钱包地址。

该 bot 的逻辑分两部分：

- 在 Rum 指定种子网络获取所有 pubkey 已绑定的 wallet 信息，指定日期每个 pubkey 的 trx 条数，筛选出有资格获得奖励的 wallet 名单
- 调用 mixin sdk，给这些有资格的 wallet 投放 token 奖励