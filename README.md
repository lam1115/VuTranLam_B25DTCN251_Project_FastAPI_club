# Tài Liệu Hướng Dẫn & Cơ Sở Dữ Liệu Dự Án

Thư mục này chứa toàn bộ tài liệu kỹ thuật, sơ đồ thiết kế cơ sở dữ liệu (Database Schema) và các hướng dẫn khởi tạo dữ liệu mẫu (Seed Data) cho **API Quản Lý Câu Lạc Bộ Sinh Viên**.

---

## Cấu Trúc Cơ Sở Dữ Liệu (Database Schema)

Dự án sử dụng cơ sở dữ liệu quan hệ (MySQL) thông qua ORM **SQLAlchemy**. Các bảng chính được thiết kế như sau:

- **Users (`Users`)**: Quản lý thông tin người dùng và phân quyền hệ thống (`ADMIN`, `USER`).
- **Clubs (`Clubs`)**: Quản lý thông tin các Câu lạc bộ (CLB) do người dùng làm chủ sở hữu (`owner_id`).
- **Club Members (`Club_members`)**: Quản lý thành viên tham gia từng CLB với vai trò (`OWNER`, `MEMBER`).
- **Club Activities (`Club_activities`)**: Quản lý các hoạt động, nhiệm vụ của CLB với trạng thái (`TODO`, `IN_PROGRESS`, `DONE`) và độ ưu tiên (`LOW`, `MEDIUM`, `HIGH`).
- **Các bảng nâng cao**: `Comments`, `Attachments`, `activity_logs`, `refresh_tokens`.

---

## Hướng Dẫn Khởi Tạo Dữ Liệu Mẫu (Seed Data)

Script `seed.py` được cung cấp nhằm giúp khởi tạo tự động tập dữ liệu chuẩn bị sẵn phục vụ cho việc kiểm thử (testing) và chạy demo dự án.

### 1. Dữ liệu mẫu khởi tạo gồm có:

- **1 Tài khoản Admin**: `vutranlam1115@gmail.com` / Mật khẩu: `123456`
- **10 Tài khoản User**: Các tài khoản sinh viên dùng để test tính năng (Mật khẩu: `123456`).
- **3 Câu lạc bộ**: CLB IT, CLB Âm Nhạc, CLB Thể Thao.
- **10 Thành viên**: Phân bổ vào 3 câu lạc bộ với vai trò Chủ CLB (`OWNER`) và Thành viên (`MEMBER`).
- **9 Hoạt động**: 3 hoạt động cho mỗi CLB với các mức độ ưu tiên và thời hạn khác nhau.

### 2. Cách thực thi lệnh Seed Dữ Liệu:

Mở Terminal tại **thư mục gốc của dự án** và chạy lệnh:

```bash
# Lệnh chuẩn chạy module Python từ thư mục gốc
python -m app.db.seed

# Lệnh chuẩn để khởi động ứng dụng từ thư mục gốc của dự án
uvicorn app.main:app --reload

```

### 4. Truy cập giao diện tài liệu API tự động:

Sau khi server khởi chạy thành công, bạn có thể kiểm thử trực tiếp các API thông qua giao diện tương tác:

- **Swagger UI (Interactive API Docs):** `http://127.0.0.1:8000/docs`
- **ReDoc (Detailed API Specs):** `http://127.0.0.1:8000/redoc`
