from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# 数据库文件路径
DATABASE = 'monitoring.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    # 获取所有显示且被监控的记录
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM monitor_settings WHERE is_displayed = 1 AND is_active = 1 order by symbol, code, type')
    records = cursor.fetchall()
    conn.close()
    return render_template('index.html', records=records)


@app.route('/monitoring_types')
def monitoring_types():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM monitoring_types')
    types = cursor.fetchall()
    conn.close()
    return render_template('monitoring_types.html', types=types)


@app.route('/set_threshold', methods=['POST'])
def set_threshold():
    symbol = request.form['symbol']
    target_price = float(request.form['target_price'])
    condition = request.form['condition']
    is_active = request.form['is_active'] == 'true'
    is_displayed = request.form['is_displayed'] == 'true'

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO monitor_settings (symbol, target_price, condition, is_active, is_displayed)
        VALUES (?, ?, ?, ?, ?)
    ''', (symbol, target_price, condition, is_active, is_displayed))
    print("插入记录：", symbol, target_price, condition, is_active, is_displayed)
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


@app.route('/edit_threshold/<int:id>', methods=['GET', 'POST'])
def edit_threshold(id):
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        target_price = float(request.form['target_price'])
        condition = request.form['condition']
        is_active = request.form['is_active'] == 'true'
        is_displayed = request.form['is_displayed'] == 'true'
        cursor.execute('''
            UPDATE monitor_settings
            SET target_price = ?, condition = ?, is_active = ?, is_displayed = ?
            WHERE id = ?
        ''', (target_price, condition, is_active, is_displayed, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        cursor.execute('SELECT * FROM monitor_settings WHERE id = ?', (id,))
        record = cursor.fetchone()
        conn.close()
        return render_template('edit.html', record=record)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)