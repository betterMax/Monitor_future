# Future Monitoring

这是一个用于监控期货价格的网页应用。用户可以设置期货标的和相应的价格阈值，当价格超过阈值时，通过 Server 酱发送通知到微信。

## 安装和使用

1. 克隆仓库：
    ```bash
    git clone <repository-url>
    ```

2. 进入项目目录：
    ```bash
    cd ~/app/future_monitoring
    ```

3. 运行初始化脚本：
    ```bash
    ./setup.sh
    ```

4. 启动应用程序：
    ```bash
    source venv/bin/activate
    python app.py
    ```

## 文件结构

- `app.py`：Flask 应用的主程序
- `requirements.txt`：Python 依赖项列表
- `templates/`：HTML 模板文件目录
- `static/`：静态文件目录（CSS、JS、图像等）
- `README.md`：项目的说明文件
- `setup.sh`：项目的初始化脚本

## 贡献

欢迎贡献代码和建议！请提交 pull request 或 issue。

