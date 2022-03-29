# smart_crypto
okx欧易交易所量化标准等差网格交易(永续合约)

使用:
1.python3.8+
2.pip install -r requestments.txt
在config.json里填入okx交易所的apikey,secret,password,其中real表示实盘，simulate表示模拟盘，需要分别申请并注意开通永续合约交易，目前只支持一个账户
在stragy目录下grid_config.json里配置
其中pair_id表示交易对ID，目前只支持SWAP交易类型（现货网格交易官网有提供)
grid_type 填 arithmetic 目前只支持arithmetic
value填网格等差，is_start_price_ratio表示value是否是起始价格百分比，0表示绝对数值，1表示起始价格的百分比数值
grid_count表示单边网格数量，总网格数是grid_count*2
start_price是起始价格，0表示当前市价
1buy_volume_per_order 到达网格买入触发价格时每单买入数量
sell_volume_per_order 到达网格卖出触发价格时每单卖出数量
leverage 杠杆倍数设置，默认是当前交易所设置

启动：
python main.py

后续将开发多币种并发，等比网格策略、组合网格策略及嵌套网格策略，以及回测模块和统计模块

加密货币及量化开发爱好者可以联系邮箱 501745@qq.com
