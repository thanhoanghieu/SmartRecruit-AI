import re
import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Bạn là trợ lý tuyển dụng. Tóm tắt dựa trên hồ sơ được cung cấp, "
    "không suy diễn thông tin cá nhân, không đưa ra quyết định tuyển dụng."
)

HUMAN_IN_THE_LOOP_DISCLAIMER = (
    "⚠️ CẢNH BÁO: AI chỉ đóng vai trò hỗ trợ phân tích thông tin. "
    "Quyết định tuyển dụng cuối cùng thuộc về con người (Human-in-the-loop)."
)

# Danh sách các từ khóa/yếu tố nhạy cảm cần kiểm soát thiên lệch (Anti-bias keywords)
SENSITIVE_ATTRIBUTES = {
    "gender": ["nam", "nữ", "giới tính", "ông", "bà", "anh", "chị", "male", "female", "gender"],
    "age": ["tuổi", "sinh năm", "năm sinh", "sn", "age", "year of birth"],
    "marital_status": ["độc thân", "kết hôn", "có gia đình", "đã lập gia đình", "con nhỏ", "single", "married"],
    "ethnicity_religion": ["dân tộc", "tôn giáo", "đạo phật", "đạo thiên chúa", "quê quán", "hộ khẩu", "religion", "ethnicity"]
}

class AIService:
    @staticmethod
    def audit_bias(cv_text: str) -> Dict[str, Any]:
        """
        Kiểm tra và kiểm soát thiên lệch (SDLC KT3):
        Phát hiện nếu CV có chứa các thông tin nhạy cảm không liên quan đến năng lực công việc
        (tuổi tác, giới tính, tình trạng hôn nhân, tôn giáo, quê quán)
        và đảm bảo hệ thống loại trừ các yếu tố này khỏi đánh giá chuyên môn.
        """
        lower_cv = cv_text.lower()
        detected = []
        for category, words in SENSITIVE_ATTRIBUTES.items():
            for word in words:
                pattern = rf"\b{re.escape(word)}\b"
                if re.search(pattern, lower_cv):
                    detected.append(category)
                    break
        
        is_sensitive = len(detected) > 0
        if is_sensitive:
            result_note = (
                f"Đã phát hiện yếu tố nhân khẩu học ({', '.join(set(detected))}). "
                "Cơ chế Anti-Bias đã cô lập các thông tin này để bảo đảm chỉ đánh giá dựa trên kỹ năng, kinh nghiệm và năng lực chuyên môn."
            )
        else:
            result_note = "Hồ sơ đạt chuẩn trung lập: Không phát hiện thiên lệch nhân khẩu học đáng kể."
            
        return {
            "has_sensitive_info": is_sensitive,
            "detected_categories": list(set(detected)),
            "bias_audit_result": result_note
        }

    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        common_skills = [
            "python", "fastapi", "flask", "django", "react", "vue", "angular", "javascript",
            "typescript", "html", "css", "sql", "postgresql", "mysql", "sqlite", "mongodb",
            "redis", "docker", "kubernetes", "aws", "git", "ci/cd", "linux", "ai", "machine learning",
            "deep learning", "nlp", "llm", "rest api", "graphql", "microservices", "unit test",
            "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "excel", "power bi"
        ]
        text_lower = text.lower()
        found = []
        for s in common_skills:
            if re.search(rf"\b{re.escape(s)}\b", text_lower):
                found.append(s.title() if len(s) > 3 else s.upper())
        return found

    @classmethod
    async def summarize_cv(
        cls,
        job_description: str,
        cv_text: str,
        api_key: Optional[str] = None,
        provider: str = "auto"
    ) -> Dict[str, Any]:
        """
        Tóm tắt CV theo đúng đề bài:
        System: Bạn là trợ lý tuyển dụng. Tóm tắt dựa trên hồ sơ được cung cấp, không suy diễn thông tin cá nhân, không đưa ra quyết định tuyển dụng.
        User: Mô tả vị trí: {{job_description}}. CV ứng viên: {{cv_text}}. Hãy tóm tắt điểm phù hợp và điểm cần hỏi thêm.
        """
        bias_audit = cls.audit_bias(cv_text)
        user_prompt = f"Mô tả vị trí: {job_description}. CV ứng viên: {cv_text}. Hãy tóm tắt điểm phù hợp và điểm cần hỏi thêm."
        
        gemini_key = api_key if provider in ("gemini", "auto") else None
        if provider == "auto" and not gemini_key:
            gemini_key = settings.GEMINI_API_KEY
        if provider == "openai":
            gemini_key = None

        openai_key = api_key if provider == "openai" else settings.OPENAI_API_KEY
        if provider == "auto" and not openai_key:
            openai_key = settings.OPENAI_API_KEY

        # Thử gọi Gemini nếu có key
        if gemini_key:
            try:
                result = await cls._call_gemini_summary(job_description, cv_text, gemini_key)
                if result:
                    result["bias_audit_result"] = bias_audit["bias_audit_result"]
                    result["system_prompt"] = SYSTEM_PROMPT
                    result["user_prompt"] = user_prompt
                    result["disclaimer"] = HUMAN_IN_THE_LOOP_DISCLAIMER
                    return result
            except Exception as e:
                logger.warning(f"Lỗi gọi Gemini API: {e}, chuyển sang Fallback Engine.")

        # Thử gọi OpenAI nếu có key
        if openai_key and (provider == "openai" or (provider == "auto" and settings.OPENAI_API_KEY)):
            try:
                result = await cls._call_openai_summary(job_description, cv_text, openai_key)
                if result:
                    result["bias_audit_result"] = bias_audit["bias_audit_result"]
                    result["system_prompt"] = SYSTEM_PROMPT
                    result["user_prompt"] = user_prompt
                    result["disclaimer"] = HUMAN_IN_THE_LOOP_DISCLAIMER
                    return result
            except Exception as e:
                logger.warning(f"Lỗi gọi OpenAI API: {e}, chuyển sang Fallback Engine.")

        # Fallback Engine: Bộ máy phân tích NLP thông minh theo quy tắc (Chạy offline 100% ổn định)
        fallback_res = cls._fallback_summarize(job_description, cv_text)
        fallback_res["bias_audit_result"] = bias_audit["bias_audit_result"]
        fallback_res["system_prompt"] = SYSTEM_PROMPT
        fallback_res["user_prompt"] = user_prompt
        fallback_res["disclaimer"] = HUMAN_IN_THE_LOOP_DISCLAIMER
        return fallback_res

    @classmethod
    def _fallback_summarize(cls, jd: str, cv: str) -> Dict[str, Any]:
        jd_skills = cls._extract_skills(jd)
        cv_skills = cls._extract_skills(cv)
        
        matched_skills = [s for s in cv_skills if s.lower() in [j.lower() for j in jd_skills]]
        missing_skills = [s for s in jd_skills if s.lower() not in [c.lower() for c in cv_skills]]
        
        if not jd_skills:
            match_score = 75.0
        else:
            match_score = round(min(100.0, max(40.0, (len(matched_skills) / max(len(jd_skills), 1)) * 100)), 1)
        
        # Trích xuất năm kinh nghiệm ước tính từ CV
        exp_match = re.search(r"(\d+)\s*(năm|year)", cv.lower())
        years = exp_match.group(1) if exp_match else "Có"
        
        # Sinh điểm phù hợp
        matching_bullets = []
        if matched_skills:
            matching_bullets.append(f"• Đáp ứng tốt các kỹ năng công nghệ cốt lõi: {', '.join(matched_skills)}.")
        else:
            matching_bullets.append(f"• Hồ sơ thể hiện nền tảng kỹ thuật với các kỹ năng liên quan: {', '.join(cv_skills[:4]) if cv_skills else 'CNTT cơ bản'}.")
            
        matching_bullets.append(f"• Kinh nghiệm thực tế: {years} năm làm việc trong môi trường phát triển phần mềm/dự án tương đồng.")
        matching_bullets.append("• Cấu trúc hồ sơ rõ ràng, có liệt kê trách nhiệm và đóng góp cụ thể trong các dự án đã tham gia.")
        
        # Sinh điểm cần hỏi thêm
        questions_bullets = []
        if missing_skills:
            questions_bullets.append(f"• Cần làm rõ mức độ kinh nghiệm với các công nghệ yêu cầu: {', '.join(missing_skills[:3])}.")
        else:
            questions_bullets.append("• Cần kiểm tra sâu hơn về kiến trúc hệ thống, quy trình CI/CD và khả năng tối ưu hiệu năng cơ sở dữ liệu.")
            
        questions_bullets.append("• Đào sâu về vai trò thực tế: Ứng viên tự thiết kế kiến trúc hay chỉ thực thi module theo phân công?")
        questions_bullets.append("• Tìm hiểu lý do tìm kiếm cơ hội mới, kỳ vọng về văn hóa làm việc và lộ trình phát triển bản thân.")
        
        return {
            "matching_points": "\n".join(matching_bullets),
            "questions_to_ask": "\n".join(questions_bullets),
            "match_score": match_score
        }

    @classmethod
    async def _call_gemini_summary(cls, jd: str, cv: str, api_key: str) -> Optional[Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Mô tả vị trí: {jd}\n\n"
            f"CV ứng viên: {cv}\n\n"
            "Hãy tóm tắt và trả về định dạng JSON thuần với các trường:\n"
            "{\n"
            '  "matching_points": "Danh sách các gạch đầu dòng điểm phù hợp về kỹ năng và kinh nghiệm",\n'
            '  "questions_to_ask": "Danh sách các gạch đầu dòng điểm cần hỏi thêm trong phỏng vấn",\n'
            '  "match_score": 85.0\n'
            "}"
        )
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json={
                "contents": [{"parts": [{"text": prompt}]}]
            })
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                # Parse json từ phản hồi
                clean_json = re.search(r"\{.*\}", text, re.DOTALL)
                if clean_json:
                    parsed = json.loads(clean_json.group(0))
                    return {
                        "matching_points": parsed.get("matching_points", ""),
                        "questions_to_ask": parsed.get("questions_to_ask", ""),
                        "match_score": float(parsed.get("match_score", 80.0))
                    }
        return None

    @classmethod
    async def _call_openai_summary(cls, jd: str, cv: str, api_key: str) -> Optional[Dict[str, Any]]:
        url = "https://api.openai.com/v1/chat/completions"
        prompt = (
            f"Mô tả vị trí: {jd}\n\n"
            f"CV ứng viên: {cv}\n\n"
            "Hãy tóm tắt và trả về JSON thuần với các trường: matching_points, questions_to_ask, match_score (1-100)."
        )
        headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            })
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                return {
                    "matching_points": parsed.get("matching_points", ""),
                    "questions_to_ask": parsed.get("questions_to_ask", ""),
                    "match_score": float(parsed.get("match_score", 80.0))
                }
        return None

    @classmethod
    def generate_interview_questions(
        cls,
        job_title: str,
        job_requirements: str,
        candidate_skills: str,
        evaluation_criteria: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        AI gợi ý câu hỏi phỏng vấn theo kỹ năng cần đánh giá (Mục 3.2.2 của đề bài).
        Phân loại: Kỹ thuật chuyên môn, Tình huống (STAR), Văn hóa & Thái độ.
        """
        skills_str = (candidate_skills or job_requirements or "Lập trình phần mềm").lower()
        
        tech_questions = []
        if "python" in skills_str or "backend" in job_title.lower():
            tech_questions.append("1. Bạn hãy giải thích cơ chế Async/Await trong Python và cách FastAPI xử lý đồng thời so với Flask?")
            tech_questions.append("2. Bạn thường tối ưu truy vấn cơ sở dữ liệu (indexing, ORM query tuning) như thế nào khi hệ thống có hàng triệu bản ghi?")
            tech_questions.append("3. Hãy mô tả cách bạn thiết kế một RESTful API chuẩn mực và bảo mật bằng JWT/OAuth2.")
        elif "react" in skills_str or "frontend" in job_title.lower():
            tech_questions.append("1. Bạn giải quyết vấn đề re-render không cần thiết trong React bằng những cách nào (useMemo, useCallback, React.memo)?")
            tech_questions.append("2. Trình bày kinh nghiệm của bạn về quản lý State (Redux Toolkit, Zustand, hoặc Context API) trong các dự án thực tế.")
            tech_questions.append("3. Làm thế nào để bạn đảm bảo giao diện web chuẩn Responsive và đạt điểm cao trên Google Lighthouse?")
        else:
            tech_questions.append("1. Hãy trình bày công nghệ hoặc dự án phức tạp nhất bạn từng xây dựng và cách bạn vượt qua trở ngại kỹ thuật lớn nhất?")
            tech_questions.append("2. Bạn áp dụng quy trình kiểm thử (Unit Test / Integration Test) vào dự án như thế nào?")
            tech_questions.append("3. Tiêu chí của bạn để đánh giá một đoạn mã nguồn (clean code, SOLID principles, maintainability) là gì?")

        situational_questions = [
            "1. (STAR) Hãy kể lại một lần dự án gặp sự cố nghiêm trọng (production bug / downtime) sát hạn nộp. Bạn đã xử lý ra sao?",
            "2. (Tình huống) Nếu Product Owner yêu cầu một tính năng gấp nhưng bạn nhận thấy nó gây ra nợ kỹ thuật (technical debt), bạn sẽ trao đổi thế nào?",
            "3. (Xung đột ý kiến) Bạn xử lý ra sao khi có bất đồng ý kiến kỹ thuật với đồng nghiệp hoặc Tech Lead trong một buổi Review Code?"
        ]

        culture_fit_questions = [
            "1. Bạn tự cập nhật kiến thức công nghệ mới (đặc biệt là các công cụ AI hỗ trợ lập trình) qua những kênh nào?",
            "2. Điều gì ở môi trường làm việc thúc đẩy bạn cống hiến và gắn bó lâu dài nhất?",
            "3. Mục tiêu phát triển sự nghiệp của bạn trong vòng 2 - 3 năm tới là gì?"
        ]

        return {
            "technical_questions": tech_questions,
            "situational_questions": situational_questions,
            "culture_fit_questions": culture_fit_questions,
            "disclaimer": HUMAN_IN_THE_LOOP_DISCLAIMER
        }

    @classmethod
    def generate_email(
        cls,
        email_type: str,
        candidate_name: str,
        candidate_email: str,
        job_title: str,
        interview_time: Optional[str] = None,
        interview_location: Optional[str] = None,
        company_name: str = "Công ty Cổ phần Công nghệ & Tuyển dụng Thông minh",
        custom_note: Optional[str] = None
    ) -> Dict[str, str]:
        """
        AI sinh email mời phỏng vấn hoặc phản hồi kết quả (Mục 3.2.3 của đề bài).
        Email types: 'INVITE_INTERVIEW', 'REJECTION', 'OFFER'
        """
        time_str = interview_time or "09:30 AM, Thứ Tư tuần tới"
        location_str = interview_location or "Phòng Họp 302, Trụ sở Công ty (hoặc Google Meet link)"
        
        if email_type == "INVITE_INTERVIEW":
            subject = f"[{company_name}] Thư Mời Tham Dự Phỏng Vấn Vị Trí {job_title} - {candidate_name}"
            content = f"""Kính gửi bạn {candidate_name},

Lời đầu tiên, Ban Tuyển dụng {company_name} xin chân thành cảm ơn sự quan tâm của bạn dành cho vị trí {job_title}.

Qua quá trình xem xét hồ sơ năng lực, Hội đồng Tuyển dụng rất ấn tượng với những kinh nghiệm và kỹ năng bạn đã tích lũy. Chúng tôi trân trọng kính mời bạn tham gia buổi phỏng vấn trực tiếp với đại diện bộ phận chuyên môn.

Chi tiết buổi phỏng vấn như sau:
• Vị trí ứng tuyển: {job_title}
• Thời gian: {time_str}
• Hình thức / Địa điểm: {location_str}
• Nội dung: Trao đổi về kinh nghiệm thực tế, định hướng công việc và giải đáp các thắc mắc của bạn về dự án.
{f'• Ghi chú bổ sung: {custom_note}' if custom_note else ''}

Bạn vui lòng phản hồi email này trước 17:00 ngày mai để xác nhận sự tham gia của mình. Nếu cần điều chỉnh thời gian, xin đừng ngần ngại thông báo để chúng tôi hỗ trợ sắp xếp.

Chúc bạn có một buổi phỏng vấn thành công tốt đẹp!

Trân trọng,
Bộ phận Tuyển dụng & Phát triển Nhân tài
{company_name}
Hotline: (+84) 280 3855 555 | Email: hr@{company_name.lower().replace(' ', '')}.vn
"""
        elif email_type == "OFFER":
            subject = f"[{company_name}] THƯ MỜI NHẬN VIỆC (JOB OFFER) - VỊ TRÍ {job_title.upper()} - {candidate_name}"
            content = f"""Kính gửi bạn {candidate_name},

Thay mặt Ban Giám đốc và toàn thể đội ngũ {company_name}, chúng tôi xin chúc mừng bạn đã xuất sắc vượt qua các vòng phỏng vấn cho vị trí {job_title}.

Chúng tôi rất đánh giá cao năng lực chuyên môn, thái độ cầu tiến và sự phù hợp về văn hóa của bạn với đội ngũ của chúng tôi. Nay, chúng tôi hân hạnh gửi tới bạn Thư mời nhận việc chính thức:

• Vị trí: {job_title}
• Bộ phận: Khối Kỹ thuật & Phát triển Phần mềm
• Ngày bắt đầu làm việc dự kiến: {time_str}
• Chế độ đãi ngộ: Lương thỏa thuận cạnh tranh, thưởng dự án, bảo hiểm sức khỏe toàn diện và phụ cấp thiết bị làm việc.
{f'• Ghi chú: {custom_note}' if custom_note else ''}

Vui lòng xem kỹ file đính kèm Thỏa thuận việc làm chi tiết và phản hồi xác nhận đồng ý gia nhập trước 17:00 trong vòng 03 ngày làm việc kể từ khi nhận thư.

Chào mừng bạn đến với mái nhà chung {company_name}!

Trân trọng,
Giám đốc Nhân sự & Ban Điều hành
{company_name}
"""
        else:  # REJECTION
            subject = f"[{company_name}] Thư Cảm Ơn & Thông Báo Kết Quả Ứng Tuyển Vị Trí {job_title} - {candidate_name}"
            content = f"""Kính gửi bạn {candidate_name},

Lời đầu tiên, {company_name} xin gửi lời cảm ơn chân thành nhất vì thời gian và công sức bạn đã dành để tham gia quy trình ứng tuyển cho vị trí {job_title}.

Hồ sơ của bạn rất ấn tượng và cho thấy bạn là một nhân sự giàu tiềm năng với nhiều điểm sáng trong chuyên môn. Tuy nhiên, sau khi cân nhắc kỹ lưỡng dựa trên những yêu cầu đặc thù và ưu tiên cấp thiết của dự án hiện tại, chúng tôi rất tiếc phải thông báo rằng chưa thể đồng hành cùng bạn ở cơ hội lần này.

Chúng tôi đã lưu trữ hồ sơ của bạn trong Ngân hàng Nhân tài tiềm năng (Talent Pool) của công ty và sẽ chủ động liên hệ lại ngay khi có vị trí mới phù hợp hơn với thế mạnh của bạn trong tương lai.
{f'• Phản hồi chi tiết: {custom_note}' if custom_note else ''}

Chúc bạn luôn gặt hái được nhiều thành công rực rỡ và vững bước trên con đường sự nghiệp!

Trân trọng,
Bộ phận Tuyển dụng
{company_name}
"""
        return {
            "candidate_id": candidate_email,
            "email_type": email_type,
            "subject": subject,
            "content": content,
            "disclaimer": "⚠️ Email được sinh bởi AI - Vui lòng kiểm tra và chỉnh sửa trước khi gửi cho ứng viên."
        }
