import sqlite3
import os

def check_comments():
    # 获取正确的数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tabletennis.db')
    print(f"使用数据库路径: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 先检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comments'")
    if cursor.fetchone():
        print("comments 表存在")
    else:
        print("comments 表不存在！")
        return
    
    # 查看简单的评论数据
    print("\n=== Comments Basic Info ===")
    cursor.execute("SELECT * FROM comments")
    comments = cursor.fetchall()
    print(f"找到 {len(comments)} 条评论")
    
    if len(comments) > 0:
        # 如果有评论数据，再尝试关联查询
        print("\n=== Comments Details ===")
        cursor.execute("""
            SELECT c.id, c.booking_id, c.rating, c.content, c.created_at,
                b.coach_id, b.student_id
            FROM comments c
            JOIN bookings b ON c.booking_id = b.id
        """)
        comments = cursor.fetchall()
        for comment in comments:
            print(f"Comment ID: {comment[0]}")
            print(f"Booking ID: {comment[1]}")
            print(f"Rating: {comment[2]}")
            print(f"Content: {comment[3]}")
            print(f"Created At: {comment[4]}")
            print(f"Coach ID: {comment[5]}")
            print(f"Student ID: {comment[6]}")
            print("-" * 40)
    
        # 查看对应的预约状态
        print("\n=== Bookings Status ===")
        cursor.execute("""
            SELECT b.id, b.coach_id, b.student_id, b.status
            FROM bookings b
            WHERE b.id IN (SELECT booking_id FROM comments)
        """)
        bookings = cursor.fetchall()
        for booking in bookings:
            print(f"Booking ID: {booking[0]}")
            print(f"Coach ID: {booking[1]}")
            print(f"Student ID: {booking[2]}")
            print(f"Status: {booking[3]}")
            print("-" * 40)

    conn.close()

if __name__ == "__main__":
    check_comments()