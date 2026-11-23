# 土木工地日常行政與材料進出貨管理系統 (第一版)

## 系統架構
- 後端框架：Python Flask
- 資料庫：SQLite (`construction_site.db`)，包含 4 張資料表：
  1. `vendors`（協力廠商名錄）
  2. `materials_log`（材料進出貨紀錄，外鍵關聯 `vendors.id`）
  3. `petty_cash`（日常行政零用金）
  4. `equipment_rentals`（小型機具借還登記）
- 前端介面：HTML5 + Tailwind CSS + Vanilla JavaScript (支援完整 CRUD)

## 本機執行方式
```bash
pip install -r requirements.txt
python app.py
```
啟動後開啟瀏覽器前往 `http://127.0.0.1:5000`。

## 免費雲端部署 (Render)
1. 將本資料夾上傳至 GitHub 公開/私人倉庫。
2. 登入 [Render](https://render.com) → New → Web Service → 連結該 GitHub 倉庫。
3. Build Command 填 `pip install -r requirements.txt`，Start Command 填 `gunicorn app:app`。
4. 選擇 Free 方案即可取得專屬公開網址。
