from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, TIMESTAMP, CheckConstraint, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.schema import Table

DATABASE_URL = "sqlite:///monitoring.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 定义类别
class MonitoringType(Base):
    __tablename__ = 'monitoring_types'
    __table_args__ = {'comment': '用于存储监控类别'}

    id = Column(Integer, primary_key=True, index=True, comment='监控类型的识别码')
    monitor_type = Column(String, unique=True, index=True, comment='具体监控类别的中文名称')


# 定义期货信息
class FutureInfo(Base):
    __tablename__ = 'future_info'
    __table_args__ = {'comment': '用于存储期货的基本信息'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='用于识别期货')
    symbol = Column(String, nullable=False, index=True, comment='期货的核心识别码')
    market = Column(String, nullable=False, comment='交易所信息')
    name = Column(String, nullable=False, comment='中文名称')
    unit = Column(Integer, nullable=False, comment='单位数量')
    leverage = Column(Float, nullable=False, comment='杠杆，两位小数')
    # margin = Column(Float, nullable=False, comment='保证金，一位小数') 保证金=单价*单位*杠杆
    night_session = Column(Boolean, nullable=False, comment='是否有夜盘 0是没有，1是有')
    created_at = Column(TIMESTAMP, server_default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment='更新时间')


# 定义监控设置
class MonitorSettings(Base):
    __tablename__ = 'monitor_settings'
    __table_args__ = (
        CheckConstraint("LENGTH(symbol) BETWEEN 1 AND 2"),
        CheckConstraint("condition IN ('>', '>=', '<', '<=')"),
        {'comment': '用于存储所有监控标的及通知条件'},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment='用于识别记录')
    symbol = Column(String, ForeignKey('future_info.symbol'), nullable=False, index=True, comment='期货的核心识别码')
    future_code = Column(String, nullable=False, index=True, comment='期货完整代码')
    monitor_id = Column(Integer, ForeignKey('monitoring_types.id'), nullable=False, comment='关联监控类别')
    target_price = Column(Float, nullable=False, comment='目标价格')
    latest_price = Column(Float, comment='最新价格')
    condition = Column(String, nullable=False, comment='条件符')
    created_at = Column(TIMESTAMP, server_default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_active = Column(Boolean, nullable=False, index=True, comment='是否监控')
    is_displayed = Column(Boolean, nullable=False, index=True, comment='是否显示')


# 创建所有表（如果它们还不存在）
Base.metadata.create_all(bind=engine)
