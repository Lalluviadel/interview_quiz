from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic.base import View


class UserDispatchMixin(View):
    @method_decorator(user_passes_test(lambda user: user.is_authenticated))
    def dispatch(self, request, *args, **kwargs):
        return super(UserDispatchMixin, self).dispatch(request, *args, **kwargs)
