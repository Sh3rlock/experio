from allauth.account.adapter import DefaultAccountAdapter


class ExperioAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.is_customer = True
        if commit:
            user.save()
        return user
