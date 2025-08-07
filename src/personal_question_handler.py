import re
from typing import Optional

USER_DEFINED_ANSWERS = {
    "referral": "No one referred me. I found this opportunity through your official listing.",
    "gender": "Male",
    "religion_or_caste": "Prefer not to disclose. I believe in equal opportunity based on merit.",
    "marital_status": "Single",
    "nationality": "Indian",
    "family_background": "My father is a farmer. I believe in hard work and learning from the ground up.",
    "medical_condition": "I have no medical conditions. I am fully fit and ready to take on this internship.",
    "work_eligibility": "Currently, I don't have a work visa for international roles. Open to remote roles.",
    "relocation": "I’m flexible. Location can be discussed based on internship needs.",
    "referrals": "I do not have any current referrals in the organization.",
    "strengths_and_weaknesses": "Yes, I have a good mix of technical knowledge and eagerness to learn. I'm constantly improving my time management and communication skills.",
    "handling_stress": "I handle stress by playing games and balancing it with short mental breaks. It helps me stay focused and calm."
}

QUESTION_PATTERNS = {
    "referral": re.compile(r"referr(ed|al)|who told|who asked", re.I),
    "gender": re.compile(r"gender|male|female|pronoun", re.I),
    "religion_or_caste": re.compile(r"religion|caste|community|faith", re.I),
    "marital_status": re.compile(r"marital status|married|single|spouse|wife|husband", re.I),
    "nationality": re.compile(r"nationality|citizen|country", re.I),
    "family_background": re.compile(r"family|father|mother|parents|background", re.I),
    "medical_condition": re.compile(r"medical|health|disability|illness|disease|fit", re.I),
    "work_eligibility": re.compile(r"work permit|visa|eligibility|authorized|authorization", re.I),
    "relocation": re.compile(r"relocat(e|ion)|move|shift|transfer", re.I),
    "referrals": re.compile(r"referral|reference|recommend(ed|ation)", re.I),
    "strengths_and_weaknesses": re.compile(r"strength|weakness|improve|improvement", re.I),
    "handling_stress": re.compile(r"stress|pressure|cope|deal with stress", re.I)
}

FALLBACK_ANSWER = (
    "I prefer to focus on my skills, experience, and how I can contribute to your organization. "
    "If you need any specific information, please let me know."
)

class PersonalQuestionHandler:
    def __init__(self, user_answers=None):
        self.answers = user_answers or USER_DEFINED_ANSWERS
        self.patterns = QUESTION_PATTERNS

    def handle(self, question: str) -> str:
        q = question.strip().lower()
        for key, pattern in self.patterns.items():
            if pattern.search(q):
                return self.answers.get(key, FALLBACK_ANSWER)
        return FALLBACK_ANSWER

# Example usage:
# handler = PersonalQuestionHandler()
# answer = handler.handle("What is your religion?")
# print(answer)