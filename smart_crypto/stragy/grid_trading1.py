from exanges import ExangeFactroy
from logger import logger
import config_file
import os


DEFAULT_GRID_COUNT = 10
DEFAULT_GRID_TYPE = "arithmetic"


class GridTradingBot:
    def __init__(self,exange_id,auth_info,is_simulate):
        self.exange=ExangeFactroy.getExange(exange_id,auth_info,is_simulate)
        #获取配置信息
        current_folder = os.path.dirname(__file__)
        config_path = os.path.join(current_folder, "grid_config.json")
        self.grid_config=config_file.getConfigFile(config_path)
        self.settings=self.grid_config['settings']
        self._addDefaultSetting()
        #订单数据
        self.orders={}
        #print(self.grid_config)


    #所有币种最小所需保证金数量
    def _minRequriedEq(self):
        required_eq=0
        settings = self.settings
        #对每个交易品种分别计算所需最小保证金然后求和
        for setting in settings:
            #每个交易品种所需的最小保证金总和
            per_eq=self._minRequriedEqForPair(setting)
            required_eq +=per_eq
            print(per_eq)

        return required_eq

    #单个币种设置所需保证金数量
    def _minRequriedEqForPair(self,setting):
        per_eq = 0
        # 交易品种ID
        pair_id = setting['pair_id']
        start_price = setting['start_price']
        if start_price == "0":
            r = self.exange.getTicker(pair_id=pair_id)
            if r['code'] != '0':
                return 0
            start_price = r['data'][0]['last']
        # 获取网格类型，默认为等差
        grid_type = setting['grid_type']
        # 获取杠杆倍数，默认为系统设置倍数
        leverage = setting['leverage']
        # 获取每单的交易数量，默认为系统规定的最小数量
        buy_volume_per_order = setting['buy_volume_per_order']
        # 网格数量，默认为10
        grid_count = setting['grid_count']
        # 求和相关变量
        n = int(grid_count)
        a = float(start_price)
        v = float(buy_volume_per_order)
        l = float(leverage)
        # 首项
        a1 = a * v / l
        # 等差数列情况
        if grid_type == "arithmetic":
            # 如果没有设置差则跳过
            if setting['difference']['value'] == "":
                return 0
            d = 0.0
            if setting['difference']['is_start_price_ratio'] == '0':
                d = float(setting['difference']['value'])
            else:
                d = float(setting['difference']['value']) * float(start_price)
            per_eq = n * a1 + n * (n - 1) * d / 2.0
        if grid_type == "geometric":
            # 如果没有设置比例则跳过
            if setting['ratio'] == "":
                return 0
            q = float(setting['ratio'])
            if q == 1.0:
                per_eq = n * a1
            else:
                per_eq = a1 * (1 - pow(q, n)) / (1 - q)
        return per_eq

    #当前未成交订单数量
    def _currentOrderCount(self):
        pass
    #当前持仓数量
    def _currentPosCount(self):
        pass

    #全币种设置保证金是否充足
    def _isAvailEqSufficient(self) ->dict:
        res = {}
        error = 0
        msg="OK"
        # 获取账户USDT余额信息
        r = self.exange.fetchBalance(ccy='USDT')
        if not r['code']:
            error = 2
            msg="Cannot get account balance,please check your network or api auth info"
            logger.ouputlog("get balance error!","ERROR")
            res ={"error":error,"msg":msg}
            return res
        # 获取USD可用保证金余额
        avail_eq = r['data'][0]['details'][0]['availEq']
        required_eq= self._minRequriedEq()
        diff = float(avail_eq) - float(required_eq)
        if diff <= 0:
            error = 1
            msg="The avail_eq is not enough！ Please add your eq"
        res={"error":error,"avail_eg":avail_eq,"required_eq":required_eq,"diff":diff,"msg":msg}
        return res

        # 保证金是否充足

    #单币种设置保证金是否充足
    def _isAvailEqSufficientForPair(self,setting) -> dict:
        res = {}
        error = 0
        msg = "OK"
        # 获取账户USDT余额信息
        r = self.exange.fetchBalance(ccy='USDT')
        if not r['code']:
            error = 2
            msg = "Cannot get account balance,please check your network or api auth info"
            print("get balance error!")
            res = {"error": error, "msg": msg}
            return res
        # 获取USD可用保证金余额
        avail_eq = r['data'][0]['details'][0]['availEq']
        required_eq = self._minRequriedEqForPair(setting)
        diff = float(avail_eq) - float(required_eq)
        if diff <= 0:
            error = 1
            msg = "The avail_eq is not enough！ Please add your eq"
        res = {"error": error, "avail_eg": avail_eq, "required_eq": required_eq, "diff": diff, "msg": msg}
        return res

    #对不完整设置添加默认设置
    def _addDefaultSetting(self):
        settings_list=[]
        for setting in self.settings:
            pair_id = setting['pair_id']
            # 如果交易品种ID为空则跳过
            if pair_id == "":
                continue
            # 获取网格类型，默认为等差
            if setting['grid_type'] == "":
                setting['grid_type'] = DEFAULT_GRID_TYPE
            # 获取杠杆倍数，默认为系统设置倍数
            leverage = setting['leverage']
            if leverage == "":
                if setting['grid_type'] == DEFAULT_GRID_TYPE:
                    d = setting['difference']['value']
                    if d =="":
                        continue
                    r = self.exange.getLeverage(pair_id, mgn_mode="isolated")
                    if float(d) <= 0:
                        setting['leverage'] = r['data'][0]['lever']
                    else:
                        setting['leverage'] = r['data'][1]['lever']
                if setting['grid_type'] == "geometric":
                    q = setting['ratio']
                    if q <=1 :
                        setting['leverage'] = r['data'][0]['lever']
                    else:
                        setting['leverage'] = r['data'][1]['lever']
            else:
                #设置杠杆倍数，多空双向都设置同样的杠杆倍数
                r=self.exange.setLeverage(lever=leverage, mgn_mode="isolated", pair_id=pair_id, pos_side="long")
                r=self.exange.setLeverage(lever=leverage, mgn_mode="isolated", pair_id=pair_id, pos_side="short")
            if setting['sell_volume_per_order'] == "":
                setting['sell_volume_per_order'] = setting['buy_volume_per_order']
            # 网格数量，默认为10
            if setting['grid_count'] == "":
                setting['grid_count'] = DEFAULT_GRID_COUNT
            settings_list.append(setting)
        self.settings = settings_list
        return settings_list

    #获取设置信息
    def getSettings(self):
        return self.settings

    #单个币种单向等差网格策略 ！这个暂停
    #TODO
    def arithmeticGridTradeForPair(self,setting):
        orders=[]
        pos_side = ""
        ord_type = 'limit'
        ord_side = ""

        if float(setting['difference']['value']) <= 0:
            pos_side = "long"
            ord_side = "buy"
        else:
            pos_side = "short"
            ord_side = "sell"
        while True:
            r = self._isAvailEqSufficientForPair(setting)
            if r['error']!=0:
               break
            #订单集为空
            if len(orders) == 0:
                start_price=""
                if setting['start_price'] == "0":
                    r = self.exange.getTicker(setting['pair_id'])
                    start_price=r['data'][0]['askPx']
                else:
                    start_price = setting['start_price']
                r = self.exange.createOrder(pair_id=setting['pair_id'], side=ord_side, td_mode="isolated",
                                            ord_type=ord_type,amount=setting['buy_volume_per_order'], )

    #市价全平
    def _closePostions(self,pair_id,mgn_mode,pos_side,auto_cxl):
        #获得未完成交易订单
        r=self.exange.getPendingOrdersList(pair_id=pair_id)
        if r['code'] == "0" and len(r['data'])> 0:
            order_list = []
            for o in r['data']:
                order_info = {}
                order_info['instId'] = o['instId']
                order_info['ordId'] = o['ordId']
                order_list.append(order_info)
            if len(order_list) > 0:
                #未完成订单全部撤单
                self.exange.cancelOrders(order_list)
        r=self.exange.closePostions(pair_id=pair_id,mgn_mode=mgn_mode,pos_side=pos_side,auto_cxl=auto_cxl)
        return r

    #单个币种双向等差网格策略 仅支持合约
    def arithmeticStandardGridTradeForPairSwap(self,setting):
        #止损后重新开始的基线价格
        new_start_price="0"
        #起始价格
        start_price=0.0
        #下一个网格上限
        next_grid_upper_bound = 0.0
        #下一个网格下限
        next_grid_lower_bound = 0.0
        #止损上限价格
        upper_limit_bound = 0.0
        #止损下限价格
        lower_limit_bound = 0.0
        #网格价差
        diff = 0.0
        #是否开始状态
        start_state = True
        #自定义做多订单前缀
        prefix_long ="long"
        #自定义做空订单前缀
        prefix_short = "short"
        #自定义做多订单ID号
        long_id = 0
        #自定义做空订单ID号
        short_id =0
        #取得合约面值
        r = self.exange.getInstruments(inst_type="SWAP", pair_id=setting['pair_id'])
        ct_val = r['data'][0]['ctVal']
        #设置量和合约面值之间的换算
        volume = 0
        if ct_val!='0':
            contract_count = float(setting['buy_volume_per_order']) / float(ct_val)
            if contract_count < 1:
                logger.ouputlog("%s最小下单量必须是 %s的整数倍!" % (setting["pair_id"],ct_val),"WARNING")
                return
            volume = round(contract_count)
        logger.ouputlog("网格交易启动","INFO")
        if setting['difference']['is_start_price_ratio'] == "0":
            diff = setting['difference']['value']
        while True:
            r = self._isAvailEqSufficientForPair(setting)
            if r['error']!=0:
                logger.ouputlog("AvailEq is not enough!")
                break
            if start_state == True:
                if new_start_price == "0":
                    if setting['start_price'] == "0":
                        r = self.exange.getTicker(setting['pair_id'])
                        start_price=float(r['data'][0]['askPx'])
                    else:
                        start_price = float(setting['start_price'])
                else:
                    start_price = float(new_start_price)

                if setting['difference']['is_start_price_ratio'] != "0":
                    diff = float(setting['difference']['value']) * start_price
                next_grid_upper_bound = start_price+ float(diff)
                next_grid_lower_bound = start_price -float(diff)
                upper_limit_bound = start_price+(int(setting['grid_count'])+1)*float(diff)
                lower_limit_bound = start_price-(int(setting['grid_count'])+1)*float(diff)
                logger.ouputlog("起始价格：%s"%start_price)
                logger.ouputlog("下一个网格下界:%s"%next_grid_lower_bound)
                logger.ouputlog("下一个网格上界:%s"%next_grid_upper_bound)
                logger.ouputlog("当前做多止损价格:%s"%lower_limit_bound)
                logger.ouputlog("当前做空止损价格:%s"%upper_limit_bound)
                start_state = False
            r=self.exange.getTicker(setting['pair_id'])
            cur_price = r['data'][0]['last']
            logger.ouputlog("当前成交价格:%s"%cur_price)
            if float(cur_price) <= start_price:
                if float(cur_price) <lower_limit_bound:
                    logger.ouputlog("触达当前做多止损价，准备平仓止损....")
                    r=self._closePostions(setting['pair_id'],"isolated","long",auto_cxl=True)
                    #r = self.exange.closePostions(setting['pair_id'],"isolated","long",auto_cxl=True)
                    if r['code'] == "0":
                        new_start_price = str(lower_limit_bound)
                        start_state = True
                        logger.ouputlog("平仓成功，将从新的起始价格开始....")
                        continue
                    else:
                        print("平仓失败，退出程序")
                        break
                if float(cur_price) < next_grid_lower_bound:
                    logger.ouputlog("触达新的做多下线网格价格，准备下单....")
                    long_id +=1
                    clord_id = prefix_long + str(long_id)
                    r = self.exange.createOrder(pair_id=setting['pair_id'], side="buy", td_mode="isolated",ord_type="limit",amount=str(volume),
                                                pos_side="long",clord_id=clord_id,price = str(next_grid_lower_bound),tp_trigger_px_type ="last",
                                                tp_trigger_px=str(next_grid_lower_bound+float(diff)),tp_ord_px="-1")
                    logger.ouputlog(r)
                    if r['code'] == '0':
                        next_grid_lower_bound = next_grid_lower_bound -float(diff)
                        next_grid_upper_bound = next_grid_upper_bound -float(diff)
                        logger.ouputlog("做多下单成功 设置新的网格下限价格:%s"%next_grid_lower_bound)
                        logger.ouputlog("做多下单成功 设置新的网格上限价格:%s" % next_grid_upper_bound)

                    logger.ouputlog(r['code'])
                    logger.ouputlog("order created id:%s"%r['data'][0]['clOrdId'])
                if float(cur_price) >next_grid_upper_bound:
                    next_grid_lower_bound = next_grid_lower_bound + float(diff)
                    next_grid_upper_bound = next_grid_upper_bound + float(diff)
                    logger.ouputlog("触达当前做多网格上限，设置新的网格下限价格:%s" % next_grid_lower_bound)
                    logger.ouputlog("触达当前做多网格上限，设置新的网格上限价格:%s" % next_grid_upper_bound)
            else:
                if float(cur_price) > upper_limit_bound:
                    logger.ouputlog("触达当前做空止损价，准备平仓止损....")
                    r = self._closePostions(setting['pair_id'], "isolated", "short", auto_cxl=True)
                    #r = self.exange.closePostions(setting['pair_id'], "isolated", "short", auto_cxl=True)
                    if r['code'] == "0":
                        new_start_price = str(upper_limit_bound)
                        start_state = True
                        continue
                    else:
                        logger.ouputlog("平仓失败，退出程序")
                        break
                if float(cur_price) > next_grid_upper_bound:
                    logger.ouputlog("触达新的做空网格上限价格，准备下单....")
                    short_id +=1
                    clord_id = prefix_short+str(short_id)
                    r = self.exange.createOrder(pair_id=setting['pair_id'], side="sell", td_mode="isolated",
                                                ord_type="limit", amount=str(volume),
                                                pos_side="short", clord_id=clord_id, price=str(next_grid_upper_bound),
                                                tp_trigger_px_type="last",
                                                tp_trigger_px=str(next_grid_upper_bound - float(diff)), tp_ord_px="-1")
                    logger.ouputlog(r)
                    if r['code'] == '0':
                        next_grid_lower_bound = next_grid_lower_bound +float(diff)
                        next_grid_upper_bound = next_grid_upper_bound +float(diff)
                        logger.ouputlog("做空下单成功 设置新的网格上限价格:%s"%next_grid_upper_bound)
                        logger.ouputlog("做空下单成功 设置新的网格下限价格:%s" % next_grid_lower_bound)
                    logger.ouputlog(r['code'])
                    logger.ouputlog("order created id:%s"%r['data'][0]['clOrdId'])
                if float(cur_price) < next_grid_lower_bound:
                    next_grid_lower_bound = next_grid_lower_bound - float(diff)
                    next_grid_upper_bound = next_grid_upper_bound - float(diff)
                    logger.ouputlog("触达当前做空网格下限，设置新的网格下限价格:%s" % next_grid_lower_bound)
                    logger.ouputlog("触达当前做空网格下限，设置新的网格上限价格:%s" % next_grid_upper_bound)

    def run(self,setting):
        self.arithmeticStandardGridTradeForPairSwap(setting)







if __name__=="__main__":
    conf = config_file.getConfigFile("..\\config.json")
    authSimulate = conf['account']['okex']['simulate'][0]
    grid_bot=GridTradingBot("okex",authSimulate,True)
    #r=grid_bot._isAvailEqSufficient()
    #print(r)
    #r=grid_bot.getSettings()
    #print(r)
    #r=grid_bot._isAvailEqSufficientForPair(grid_bot.settings[0])
    #print(r)
    #settings = grid_bot.settings
    #grid_bot.arithmeticStandardGridTradeForPairSwap(settings[0])
    r=grid_bot._closePostions('ETC-USDT-SWAP',"isolated","long",True)
    print(r)