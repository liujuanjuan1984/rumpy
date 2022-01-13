# 案例：whosays.py

筛选某人在多个种子网络的动态，并转发到自定义的种子网络。


- [源码](./whosays.py)
- [实例](./doit.py)
- [实例产生的数据文件](./huoju_says.json)

### 如何使用？

请先修改 `doit.py` 中的参数，再运行。

```bash
python .\examples\whosays\doit.py
```


### 实现细节:

- 参数：此人在种子网络的多个 pubkey 所构成的参数

```python
{
    "group_id1":["pubkey1","pubkey2"],
    "group_id2":["pubkey3","pubkey4"],
}
```

- 从种子网络获取所有 trxs ，并筛选此人发布的 trxs

    通过 group 的 content 方法来获取所有 trxs

    通过 trx 的 publisher 字段来识别是否由此人发布

- 对 trxs 进行分类，生成相应的文本/复制相应图片，引用相关 trx（比如点赞给，评论给 trx），并标记种子网络的来源（seed of group）

    通过 group 的 content 方法来获取所有 trxs 然后再筛选出指定 trx 的数据

    trx 的构成虽然较多变，但组合依然较为固定，可自定义生成相应信息
    
    通过 group 的 seed 方法来获取 seed（依赖 quorum 最新版本）

- 把这些处理过的动态，发布到指定 group （默认 timeline 模板）

    通过 group 的 send_note 方法

- 本案例采用 json 数据文件来收录动态及发布进展


### 备注：

- 种子网络（seednet）是产品层面的说法，在代码层面称之为 group，每个 group 都有一条 group chain（block 顺序衔接而成），每个 block 中至少有一个 trx 

