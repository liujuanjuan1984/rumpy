# 案例: search_seeds.py


- [源码](./search_seeds.py)
- [实例](./doit.py)
- [实例产生的数据文件](./data/search_seeds_and_joined_data.json)


### 搜寻种子网络并自动加入：

- 根据你已经加入的种子网络，搜寻更多种子网络（通过别人分享的种子）
- 离开某些种子网络，可选，比如离开临时测试创建的种子网络，离开0区块的种子网络等；离开过的种子网络会自动标记为不值得加入，避免再次重复加入
- 自动加入搜寻到的、且值得加入的种子网络

### 如何使用？

请先修改 [`doit.py`](./doit.py) 中的参数，再运行。

```bash
python .\examples\search_seeds\doit.py
```