import os
import streamlit as st
import pandas as pd
from datetime import datetime
from google import genai

# 1. Cấu hình API Key của Gemini (Lấy từ biến môi trường để bảo mật)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 2. Cấu hình giao diện Streamlit
st.set_page_config(page_title="Cybersecurity Writing Feedback", layout="wide")
st.title("🛡️ IT Security Writing Task: User Warning Message")
st.caption("Sinh viên làm bài điền vào chỗ trống và nhận kết quả. Điểm số sẽ tự động lưu vào file Excel của Giáo viên.")

# Kiểm tra nếu chưa cấu hình key trên máy thì báo lỗi bảo mật ngay
if not GEMINI_API_KEY:
    st.error("🔒 Lỗi: Chưa cấu hình GEMINI_API_KEY trong hệ thống của bạn!")
    st.info("Vui lòng xem hướng dẫn ở Bước 3 phía dưới để biết cách nạp Key khi chạy ứng dụng.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# Đường dẫn lưu file Excel (Sẽ nằm cùng thư mục với file app.py)
EXCEL_FILE = "danh_sach_diem_writing.xlsx"

# Định nghĩa yêu cầu đề bài
with st.expander("📌 ĐỀ BÀI & YÊU CẦU (CLICK ĐỂ XEM)", expanded=True):
    st.markdown("""
    **Task:** Based on the incident scenario your group has analyzed, complete the email template below to issue an urgent security warning to the company's users.
    **Requirements:**
    * Fill in all the blanks with specific details from your scenario.
    * Use professional IT/Cybersecurity vocabulary.
    * Make sure Action 1 and Action 2 are clear and easy for normal users to follow.
    """)

st.write("---")

# Chia màn hình làm 2 cột
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("✍️ Điền vào các khoảng trống (Blanks)")
    
    # Bổ sung thêm thông tin định danh sinh viên để lưu vào Excel
    student_name = st.text_input("👤 Họ và tên Sinh viên:", placeholder="Ví dụ: Nguyễn Văn A")
    student_id = st.text_input("🪪 Mã số Sinh viên (MSSV):", placeholder="Ví dụ: ANT12345")
    
    st.write("---")
    
    # Các ô nhập liệu bài làm
    subject_blank = st.text_input("Subject: [URGENT/IMPORTANT] Security Alert: ...", placeholder="e.g., Phishing Attack Detected")
    recipient = st.selectbox("Dear ...", ["Users", "Staff", "Team", "All Employees"])
    incident_desc = st.text_area("1. Mô tả ngắn gọn sự cố (detected an incident regarding...):")
    threat_name = st.text_input("2. Tên loại tấn công (The identified threat is...):")
    consequence = st.text_area("3. Hậu quả đối với user (you may experience...):")
    action_1 = st.text_input("4. Action 1 (Hành động khẩn cấp 1):")
    action_2 = st.text_input("5. Action 2 (Hành động khẩn cấp 2):")
    it_measure = st.text_area("6. Biện pháp IT đang làm (working to resolve the issue by...):")

    submit_btn = st.button("🚀 Nộp bài & Nhận Feedback", type="primary")

with col2:
    st.subheader("📧 Email Preview (Xem trước bài làm)")
    
    # Lắp ghép các ô input thành bài email hoàn chỉnh
    full_email = f"""
**Subject:** [URGENT/IMPORTANT] Security Alert: {subject_blank if subject_blank else '____________________'}

Dear {recipient},

We are writing to inform you that we have detected an incident regarding {incident_desc if incident_desc else '_________________ (mô tả ngắn gọn sự cố)'}.

The identified threat is {threat_name if threat_name else '_________________ (tên loại tấn công)'}. This means that you may experience {consequence if consequence else '_________________ (hậu quả)'}.

To protect your data and our systems, we strongly advise you to take the following actions immediately:
* **Action 1:** {action_1 if action_1 else '__________________________________________________'}
* **Action 2:** {action_2 if action_2 else '__________________________________________________'}

Our IT Security Team is currently working to resolve the issue by {it_measure if it_measure else '_________________ (biện pháp IT đang làm)'}.

Thank you for your prompt cooperation.

Sincerely,  
IT Security Department
    """
    
    st.info(full_email)

    if submit_btn:
        # Kiểm tra thông tin bắt buộc
        if not student_name or not student_id:
            st.warning("⚠️ Vui lòng điền Họ tên và MSSV trước khi nộp bài!")
        elif not all([subject_blank, incident_desc, threat_name, consequence, action_1, action_2, it_measure]):
            st.warning("⚠️ Bạn chưa hoàn thành hết các khoảng trống trong email!")
        else:
            with st.spinner("🤖 AI đang chấm bài và ghi nhận điểm số..."):
                try:
                    # Prompt ép AI chấm điểm và trả về điểm số ở dòng đầu tiên theo đúng cú pháp cố định
                    prompt = f"""
                    Bạn là giảng viên chuyên ngành Cybersecurity chấm bài viết tiếng Anh của sinh viên.
                    
                    BÀI LÀM CỦA SINH VIÊN:
                    {full_email}

                    HÃY TRẢ VỀ FEEDBACK THEO ĐÚNG CẤU TRÚC SAU (Bắt buộc dòng đầu tiên phải ghi điểm số dạng số như quy định):
                    [SCORE]: <Chỉ điền một con số từ 0 đến 10 ở đây, ví dụ: 8.5>
                    
                    ## 📊 ĐIỂM SỐ ĐỀ XUẤT: <Điền lại số điểm>/10
                    
                    ## 🔍 ĐÁNH GIÁ CHI TIẾT THEO YÊU CẦU ĐỀ BÀI
                    1. **Nội dung & Ngữ cảnh (Scenario Details):** [Đánh giá tính nhất quán logic]
                    2. **Từ vựng chuyên ngành (IT Vocabulary):** [Đánh giá các thuật ngữ IT được dùng]
                    3. **Tính rõ ràng của Hành động (Clarity of Actions):** [Đánh giá xem user thường có dễ làm theo không]

                    ## ✍️ GỢI Ý CẢI THIỆN CHI TIẾT
                    - [Chỉ ra lỗi ngữ pháp nếu có và đưa ra câu sửa lại mượt mà hơn]
                    """

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )
                    
                    ai_output = response.text
                    
                    # Tách lấy điểm số bằng lập trình để lưu vào Excel
                    score_value = "0.0"
                    try:
                        for line in ai_output.split("\n"):
                            if "[SCORE]:" in line:
                                score_value = line.replace("[SCORE]:", "").strip()
                                break
                    except:
                        score_value = "N/A"

                    # --- PHẦN XỬ LÝ LƯU VÀO EXCEL ---
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Chuẩn bị dữ liệu một dòng mới
                    new_data = {
                        "Thời gian nộp": [current_time],
                        "MSSV": [student_id],
                        "Họ và Tên": [student_name],
                        "Điểm số": [score_value],
                        "Subject": [subject_blank],
                        "Bài làm hoàn chỉnh": [full_email]
                    }
                    new_df = pd.DataFrame(new_data)
                    
                    # Nếu file Excel đã tồn tại, đọc file cũ lên và nối dòng mới vào
                    if os.path.exists(EXCEL_FILE):
                        try:
                            old_df = pd.read_excel(EXCEL_FILE)
                            updated_df = pd.concat([old_df, new_df], ignore_index=True)
                        except:
                            updated_df = new_df
                    else:
                        updated_df = new_df
                        
                    # Ghi đè lại file Excel
                    updated_df.to_excel(EXCEL_FILE, index=False)
                    # --------------------------------

                    # Hiển thị kết quả chấm điểm lên màn hình cho sinh viên xem
                    st.write("---")
                    st.success("✅ Bài làm và điểm số của bạn đã được hệ thống lưu lại thành công!")
                    
                    # Hiển thị phần nhận xét của AI (Bỏ dòng [SCORE] ở đầu đi cho đẹp)
                    clean_feedback = "\n".join([line for line in ai_output.split("\n") if "[SCORE]:" not in line])
                    st.markdown(clean_feedback)
                    
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi hệ thống: {e}")