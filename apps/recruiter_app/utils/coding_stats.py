from django.core.cache import cache
from apps.problem_app.models import Submission
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

# def calculate_coding_stats(user):
#     cache_key = f"user_coding_stats_{user.id}"
#     cached_stats = cache.get(cache_key)
#     if cached_stats:
#         return cached_stats

#     # High-performance database aggregation
#     stats_data = Submission.objects.filter(user=user).aggregate(
#         total_attempts=Count('id'),
#         accepted_count=Count('id', filter=Q(status='Accepted')),
#         easy=Count('id', filter=Q(status='Accepted', problem__difficulty='EASY')),
#         medium=Count('id', filter=Q(status='Accepted', problem__difficulty='MEDIUM')),
#         hard=Count('id', filter=Q(status='Accepted', problem__difficulty='HARD')),
#         total_solved=Count('problem', distinct=True, filter=Q(status='Accepted'))
#     )

#     total_attempts = stats_data['total_attempts']
#     accepted_count = stats_data['accepted_count']
    
#     acceptance_rate = (
#         round((accepted_count / total_attempts) * 100, 2)
#         if total_attempts > 0
#         else 0.0
#     )
    
#     easy = stats_data['easy']
#     medium = stats_data['medium']
#     hard = stats_data['hard']
    
#     coding_score = (easy * 1) + (medium * 3) + (hard * 6)

#     stats = {
#         "easy": easy,
#         "medium": medium,
#         "hard": hard,
#         "totalSolved": stats_data['total_solved'],
#         "acceptanceRate": acceptance_rate,
#         "score": coding_score,
#     }
    
#     # Cache for 10 minutes
#     cache.set(cache_key, stats, 600)
#     return stats




def calculate_coding_stats(user):
    submissions = Submission.objects.filter(
        user=user,
        status="Accepted"
    ).select_related("problem")

    easy = medium = hard = 0
    total_attempts = submissions.count()

    for sub in submissions:
        if sub.problem.difficulty == "EASY":
            easy += 1
        elif sub.problem.difficulty == "MEDIUM":
            medium += 1
        elif sub.problem.difficulty == "HARD":
            hard += 1

    total_solved = easy + medium + hard

    # acceptance_rate = (
    #     round((total_solved / total_attempts) * 100, 2)
    #     if total_attempts > 0
    #     else 0.0
    # )

    score = (easy * 1) + (medium * 3) + (hard * 6)

    return {
        "easy": easy,
        "medium": medium,
        "hard": hard,
        "totalSolved": total_solved,
        # "acceptanceRate": acceptance_rate,
        "score": score,
    }



User = get_user_model()

def calculate_ranks_for_users():
    cache_key = "global_user_ranks"
    cached_ranks = cache.get(cache_key)
    if cached_ranks:
        return cached_ranks

    users_with_scores = User.objects.annotate(
        easy=Count('submission', filter=Q(submission__status='Accepted', submission__problem__difficulty='EASY')),
        medium=Count('submission', filter=Q(submission__status='Accepted', submission__problem__difficulty='MEDIUM')),
        hard=Count('submission', filter=Q(submission__status='Accepted', submission__problem__difficulty='HARD')),
    ).annotate(
        total_score=(Count('submission', filter=Q(submission__status='Accepted', submission__problem__difficulty='EASY')) * 1) +
                    (Count('submission', filter=Q(submission__status='Accepted', submission__problem__difficulty='MEDIUM')) * 3) +
                    (Count('submission', filter=Q(submission__status='Accepted', submission__problem__difficulty='HARD')) * 6)
    ).values('id', 'total_score').order_by('-total_score')

    rank_map = {}
    for index, item in enumerate(users_with_scores, start=1):
        rank_map[item['id']] = index
        
    
    cache.set(cache_key, rank_map, 300)
    return rank_map
