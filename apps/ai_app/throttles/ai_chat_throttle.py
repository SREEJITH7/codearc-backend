from rest_framework.throttling import UserRateThrottle


class AiChatThrottle(UserRateThrottle):
    scope = "ai_chat"
    rate = "20/day"