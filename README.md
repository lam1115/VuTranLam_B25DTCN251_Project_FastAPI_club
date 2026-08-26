### 1. Cách thực thi lệnh Seed Dữ Liệu:

Mở Terminal tại **thư mục gốc của dự án** và chạy lệnh:

```bash
# Lệnh chuẩn chạy module Python từ thư mục gốc
python -m app.db.seed

# Lệnh chuẩn để khởi động ứng dụng từ thư mục gốc của dự án
uvicorn app.main:app --reload

```

### 2. Truy cập giao diện tài liệu API tự động:

Sau khi server khởi chạy thành công, bạn có thể kiểm thử trực tiếp các API thông qua giao diện tương tác:

- **Swagger UI (Interactive API Docs):** `http://127.0.0.1:8000/docs`
- **ReDoc (Detailed API Specs):** `http://127.0.0.1:8000/redoc`
