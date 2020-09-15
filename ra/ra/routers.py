from rest_framework import routers

from address import views as address_views
from personality_insights import views as pi_views
from players import views as player_views
from ra_user import views as ra_user_views
from social_engagement import views as social_views
from notifications import views as notification_views
router = routers.DefaultRouter()


# RA_Users Router
router.register(r'users', ra_user_views.UserViewSet, base_name='user')

router.register(r'user_roles', ra_user_views.UserRoleViewSet,
                base_name="user_roles")

router.register(r'user_otp', ra_user_views.UserOtpViewSet,
                base_name='user_otp')

router.register(r'user_subscription', ra_user_views.UserSubscriptionViewSet,
                base_name='user_subscription')


router.register(r'watchlists', ra_user_views.WatchListViewSet,
                base_name='watchlists')

router.register(r'my_board', ra_user_views.MyBoardViewSet,
                base_name='my_board')

router.register(r'user_billing_address', ra_user_views.UserBillingAddressViewSet,
                base_name='user_billing_address')

# Address Router
router.register(r'address', address_views.AddressViewSet, base_name="address")

router.register(r'cities', address_views.CityViewSet, base_name="cities")

router.register(r'states', address_views.StateViewSet, base_name="states")

router.register(
    r'regions', address_views.RegionViewSet, base_name="regions")

router.register(r'country', address_views.CountryViewSet, base_name="country")
# Schools Router
router.register(r'schools', address_views.SchoolViewSet, base_name="schools")

# College Router
router.register(r'colleges', address_views.CollegeViewSet,
                base_name="colleges")
# Players Router
router.register(r'players', player_views.PlayerViewSet, base_name="players")

router.register(r'players_type', player_views.PlayerTypeViewSet,
                base_name="players_type")

router.register(r'player_notes', player_views.NotesViewSet,
                base_name="player_notes")

router.register(r'player_types', player_views.PlayerTypeViewSet,
                base_name="player_types")

router.register(r'classications', player_views.ClassificationViewSet,
                base_name="classifications")

router.register(r'positions', player_views.PositionsViewSet,
                base_name="positions")

router.register(r'position_groups', player_views.PositionGroupViewSet,
                base_name="position_groups")

# router.register(r'uc_prospects', player_views.UndercruitedPlayersViewSet,
# base_name='uc_prospects')

router.register(r'personality_insights',
                pi_views.PersonalityInsightViewSet,
                base_name='personality_insights')

router.register(r'prospect_personality',
                pi_views.ProspectPersonalityViewSet,
                base_name='prospect_personality')

router.register(r'prospect_needs', pi_views.ProspectNeedsViewSet,
                base_name='prospect_needs')

router.register(r'prospect_values', pi_views.ProspectValuesViewSet,
                base_name='prospect_values')

router.register(r'school_visits', player_views.SchoolsVisitViewSet,
                base_name='school_visits')

router.register(r'fbs_offers', player_views.FbsOffersViewSet,
                base_name='fbs_offers')

router.register(r'fbs_hard_commit', player_views.FbsHardCommitViewSet,
                base_name='fbs_hard_commit')

router.register(r'fbs_decommits', player_views.FbsDeCommitViewSet,
                base_name='fbs_decommits')


router.register(r'fitfinder_searches', player_views.SavedSearchViewSet,
                base_name='fitfinder_searches')

router.register(r'social_engagements', social_views.SocialEngagementViewSet,
                base_name='social_engagements')

router.register(r'performance_rankings', player_views.PerformanceRankingViewSet,
                base_name='performance_rankings')

router.register(r'player_notifications', notification_views.NotificationsViewSet,
                base_name='player_notifications')

router.register(r'comments', player_views.CommentsViewSet,
                base_name='comments')

router.register(r'fbs_schools', player_views.FbsSchoolsViewSet,
                base_name='fbs_schools')


router.register(r'notification_reports', notification_views.NotificationsReportViewSet,
                base_name='notification_reports')
