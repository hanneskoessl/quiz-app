def can_access_quiz(user, quiz, token=None):
    if quiz.owner == user:
        return True
    
    if quiz.visibility == "private":
        return False

    if quiz.allowed_users.filter(id=user.id).exists():
        return True
    
    if quiz.visibility == "unlisted" and str(quiz.share_token) == str(token):
        return True

    return False
