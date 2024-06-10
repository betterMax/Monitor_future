from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os
import csv
from datetime import datetime
import requests

app = Flask(__name__)

# 数据库文件路径
DATABASE = 'monitoring.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def dict_from_row(row):
    return {k: row[k] for k in row.keys()}


@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()

    symbol = request.args.get('symbol', '')
    monitor_type = request.args.get('monitor_type', '')
    is_active = request.args.get('is_active', '')
    is_displayed = request.args.get('is_displayed', '')

    query = """
        SELECT ms.id, ms.symbol, fi.name as chinese_name, ms.future_code, mt.monitor_type, fi.unit, fi.leverage, 
               CASE WHEN ms.latest_price IS NOT NULL THEN (ms.latest_price * fi.unit * fi.leverage) ELSE NULL END as margin,
               ms.condition, ms.target_price, ms.latest_price, ms.updated_at, ms.created_at, ms.is_active
        FROM monitor_settings ms
        JOIN future_info fi ON ms.symbol = fi.symbol
        JOIN monitoring_types mt ON ms.monitor_id = mt.id
        WHERE 1=1
    """
    params = []
    if symbol:
        query += " AND ms.symbol LIKE ?"
        params.append(f"%{symbol}%")
    if monitor_type:
        query += " AND mt.monitor_type LIKE ?"
        params.append(f"%{monitor_type}%")
    if is_active:
        query += " AND ms.is_active = ?"
        params.append(is_active)
    if is_displayed:
        query += " AND ms.is_displayed = ?"
        params.append(is_displayed)

    query += " ORDER BY ms.future_code, ms.monitor_id"
    cursor.execute(query, params)
    records = cursor.fetchall()
    records = [dict_from_row(record) for record in records]  # 转换为字典
    # print(f"records: {records}")

    cursor.execute("SELECT * FROM monitoring_types")
    monitoring_types = cursor.fetchall()
    monitoring_types = [dict_from_row(type) for type in monitoring_types]

    conn.close()
    return render_template('index.html', records=records, monitoring_types=monitoring_types)


@app.route('/monitoring_types')
def monitoring_types():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM monitoring_types')
    types = cursor.fetchall()
    conn.close()
    return render_template('monitoring_types.html', types=types)

#
# @app.route('/set_threshold', methods=['POST'])
# def set_threshold():
#     symbol = request.form['symbol']
#     target_price = float(request.form['target_price'])
#     condition = request.form['condition']
#     is_active = request.form['is_active'] == 'true'
#     is_displayed = request.form['is_displayed'] == 'true'
#
#     conn = get_db()
#     cursor = conn.cursor()
#     cursor.execute('''
#         INSERT INTO monitor_settings (symbol, target_price, condition, is_active, is_displayed)
#         VALUES (?, ?, ?, ?, ?)
#     ''', (symbol, target_price, condition, is_active, is_displayed))
#     print("插入记录：", symbol, target_price, condition, is_active, is_displayed)
#     conn.commit()
#     conn.close()
#
#     return redirect(url_for('index'))


@app.route('/edit_threshold/<int:id>', methods=['GET', 'POST'])
def edit_threshold(id):
    print(f"Received ID: {id}")  # 调试信息
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        # print(request.form)  # 打印接收到的表单数据

        # 检查请求数据是否包含所有预期字段
        if not all(key in request.form for key in
                   ('future_code', 'target_price', 'condition', 'is_active', 'is_displayed')):
            return "Bad Request: Missing fields", 400

        future_code = request.form['future_code']
        target_price = request.form['target_price']
        condition = request.form['condition']
        is_active = request.form['is_active'] == 'true'
        is_displayed = request.form['is_displayed'] == 'true'

        # 计算期货核心识别码
        symbol = future_code[:-4]
        # print(f"symbol: {symbol}, future_code: {future_code}, target_price: {target_price}, condition: {condition}, is_active: {is_active}, is_displayed: {is_displayed}")
        cursor.execute("""
            UPDATE monitor_settings
            SET future_code = ?, target_price = ?, condition = ?, is_active = ?, is_displayed = ?, symbol = ?
            WHERE id = ?
        """, (future_code, target_price, condition, is_active, is_displayed, symbol, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM monitor_settings WHERE id = ?", (id,))
    record = cursor.fetchone()
    if not record:
        conn.close()
        return "Record not found", 404

    cursor.execute("SELECT * FROM monitoring_types")
    monitoring_types = cursor.fetchall()
    conn.close()
    return render_template('edit.html', record=record, monitoring_types=monitoring_types)


@app.route('/toggle_display/<int:id>')
def toggle_display(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE monitor_settings
        SET is_displayed = NOT is_displayed
        WHERE id = ?
    ''', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/import_future_info', methods=['POST'])
def import_future_info():
    conn = get_db()
    cursor = conn.cursor()

    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        csv_reader = csv.reader(file)
        next(csv_reader)  # 跳过表头
        for row in csv_reader:
            symbol, name, unit, leverage = row
            # 校验数据格式
            if not symbol or not name or not unit or not leverage:
                conn.close()
                return "数据格式错误", 400

            cursor.execute("""
                INSERT INTO future_info (symbol, name, unit, leverage) VALUES (?, ?, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET name=excluded.name, unit=excluded.unit, leverage=excluded.leverage
            """, (symbol, name, unit, leverage))
        conn.commit()
    conn.close()
    return redirect(url_for('manage_future_info'))


@app.route('/update_future_info/<int:id>', methods=['POST'])
def update_future_info(id):
    conn = get_db()
    cursor = conn.cursor()
    symbol = request.form['symbol']
    name = request.form['name']
    unit = request.form['unit']
    leverage = request.form['leverage']

    cursor.execute("""
        UPDATE future_info SET symbol = ?, name = ?, unit = ?, leverage = ?
        WHERE id = ?
    """, (symbol, name, unit, leverage, id))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_future_info'))


@app.route('/manage_future_info')
def manage_future_info():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM future_info")
    future_info = cursor.fetchall()
    conn.close()
    return render_template('manage_future_info.html', future_info=future_info)


@app.route('/manage_monitoring_types')
def manage_monitoring_types():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM monitoring_types")
    monitoring_types = cursor.fetchall()
    conn.close()
    return render_template('manage_monitoring_types.html', monitoring_types=monitoring_types)


@app.route('/add_monitoring_type', methods=['POST'])
def add_monitoring_type():
    conn = get_db()
    cursor = conn.cursor()
    monitor_type = request.form['monitor_type']
    cursor.execute("INSERT INTO monitoring_types (monitor_type) VALUES (?)", (monitor_type,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_monitoring_types'))


@app.route('/add_record', methods=['POST'])
def add_record():
    conn = get_db()
    cursor = conn.cursor()
    future_code = request.form['future_code']
    monitor_id = request.form['monitor_id']
    target_price = request.form['target_price']
    condition = request.form['condition']
    is_active = request.form['is_active']
    is_displayed = request.form['is_displayed']
    created_at = datetime.now()

    # 计算期货核心识别码
    symbol = future_code[:-4]

    try:
        cursor.execute("""
            INSERT INTO monitor_settings (symbol, future_code, monitor_id, target_price, condition, is_active, is_displayed, created_at, latest_price, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)
        """, (symbol, future_code, monitor_id, target_price, condition, is_active, is_displayed, created_at))
        conn.commit()
        print("插入记录成功")
    except Exception as e:
        print(f"插入失败，错误为: {e}")
        conn.rollback()
    finally:
        conn.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)