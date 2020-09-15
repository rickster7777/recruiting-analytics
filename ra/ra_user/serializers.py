from django.contrib.auth import get_user_model, settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
import math
from rest_auth.models import TokenModel as Token
from rest_auth.serializers import (LoginSerializer, PasswordChangeSerializer,
                                   PasswordResetConfirmSerializer,
                                   PasswordResetSerializer, TokenSerializer)
from rest_framework import serializers
from rest_framework.serializers import Serializer
from rest_auth.app_settings import settings as setting
from players.models import Notes, Player, Positions
from ra_user.forms import CustomSetPasswordForm, ForgotPasswordForm
from ra_user.models import (MyBoard, UserBillingAddress, UserOtp,
                            UserSubscription, WatchList)
# from players.serializers import GetPlayerSerializer


User = get_user_model()


class GetUserSerializer(serializers.ModelSerializer):
    """
    Django inbuilt User model serializers
    """

    class Meta:
        """
        Serializing all fields
        """
        model = User
        exclude = ('password', 'last_login', 'date_joined', 'user_permissions',
                   'is_superuser', 'is_staff')
        depth = 3


class UserSerializer(serializers.ModelSerializer):
    """
    Django inbuilt User model serializers
    """

    class Meta:
        """
        Serializing all fields
        """
        model = User
        fields = '__all__'

    def validate_password(self, password: str) -> str:
        return make_password(password)


class PutUserSerializer(serializers.ModelSerializer):
    """
    Custom User Model for excludes some fields
    """
    class Meta:
        model = User
        exclude = ('password', 'last_login', 'date_joined', 'user_permissions',
                   'is_superuser', 'is_staff')

    def validate_password(self, password: str) -> str:
        return make_password(password)


class PatchUserSerializer(serializers.ModelSerializer):
    """
    Custom User Model for excludes some fields
    """
    class Meta:
        model = User
        exclude = ('last_login', 'date_joined', 'user_permissions',
                   'is_superuser', 'is_staff')

    def validate_password(self, password: str) -> str:
        return make_password(password)


class CustomTokenSerializer(TokenSerializer):
    """
    Custom Token serializers
      - We have customized rest-auth TokenSerializer to
        get token key and user id.
    """
    user_data = serializers.SerializerMethodField('get_user')

    def get_user(self, obj):

        user_data = User.objects.get(username=self.instance.user)
        return GetUserSerializer(user_data).data

    class Meta:
        model = Token
        fields = ('key', "created", 'user_data')


class UserOtpSerializer(serializers.ModelSerializer):
    """
    UserOtp model serializers
    """
    # expired_on = serializers.DateField(
    #     format="%Y-%m-%d %H:%M:%S", read_only=True)
    # created_on = serializers.DateField(
    #     format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        """
        Serializing all fields
        """
        model = UserOtp
        fields = '__all__'
        depth = 1


class CustomPasswordResetSerializer(PasswordResetSerializer,
                                    serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()
    domain = serializers.CharField()

    password_reset_form_class = ForgotPasswordForm

    def get_email_options(self):
        return {}

    def validate_email(self, value):
        self.reset_form = self.password_reset_form_class(
            data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    def save(self):
        request = self.context.get('request')
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)


# Verify OTP Serializer
class VerifyOtpSerializer(serializers.Serializer):

    otp = serializers.IntegerField()
    email = serializers.EmailField()

    def validate(self, attrs):
        # user_email = CustomPasswordResetSerializer.validate_email(
        #     self, attrs['email'])
        verify_otp = UserOtp.objects.get(user__email=attrs['email'])
        if timezone.now() < verify_otp.created_at + timezone.timedelta(minutes=15):
            if attrs['otp'] != verify_otp.otp:
                raise serializers.ValidationError(
                    "Otp is Invalid!"
                )
        else:
            raise serializers.ValidationError(
                "Otp is Invalid!"
            )
        verify_otp.verified = True
        verify_otp.save()
        return True


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """
        User Subscription serializers
    """
    user = GetUserSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['id', 'customer_id', 'subscription_id', 'plan', 'status',
                  'user']


class UserRoleSerializer(serializers.ModelSerializer):
    """ UserRoles Serializer """
    class Meta:
        model = Group
        fields = '__all__'


class MyBoardSerializer(serializers.ModelSerializer):
    """ MyBoard Serializer """
    class Meta:
        model = MyBoard
        fields = '__all__'


class PlayerBoardSerializer(serializers.ModelSerializer):
    """ Player MyBoard Serializer for exclude some fields which no longer used """
    class Meta:
        model = Player
        exclude = ('notes', 'social_engagement', 'team', 'personality_insight',
                   )
        depth = 2


class UsersBoardSerializer(serializers.ModelSerializer):
    """ Users MyBoard Serializer """
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email',
                  'groups', 'is_active', 'title', 'cell_phone', )
        read_only_fields = (fields, )
        depth = 1


class GetMyBoardSerializer(serializers.ModelSerializer):
    """ MyBoard Serializer """
    pin_user_watchlist = serializers.SerializerMethodField()
    user_note = serializers.SerializerMethodField()
    player_height = serializers.SerializerMethodField()
    player = PlayerBoardSerializer(read_only=True)
    user = UsersBoardSerializer(read_only=True)

    class Meta:
        model = MyBoard
        fields = '__all__'
        # depth = 3
        read_only_fields = (fields, )

    def get_player_height(self, myboard):
        if myboard.player.height != None and myboard.player.height > 0:
            height_val = myboard.player.height
            feet_obj = height_val / 12
            feet = int(math.modf(feet_obj)[1])
            remainder_value = 12 * feet
            inches = int(height_val - remainder_value)

            feet_inches = str(feet) + '.' + str(inches)
            return feet_inches
        else:
            return None

    def get_user_note(self, myboard):
        request_user = self._context['request'].user
        user_group = User.objects.filter(
            username=request_user.username
        ).values_list('groups__name', flat=True)
        if 'coach' in user_group and request_user.college_address is not None \
                and request_user.college_address.name is not None:
            user_notes = Notes.objects.select_related(
                'created_by').prefetch_related('comments').filter(
                created_by__college_address__name=request_user.college_address.name,
                id__in=myboard.player.notes.all()).distinct()
        else:
            user_notes = None
        if user_notes:
            return getattr(myboard, 'user_note', True)
        else:
            return getattr(myboard, 'user_note', False)

    def get_pin_user_watchlist(self, watchlist):
        request_user = self._context['request'].user
        user_watchlist = WatchList.objects.select_related('user', 'player', ).filter(
            user=request_user,
            player__id=watchlist.player.id)
        if user_watchlist:
            return getattr(watchlist, 'pin_user_watchlist', True)
        else:
            return getattr(watchlist, 'pin_user_watchlist', False)


class WatchListSerializer(serializers.ModelSerializer):
    """ WatchList Serializer """

    class Meta:
        model = WatchList
        fields = '__all__'


class GetWatchListSerializer(serializers.ModelSerializer):
    """ WatchList Serializer """
    pin_user_board = serializers.SerializerMethodField()
    user_note = serializers.SerializerMethodField()
    player_height = serializers.SerializerMethodField()
    player = PlayerBoardSerializer(read_only=True)
    user = UsersBoardSerializer(read_only=True)

    class Meta:
        model = WatchList
        fields = '__all__'
        depth = 4

    def get_player_height(self, watchlist):
        if watchlist.player.height != None and watchlist.player.height > 0:
            height_val = watchlist.player.height
            feet_obj = height_val / 12
            feet = int(math.modf(feet_obj)[1])
            remainder_value = 12 * feet
            inches = int(height_val - remainder_value)

            feet_inches = str(feet) + '.' + str(inches)
            return feet_inches
        else:
            return None

    def get_user_note(self, watchlist):
        request_user = self._context['request'].user
        user_group = User.objects.filter(
            username=request_user.username
        ).values_list('groups__name', flat=True)
        if 'coach' in user_group and request_user.college_address is not None \
                and request_user.college_address.name is not None:
            user_notes = Notes.objects.select_related('created_by',
                                                      ).prefetch_related('comments').filter(
                created_by__college_address__name=request_user.college_address.name,
                id__in=watchlist.player.notes.all()).distinct()
        else:
            user_notes = None

        if user_notes:
            return getattr(watchlist, 'user_note', True)
        else:
            return getattr(watchlist, 'user_note', False)

    def get_pin_user_board(self, myboard):
        request_user = self._context['request'].user
        user_board = MyBoard.objects.select_related('user', 'player').filter(
            user=request_user,
            player__id=myboard.player.id)
        if user_board:
            return getattr(myboard, 'pin_user_board', True)
        else:
            return getattr(myboard, 'pin_user_board', False)


class UserBillingAddressSerializer(serializers.ModelSerializer):
    """ UserBillingAddress Serializer """

    class Meta:
        model = UserBillingAddress
        fields = '__all__'


class GetUserBillingAddressSerializer(serializers.ModelSerializer):
    """ UserBillingAddress Serializer """

    class Meta:
        model = UserBillingAddress
        fields = '__all__'
        depth = 2


class CustomPasswordChangeSerializer(PasswordChangeSerializer):
    """
    Custom Password Change Serializer for showing Old password field.
    And Logout after the change password
    """

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = getattr(
            settings, 'OLD_PASSWORD_FIELD_ENABLED', True
        )
        self.logout_on_password_change = getattr(
            settings, 'LOGOUT_ON_PASSWORD_CHANGE', True
        )
        super(PasswordChangeSerializer, self).__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop('old_password')

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value)
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError('Invalid password')
        return value

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, self.user)
