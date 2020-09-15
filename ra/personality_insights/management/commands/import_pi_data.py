import csv
import json
import os
import sys
import ssl
import requests
import twitter
import urllib3
from django.core.management.base import BaseCommand
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import PersonalityInsightsV3
from unidecode import unidecode
from players.models import Player
from social_engagement.models import SocialEngagement
from personality_insights.models import (PersonalityInsights, ProspectsNeeds,
                                         ProspectsPersonality, ProspectsValues)
from ra.settings.config_ra import main_conf as config


class Command(BaseCommand):

    help = 'Used to add Personality Insights for Players'

    def handle(self, *args, **options):
        # The Twitter API credentials
        twitter_consumer_key = config.get('twitter_consumer_key')
        twitter_consumer_secret = config.get('twitter_consumer_secret')
        twitter_access_token = config.get('twitter_access_token')
        twitter_access_secret = config.get('twitter_access_secret')

        # Invoking the Twitter API
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        twitter_api = twitter.Api(consumer_key=twitter_consumer_key,
                                  consumer_secret=twitter_consumer_secret,
                                  access_token_key=twitter_access_token,
                                  access_token_secret=twitter_access_secret
                                  )

        twitter_handle_players = Player.objects.filter(
            twitter_handle__isnull=False,
            personality_insight__isnull=True).distinct()
        print(len(twitter_handle_players), '- players handle are founded')

        for player in twitter_handle_players:

            try:
                handle = player.twitter_handle
                if handle != '':
                    # Retrieving the last no of tweets from a user
                    ssl._create_default_https_context = ssl._create_unverified_context
                    statuses = twitter_api.GetUserTimeline(
                        screen_name=unidecode(player.twitter_handle), count=200, include_rts=False)
                    # Putting all 10000 tweets into one large string called "text"
                    content = ""
                    last_status = statuses[0].text
                    for status in statuses:
                        if (status.lang == 'en'):
                            content += status.text
                    while len(content.split()) <= 2000:
                        content += content

                    # Analyzing the 10000 tweets with the Watson PI API
                    authenticator = IAMAuthenticator(
                        config.get('pi_server_key'))
                    personality_insights = PersonalityInsightsV3(
                        version='2019-10-30',
                        authenticator=authenticator)
                    personality_insights.set_disable_ssl_verification(True)
                    personality_insights.set_service_url(
                        'https://gateway-wdc.watsonplatform.net/personality-insights/api')
                    if len(content.split()) > 100:
                        profile = personality_insights.profile(content=content,
                                                               accept='application/json'
                                                               ).get_result()
                        # data.append(handle)
                        # Prospects Personality
                        personality = profile['personality']

                        raw_team_player = profile['personality'][3]['percentile']
                        team_player = "{:.1%}".format(
                            raw_team_player).replace('%', '')
                        team_player_rounded_val = float(team_player)
                        percentile_team_player = round(
                            team_player_rounded_val)
                        # data.append(str(percentile_team_player) + '%')

                        raw_coachability = profile['personality'][1]['percentile']
                        coachability = "{:.1%}".format(
                            raw_coachability).replace('%', '')
                        coachability_rounded_val = float(coachability)
                        percentile_coachability = round(
                            coachability_rounded_val)
                        # data.append(str(percentile_coachability) + '%')

                        raw_openness = profile['personality'][0]['percentile']
                        openness = "{:.1%}".format(
                            raw_openness).replace('%', '')
                        openness_rounded_val = float(openness)
                        percentile_openness = round(openness_rounded_val)
                        # data.append(str(percentile_openness) + '%')

                        raw_extraverted = profile['personality'][2]['percentile']
                        extraverted = "{:.1%}".format(
                            raw_extraverted).replace('%', '')
                        extraverted_rounded_val = float(extraverted)
                        percentile_extraverted = round(
                            extraverted_rounded_val)
                        # data.append(str(percentile_extraverted) + '%')

                        raw_temperament = profile['personality'][4]['percentile']
                        temperament = "{:.1%}".format(
                            raw_temperament).replace('%', '')
                        temperament_rounded_val = float(temperament)
                        percentile_temperament = round(
                            temperament_rounded_val)
                        # data.append(str(percentile_temperament) + '%')

                        # Prospects Needs

                        raw_challenge = profile['needs'][0]['percentile']
                        challenge = "{:.1%}".format(
                            raw_challenge).replace('%', '')
                        challenge_rounded_val = float(challenge)
                        percentile_challenge = round(challenge_rounded_val)
                        # data.append(str(percentile_challenge) + '%')

                        raw_structure = profile['needs'][11]['percentile']
                        structure = "{:.1%}".format(
                            raw_structure).replace('%', '')
                        structure_rounded_val = float(structure)
                        percentile_structure = round(structure_rounded_val)
                        # data.append(str(percentile_structure) + '%')

                        raw_stability = profile['needs'][10]['percentile']
                        stability = "{:.1%}".format(
                            raw_stability).replace('%', '')
                        stability_rounded_val = float(stability)
                        percentile_stability = round(stability_rounded_val)
                        # data.append(str(percentile_stability) + '%')

                        raw_excitement = profile['needs'][3]['percentile']
                        excitement = "{:.1%}".format(
                            raw_excitement).replace('%', '')
                        excitement_rounded_val = float(excitement)
                        percentile_excitement = round(
                            excitement_rounded_val)
                        # data.append(str(percentile_excitement) + '%')

                        raw_ideal = profile['needs'][5]['percentile']
                        ideal = "{:.1%}".format(raw_ideal).replace('%', '')
                        ideal_rounded_val = float(ideal)
                        percentile_ideal = round(ideal_rounded_val)
                        # data.append(str(percentile_ideal) + '%')

                        # Prospects Values
                        raw_tradition = profile['values'][0]['percentile']
                        tradition = "{:.1%}".format(
                            raw_tradition).replace('%', '')
                        tradition_rounded_val = float(tradition)
                        percentile_tradition = round(tradition_rounded_val)
                        # data.append(str(percentile_tradition) + '%')

                        raw_stimulation = profile['values'][1]['percentile']
                        stimulation = "{:.1%}".format(
                            raw_stimulation).replace('%', '')
                        stimulation_rounded_val = float(stimulation)
                        percentile_stimulation = round(
                            stimulation_rounded_val)
                        # data.append(str(percentile_stimulation) + '%')

                        raw_helping_others = profile['values'][4]['percentile']
                        helping_others = "{:.1%}".format(
                            raw_helping_others).replace('%', '')
                        helping_others_rounded_val = float(helping_others)
                        percentile_helping_others = round(
                            helping_others_rounded_val)
                        # data.append(str(percentile_helping_others) + '%')

                        raw_achievement = profile['values'][3]['percentile']
                        achievement = "{:.1%}".format(
                            raw_achievement).replace('%', '')
                        achievement_rounded_val = float(achievement)
                        percentile_achievement = round(
                            achievement_rounded_val)
                        # data.append(str(percentile_achievement) + '%')

                        raw_taking_pleasure_in_life = profile['values'][2]['percentile']
                        taking_pleasure_in_life = "{:.1%}".format(
                            raw_taking_pleasure_in_life).replace('%', '')
                        taking_pleasure_in_life_rounded_val = float(
                            taking_pleasure_in_life)
                        percentile_taking_pleasure_in_life = round(
                            taking_pleasure_in_life_rounded_val)
                        # data.append(str(percentile_taking_pleasure_in_life) + '%')

                        if player.personality_insight is not None and \
                                player.personality_insight.personality is not None:
                            prospect_personality_obj = \
                                ProspectsPersonality.objects.get(
                                    id=player.personality_insight.personality.id
                                )
                            prospect_personality_obj.team_player = \
                                percentile_team_player
                            prospect_personality_obj.coachability = \
                                percentile_coachability
                            prospect_personality_obj.openness = \
                                percentile_openness
                            prospect_personality_obj.extroverted = \
                                percentile_extraverted
                            prospect_personality_obj.temperament = \
                                percentile_temperament
                            prospect_personality_obj.save()
                        else:
                            prospect_personality_obj = ProspectsPersonality.objects.create(
                                team_player=percentile_team_player,
                                coachability=percentile_coachability,
                                openness=percentile_openness,
                                extroverted=percentile_extraverted,
                                temperament=percentile_temperament
                            )
                        if player.personality_insight is not None and \
                                player.personality_insight.needs is not None:
                            prospect_needs_obj = ProspectsNeeds.objects.get(
                                id=player.personality_insight.needs.id
                            )
                            prospect_needs_obj.challenge = percentile_challenge
                            prospect_needs_obj.structure = percentile_structure
                            prospect_needs_obj.stability = percentile_stability
                            prospect_needs_obj.excitement = percentile_excitement
                            prospect_needs_obj.ideal = percentile_ideal
                            prospect_needs_obj.save()
                        else:
                            prospect_needs_obj = ProspectsNeeds.objects.create(
                                challenge=percentile_challenge,
                                structure=percentile_structure,
                                stability=percentile_stability,
                                excitement=percentile_excitement,
                                ideal=percentile_ideal,
                            )
                        if player.personality_insight is not None and \
                                player.personality_insight.values is not None:
                            prospect_values_obj = ProspectsValues.objects.get(
                                id=player.personality_insight.values.id
                            )
                            prospect_values_obj.tradition = percentile_tradition
                            prospect_values_obj.stimulation = \
                                percentile_stimulation
                            prospect_values_obj.helping_others = \
                                percentile_helping_others
                            prospect_values_obj.achievement = \
                                percentile_achievement
                            prospect_values_obj.taking_pleasure_in_life = \
                                percentile_taking_pleasure_in_life
                            prospect_values_obj.save()
                        else:
                            prospect_values_obj = ProspectsValues.objects.create(
                                tradition=percentile_tradition,
                                stimulation=percentile_stimulation,
                                helping_others=percentile_helping_others,
                                achievement=percentile_achievement,
                                taking_pleasure_in_life=percentile_taking_pleasure_in_life,
                            )
                        if player.personality_insight is not None:
                            personality_insights = \
                                PersonalityInsights.objects.get(
                                    id=player.personality_insight.id
                                )
                            personality_insights.personality = prospect_personality_obj
                            personality_insights.needs = prospect_needs_obj
                            personality_insights.values = prospect_values_obj
                            personality_insights.save()
                        else:
                            personality_insights = PersonalityInsights.objects.create(
                                personality=prospect_personality_obj,
                                needs=prospect_needs_obj,
                                values=prospect_values_obj,
                            )
                            player.personality_insight = personality_insights
                            player.save()
                        print(
                            player.first_name, '-', handle, "player PI and twiiter information added successfully")
            except Exception as e:
                print(e, player.full_name,' - ',  player.twitter_handle)

        twitter_handle_players = Player.objects.filter(
            twitter_handle__isnull=False,
            personality_insight__personality__openness__isnull=True).distinct()
        print(len(twitter_handle_players), '- players handle are founded')

        for player in twitter_handle_players:

            try:
                handle = player.twitter_handle
                if handle != '':
                    # Retrieving the last no of tweets from a user
                    ssl._create_default_https_context = ssl._create_unverified_context
                    statuses = twitter_api.GetUserTimeline(
                        screen_name=unidecode(player.twitter_handle), count=200, include_rts=False)
                    # Putting all 10000 tweets into one large string called "text"
                    content = ""
                    last_status = statuses[0].text
                    for status in statuses:
                        if (status.lang == 'en'):
                            content += status.text
                    while len(content.split()) <= 2000:
                        content += content

                    # Analyzing the 10000 tweets with the Watson PI API
                    authenticator = IAMAuthenticator(
                        config.get('pi_server_key'))
                    personality_insights = PersonalityInsightsV3(
                        version='2019-10-30',
                        authenticator=authenticator)
                    personality_insights.set_disable_ssl_verification(True)
                    personality_insights.set_service_url(
                        'https://gateway-wdc.watsonplatform.net/personality-insights/api')
                    if len(content.split()) > 100:
                        profile = personality_insights.profile(content=content,
                                                               accept='application/json'
                                                               ).get_result()
                        # data.append(handle)
                        # Prospects Personality
                        personality = profile['personality']

                        raw_team_player = profile['personality'][3]['percentile']
                        team_player = "{:.1%}".format(
                            raw_team_player).replace('%', '')
                        team_player_rounded_val = float(team_player)
                        percentile_team_player = round(
                            team_player_rounded_val)
                        # data.append(str(percentile_team_player) + '%')

                        raw_coachability = profile['personality'][1]['percentile']
                        coachability = "{:.1%}".format(
                            raw_coachability).replace('%', '')
                        coachability_rounded_val = float(coachability)
                        percentile_coachability = round(
                            coachability_rounded_val)
                        # data.append(str(percentile_coachability) + '%')

                        raw_openness = profile['personality'][0]['percentile']
                        openness = "{:.1%}".format(
                            raw_openness).replace('%', '')
                        openness_rounded_val = float(openness)
                        percentile_openness = round(openness_rounded_val)
                        # data.append(str(percentile_openness) + '%')

                        raw_extraverted = profile['personality'][2]['percentile']
                        extraverted = "{:.1%}".format(
                            raw_extraverted).replace('%', '')
                        extraverted_rounded_val = float(extraverted)
                        percentile_extraverted = round(
                            extraverted_rounded_val)
                        # data.append(str(percentile_extraverted) + '%')

                        raw_temperament = profile['personality'][4]['percentile']
                        temperament = "{:.1%}".format(
                            raw_temperament).replace('%', '')
                        temperament_rounded_val = float(temperament)
                        percentile_temperament = round(
                            temperament_rounded_val)
                        # data.append(str(percentile_temperament) + '%')

                        # Prospects Needs

                        raw_challenge = profile['needs'][0]['percentile']
                        challenge = "{:.1%}".format(
                            raw_challenge).replace('%', '')
                        challenge_rounded_val = float(challenge)
                        percentile_challenge = round(challenge_rounded_val)
                        # data.append(str(percentile_challenge) + '%')

                        raw_structure = profile['needs'][11]['percentile']
                        structure = "{:.1%}".format(
                            raw_structure).replace('%', '')
                        structure_rounded_val = float(structure)
                        percentile_structure = round(structure_rounded_val)
                        # data.append(str(percentile_structure) + '%')

                        raw_stability = profile['needs'][10]['percentile']
                        stability = "{:.1%}".format(
                            raw_stability).replace('%', '')
                        stability_rounded_val = float(stability)
                        percentile_stability = round(stability_rounded_val)
                        # data.append(str(percentile_stability) + '%')

                        raw_excitement = profile['needs'][3]['percentile']
                        excitement = "{:.1%}".format(
                            raw_excitement).replace('%', '')
                        excitement_rounded_val = float(excitement)
                        percentile_excitement = round(
                            excitement_rounded_val)
                        # data.append(str(percentile_excitement) + '%')

                        raw_ideal = profile['needs'][5]['percentile']
                        ideal = "{:.1%}".format(raw_ideal).replace('%', '')
                        ideal_rounded_val = float(ideal)
                        percentile_ideal = round(ideal_rounded_val)
                        # data.append(str(percentile_ideal) + '%')

                        # Prospects Values
                        raw_tradition = profile['values'][0]['percentile']
                        tradition = "{:.1%}".format(
                            raw_tradition).replace('%', '')
                        tradition_rounded_val = float(tradition)
                        percentile_tradition = round(tradition_rounded_val)
                        # data.append(str(percentile_tradition) + '%')

                        raw_stimulation = profile['values'][1]['percentile']
                        stimulation = "{:.1%}".format(
                            raw_stimulation).replace('%', '')
                        stimulation_rounded_val = float(stimulation)
                        percentile_stimulation = round(
                            stimulation_rounded_val)
                        # data.append(str(percentile_stimulation) + '%')

                        raw_helping_others = profile['values'][4]['percentile']
                        helping_others = "{:.1%}".format(
                            raw_helping_others).replace('%', '')
                        helping_others_rounded_val = float(helping_others)
                        percentile_helping_others = round(
                            helping_others_rounded_val)
                        # data.append(str(percentile_helping_others) + '%')

                        raw_achievement = profile['values'][3]['percentile']
                        achievement = "{:.1%}".format(
                            raw_achievement).replace('%', '')
                        achievement_rounded_val = float(achievement)
                        percentile_achievement = round(
                            achievement_rounded_val)
                        # data.append(str(percentile_achievement) + '%')

                        raw_taking_pleasure_in_life = profile['values'][2]['percentile']
                        taking_pleasure_in_life = "{:.1%}".format(
                            raw_taking_pleasure_in_life).replace('%', '')
                        taking_pleasure_in_life_rounded_val = float(
                            taking_pleasure_in_life)
                        percentile_taking_pleasure_in_life = round(
                            taking_pleasure_in_life_rounded_val)
                        # data.append(str(percentile_taking_pleasure_in_life) + '%')

                        if player.personality_insight is not None and \
                                player.personality_insight.personality is not None:
                            prospect_personality_obj = \
                                ProspectsPersonality.objects.get(
                                    id=player.personality_insight.personality.id
                                )
                            prospect_personality_obj.team_player = \
                                percentile_team_player
                            prospect_personality_obj.coachability = \
                                percentile_coachability
                            prospect_personality_obj.openness = \
                                percentile_openness
                            prospect_personality_obj.extroverted = \
                                percentile_extraverted
                            prospect_personality_obj.temperament = \
                                percentile_temperament
                            prospect_personality_obj.save()
                        else:
                            prospect_personality_obj = ProspectsPersonality.objects.create(
                                team_player=percentile_team_player,
                                coachability=percentile_coachability,
                                openness=percentile_openness,
                                extroverted=percentile_extraverted,
                                temperament=percentile_temperament
                            )
                        if player.personality_insight is not None and \
                                player.personality_insight.needs is not None:
                            prospect_needs_obj = ProspectsNeeds.objects.get(
                                id=player.personality_insight.needs.id
                            )
                            prospect_needs_obj.challenge = percentile_challenge
                            prospect_needs_obj.structure = percentile_structure
                            prospect_needs_obj.stability = percentile_stability
                            prospect_needs_obj.excitement = percentile_excitement
                            prospect_needs_obj.ideal = percentile_ideal
                            prospect_needs_obj.save()
                        else:
                            prospect_needs_obj = ProspectsNeeds.objects.create(
                                challenge=percentile_challenge,
                                structure=percentile_structure,
                                stability=percentile_stability,
                                excitement=percentile_excitement,
                                ideal=percentile_ideal,
                            )
                        if player.personality_insight is not None and \
                                player.personality_insight.values is not None:
                            prospect_values_obj = ProspectsValues.objects.get(
                                id=player.personality_insight.values.id
                            )
                            prospect_values_obj.tradition = percentile_tradition
                            prospect_values_obj.stimulation = \
                                percentile_stimulation
                            prospect_values_obj.helping_others = \
                                percentile_helping_others
                            prospect_values_obj.achievement = \
                                percentile_achievement
                            prospect_values_obj.taking_pleasure_in_life = \
                                percentile_taking_pleasure_in_life
                            prospect_values_obj.save()
                        else:
                            prospect_values_obj = ProspectsValues.objects.create(
                                tradition=percentile_tradition,
                                stimulation=percentile_stimulation,
                                helping_others=percentile_helping_others,
                                achievement=percentile_achievement,
                                taking_pleasure_in_life=percentile_taking_pleasure_in_life,
                            )
                        if player.personality_insight is not None:
                            personality_insights = \
                                PersonalityInsights.objects.get(
                                    id=player.personality_insight.id
                                )
                            personality_insights.personality = prospect_personality_obj
                            personality_insights.needs = prospect_needs_obj
                            personality_insights.values = prospect_values_obj
                            personality_insights.save()
                        else:
                            personality_insights = PersonalityInsights.objects.create(
                                personality=prospect_personality_obj,
                                needs=prospect_needs_obj,
                                values=prospect_values_obj,
                            )
                            player.personality_insight = personality_insights
                            player.save()
                        print(
                            player.first_name, '-', handle, "player PI and twiiter information added successfully")
            except Exception as e:
                print(e, player.full_name,' - ',  player.twitter_handle)
        print("All Players Personality Insights Data added successfully")
