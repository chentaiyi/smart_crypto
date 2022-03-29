import config_file
import okex.Account_api as Account
import okex.Funding_api as Funding
import okex.Market_api as Market
import okex.Public_api as Public
import okex.Trade_api as Trade
import okex.subAccount_api as SubAccount
import okex.status_api as Status
import okex.websocket_api as WebSocketAPI
import json


class ExangeFactroy:
    @staticmethod
    def getExange(exange_id,auth_info,is_simulate):
        if exange_id=="okex":
            return OkxExange(auth_info,is_simulate)



class OkxExange:
    def __init__(self,auth_info,is_simulate=False):
        self.exange_id="okex"
        flag="0"
        if is_simulate:
            flag="1"
        api_key = auth_info["apikey"]
        secret_key = auth_info["secret"]
        passphrase = auth_info["password"]
        self.accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
        self.fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
        self.marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, flag)
        self.publicAPI = Public.PublicAPI(api_key, secret_key, passphrase, False, flag)
        self.tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
        self.subAccountAPI = SubAccount.SubAccountAPI(api_key, secret_key, passphrase, False, flag)
        self.Status = Status.StatusAPI(api_key, secret_key, passphrase, False, flag)

    #查询余额 ccy 币种
    def fetchBalance(self,ccy=None):
        return self.accountAPI.get_account(ccy=ccy)

    # 订单 pair_id 交易对ID 必填 clOrdId 自定义订单ID，非必填
    # side buy 买入 sell 卖出 必填
    # ord_type 订单类型 market：市价单 limit：限价单 post_only：只做maker单  fok：全部成交或立即取消  ioc：立即成交并取消剩余 必填
    # td_mode isolated 逐仓 cross 全仓 必填
    # amount 委托数量 必填
    # price 委托价格 限价单必填
    # pos_side 方向 long表示做多，short表示做空，必填
    # tp_trigger_px 止盈触发价，如果填写此参数 必须填写 止盈委托价
    # tp_ord_px 止盈委托价，如果填写此参数，必须填写 止盈触发价 委托价格为-1时，执行市价止盈
    # sl_trigger_px_type 止损触发价，如果填写此参数，必须填写 止损委托价
    # sl_ord_px 止损委托价，如果填写此参数，必须填写 止损触发价 委托价格为-1时，执行市价止损
    # tp_trigger_px_type 止盈触发价类型 last：最新价格 index：指数价格  mark：标记价格 默认为last
    # sl_trigger_px_type 止损触发价类型 last：最新价格 index：指数价格  mark：标记价格 默认为last

    def createOrder(self, pair_id,side, ord_type, td_mode, amount,clord_id=None,pos_side=None, price=None, tp_trigger_px_type=None,
                        tp_trigger_px=None, tp_ord_px=None, sl_trigger_px_type=None, sl_trigger_px=None, sl_ord_px=None) -> dict:

        return self.tradeAPI.place_order2(instId=pair_id,tdMode=td_mode, side=side, ordType=ord_type, sz=amount, ccy=None,clOrdId=clord_id,
                                          tag=None, posSide=pos_side, px=price,reduceOnly=None,tpTriggerPxType=tp_trigger_px_type, tpTriggerPx=tp_trigger_px,
                                          tpOrdPx=tp_ord_px, slTriggerPxType=sl_trigger_px_type,slTriggerPx=sl_trigger_px, slOrdPx=sl_ord_px,
                                          triggerPx=None, orderPx=None)
    #批量下单
    #[{'instId': instId, 'tdMode': tdMode, 'side': side, 'ordType': ordType, 'sz': sz, 'ccy': ccy,
    #  'clOrdId':clOrdId, 'tag':tag,  'posSide': posSide, 'px':px,'reduceOnly': reduceOnly,
    #  'tpTriggerPxType': tpTriggerPxType, 'tpTriggerPx': tpTriggerPx,'tpOrdPx': tpOrdPx,
    #  'slTriggerPxType': slTriggerPxType,'slTriggerPx': slTriggerPx, 'slOrdPx': slOrdPx,
    #  'triggerPx': triggerPx, 'orderPx': orderPx}]

    def createMutiOrder(self,order_data):
        return self.tradeAPI.place_multiple_orders(self,order_data=order_data)

    # 设置杠杆
    def setLeverage(self,lever, mgn_mode, pair_id=None, ccy=None, pos_side=None):
        return self.accountAPI.set_leverage(lever=lever, mgnMode=mgn_mode, instId=pair_id, ccy=ccy, posSide=pos_side)

    #获取当前杠杆
    def getLeverage(self,pair_id,mgn_mode):
        return self.accountAPI.get_leverage(instId=pair_id,mgnMode=mgn_mode)

    #获取当前费率
    def getFeeRate(self,inst_type, pair_id=None, uly=None, category=None):
        return self.accountAPI.get_fee_rates(instType=inst_type,instId=pair_id,uly=uly,category=category)

    #获取最大可用数量
    def getMaxAvailableSize(self, pair_id, td_mode, ccy=None, reduce_only=None):
        return self.accountAPI.get_max_avail_size(instId=pair_id, tdMode=td_mode, ccy=ccy, reduceOnly=reduce_only)

    #获取最大可买卖开仓数量
    def getMaxTradeSize(self,pair_Id, td_mode, ccy=None, price=None):
        return self.accountAPI.get_maximum_trade_size(instId=pair_Id, tdMode=td_mode, ccy=ccy, px=price)

    #获取单个交易产品基础信息
    def getInstruments(self, inst_type, uly=None, pair_id=None):
        return self.publicAPI.get_instruments(instType=inst_type,uly=uly,instId=pair_id)

    #获取币种行情信息
    def getTicker(self,pair_id):
        return self.marketAPI.get_ticker(instId=pair_id)

    #获取订单信息
    def getOrder(self,pair_id,order_id):
        return self.tradeAPI.get_orders(instId=pair_id,ordId=order_id)

    #市价全平
    def closePostions(self,pair_id,mgn_mode,pos_side,auto_cxl):
        return self.tradeAPI.close_positions2(instId=pair_id,mgnMode=mgn_mode,posSide=pos_side,autoCxl=auto_cxl)

    #未完成订单列表
    def getPendingOrdersList(self,inst_type=None,pair_id=None,ord_type=None,state=None,after=None,before=None,limit=None):
        return self.tradeAPI.get_order_list(instType=inst_type, uly=None, instId=pair_id, ordType=ord_type, state=state,
                                            after=after, before=before,limit=limit)

    #批量撤单
    def cancelOrders(self,order_list):
        return self.tradeAPI.cancel_multiple_orders(order_list)

if __name__=="__main__":
    conf = config_file.getConfigFile("config.json")
    authSimulate = conf['account']['okex']['simulate'][1]
    okx = OkxExange(authSimulate,True)
    r=okx.fetchBalance(ccy='USDT')
    #r = okx.createOrder("LTC-USDT-SWAP", ord_type="market", td_mode="isolated", side="buy", amount="2",clord_id="long1",
    #                         pos_side="long", price=None, tp_trigger_px_type="mark",
    #                        tp_trigger_px="128", tp_ord_px="127", sl_trigger_px_type="mark", sl_trigger_px="99", sl_ord_px="100")
    #r = okx.createOrder("TORN-USDT", ord_type="limit", td_mode="isolated", side="buy", amount="2",
    #                      price="30")
    #print(r['data'][0]['clOrdId'])
    #r = okx.createOrder("LTC-USDT-SWAP", ord_type="market", td_mode="isolated", side="sell", amount="2",
    #                pos_side = "short", price = None, tp_trigger_px_type = "mark",
    #                tp_trigger_px = "120", tp_ord_px = "121", sl_trigger_px_type = "mark", sl_trigger_px = "128", sl_ord_px = "127")
    #print(r)
    #print(r['data'][0]['details'][0]['availEq'])
    #r=okx.setLeverage(lever="3",mgn_mode="isolated",pair_id="ETH-USDT-SWAP",pos_side="long")
    #r=okx.getLeverage(pair_id="XMR-USDT-SWAP",mgn_mode="isolated")
    #print(r)
    #r=okx.getFeeRate("SWAP",pair_id="ETH-USDT",category=1)
    #print(r)
    #r=okx.getMaxAvailableSize(pair_id="ETH-USDT-SWAP",td_mode="isolated")
    #print(r)
    #r=okx.getMaxTradeSize('LTC-USDT-SWAP','isolated',price='2900')
    #print(r)
    #r=okx.getInstruments(inst_type="SWAP",pair_id="DOGE-USDT-SWAP")
    #print(r['data'][0]['ctVal'])
    #r= okx.getTicker("ETH-USDT-SWAP")
    #print(r)
    #r= okx.getOrder("LTC-USDT-SWAP",'426478842080010241')
    #print(r)
    #r=okx.closePostions('LTC-USDT-SWAP','isolated','short',True)
    r=okx.getPendingOrdersList(pair_id='TORN-USDT-SWAP')
    order_list=[]

    for o in r['data']:
        order_info = {}
        order_info['instId'] = o['instId']
        order_info['ordId'] = o['ordId']
        order_list.append(order_info)
    print(order_list)
    r=okx.cancelOrders(order_list)
    print(r)