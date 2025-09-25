import sqlite3
import os

def check_coaches():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tabletennis.db')
    print(f"使用数据库路径: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查教练数据
    print("\n=== Coaches Info ===")
    cursor.execute("""
        SELECT c.id, c.user_id, c.level, u.real_name, u.gender
        FROM coaches c
        JOIN users u ON c.user_id = u.id
    """)
    coaches = cursor.fetchall()
    for coach in coaches:
        print(f"Coach ID: {coach[0]}")
        print(f"User ID: {coach[1]}")
        print(f"Level: {coach[2]}")
        print(f"Name: {coach[3]}")
        print(f"Gender: {coach[4]}")
        print("-" * 40)
    
    # 检查评价对应的预约和教练数据
    print("\n=== Comment-Booking-Coach Relationship ===")
    cursor.execute("""
        SELECT 
            c.id as comment_id,
            c.booking_id,
            b.coach_id,
            co.user_id as coach_user_id,
            u.real_name as coach_name
        FROM comments c
        JOIN bookings b ON c.booking_id = b.id
        JOIN coaches co ON b.coach_id = co.id
        JOIN users u ON co.user_id = u.id
    """)
    relationships = cursor.fetchall()
    for rel in relationships:
        print(f"Comment ID: {rel[0]}")
        print(f"Booking ID: {rel[1]}")
        print(f"Coach ID: {rel[2]}")
        print(f"Coach User ID: {rel[3]}")
        print(f"Coach Name: {rel[4]}")
        print("-" * 40)
    
    conn.close()

if __name__ == "__main__":
    check_coaches()