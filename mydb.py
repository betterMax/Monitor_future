from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, TIMESTAMP, CheckConstraint, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = "sqlite:///monitoring.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 定义类别
class MonitoringType(Base):
    __tablename__ = 'monitoring_types'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


# 定义模型
class MonitorSettings(Base):
    __tablename__ = 'monitor_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, ForeignKey('monitoring_types.name'), nullable=False, index=True)
    future_code = Column(String, nullable=False, index=True)
    monitor_type = Column(String, nullable=False, index=True)
    target_price = Column(Float, nullable=False)
    condition = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default="CURRENT_TIMESTAMP")
    is_active = Column(Boolean, nullable=False, index=True)
    is_displayed = Column(Boolean, nullable=False, index=True)

    __table_args__ = (
        CheckConstraint("LENGTH(symbol) BETWEEN 5 AND 6"),
        CheckConstraint("condition IN ('>', '>=', '<', '<=')"),
        CheckConstraint("is_active IN (0, 1)"),
        CheckConstraint("is_displayed IN (0, 1)"),
    )


# 创建所有表（如果它们还不存在）
Base.metadata.create_all(bind=engine)
