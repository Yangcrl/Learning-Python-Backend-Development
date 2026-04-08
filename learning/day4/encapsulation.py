"""
手机号类封装：演示类的封装、继承、MRO顺序
"""

class PhoneNumber:
    """
    手机号基类：封装通用属性和格式验证方法
    属性：
        number：手机号字符串
        operator：运营商名称（如：中国移动、中国联通、中国电信）
    方法：
        validate_format：验证手机号格式是否合法
    """

    def __init__(self, number):
        self.number = number
        self.operator = None # 运营商，子类实现自动识别

    def validate_format(self):
        """
        通用手机号格式验证（基类逻辑：11位纯数字）
        :return: 是否合法，提示信息
        """
        if not isinstance(self.number, str):
            return False, '手机号必须是字符串类型'
        if not len(self.number) == 11:
            return False, '手机号长度必须为11位'
        if not self.number.isdigit():
            return False, '手机号必须是纯数字'
        if not self.number.startswith('1'):
            return False, '手机号必须以1开头'
        return True, '手机号格式合法'

    def __str__(self):
        """自定义输出格式"""
        return f'手机号：{self.number}，运营商：{self.operator}'

class ChinaPhoneNumber(PhoneNumber):
    """
    中国手机号子类（第一层继承）：继承PhoneNumber，添加归属地、运营商识别
    扩展：
        1. 重写__init__：自动识别运营商
        2. 添加get_location：模拟归属地查询
    """

    # 模拟运营商号段库（真实场景可对接接口）
    OPERATOR_SEGMENTS = {
        '中国移动': ['134', '135', '136', '137', '138', '139', '147', '150', '151', '152', '157', '158', '159', '178', '182', '183', '184', '187', '188', '195'],
        '中国联通': ['130', '131', '132', '145', '155', '156', '166', '171', '175', '176', '185', '186'],
        '中国电信': ['133', '153', '173', '177', '180', '181', '189', '199']
    }

    # 模拟归属地库（真实场景可调用第三方API）
    LOCATION_DB = {
        '110000': '北京',
        '310000': '上海',
        '440000': '广州',
        '510000': '成都',
        '620000': '西安',
        '530000': '昆明',
        '610000': '武汉',
        '460000': '深圳',
    }

    def __init__(self, number):
        # 先调用父类构造方法初始化基础属性
        super().__init__(number)
        # 子类扩展：自动识别运营商
        self._identify_operator()

    def _identify_operator(self):
        """私有方法：根据号段识别运营商"""
        # 先验证格式，再识别
        is_valid, msg = self.validate_format()
        if not is_valid:
            self.operator = '未知(格式错误)'
            return

        # 取前3位号段匹配运营商
        prefix = self.number[:3]
        for operator, prefixes in self.OPERATOR_SEGMENTS.items():
            if prefix in prefixes:
                self.operator = operator
                break
        # 此为for 循环的 else 分支，不是if的else，循环正常结束才会执行
        else:
            self.operator = '未知(号段未匹配)'

    def get_location(self):
        """
        模拟归属地查询（中国手机号专属）
        :return: 归属地字符串（模拟逻辑：取前6位匹配）
        """
        is_valid, msg = self.validate_format()
        if not is_valid:
            return f'归属地查询失败：{msg}'

        # 模拟逻辑：取前6位匹配归属地（真实场景可调用API）
        prefix6 = self.number[:6]
        return self.LOCATION_DB.get(prefix6, f'未知(未匹配归属地{prefix6})')

    def show_info(self):
        """中国手机号通用信息展示"""
        print(f"【中国手机号信息】")
        print(f"号码：{self.number}")
        print(f"运营商：{self.operator}")
        print(f"归属地：{self.get_location()}")

class ChinaMobileNumber(ChinaPhoneNumber):
    """
    中国移动手机号子类（第二层继承）：继承ChinaPhoneNumber
    扩展：中国移动专属方法
    """
    def __init__(self, number):
        super().__init__(number)
        if self.operator != '中国移动':
            raise ValueError(f'号码{number}不是中国移动号段')

    def mobile_service(self):
        """中国移动专属服务"""
        return f'中国移动专属服务：{self.number},可办理5G畅享套餐，月租199元含100G流量'

class ChinaUnicomNumber(ChinaPhoneNumber):
    """
    中国联通手机号子类（第二层继承）：继承ChinaPhoneNumber
    扩展：中国联通专属方法
    """
    def __init__(self, number):
        super().__init__(number)
        if self.operator != '中国联通':
            raise ValueError(f'号码{number}不是中国联通号段')

    def mobile_service(self):
        """中国联通专属服务"""
        return f'中国联通专属服务：{self.number},可办理腾讯大王卡，月租19元免流腾讯系APP'

class ChinaTelecomNumber(ChinaPhoneNumber):
    """
    中国电信手机号子类（第二层继承）：继承ChinaPhoneNumber
    扩展：中国电信专属方法
    """
    def __init__(self, number):
        super().__init__(number)
        if self.operator != '中国电信':
            raise ValueError(f'号码{number}不是中国电信号段')

    def mobile_service(self):
        """中国电信专属服务"""
        return f'中国电信专属服务：{self.number},可办理星卡，月租19元含30G定向流量'


# 验证MRO顺序和功能
if __name__ == "__main__":
    # 1. 验证MRO（方法解析顺序）
    print("===验证MRO顺序===")
    print("ChinaMobileNumber的MPR：", ChinaMobileNumber.__mro__)
    print("ChinaUnicomNumber的MPR：", ChinaUnicomNumber.__mro__)

    # 2. 测试基类格式验证
    print("===测试基类格式验证===")
    invalid_phone = PhoneNumber('123456')
    print(invalid_phone.validate_format())
    valid_phone = PhoneNumber('13812345678')
    print(valid_phone.validate_format())

    # 3. 测试中国手机号子类（归属地+运营商识别）
    print("===测试中国手机号子类（归属地+运营商识别）===")
    china_phone = ChinaPhoneNumber('13812345678')
    china_phone.show_info()

    # 4. 测试运营商子类（继承+专属方法）
    print("===测试运营商子类（继承+专属方法）===")
    try:
        mobile = ChinaMobileNumber('13812345678')
        print(mobile) # 调用父类__str__
        print(mobile.mobile_service()) # 专属方法
        print(mobile.get_location()) # 继承自ChinaPhoneNumber的方法
        print(mobile.validate_format()) # 继承自PhoneNumber的方法
    except ValueError as e:
        print(e)

    try:
        # 测试错误号段
        wrong_mobile = ChinaMobileNumber('13012345678')
    except ValueError as e:
        print(e)

    # 5. 验证MRO调用顺序（重写方法时的优先级）
    print("===验证MRO调用顺序===")
    # 定义一个重写方法的子类，验证调用优先级
    class TestMRO(ChinaMobileNumber):
        def validate_format(self):
            """重写基类的格式验证方法"""
            print('TestMRO的validate_format方法被调用')
            return super().validate_format() # 调用父类的方法

    test_mro = TestMRO('13812345678')
    test_mro.validate_format()
