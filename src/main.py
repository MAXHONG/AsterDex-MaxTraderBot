"""
AsterDEX 自动化交易机器人主程序
"""
import os
import sys
import time
import signal
from datetime import datetime
from typing import Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from api import AsterDexClient, DeepSeekClient
from strategies import DoubleMaStrategy
from trading import Trader, RiskManager
from utils import get_config, setup_logger, get_logger


class TradingBot:
    """交易机器人主类"""
    
    def __init__(self, config_path: str = None):
        """
        初始化交易机器人
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = get_config(config_path)
        
        # 设置日志
        log_config = self.config.logging_config
        self.logger = setup_logger(
            name='trading_bot',
            log_file=log_config.get('log_file', 'logs/trading_bot.log'),
            level=log_config.get('level', 'INFO'),
            max_bytes=log_config.get('max_bytes', 10485760),
            backup_count=log_config.get('backup_count', 5)
        )
        
        self.logger.info("=" * 60)
        self.logger.info("AsterDEX 自动化交易机器人启动")
        self.logger.info("=" * 60)
        
        # 初始化客户端
        self.asterdex_client = self._init_asterdex_client()
        self.deepseek_client = self._init_deepseek_client()
        
        # 初始化策略
        self.strategies = self._init_strategies()
        
        # 初始化风险管理器
        self.risk_manager = self._init_risk_manager()
        
        # 初始化交易器
        self.traders = {}
        self._init_traders()
        
        # 初始化调度器
        self.scheduler = BackgroundScheduler()
        
        # 运行标志
        self.is_running = False
    
    def _init_asterdex_client(self) -> AsterDexClient:
        """初始化 AsterDEX 客户端"""
        asterdex_config = self.config.asterdex
        
        return AsterDexClient(
            user=asterdex_config['user'],
            signer=asterdex_config['signer'],
            private_key=asterdex_config['private_key'],
            api_base_url=asterdex_config.get('api_base_url', 'https://fapi.asterdex.com'),
            recv_window=self.config.trading.get('recv_window', 50000)
        )
    
    def _init_deepseek_client(self) -> DeepSeekClient:
        """初始化 DeepSeek 客户端（可选）"""
        deepseek_config = self.config.deepseek
        
        if not deepseek_config or not deepseek_config.get('api_key'):
            self.logger.warning("=" * 60)
            self.logger.warning("⚠️  未配置 DeepSeek API")
            self.logger.warning("机器人将使用纯本地策略运行（无AI辅助）")
            self.logger.warning("这不影响交易功能，只是少了AI的二次确认")
            self.logger.warning("=" * 60)
            return None
        
        try:
            client = DeepSeekClient(
                api_key=deepseek_config['api_key'],
                api_base_url=deepseek_config.get('api_base_url', 'https://api.deepseek.com'),
                model=deepseek_config.get('model', 'deepseek-chat')
            )
            self.logger.info("✅ DeepSeek AI 客户端初始化成功（将作为辅助决策）")
            return client
        except Exception as e:
            self.logger.warning(f"⚠️  DeepSeek 初始化失败: {e}")
            self.logger.warning("机器人将使用纯本地策略运行")
            return None
    
    def _init_strategies(self) -> Dict[str, DoubleMaStrategy]:
        """初始化交易策略"""
        strategies_config = self.config.strategies
        strategies = {}
        
        # 高频策略
        if strategies_config.get('high_frequency', {}).get('enabled', False):
            hf_config = strategies_config['high_frequency']
            ma_periods = hf_config.get('ma_periods', {})
            
            strategies['high_frequency'] = DoubleMaStrategy(
                sma_periods=[
                    ma_periods.get('sma_short', 20),
                    ma_periods.get('sma_medium', 60),
                    ma_periods.get('sma_long', 120)
                ],
                ema_periods=[
                    ma_periods.get('ema_short', 20),
                    ma_periods.get('ema_medium', 60),
                    ma_periods.get('ema_long', 120)
                ],
                convergence_threshold=hf_config.get('convergence_threshold_percent', 2.0),
                breakout_confirmation_minutes=hf_config.get('breakout_confirmation_minutes', 30)
            )
            self.logger.info("高频策略已启用")
        
        # 中频策略
        if strategies_config.get('medium_frequency', {}).get('enabled', False):
            mf_config = strategies_config['medium_frequency']
            ma_periods = mf_config.get('ma_periods', {})
            
            strategies['medium_frequency'] = DoubleMaStrategy(
                sma_periods=[
                    ma_periods.get('sma_short', 20),
                    ma_periods.get('sma_medium', 60),
                    ma_periods.get('sma_long', 120)
                ],
                ema_periods=[
                    ma_periods.get('ema_short', 20),
                    ma_periods.get('ema_medium', 60),
                    ma_periods.get('ema_long', 120)
                ],
                convergence_threshold=mf_config.get('convergence_threshold_percent', 2.0),
                breakout_confirmation_minutes=mf_config.get('breakout_confirmation_minutes', 30)
            )
            self.logger.info("中频策略已启用")
        
        return strategies
    
    def _init_risk_manager(self) -> RiskManager:
        """初始化风险管理器"""
        trading_config = self.config.trading
        
        return RiskManager(
            max_leverage=trading_config.get('max_leverage', 5),
            max_position_percent=trading_config.get('max_position_percent', 30.0),
            margin_type=trading_config.get('margin_type', 'ISOLATED')
        )
    
    def _init_traders(self):
        """初始化交易器"""
        trading_config = self.config.trading
        leverage = trading_config.get('max_leverage', 5)
        
        for strategy_name, strategy in self.strategies.items():
            trader = Trader(
                asterdex_client=self.asterdex_client,
                deepseek_client=self.deepseek_client,
                risk_manager=self.risk_manager,
                strategy=strategy,
                leverage=leverage
            )
            
            # 初始化交易器
            trader.initialize()
            
            self.traders[strategy_name] = trader
            self.logger.info(f"{strategy_name} 交易器已初始化")
        
        # 设置交易对
        symbols = trading_config.get('symbols', [])
        for symbol in symbols:
            for trader in self.traders.values():
                try:
                    trader.setup_symbol(symbol)
                    self.logger.info(f"{symbol} 设置完成")
                except Exception as e:
                    self.logger.error(f"{symbol} 设置失败: {e}")
    
    def _run_high_frequency_strategy(self):
        """运行高频策略"""
        if 'high_frequency' not in self.strategies:
            return
        
        try:
            self.logger.info("=" * 40)
            self.logger.info(f"执行高频策略检查 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            
            strategy = self.strategies['high_frequency']
            trader = self.traders['high_frequency']
            
            hf_config = self.config.strategies['high_frequency']
            interval = hf_config.get('interval', '15m')
            symbols = self.config.trading.get('symbols', [])
            
            for symbol in symbols:
                try:
                    # 获取K线数据
                    klines = self.asterdex_client.get_klines(
                        symbol=symbol,
                        interval=interval,
                        limit=150  # 获取足够的数据来计算均线
                    )
                    
                    # 分析信号
                    signal = strategy.analyze(symbol, klines, interval)
                    
                    self.logger.info(
                        f"[{symbol}] 信号: {signal['action']}, "
                        f"信心: {signal['confidence']}, "
                        f"理由: {signal['reason']}"
                    )
                    
                    # 执行交易
                    if signal['action'] != 'HOLD':
                        trader.execute_signal(symbol, signal, interval)
                
                except Exception as e:
                    self.logger.error(f"处理 {symbol} 时出错: {e}")
            
            self.logger.info("高频策略检查完成")
        
        except Exception as e:
            self.logger.error(f"高频策略执行失败: {e}")
    
    def _run_medium_frequency_strategy(self):
        """运行中频策略"""
        if 'medium_frequency' not in self.strategies:
            return
        
        try:
            self.logger.info("=" * 40)
            self.logger.info(f"执行中频策略检查 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            
            strategy = self.strategies['medium_frequency']
            trader = self.traders['medium_frequency']
            
            mf_config = self.config.strategies['medium_frequency']
            interval = mf_config.get('interval', '4h')
            symbols = self.config.trading.get('symbols', [])
            
            for symbol in symbols:
                try:
                    # 获取K线数据
                    klines = self.asterdex_client.get_klines(
                        symbol=symbol,
                        interval=interval,
                        limit=150
                    )
                    
                    # 分析信号
                    signal = strategy.analyze(symbol, klines, interval)
                    
                    self.logger.info(
                        f"[{symbol}] 信号: {signal['action']}, "
                        f"信心: {signal['confidence']}, "
                        f"理由: {signal['reason']}"
                    )
                    
                    # 执行交易
                    if signal['action'] != 'HOLD':
                        trader.execute_signal(symbol, signal, interval)
                
                except Exception as e:
                    self.logger.error(f"处理 {symbol} 时出错: {e}")
            
            self.logger.info("中频策略检查完成")
        
        except Exception as e:
            self.logger.error(f"中频策略执行失败: {e}")
    
    def start(self):
        """启动交易机器人"""
        if self.is_running:
            self.logger.warning("交易机器人已在运行")
            return
        
        self.logger.info("启动交易机器人...")
        
        # 添加调度任务
        strategies_config = self.config.strategies
        
        # 高频策略
        if strategies_config.get('high_frequency', {}).get('enabled', False):
            hf_interval = strategies_config['high_frequency'].get('check_interval_seconds', 300)
            self.scheduler.add_job(
                self._run_high_frequency_strategy,
                trigger=IntervalTrigger(seconds=hf_interval),
                id='high_frequency',
                name='高频策略',
                max_instances=1
            )
            self.logger.info(f"高频策略已调度，每 {hf_interval} 秒执行一次")
        
        # 中频策略
        if strategies_config.get('medium_frequency', {}).get('enabled', False):
            mf_interval = strategies_config['medium_frequency'].get('check_interval_seconds', 3600)
            self.scheduler.add_job(
                self._run_medium_frequency_strategy,
                trigger=IntervalTrigger(seconds=mf_interval),
                id='medium_frequency',
                name='中频策略',
                max_instances=1
            )
            self.logger.info(f"中频策略已调度，每 {mf_interval} 秒执行一次")
        
        # 启动调度器
        self.scheduler.start()
        self.is_running = True
        
        self.logger.info("交易机器人已启动")
        
        # 立即执行一次检查
        if 'high_frequency' in self.strategies:
            self._run_high_frequency_strategy()
        if 'medium_frequency' in self.strategies:
            self._run_medium_frequency_strategy()
    
    def stop(self):
        """停止交易机器人"""
        if not self.is_running:
            return
        
        self.logger.info("正在停止交易机器人...")
        
        # 停止调度器
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
        
        self.is_running = False
        self.logger.info("交易机器人已停止")
    
    def run(self):
        """运行交易机器人（阻塞）"""
        self.start()
        
        try:
            # 保持运行
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("收到中断信号")
        finally:
            self.stop()


def main():
    """主函数"""
    # 确保日志目录存在
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建交易机器人
    bot = TradingBot()
    
    # 注册信号处理器
    def signal_handler(signum, frame):
        bot.logger.info(f"收到信号 {signum}，正在退出...")
        bot.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 运行
    bot.run()


if __name__ == '__main__':
    main()
