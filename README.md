# AHR999 Auto-Invest

基于AHR999指标的加密货币自动定投系统，支持Binance、OKX、Bitget等主流交易所。

## 功能特性

- 🤖 **自动定投**：根据AHR999指标自动执行定投策略
- 📊 **智能策略**：
  - AHR999 < 0.45：定投200U（抄底线）
  - AHR999 < 1.0：定投100U（定投线）
  - AHR999 >= 1.0：不操作
- 🌐 **多交易所支持**：Binance、OKX、Bitget
- ⏰ **定时执行**：每天北京时间00:00自动检查并执行
- 📝 **详细日志**：记录所有操作和交易历史
- 🧪 **干运行模式**：测试策略不实际交易

## AHR999指标说明

AHR999是由微博用户ahr999创建的比特币投资指标，计算公式：

```
AHR999 = (BTC当前价格 / BTC 200日定投成本) × (BTC当前价格 / BTC拟合价格)
```

- **< 0.45**：抄底区域，适合大额买入
- **0.45 - 1.0**：定投区域，适合定期买入
- **> 1.0**：观望区域，不建议买入

## 安装

### 环境要求

- Python 3.9+
- pip

### 安装步骤

1. 克隆项目
```bash
cd ahr999-auto-invest
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入您的交易所API密钥
```

4. 配置策略参数
```bash
# 编辑 config.yaml 文件，配置定投参数
```

## 配置说明

### API密钥配置（.env文件）

```env
# Binance
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# OKX
OKX_API_KEY=your_okx_api_key
OKX_API_SECRET=your_okx_api_secret
OKX_PASSPHRASE=your_okx_passphrase

# Bitget
BITGET_API_KEY=your_bitget_api_key
BITGET_API_SECRET=your_bitget_api_secret
BITGET_PASSPHRASE=your_bitget_passphrase
```

### 策略配置（config.yaml文件）

请参考 `config.yaml` 文件中的详细注释进行配置。

## 使用方法

### 查看当前AHR999指标
```bash
python main.py --show-ahr999
```

### 测试交易所连接
```bash
python main.py --test-exchange binance
python main.py --test-exchange okx
python main.py --test-exchange bitget
```

### 验证配置
```bash
python main.py --validate-config
```

### 干运行（不实际交易）
```bash
python main.py --dry-run --execute-once
```

### 执行一次定投检查
```bash
python main.py --execute-once
```

### 启动定时任务
```bash
python main.py
```

## API密钥获取指南

### Binance
1. 登录 [Binance](https://www.binance.com/)
2. 进入 账户 → API管理
3. 创建新的API密钥
4. 启用"现货交易"权限
5. 设置IP白名单（推荐）

### OKX
1. 登录 [OKX](https://www.okx.com/)
2. 进入 个人中心 → API
3. 创建新的API密钥
4. 启用"交易"权限
5. 记录Passphrase（仅显示一次）

### Bitget
1. 登录 [Bitget](https://www.bitget.com/)
2. 进入 API管理
3. 创建新的API密钥
4. 启用"现货交易"权限
5. 记录Passphrase

## 安全建议

1. ⚠️ **永远不要**将 `.env` 文件提交到Git仓库
2. 🔒 建议设置API密钥的IP白名单
3. 💰 初期使用小额资金测试
4. 📊 定期检查日志和交易记录
5. 🔑 定期更换API密钥

## 项目结构

```
ahr999-auto-invest/
├── main.py                          # 主程序入口
├── config.yaml                      # 策略配置文件
├── .env                            # API密钥配置（需创建）
├── .env.example                    # 环境变量示例
├── requirements.txt                # Python依赖
├── README.md                       # 项目文档
├── src/
│   ├── data/
│   │   ├── ahr999_calculator.py   # AHR999计算
│   │   └── price_fetcher.py       # 价格数据获取
│   ├── exchanges/
│   │   ├── base_exchange.py       # 交易所基类
│   │   ├── binance_exchange.py    # Binance实现
│   │   ├── okx_exchange.py        # OKX实现
│   │   ├── bitget_exchange.py     # Bitget实现
│   │   └── exchange_factory.py    # 交易所工厂
│   ├── strategy/
│   │   └── investment_strategy.py # 定投策略
│   ├── scheduler/
│   │   └── investment_scheduler.py # 定时调度
│   └── utils/
│       ├── logger.py              # 日志记录
│       └── config_loader.py       # 配置加载
└── logs/                           # 日志目录
```

## 常见问题

### Q: AHR999指标如何计算？
A: 本系统自动从交易所获取BTC历史价格，计算200日移动平均价格和拟合价格，无需依赖第三方API。

### Q: 如何修改定投金额？
A: 编辑 `config.yaml` 文件中的 `dca_amount` 和 `bottom_amount` 参数。

### Q: 可以在多个交易所同时定投吗？
A: 可以，在 `config.yaml` 中配置 `exchange` 参数为需要使用的交易所。

### Q: 如何停止定时任务？
A: 按 `Ctrl+C` 或关闭终端即可停止。

### Q: 交易失败怎么办？
A: 检查日志文件了解失败原因，常见原因包括：余额不足、API权限不足、网络问题等。

## License

MIT License

## 免责声明

本软件仅供学习和研究使用。使用本软件进行投资的所有风险由用户自行承担。作者不对任何投资损失负责。请谨慎投资，理性决策。

## 贡献

欢迎提交Issue和Pull Request！
