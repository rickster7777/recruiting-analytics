import csv
import math
import stripe
from django.contrib.auth import get_user_model, settings
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError, models
from django.http import StreamingHttpResponse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_filters.rest_framework import DjangoFilterBackend
from rest_auth.views import LoginView, PasswordChangeView, PasswordResetView
from rest_framework import (filters, generics, pagination, serializers, status,
                            viewsets)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from notifications.models import Notifications
from players.models import (Player, SchoolsVisit, FbsOffers)
from ra.settings.config_ra import main_conf as config
from ra_user.models import (MyBoard, UserBillingAddress, UserOtp,
                            UserSubscription, WatchList)
from ra_user.serializers import (CustomPasswordChangeSerializer,
                                 CustomPasswordResetSerializer,
                                 CustomTokenSerializer, GetMyBoardSerializer,
                                 GetUserBillingAddressSerializer,
                                 GetUserSerializer, GetWatchListSerializer,
                                 MyBoardSerializer, PatchUserSerializer,
                                 PutUserSerializer,
                                 UserBillingAddressSerializer,
                                 UserOtpSerializer, UserRoleSerializer,
                                 UserSerializer, UserSubscriptionSerializer,
                                 VerifyOtpSerializer, WatchListSerializer)
from address.models import College
from django.utils import timezone
from django.http import HttpResponse
User = get_user_model()

stripe.api_key = config.get('STRIPE_API_KEY')


class MyBoardWatchListPagination(pagination.PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'


# Helpers
def get_stripe_plan(plan):
    if plan == "yearly":
        return config.get('STRIPE_YEARLY_SUBSCRIPTION_ID')

    return config.get('STRIPE_MONTHLY_SUBSCRIPTION_ID')


def create_stripe_customer(user_email, token, plan):
    # if User.objects.filter(email__iexact=user_email).exists():
    customer = stripe.Customer.create(
        email=user_email,
        source=token,
    )
    try:
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
                {
                    'plan': get_stripe_plan(plan),
                },
            ],
            expand=['latest_invoice.payment_intent'],
        )
        return customer, subscription, None
    except stripe.error.CardError as e:
        return customer, None, e
    except stripe.error.InvalidRequestError as e:
        return customer, None, e
    # else:
    #     return False


class UserPagination(pagination.PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    Only staff user has permission to CRUD.status.HTTP_405_METHOD_NOT_ALLOWED
    """
    # permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    pagination_class = UserPagination
    serializer_class = UserSerializer
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )

    ordering_fields = ('id',
                        'username',
                        'first_name',
                        'last_name',
                        'title',
                        'email',
                        'cell_phone',
                        'coach_address__name',
                        'coach_address__address__city',
                        'coach_address__address__state',
                        'is_active'
                    )

    search_fields = ('id',
                     'username',
                     'first_name',
                     'email',
                     'title',
                     'cell_phone',
                     'coach_address__name',
                     'coach_address__address__city',
                     'coach_address__address__state',
                     )

    filter_fields = {
        'id': ['exact'],
        'first_name': ['iexact', 'icontains', 'istartswith'],
        'username': ['iexact', 'icontains', 'istartswith'],
        'email': ['iexact', 'icontains', 'istartswith'],
        'title': ['iexact', 'icontains', 'istartswith'],
        'college_address__name': ['iexact', 'icontains', 'istartswith'],
        'college_address': ['isnull'],
        'groups__name': ['iexact', 'icontains', 'istartswith'],
    }

    def get_queryset(self):

        user_group = User.objects.filter(
            username=self.request.user
        ).values_list('groups__name', flat=True)

        if self.request.query_params.get('delete_users'):
            user_ids = self.request.query_params.get('delete_users')
            ids = user_ids.split(',')
            for user_id in ids:
                user_obj = User.objects.get(id=user_id)
                if user_obj.subscription and user_obj.subscription.customer_id:
                    customer_id = user_obj.subscription.customer_id
                    stripe.Customer.delete(customer_id)
                    sbscription_obj = UserSubscription.objects.filter(subscription_id=user_obj.subscription.id)
                    sbscription_obj.delete()
                user_myboard = MyBoard.objects.filter(user__id=user_obj.id)
                user_myboard.delete()

                user_watchlist = WatchList.objects.filter(user__id=user_obj.id)
                user_watchlist.delete()

                user_notifications = Notifications.objects.filter(user__id=user_obj.id)
                user_notifications.delete()

            users = User.objects.filter(id__in=ids).delete()
            queryset = User.objects.none()

        if self.request.user.is_staff or 'admin' in user_group:
            queryset = User.objects.all()

        # elif 'coach' in user_group:
        #     queryset = User.objects.filter(username=self.request.user)
        elif self.request.user:
            queryset = User.objects.filter(username=self.request.user)
        else:
            queryset = User.objects.none()

        return queryset

    def create(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            if not User.objects.filter(email__iexact=request.POST.get('email')).exists():
                serializer.save()
                user = User.objects.get(username=request.data['username'])
                # if not User.objects.filter(email__iexact=user.email).exists():
                group = Group.objects.get(name='coach')
                user.is_active = True
                user.save()
                if user.subscription:
                    user.groups.add(group)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            else:
                raise serializers.ValidationError(
                    {
                        'error': "Email alreay exists",
                    }
                )

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'PUT':
            serializer_class = PutUserSerializer
        elif self.request.method == 'PATCH':
            serializer_class = PatchUserSerializer
        elif self.request.method == 'GET':
            serializer_class = GetUserSerializer
        return serializer_class

    def destroy(self, request, *args, **kwargs):
        try:
            user_obj = User.objects.get(id=self.kwargs["pk"])
            if user_obj:
                if user_obj.subscription and user_obj.subscription.customer_id:
                    customer_id = user_obj.subscription.customer_id
                    stripe.Customer.delete(customer_id)
                    sbscription_obj = UserSubscription.objects.filter(subscription_id=user_obj.subscription.id)
                    sbscription_obj.delete()
                user_myboard = MyBoard.objects.filter(user__id=user_obj.id)
                user_myboard.delete()

                user_watchlist = WatchList.objects.filter(user__id=user_obj.id)
                user_watchlist.delete()

                user_notifications = Notifications.objects.filter(user__id=user_obj.id)
                user_notifications.delete()

                user_obj.delete()

                return Response(status.HTTP_200_OK)
        except Exception as e:
            return Response("User not found")
            print(e)


class CustomLoginView(LoginView):
    """
    Check the credentials and return the REST Token
    if the credentials are valid and authenticated.

    Accept the following POST parameters: username, password
    Return the REST Framework Token Object's key and user id.
    """

    def get_response(self):
        serializer_class = CustomTokenSerializer
        user_group = User.objects.filter(
            username=self.user.username).values_list('groups__name', flat=True)
        if self.user.is_staff or 'admin' in user_group:
            if getattr(settings, 'REST_USE_JWT', False):
                data = {
                    'user': self.user,
                    'token': self.token
                }
                serializer = serializer_class(
                    instance=data, context={'request': self.request}
                )
            else:
                serializer = serializer_class(
                    instance=self.token, context={'request': self.request}
                )

            return Response(serializer.data, status=status.HTTP_200_OK)
        if 'coach' in user_group:
            if self.user.subscription:
                subscription = stripe.Subscription.retrieve(
                    self.user.subscription.subscription_id
                )
                if subscription.plan.active == True:
                    if getattr(settings, 'REST_USE_JWT', False):
                        data = {
                            'user': self.user,
                            'token': self.token
                        }
                        serializer = serializer_class(
                            instance=data, context={'request': self.request}
                        )
                    else:
                        serializer = serializer_class(
                            instance=self.token, context={
                                'request': self.request}
                        )

                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Subscription has been expired!"},
                                    status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"error": "Subscription not found."},
                            status=status.HTTP_401_UNAUTHORIZED)


class UserOtpViewSet(viewsets.ModelViewSet):

    pagination_class = UserPagination
    queryset = UserOtp.objects.all()
    serializer_class = UserOtpSerializer

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = ('id',
                       'otp',
                       'user__email',
                       'user__username',
                       )
    search_fields = (
        'id',
        'otp',
        'user__id'
        'user__email',
        'user__username',
    )

    filter_fields = {
        'id': ['exact'],
        'user__id': ['iexact', 'icontains', 'in'],
        'user__email': ['iexact', 'icontains', 'istartswith', 'in'],
        'user__username': ['iexact', 'icontains', 'istartswith', 'in'],

    }


class CustomPasswordResetView(PasswordResetView):
    """
        Calls Django Auth PasswordResetForm save method.
        Accepts the following POST parameters: email
        Returns the success/fail message.
    """
    serializer_class = CustomPasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        # Return the success message with OK HTTP status
        return Response(
            {"detail": ("Password reset e-mail has been sent.")},
            status=status.HTTP_200_OK
        )


class VerifyOtpView(CustomPasswordResetView):

    serializer_class = VerifyOtpSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.get(email=request.data['email'])
            uid = urlsafe_base64_encode(force_bytes(user.pk)),
            token = default_token_generator.make_token(user),

            return Response(
                {
                    "detail": ("Otp Verified successfully."),
                    "uid": uid,
                    "token": token
                }
            )


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """
        list:
            Return a list of all the existing user subscription.
        create:
            Create a new user subscription.
        retrieve:
            Return the given user subscription.
        update:
            Update the given user subscription.
        destroy:
            Delete the given user subscription.
        """
    pagination_class = UserPagination
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer

    # filterset_fields = 'user__email'

    def create(self, request, **kwargs):
        # Create Account
        user_subscription = UserSubscription()
        plan = request.data.get('plan')
        # stripeObject = create_stripe_customer(
        #     request.data.get('email'), request.data.get('card_token'), plan
        # )
        # if isinstance(stripeObject, bool):
        #     return Response(
        #         {
        #             "detail": ("User Already Exists."),
        #         }, status=status.HTTP_200_OK
        #     )
        # else:
        customer, subscription, error = create_stripe_customer(
            request.data.get('email'), request.data.get('card_token'), plan
        )

        user_subscription.customer_id = customer.id
        if subscription is None and error is not None:
            return Response(
                error.json_body,
                status.HTTP_400_BAD_REQUEST
            )
        # Create Subscription
        else:
            user_subscription.subscription_id = subscription.id
            user_subscription.plan = plan
            user_subscription.status = subscription.status
            user_subscription.save()
        # Handle Status
        return Response(
            UserSubscriptionSerializer(user_subscription).data,
            status.HTTP_201_CREATED
        )


class UserRoleViewSet(viewsets.ModelViewSet):
    """
        list:
            Return a list of all the existing user Role.
        create:
            Create a new user Role.
        retrieve:
            Return the given user Role.
        update:
            Update the given user Role.
        destroy:
            Delete the given user Role.
        """
    queryset = Group.objects.all()
    serializer_class = UserRoleSerializer


class MyBoardViewSet(viewsets.ModelViewSet):
    """
        list:
            Return a list of all the existing players in MyBoard.
        create:
            Create a new players in MyBoard.
        retrieve:
            Return the given players in MyBoard.
        update:
            Update the given players in MyBoard.
        destroy:
            Delete the given players in MyBoard.
    """
    pagination_class = MyBoardWatchListPagination
    permission_classes = (IsAuthenticated,)
    queryset = MyBoard.objects.all()
    serializer_class = MyBoardSerializer
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )

    filter_fields = {
        'id': ['exact'],
        'user__username': ['iexact', 'icontains', 'istartswith'],
        'player__first_name': ['iexact', 'icontains', 'startswith', 'in', 'isnull'],
        'player__last_name': ['iexact', 'icontains', 'startswith', 'in', 'isnull'],
        'player__full_name': ['iexact', 'icontains', 'istartswith', 'startswith', 'in', 'isnull'],
        'player__height': ['iexact', 'icontains', 'lt', 'gt', 'lte', 'gte', 'in', 'isnull'],
        'player__weight': ['iexact', 'lt', 'gt', 'lte', 'gte', 'istartswith', 'isnull', 'iexact', 'in'],
        'player__fourty_yard_dash': ['iexact', 'icontains', 'startswith',
                                     'istartswith', 'isnull', 'iexact', 'in'],
        'player__short_shuttle': ['iexact', 'icontains', 'isnull', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__vertical': ['iexact', 'icontains', 'istartswith', 'isnull', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__hundred_yard_dash': ['iexact', 'icontains', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__twitter_handle': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__jersey_number': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__role__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__school__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__position__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__position__group__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__classification__year': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__film_grade': ['iexact', 'icontains', 'istartswith', 'lt', 'gt', 'lte', 'gte', 'in', 'isnull'],
        'player__athleticism': ['iexact', 'icontains', 'istartswith', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__play_making': ['iexact', 'icontains', 'istartswith', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__top_speed': ['iexact', 'icontains', 'istartswith', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__rank': ['iexact', 'icontains', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__fbs_offers': ['isnull'],

    }

    def get_queryset(self):
        user_group = User.objects.filter(
            username=self.request.user
        ).values_list('groups__name', flat=True)

        if self.request.user.is_staff or 'admin' in user_group:

            queryset = MyBoard.objects.all().select_related('user', 'player')

        elif 'coach' in user_group:
            queryset = MyBoard.objects.filter(
                user=self.request.user)
        else:
            queryset = MyBoard.objects.none()

        return queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'GET':
            serializer_class = GetMyBoardSerializer
        return serializer_class


class WatchListViewSet(viewsets.ModelViewSet):
    """
        list:
            Return a list of all the existing players in WatchList.
        create:
            Create a new players in WatchList.
        retrieve:
            Return the given players in WatchList.
        update:
            Update the given players in WatchList.
        destroy:
            Delete the given players in WatchList.
    """
    pagination_class = MyBoardWatchListPagination
    permission_classes = (IsAuthenticated,)
    queryset = WatchList.objects.all()
    serializer_class = WatchListSerializer

    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )

    filter_fields = {
        'id': ['exact'],
        'user__username': ['iexact', 'icontains', 'istartswith'],
        'player__first_name': ['iexact', 'icontains', 'startswith', 'in', 'isnull'],
        'player__last_name': ['iexact', 'icontains', 'startswith', 'in', 'isnull'],
        'player__full_name': ['iexact', 'icontains', 'istartswith', 'startswith', 'in', 'isnull'],
        'player__height': ['iexact', 'icontains', 'lt', 'gt', 'lte', 'gte', 'in', 'isnull'],
        'player__weight': ['iexact', 'lt', 'gt', 'lte', 'gte', 'istartswith', 'isnull', 'iexact', 'in'],
        'player__fourty_yard_dash': ['iexact', 'icontains', 'startswith',
                                     'istartswith', 'isnull', 'iexact', 'in'],
        'player__short_shuttle': ['iexact', 'icontains', 'isnull', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__vertical': ['iexact', 'icontains', 'istartswith', 'isnull', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__hundred_yard_dash': ['iexact', 'icontains', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__twitter_handle': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__jersey_number': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__role__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__school__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__position__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__position__group__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__classification__year': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'player__film_grade': ['iexact', 'icontains', 'istartswith', 'lt', 'gt', 'lte', 'gte', 'in', 'isnull'],
        'player__athleticism': ['iexact', 'icontains', 'istartswith', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__play_making': ['iexact', 'icontains', 'istartswith', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__top_speed': ['iexact', 'icontains', 'istartswith', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__rank': ['iexact', 'icontains', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'player__fbs_offers': ['isnull'],

    }

    def get_queryset(self):
        user_group = User.objects.filter(
            username=self.request.user
        ).values_list('groups__name', flat=True)

        if self.request.user.is_staff or 'admin' in user_group:

            queryset = WatchList.objects.all().select_related('user', 'player')

        elif 'coach' in user_group:
            queryset = WatchList.objects.filter(
                user=self.request.user)
        else:
            queryset = WatchList.objects.none()

        return queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'GET':
            serializer_class = GetWatchListSerializer

        return serializer_class


class UserBillingAddressViewSet(viewsets.ModelViewSet):
    """
        list:
            Return a list of all the existing billing address in users.
        create:
            Create a new billing address in users.
        retrieve:
            Return the given billing address in users.
        update:
            Update the given billing address in users.
        destroy:
            Delete the given billing address in users.
    """
    pagination_class = UserPagination
    queryset = UserBillingAddress.objects.all()
    serializer_class = UserBillingAddressSerializer

    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )
    filter_fields = {
        'id': ['exact'],
        'city__name': ['iexact', 'icontains', 'istartswith'],
        'state__name': ['iexact', 'icontains', 'startswith', 'in', 'isnull'],
        'state__abbreviation': ['iexact', 'icontains', 'startswith', 'in', 'isnull'],
        'zip_code': ['iexact', 'icontains', 'startswith', 'in', 'isnull'],
    }

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'GET':
            serializer_class = GetUserBillingAddressSerializer

        return serializer_class


class CustomSetPasswordView(PasswordChangeView):
    """
    Override password change view to set value of Password is Hashed.
    And logout after the Changing User Password.
    """
    serializer_class = CustomPasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.password_set = True
        request.user.save()
        serializer.save()
        return Response({"detail": "New password has been saved."})


def myboard_export_view(request):
    # export_players = request.GET['export_players']
    # if request.GET['export_players'] == 'true':
    result = export_player_csv(request)
    return result


class MyboardPlayers:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def export_player_csv(request):
    board_type = request.GET['type']
    token = request.GET['token']
    request_user = Token.objects.get(key=token).user
    if board_type == "prospects":
        board_players = MyBoard.objects.select_related('user', 'player').filter(
            user=request_user,
        ).values_list('player__id', flat=True)
    elif board_type == "watchlist":
        board_players = WatchList.objects.filter(
            user=request_user,
        ).values_list('player__id', flat=True)
    user_board_players = Player.objects.filter(id__in=board_players)
    print(len(user_board_players))

    model = user_board_players.model
    model_fields = [

        model._meta.get_field('first_name'),
        model._meta.get_field('last_name'),
        model._meta.get_field('classification'),
        model._meta.get_field('position'),
        model._meta.get_field('school'),
        model._meta.get_field('city'),
        model._meta.get_field('state'),
        model._meta.get_field('film_grade'),
        model._meta.get_field('athleticism'),
        model._meta.get_field('play_making'),
        model._meta.get_field('height'),
        model._meta.get_field('weight'),
        model._meta.get_field('fourty_yard_dash'),
        model._meta.get_field('short_shuttle'),
        model._meta.get_field('jersey_number'),
        model._meta.get_field('star_rating'),
        model._meta.get_field('vertical'),
    ]

    model_fields1 = [
        model._meta.get_field('avg_transition_time'),
        model._meta.get_field('avg_yards_of_seperation'),
        model._meta.get_field('top_speed'),
        model._meta.get_field('time_to_top_speed'),
        model._meta.get_field('avg_closing_speed'),
        model._meta.get_field('interception'),
        model._meta.get_field('sack'),
        model._meta.get_field('touchdown'),

    ]

    headers = ['Player Details', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Performance Data', '', '', '', '', '', '', '', 'Social Engagement', '',
               '', '', '', '', '', '', '', 'IntangeAlytics - Personality', '', '', '', '', 'IntangeAlytics - Prospect Needs', '', '', '', '', 'IntangeAlytics - Values', '', '', '', '']

    Display_header = ['First Name', 'Last Name', 'Class', 'Position', 'High School', 'City', 'State',
                      'Film Grade', 'Athleticism', 'Playmaking', 'Height', 'Weight', '40 Yards', 'Short Shuttle', 'Jersey #',
                      'Star Rating', 'Vertical', 'Offers', 'Commit', 'Decommit', 'Visits', 'Avg Tranisition Time', 'Avg Yards of Seperation',
                      'Max Speed', 'Time to Max Speed', 'Avg Closing Speed', 'Interceptions', 'Sacks', 'Touchdowns',
                      'Twitter Handle', 'Followers', 'New Followers', 'Following', 'Number of Retweets',
                      'Key People (Followers)', 'Number of Tweets', 'Newly Followed',
                      'Key People (Following)', 'Team Player', 'Coachability', 'Extroverted', 'Temperment',
                      'Openness', 'Challenge', 'Structure', 'Stability', 'Excitement', 'Ideal', 'Tradition',
                      'Stimulation', 'Achievement', 'Helping Others', 'Taking Pleasure in life']

    headers1 = [field.name for field in model_fields]
    headers_fbs = [field.name for field in model_fields1]
    fbs_offers = ['offers', 'commit', 'decommit', 'visits']
    headers1 = headers1 + fbs_offers + headers_fbs

    headers1 = headers1 + ['twitter_handle',
                           'followers', 'following', 'new_followers', 'key_people_followers',
                           'key_people_followings',  'tweets', 'retweets', 'newly_followed',
                           'team_player', 'coachability', 'openness', 'extroverted', 'temperament',
                           'challenge', 'structure', 'stability', 'excitement', 'ideal', 'tradition', 'stimulation',
                           'helping_others', 'achievement', 'taking_pleasure_in_life']

    model_fields = model_fields+fbs_offers+model_fields1 + ['twitter_handle',
                                                            'followers', 'following', 'new_followers', 'key_people_followers',
                                                            'key_people_followings',  'tweets', 'retweets', 'newly_followed',
                                                            'team_player', 'coachability', 'openness', 'extroverted', 'temperament',
                                                            'challenge', 'structure', 'stability', 'excitement', 'ideal', 'tradition', 'stimulation',
                                                            'helping_others', 'achievement', 'taking_pleasure_in_life']

    def get_row(obj):
        row = []
        for field in model_fields:
            if type(field) == models.ForeignKey:
                val = getattr(obj, field.name)
                if val:
                    val = str(val)
                else:
                    val = ''
            elif type(field) == models.ManyToManyField:
                val = ', '.join([str(item) for item in getattr(
                    obj, field.name).all()])
            elif type(field) == models.DateTimeField:
                value = getattr(obj, field.name,)
                if value:
                    val = value.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    val = ''
            else:
                try:
                    if type(field) != str:
                        value = getattr(obj, field.name)
                        if field.name == 'height':
                            if value != None and value >= 0:
                                height_val = value
                                feet_obj = height_val / 12
                                feet = int(math.modf(feet_obj)[1])
                                remainder_value = 12 * feet
                                inches = int(height_val - remainder_value)

                                feet_inches = str(feet) + '\'' + str(inches)
                                val = feet_inches
                            else:
                                val = ''

                    if type(field) != str:
                        if field.name != 'height':
                            if value != '':
                                val = value
                            else:
                                val = ''

                    if type(field) == str:
                        if field == 'offers':
                            val = getattr(obj, 'fbs_offers')
                            if val:
                                if val.total != None:
                                    offers_lis = []
                                    f = FbsOffers.objects.filter(id=val.id).values_list(
                                        'schools__name', flat=True)
                                    try:
                                        for entries in f:
                                            if entries != None:
                                                offers_lis.append(entries)
                                        val = offers_lis
                                    except Exception as e:
                                        print(e)
                                        val = ''
                                else:
                                    val = ''
                            else:
                                val = ''
                        elif field == 'commit':
                            val = getattr(obj, 'fbs_offers')
                            if val:
                                if val.hard_commit != None and val.hard_commit.school != None and val.hard_commit.commited_on != None:
                                    val = str(val.hard_commit.school.name) + ', ' + \
                                        str(val.hard_commit.commited_on)
                                else:
                                    val = ''
                            else:
                                val = ''
                        elif field == 'decommit':
                            val = getattr(obj, 'fbs_offers')
                            if val:
                                if val.decommit != None:
                                    if val.decommit != None and val.decommit.school != None and val.decommit.decommited_on != None:
                                        val = str(val.decommit.school.name) + ', ' + \
                                            str(val.decommit.decommited_on)
                                    else:
                                        val = ''
                                else:
                                    val = ''
                            else:
                                val = ''
                        elif field == 'visits':
                            val = getattr(obj, 'fbs_offers')
                            if val:
                                visits_lis = []
                                f = SchoolsVisit.objects.filter(
                                    id=val.visits_id).values_list('schools__name', flat=True)
                                try:
                                    for entries in f:
                                        visits_lis.append(entries)
                                    val = visits_lis
                                except Exception as e:
                                    print(e)

                            else:
                                val = ''
                        elif field == 'twitter_handle':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.twitter_handle)
                            else:
                                val = ''
                        elif field == 'followers':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.followers)
                            else:
                                val = ''
                        elif field == 'following':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.following)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'new_followers':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.new_followers)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'key_people_followers':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.key_people_followers)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'key_people_followings':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.key_people_followings)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'tweets':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.tweets)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'retweets':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.retweets)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'newly_followed':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.newly_followed)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'team_player':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.personality.team_player)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'coachability':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.personality.coachability)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'openness':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.personality.openness)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'extroverted':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.personality.extroverted)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'temperament':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.personality.temperament)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'challenge':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.needs.challenge)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'structure':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.needs.structure)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'stability':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.needs.stability)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''

                        elif field == 'excitement':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.needs.excitement)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'ideal':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.needs.ideal)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'tradition':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.values.tradition)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'stimulation':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.values.stimulation)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'helping_others':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.values.helping_others)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'achievement':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.values.achievement)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'taking_pleasure_in_life':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.values.taking_pleasure_in_life)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        else:
                            val = ''
                except Exception as e:
                    print(e)
            if not val:
                val = ''
            row.append(str(val))
            val = ''
        return row

    def stream(headers, Display_header, players):  # Helper function to inject headers
        if headers:
            yield headers
        if Display_header:
            yield Display_header
        for obj in players:
            yield get_row(obj)
    pseudo_buffer = MyboardPlayers()
    writer = csv.writer(pseudo_buffer, delimiter='\t')
    response = StreamingHttpResponse(
        (writer.writerow(row)
         for row in stream(headers, Display_header, user_board_players)),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="user_board_players.csv"'
    return response


def export_user_csv(request):
    filters = {}
    if 'user_ids' in request.GET:
        filters['id__in'] = request.GET['user_ids'].split(',')
    user_list = User.objects.filter(
        **filters,
        groups__name__iexact='coach'
        )
    outer_lis = []
    for users in user_list:
        try:
            user_lis = []
            username = users.username
            first_name = users.first_name
            last_name = users.last_name
            email = users.email
            cell_phone = users.cell_phone
            title = users.title

            user_lis.append(username)
            user_lis.append(first_name)
            user_lis.append(last_name)
            user_lis.append(email)
            user_lis.append(cell_phone)
            user_lis.append(title)

            try:
                if users.college_address != None:
                #college_address = users.college_address
                    college_obj = users.college_address
                    try:
                        if college_obj.name:
                            college_name = college_obj.name
                    except Exception as e:
                        college_name = ''

                    try:
                        if college_obj.state.name:
                            state = college_obj.state.name
                    except Exception as e:
                        state = ''

                    try:
                        if college_obj.city.name:
                            city = college_obj.city.name
                    except Exception as e:
                        city = ''
                    try:
                        zip_code = college_obj.address.zip_code
                    except Exception as e:
                        zip_code = ''
                    try:
                        office_phone = college_obj.address.phone
                    except Exception as e:
                        office_phone = ''
                else:
                    college_name = ''
                    state = ''
                    city = ''
                    zip_code = ''
                    office_phone = ''


                user_lis.append(college_name)
                user_lis.append(state)
                user_lis.append(city)
                user_lis.append(zip_code)
                user_lis.append(office_phone)
                outer_lis.append(user_lis)

            except Exception as e:
                pass
                #print(e)
        except Exception as e:
            print(e)
    headers = ['Username','First Name','Last Name','Email-id','Cell Phone','Title','College Name','State','City','Zip Code','Office Phone']
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="admin_user_export.csv"'
    writer = csv.writer(response,delimiter='\t')
    writer.writerow(headers)
    writer.writerows(outer_lis)
    return response