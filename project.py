import streamlit as st
import os, time, random, base64, io
from PIL import Image
import nltk
from streamlit_tags import st_tags
from custom_resume_parser import ResumeParser
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter

nltk.download('stopwords')

st.set_page_config(page_title="AI Resume Analyzer", page_icon='./Logo/logo2.png')

# ---------------- PDF Functions ---------------- #
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 🎓**")
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    rec_course = []
    for i, (c_name, c_link) in enumerate(course_list):
        if i == no_of_reco:
            break
        st.markdown(f"({i+1}) [{c_name}]({c_link})")
        rec_course.append(c_name)
    return rec_course

# ---------------- Main App ---------------- #
def run():
    img = Image.open('./Logo/logo2.png')
    st.image(img)
    st.title("AI Resume Analyzer")

    st.sidebar.markdown("## Select User Type")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Mode:", activities)

    if choice == "User":
        st.markdown("### ✨ Upload your resume and get insights")

        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file:
            save_path = os.path.join('./Uploaded_Resumes', pdf_file.name)
            os.makedirs('./Uploaded_Resumes', exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            with st.spinner('Analyzing your Resume...'):
                time.sleep(2)

            show_pdf(save_path)
            resume_data = ResumeParser(save_path).get_extracted_data()

            if resume_data:
                resume_text = pdf_reader(save_path)

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data.get('name', 'Candidate'))

                st.text(f"Name: {resume_data.get('name', '')}")
                st.text(f"Email: {resume_data.get('email', '')}")
                st.text(f"Contact: {resume_data.get('mobile_number', '')}")
                st.text(f"Pages: {resume_data.get('no_of_pages', '')}")

                pages = resume_data.get('no_of_pages', 0)
                if pages == 1:
                    st.info("🔹 You are at Fresher Level")
                elif pages == 2:
                    st.success("🟢 You are Intermediate Level")
                elif pages >= 3:
                    st.warning("🔶 You are Experienced")

                st_tags(label='### Your Current Skills',
                        text='See our skills recommendation below',
                        value=resume_data['skills'], key='1')

                all_skills = [s.lower() for s in resume_data['skills']]
                reco_field = ''
                recommended_skills = []
                rec_course = []

                fields = {
                    'Data Science': ds_course,
                    'Web Development': web_course,
                    'Android Development': android_course,
                    'IOS Development': ios_course,
                    'UI-UX Development': uiux_course
                }

                keywords_dict = {
                    'Data Science': ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit'],
                    'Web Development': ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'flask'],
                    'Android Development': ['android', 'flutter', 'kotlin', 'xml', 'kivy'],
                    'IOS Development': ['ios', 'swift', 'cocoa', 'xcode'],
                    'UI-UX Development': ['ux', 'adobe xd', 'figma', 'zeplin', 'ui']
                }

                for field, keywords in keywords_dict.items():
                    if any(skill in keywords for skill in all_skills):
                        reco_field = field
                        st.success(f"✅ Our analysis says you're interested in **{field}**")
                        recommended_skills = keywords[:5]
                        st_tags(label='### Recommended Skills', value=recommended_skills, key='rec-skills')
                        rec_course = course_recommender(fields[field])
                        break

                st.subheader("**Resume Score📝**")
                resume_score = 0
                for section in ['Objective', 'Declaration', 'Hobbies', 'Interests', 'Achievements', 'Projects']:
                    if section.lower() in resume_text.lower():
                        resume_score += 20

                my_bar = st.progress(0)
                for percent_complete in range(resume_score):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1)

                st.success(f'**Your Resume Score: {resume_score} / 100**')

                st.header("**Bonus Video for Resume Writing Tips💡**")
                st.video(random.choice(resume_videos))

                st.header("**Bonus Video for Interview Tips💡**")
                st.video(random.choice(interview_videos))

            else:
                st.error("❌ Couldn't parse your resume. Please try a different file.")

    elif choice == "Admin":
        st.subheader("🔐 Admin Login")

        if "admin_logged_in" not in st.session_state:
            st.session_state.admin_logged_in = False
        if "required_skills_input" not in st.session_state:
            st.session_state.required_skills_input = ""
        if "pdf_file" not in st.session_state:
            st.session_state.pdf_file = None

        if not st.session_state.admin_logged_in:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.button("Login")

            if login_button:
                if username == "ahmed" and password == "123123":
                    st.session_state.admin_logged_in = True
                    st.success("✅ Logged in successfully as ahmed")
                else:
                    st.error("❌ Incorrect username or password.")

        if st.session_state.admin_logged_in:
            st.session_state.required_skills_input = st.text_input(
                "✍️ Enter required skills (separate by comma)",
                value=st.session_state.required_skills_input
            )

            if st.session_state.required_skills_input:
                required_skills = [s.lower().strip() for s in st.session_state.required_skills_input.replace("،", ",").split(",")]
                st.markdown(f"### 🎯 Required Skills: {required_skills}")

                uploaded_file = st.file_uploader("📥 Upload Resume (PDF only)", type=["pdf"])
                if uploaded_file:
                    st.session_state.pdf_file = uploaded_file

                if st.session_state.pdf_file:
                    save_path = os.path.join('./Uploaded_Resumes', st.session_state.pdf_file.name)
                    os.makedirs('./Uploaded_Resumes', exist_ok=True)
                    with open(save_path, "wb") as f:
                        f.write(st.session_state.pdf_file.getbuffer())
                    st.success("📄 Resume uploaded successfully")

                    data = ResumeParser(save_path).get_extracted_data()
                    if data:
                        resume_skills = [s.lower().strip() for s in data.get("skills", [])]
                        st.markdown("### ✅ Extracted Skills from Resume:")
                        st.write(resume_skills)

                        matched = list(set(resume_skills).intersection(required_skills))
                        missing = list(set(required_skills) - set(resume_skills))

                        st.markdown("#### ✅ Matched Skills:")
                        if matched:
                            st.success(matched)
                        else:
                            st.warning("No matching skills found")

                        st.markdown("#### ❌ Missing Skills:")
                        if missing:
                            st.error(missing)
                        else:
                            st.success("All required skills are present")

                        score = (len(matched) / len(required_skills)) * 100 if required_skills else 0
                        st.info(f"📊 Compatibility Score: **{score:.2f}%**")

                        if score >= 70:
                            st.success("✅ Result: Accepted")
                        else:
                            st.error("❌ Result: Failed")
                    else:
                        st.error("❌ Failed to extract data from the resume.")
            else:
                st.info("⏳ Please enter required skills first")


if __name__ == '__main__':
    run()
