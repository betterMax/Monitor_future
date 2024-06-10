import requests
import sqlite3
from config import API_BASE_URL, APP_KEY

# 数据库连接设置
DATABASE = "monitoring.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def get_active_monitor_settings():
    # 获取所有活跃的监控设置
    conn = get_db()
    cursor = conn.cursor()
    query = """
        SELECT ms.id, ms.future_code, fi.market 
        FROM monitor_settings ms
        JOIN future_info fi ON ms.symbol = fi.symbol
        WHERE ms.is_active = 1
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    # 将结果转换为字典列表
    monitor_settings = [dict(row) for row in rows]

    return monitor_settings


def fetch_market_data(market):
    # 构建API请求URL
    url = f"{API_BASE_URL}{market}futures?appkey={APP_KEY}"
    response = requests.get(url)
    data = response.json()
    return data


def update_monitor_settings(market_data, monitor_settings):
    # 更新监控设置表
    conn = get_db()
    cursor = conn.cursor()
    for setting in monitor_settings:
        future_code = setting['future_code']
        id = setting['id']
        # 筛选出对应的future数据
        for future in market_data:
            if future['type'] == future_code:
                latest_price = future['price']
                updated_at = future['updatetime']

                query = """
                    UPDATE monitor_settings
                    SET latest_price = ?,
                        updated_at = ?
                    WHERE id = ?
                """
                cursor.execute(
                    query,
                    (latest_price, updated_at, id)
                )
    conn.commit()
    conn.close()


def main():
    monitor_settings = get_active_monitor_settings()
    markets = set(setting['market'] for setting in monitor_settings)
    combined_data = []

    for market in markets:
        data = fetch_market_data(market)
        if data['status'] == 0:
            for key in data['result']:
                combined_data.extend(data['result'][key])

    update_monitor_settings(combined_data, monitor_settings)


if __name__ == "__main__":
    main()
