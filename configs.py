SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

SUBJECT = '''
    Referral Request for {position} – Would Appreciate Your Help!
    '''
MAIL_BODY = '''Hi {name},

I hope you’re doing well. I’m currently working as an AI Backend Engineer at Inviz Labs and recently came across an opening for a {position} role at {company}. I’d love to apply and would truly appreciate it if you could consider referring me.  

Why me?  
- ~3 years of experience building scalable AI/ML solutions.  
- Delivered an AI-powered RAG chatbot with GPT/Gemini for Nasdaq’s staging environment.  
- Built Shopflow, an AI conversational agent handling millions of SKUs and multi-intent queries.  
- Designed recommendation engines and cloud-based ML services for 1M+ users using PySpark, GCP, FastAPI, and Docker.  

I’ve attached my resume for your reference. Thank you for your time and consideration!  

Thanks,
Shashank
+91-7483402123
'''

RESUME_PATH = r"D:\DOCS\CV\Shashank-Resume.pdf"
LEAVE_MSG = ["out of office", "wasn't delivered", "could not be delivered", "delivered", "postmaster",
             "address not found", "ooo", "leave", "no access", "blocked", "delayed response"]
TIME_DIFF_FAILURE = 120
