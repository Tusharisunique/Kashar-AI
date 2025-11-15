
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** Kashar AI
- **Date:** 2025-11-15
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001
- **Test Name:** test user signup api
- **Test Code:** [TC001_test_user_signup_api.py](./TC001_test_user_signup_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 129, in <module>
  File "<string>", line 30, in test_user_signup_api
AssertionError: Expected 201 or 200 but got 400

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/3cc27e53-0626-4910-9c41-115e313ea325/9c4c8058-ef77-4cd4-ac72-f189dbecd45c
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002
- **Test Name:** test user login api
- **Test Code:** [TC002_test_user_login_api.py](./TC002_test_user_login_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 96, in <module>
  File "<string>", line 83, in test_user_login_api
AssertionError: Error message field missing or not string in response #6

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/3cc27e53-0626-4910-9c41-115e313ea325/152ea522-8573-40bb-a81a-cc7d2aec62b8
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003
- **Test Name:** test pdf upload api
- **Test Code:** [TC003_test_pdf_upload_api.py](./TC003_test_pdf_upload_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 74, in <module>
  File "<string>", line 34, in test_pdf_upload_api
AssertionError: Unexpected status code: 403 - {"detail":"Not authenticated"}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/3cc27e53-0626-4910-9c41-115e313ea325/a04b842e-d1e1-4d75-87dd-41e86249223a
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004
- **Test Name:** test get user documents api
- **Test Code:** [TC004_test_get_user_documents_api.py](./TC004_test_get_user_documents_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 53, in <module>
  File "<string>", line 19, in test_get_user_documents_api
AssertionError: Expected status code 200 but got 403

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/3cc27e53-0626-4910-9c41-115e313ea325/d15150b2-d025-4836-8fec-f64414c109a4
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005
- **Test Name:** test start tutor session api
- **Test Code:** [TC005_test_start_tutor_session_api.py](./TC005_test_start_tutor_session_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 86, in <module>
  File "<string>", line 25, in test_start_tutor_session_api
AssertionError: Expected success status code for session_type=text, got 403

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/3cc27e53-0626-4910-9c41-115e313ea325/deaf58b8-9431-4173-91be-7afed13181c3
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC006
- **Test Name:** test send message to ai tutor api
- **Test Code:** [TC006_test_send_message_to_ai_tutor_api.py](./TC006_test_send_message_to_ai_tutor_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 112, in <module>
  File "<string>", line 66, in test_send_message_to_ai_tutor_api
AssertionError: AI response is empty or invalid

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/3cc27e53-0626-4910-9c41-115e313ea325/422f7c5a-6cbe-472e-a9da-77fb1c48ca52
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC007
- **Test Name:** test generate quiz api
- **Test Code:** [TC007_test_generate_quiz_api.py](./TC007_test_generate_quiz_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 81, in <module>
  File "<string>", line 41, in test_generate_quiz_api
AssertionError: Unexpected status code: 403 for payload: {'topic': 'Mathematics', 'difficulty': 'medium', 'num_questions': 5}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/3cc27e53-0626-4910-9c41-115e313ea325/f87dc712-b3ec-49e4-9fd9-882edbe77386
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC008
- **Test Name:** test submit quiz answers api
- **Test Code:** [TC008_test_submit_quiz_answers_api.py](./TC008_test_submit_quiz_answers_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 82, in <module>
  File "<string>", line 34, in test_submit_quiz_answers_api
AssertionError: Expected status 200/201 but got 500

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/3cc27e53-0626-4910-9c41-115e313ea325/67c7449c-5cf0-46df-9571-5416740db1a9
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC009
- **Test Name:** test generate flashcards api
- **Test Code:** [TC009_test_generate_flashcards_api.py](./TC009_test_generate_flashcards_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 116, in <module>
  File "<string>", line 63, in test_generate_flashcards_api
AssertionError: Number of flashcards generated does not match requested num_cards

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/3cc27e53-0626-4910-9c41-115e313ea325/2a967c98-4047-4aac-9d1a-570f7804d604
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC010
- **Test Name:** test get user progress data api
- **Test Code:** [TC010_test_get_user_progress_data_api.py](./TC010_test_get_user_progress_data_api.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/3cc27e53-0626-4910-9c41-115e313ea325/da7f6ce9-0e07-4c9f-9e25-59a31db9acab
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **10.00** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---