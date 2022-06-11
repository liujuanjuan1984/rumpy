# export_data.py

导出你在 Rum 所发布的数据

### 如何使用？


```bash
from rumpy.bots import ExportData
from rumpy import FullNode

full = FullNode()
bot = ExportData(full)
datadir = r"D:\export_data_test"
group_id = "4e784292-6a65-471e-9f80-e91202e3358c"
# bot.save_to_dir(group_id, datadir, "md")
bot.save_to_dir(group_id, datadir, "html")

```
