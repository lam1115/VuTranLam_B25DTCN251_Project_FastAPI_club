from datetime import datetime, timedelta, timezone

# Import kết nối database
from app.db.database import SessionLocal

# Import các ORM Models
from app.models import UserModel
from app.models import ClubModel, Club_membersModel
from app.models import Club_activitiesModel

# Chuỗi Bcrypt Hash chuẩn của mật khẩu "123456"
DEFAULT_HASHED_PASSWORD = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW"


def seed_data():
    db = SessionLocal()
    try:
        print("--- Kiểm tra dữ liệu hiện tại ---")
        if db.query(UserModel).first():
            print("Cơ sở dữ liệu đã có dữ liệu. Bỏ qua bước seed!")
            return

        print("--- Khởi tạo dữ liệu mẫu theo yêu cầu mới ---")

        # -------------------------------------------------------------
        # 1. BẢNG USERS: 1 Admin + 10 Users thường
        # -------------------------------------------------------------
        admin_user = UserModel(
            email="vutranlam1115@gmail.com",
            password_hash=DEFAULT_HASHED_PASSWORD,
            full_name="Vũ Trần Lâm",
            role="ADMIN",
            is_active=True,
        )

        normal_users = [
            UserModel(
                email="nguyenvana@gmail.com",
                password_hash=DEFAULT_HASHED_PASSWORD,
                full_name="Nguyễn Văn A",
                role="USER",
                is_active=True,
            ),
            UserModel(
                email="tranthib@gmail.com",
                password_hash=DEFAULT_HASHED_PASSWORD,
                full_name="Trần Thị B",
                role="USER",
                is_active=True,
            ),
            UserModel(
                email="levanc@gmail.com",
                password_hash=DEFAULT_HASHED_PASSWORD,
                full_name="Lê Văn C",
                role="USER",
                is_active=True,
            ),
            UserModel(
                email="phamthid@gmail.com",
                password_hash=DEFAULT_HASHED_PASSWORD,
                full_name="Phạm Thị D",
                role="USER",
                is_active=True,
            ),
            UserModel(
                email="hoangvane@gmail.com",
                password_hash=DEFAULT_HASHED_PASSWORD,
                full_name="Hoàng Văn E",
                role="USER",
                is_active=True,
            ),
            UserModel(
                email="vothif@gmail.com",
                password_hash=DEFAULT_HASHED_PASSWORD,
                full_name="Võ Thị F",
                role="USER",
                is_active=True,
            ),
            UserModel(
                email="dangvang@gmail.com",
                password_hash=DEFAULT_HASHED_PASSWORD,
                full_name="Đặng Văn G",
                role="USER",
                is_active=True,
            ),
            UserModel(
                email="buitih@gmail.com",
                password_hash=DEFAULT_HASHED_PASSWORD,
                full_name="Bùi Thị H",
                role="USER",
                is_active=True,
            ),
            UserModel(
                email="donvani@gmail.com",
                password_hash=DEFAULT_HASHED_PASSWORD,
                full_name="Đỗ Văn I",
                role="USER",
                is_active=True,
            ),
            UserModel(
                email="ngokhanhk@gmail.com",
                password_hash=DEFAULT_HASHED_PASSWORD,
                full_name="Ngô Khánh K",
                role="USER",
                is_active=True,
            ),
        ]

        all_users = [admin_user] + normal_users
        db.add_all(all_users)
        db.commit()

        for u in all_users:
            db.refresh(u)

        # -------------------------------------------------------------
        # 2. BẢNG CLUBS: 3 Câu lạc bộ mẫu
        # -------------------------------------------------------------
        clubs_data = [
            ClubModel(
                club_name="CLB Lập Trình & Công Nghệ IT",
                description="Nơi chia sẻ kiến thức về Python, FastAPI, Database và Phát triển phần mềm.",
                owner_id=normal_users[0].user_id,  # Nguyễn Văn A làm chủ CLB 1
            ),
            ClubModel(
                club_name="CLB Âm Nhạc & Nghệ Thuật",
                description="Giao lưu ca hát, chơi nhạc cụ và tổ chức các sự kiện văn nghệ sinh viên.",
                owner_id=normal_users[1].user_id,  # Trần Thị B làm chủ CLB 2
            ),
            ClubModel(
                club_name="CLB Thể Thao & Rèn Luyện",
                description="Kết nối đam mê bóng đá, cầu lông và nâng cao sức khỏe sinh viên.",
                owner_id=normal_users[2].user_id,  # Lê Văn C làm chủ CLB 3
            ),
        ]

        db.add_all(clubs_data)
        db.commit()

        for c in clubs_data:
            db.refresh(c)

        club_it, club_music, club_sport = clubs_data[0], clubs_data[1], clubs_data[2]

        # -------------------------------------------------------------
        # 3. BẢNG CLUB_MEMBERS: 10 thành viên (bao gồm 3 Owner)
        # -------------------------------------------------------------
        members_data = [
            # 3 Chủ câu lạc bộ (OWNER)
            Club_membersModel(
                club_id=club_it.club_id,
                user_id=normal_users[0].user_id,
                role="OWNER",
            ),
            Club_membersModel(
                club_id=club_music.club_id,
                user_id=normal_users[1].user_id,
                role="OWNER",
            ),
            Club_membersModel(
                club_id=club_sport.club_id,
                user_id=normal_users[2].user_id,
                role="OWNER",
            ),
            # 7 Thành viên tham gia các CLB (MEMBER)
            Club_membersModel(
                club_id=club_it.club_id, user_id=admin_user.user_id, role="MEMBER"
            ),  # Vũ Trần Lâm
            Club_membersModel(
                club_id=club_it.club_id,
                user_id=normal_users[3].user_id,
                role="MEMBER",
            ),  # Phạm Thị D
            Club_membersModel(
                club_id=club_it.club_id,
                user_id=normal_users[4].user_id,
                role="MEMBER",
            ),  # Hoàng Văn E
            Club_membersModel(
                club_id=club_music.club_id,
                user_id=normal_users[5].user_id,
                role="MEMBER",
            ),  # Võ Thị F
            Club_membersModel(
                club_id=club_music.club_id,
                user_id=normal_users[6].user_id,
                role="MEMBER",
            ),  # Đặng Văn G
            Club_membersModel(
                club_id=club_sport.club_id,
                user_id=normal_users[7].user_id,
                role="MEMBER",
            ),  # Bùi Thị H
            Club_membersModel(
                club_id=club_sport.club_id,
                user_id=normal_users[8].user_id,
                role="MEMBER",
            ),  # Đỗ Văn I
        ]

        db.add_all(members_data)
        db.commit()

        # -------------------------------------------------------------
        # 4. BẢNG CLUB_ACTIVITIES: 9 hoạt động (Chia đều 3 cho mỗi CLB)
        # -------------------------------------------------------------
        activities_data = [
            # --- CLB IT (3 hoạt động) ---
            Club_activitiesModel(
                club_id=club_it.club_id,
                title="Workshop FastAPI & Database Seed",
                description="Hướng dẫn khởi tạo sơ đồ cơ sở dữ liệu và seed dữ liệu mẫu.",
                assignee_id=admin_user.user_id,
                status="IN_PROGRESS",
                priority="HIGH",
                due_date=datetime.now(timezone.utc) + timedelta(days=5),
            ),
            Club_activitiesModel(
                club_id=club_it.club_id,
                title="Seminar Clean Architecture",
                description="Chia sẻ kiến thức về cấu trúc thư mục chuẩn trong dự án Python.",
                assignee_id=normal_users[0].user_id,
                status="TODO",
                priority="MEDIUM",
                due_date=datetime.now(timezone.utc) + timedelta(days=12),
            ),
            Club_activitiesModel(
                club_id=club_it.club_id,
                title="Hackathon Sinh Viên IT 2026",
                description="Thi lập trình ứng dụng quản lý câu lạc bộ sinh viên.",
                assignee_id=normal_users[3].user_id,
                status="DONE",
                priority="HIGH",
                due_date=datetime.now(timezone.utc) - timedelta(days=2),
            ),
            # --- CLB ÂM NHẠC (3 hoạt động) ---
            Club_activitiesModel(
                club_id=club_music.club_id,
                title="Tuyển thành viên Ban nhạc khoá mới",
                description="Tổ chức phỏng vấn và thử giọng các bạn tân sinh viên.",
                assignee_id=normal_users[1].user_id,
                status="DONE",
                priority="HIGH",
                due_date=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            Club_activitiesModel(
                club_id=club_music.club_id,
                title="Tập luyện đêm nhạc Mùa Thu",
                description="Tổng duyệt danh sách bài hát và sắp xếp lịch tập acoustic.",
                assignee_id=normal_users[5].user_id,
                status="IN_PROGRESS",
                priority="MEDIUM",
                due_date=datetime.now(timezone.utc) + timedelta(days=7),
            ),
            Club_activitiesModel(
                club_id=club_music.club_id,
                title="Giao lưu Âm nhạc ngoài trời",
                description="Biểu diễn giao lưu tại khuôn viên trường.",
                assignee_id=normal_users[6].user_id,
                status="TODO",
                priority="LOW",
                due_date=datetime.now(timezone.utc) + timedelta(days=20),
            ),
            # --- CLB THỂ THAO (3 hoạt động) ---
            Club_activitiesModel(
                club_id=club_sport.club_id,
                title="Giải Bóng đá Sinh viên Thường niên",
                description="Mở đăng ký các đội bóng và bốc thăm chia bảng đấu.",
                assignee_id=normal_users[2].user_id,
                status="IN_PROGRESS",
                priority="HIGH",
                due_date=datetime.now(timezone.utc) + timedelta(days=4),
            ),
            Club_activitiesModel(
                club_id=club_sport.club_id,
                title="Đặt sân tập Cầu lông hàng tuần",
                description="Liên hệ quản lý nhà thể thao để đăng ký khung giờ tập.",
                assignee_id=normal_users[7].user_id,
                status="TODO",
                priority="LOW",
                due_date=datetime.now(timezone.utc) + timedelta(days=2),
            ),
            Club_activitiesModel(
                club_id=club_sport.club_id,
                title="Tổng kết giải Chạy Việt dã",
                description="Trao huy chương và bằng khen cho các vận động viên đạt giải.",
                assignee_id=normal_users[8].user_id,
                status="DONE",
                priority="MEDIUM",
                due_date=datetime.now(timezone.utc) - timedelta(days=1),
            ),
        ]

        db.add_all(activities_data)
        db.commit()

        print("=== Seed thành công 100% theo đúng cấu trúc yêu cầu! ===")

    except Exception as e:
        print(f"Lỗi khi seed dữ liệu: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
