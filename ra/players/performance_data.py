def get_playmaking(player, playmaking):
    print('success')
    interception_raw_score_val = playmaking[0]
    sacks_raw_score_val = playmaking[1]
    touchdowns_raw_score_val = playmaking[2]
    if interception_raw_score_val != (None and ''):
        interception_raw_score = interception_raw_score_val
    else:
        interception_raw_score = None
    if sacks_raw_score_val != (None and ''):
        sacks_raw_score = sacks_raw_score_val
    else:
        sacks_raw_score = None
    if touchdowns_raw_score_val != (None and ''):
        touchdowns_raw_score = touchdowns_raw_score_val
    else:
        touchdowns_raw_score = None

    if interception_raw_score != None:
        if 0 <= interception_raw_score <= 0.99:
            interception_val = 50
        elif 1 <= interception_raw_score <= 1.99:
            interception_val = 60
        elif 2 <= interception_raw_score <= 3.99:
            interception_val = 70
        elif 4 <= interception_raw_score <= 5.99:
            interception_val = 80
        elif 6 <= interception_raw_score <= 7.99:
            interception_val = 90
        elif interception_raw_score >= 8:
            interception_val = 100
        else:
            interception_val = 0
    else:
        interception_val = 0
    if sacks_raw_score != None:
        if 0 <= sacks_raw_score <= 0.99:
            sack_val = 50
        elif 1 <= sacks_raw_score <= 2.99:
            sack_val = 60
        elif 3 <= sacks_raw_score <= 4.99:
            sack_val = 70
        elif 5 <= sacks_raw_score <= 6.99:
            sack_val = 80
        elif 7 <= sacks_raw_score <= 8.99:
            sack_val = 90
        elif sacks_raw_score >= 9:
            sack_val = 100
        else:
            sack_val = 0
    else:
        sack_val = 0
    if touchdowns_raw_score != None:
        if 0 <= touchdowns_raw_score <= 0.99:
            touchdown_val = 50
        elif 1 <= touchdowns_raw_score <= 2.99:
            touchdown_val = 60
        elif 3 <= touchdowns_raw_score <= 4.99:
            touchdown_val = 70
        elif 5 <= touchdowns_raw_score <= 6.99:
            touchdown_val = 80
        elif 7 <= touchdowns_raw_score <= 8.99:
            touchdown_val = 90
        elif touchdowns_raw_score >= 9:
            touchdown_val = 100
        else:
            touchdown_val = 0
    else:
        touchdown_val = 0

    if interception_val != None:
        if interception_val == 100:
            interception_score = 55
            interception_score_perc = 6
        elif interception_val == 90:
            interception_score = 49.5
            interception_score_perc = 5
        elif interception_val == 80:
            interception_score = 44
            interception_score_perc = 4
        elif interception_val == 70:
            interception_score = 38.5
            interception_score_perc = 3
        elif interception_val == 60:
            interception_score = 33
            interception_score_perc = 2
        elif interception_val == 50:
            interception_score = 27.5
            interception_score_perc = 1
        else:
            interception_score = 0
            interception_score_perc = 0
    else:
        interception_score = 0
        interception_score_perc = 0
    if sack_val != None:
        if sack_val == 100:
            sack_score = 15
            sack_score_perc = 6
        elif sack_val == 90:
            sack_score = 13.5
            sack_score_perc = 5
        elif sack_val == 80:
            sack_score = 12
            sack_score_perc = 4
        elif sack_val == 70:
            sack_score = 10.5
            sack_score_perc = 3
        elif sack_val == 60:
            sack_score = 9
            sack_score_perc = 2
        elif sack_val == 50:
            sack_score = 7.5
            sack_score_perc = 1
        else:
            sack_score = 0
            sack_score_perc = 0
    else:
        sack_score = 0
        sack_score_perc = 0
    if touchdown_val != None:
        if touchdown_val == 100:
            touchdown_score = 30
            touchdown_score_perc = 6
        elif touchdown_val == 90:
            touchdown_score = 27
            touchdown_score_perc = 5
        elif touchdown_val == 80:
            touchdown_score = 24
            touchdown_score_perc = 4
        elif touchdown_val == 70:
            touchdown_score = 21
            touchdown_score_perc = 3
        elif touchdown_val == 60:
            touchdown_score = 18
            touchdown_score_perc = 2
        elif touchdown_val == 50:
            touchdown_score = 15
            touchdown_score_perc = 1
        else:
            touchdown_score = 0
            touchdown_score_perc = 0
    else:
        touchdown_score = 0
        touchdown_score_perc = 0

    playmaking_score = (interception_score +
                        sack_score+touchdown_score)
    if interception_val != 0:
        interception_play_making_raw = (
            interception_score * interception_score_perc) / interception_val
    else:
        interception_play_making_raw = 0
    if sack_val != 0:
        sack_play_making_raw = (
            sack_score * sack_score_perc) / sack_val
    else:
        sack_play_making_raw = 0
    if touchdown_val != 0:
        touchdown_play_making_raw = (
            touchdown_score * touchdown_score_perc) / touchdown_val
    else:
        touchdown_play_making_raw = 0
    total_play_making = (
        interception_play_making_raw + sack_play_making_raw + touchdown_play_making_raw)
    if playmaking_score >= 1:
        player.play_making = playmaking_score
    else:
        player.play_making = None
    if total_play_making > 0:
        player.play_making_raw_score = total_play_making
    else:
        player.play_making_raw_score = None
    return playmaking_score


def get_athleticism(player, athleticism_analyze):
    avg_yrd_separation = athleticism_analyze['avg_yards_of_seperation']
    avgtranstime = athleticism_analyze['avg_transition_time']
    topspeed = athleticism_analyze['top_speed']
    avgclospeed = athleticism_analyze['avg_closing_speed']
    timetotopspeed = athleticism_analyze['time_to_top_speed']

    # Avg Yard of Sepeeration
    if avg_yrd_separation != None:
        if 0 < avg_yrd_separation < 1:
            avg_yrd_separation_val = 100
        elif 1 <= avg_yrd_separation <= 2.99:
            avg_yrd_separation_val = 90
        elif 3 <= avg_yrd_separation <= 4.99:
            avg_yrd_separation_val = 80
        elif 5 <= avg_yrd_separation <= 6.99:
            avg_yrd_separation_val = 70
        elif 7 <= avg_yrd_separation <= 9.99:
            avg_yrd_separation_val = 60
        elif avg_yrd_separation >= 10:
            avg_yrd_separation_val = 50
        else:
            avg_yrd_separation_val = 0
    else:
        avg_yrd_separation_val = 0

    # Avg Transition Time
    if avgtranstime != None:
        if 0 < avgtranstime < 0.1:
            avgtranstime_val = 100
        elif 0.1 <= avgtranstime <= 0.29:
            avgtranstime_val = 90
        elif 0.3 <= avgtranstime <= 0.49:
            avgtranstime_val = 80
        elif 0.5 <= avgtranstime <= 0.69:
            avgtranstime_val = 70
        elif 0.7 <= avgtranstime <= 0.89:
            avgtranstime_val = 60
        elif avgtranstime > 0.89:
            avgtranstime_val = 50
        else:
            avgtranstime_val = 0
    else:
        avgtranstime_val = 0

    # Top Speed
    if topspeed != None:
        if topspeed >= 20:
            topspeed_val = 100
        elif 18 <= topspeed <= 19.99:
            topspeed_val = 90
        elif 16 <= topspeed <= 17.99:
            topspeed_val = 80
        elif 14 <= topspeed <= 15.99:
            topspeed_val = 70
        elif 12 <= topspeed <= 13.99:
            topspeed_val = 60
        elif 0 < topspeed < 12:
            topspeed_val = 50
        else:
            topspeed_val = 0
    else:
        topspeed_val = 0

    # Avg Closing Speed
    if avgclospeed != None:
        if 0 < avgclospeed < 0.1:
            avgclospeed_val = 100
        elif 0.1 <= avgclospeed <= 0.39:
            avgclospeed_val = 90
        elif 0.4 <= avgclospeed <= 0.59:
            avgclospeed_val = 80
        elif 0.6 <= avgclospeed <= 0.79:
            avgclospeed_val = 70
        elif 0.8 <= avgclospeed <= 0.99:
            avgclospeed_val = 60
        elif avgclospeed > 0.99:
            avgclospeed_val = 50
        else:
            avgclospeed_val = 0
    else:
        avgclospeed_val = 0

    # Time To Top Speed
    if timetotopspeed != None:
        if 0 < timetotopspeed < 0.1:
            timetotopspeed_val = 100
        elif 0.1 <= timetotopspeed <= 0.29:
            timetotopspeed_val = 90
        elif 0.3 <= timetotopspeed <= 0.49:
            timetotopspeed_val = 80
        elif 0.5 <= timetotopspeed <= 0.69:
            timetotopspeed_val = 70
        elif 0.7 <= timetotopspeed <= 0.89:
            timetotopspeed_val = 60
        elif timetotopspeed >= 0.9:
            timetotopspeed_val = 50
        else:
            timetotopspeed_val = 0
    else:
        timetotopspeed_val = 0

    # Avg Yard of Sepeeration Percentage
    if avg_yrd_separation_val:
        if avg_yrd_separation_val == 100:
            avg_yrd_separation_score = 30
            avg_yrd_separation__perc = 5
        elif avg_yrd_separation_val == 90:
            avg_yrd_separation_score = 27
            avg_yrd_separation__perc = 4
        elif avg_yrd_separation_val == 80:
            avg_yrd_separation_score = 24
            avg_yrd_separation__perc = 3
        elif avg_yrd_separation_val == 70:
            avg_yrd_separation_score = 21
            avg_yrd_separation__perc = 2
        elif avg_yrd_separation_val == 60:
            avg_yrd_separation_score = 18
            avg_yrd_separation__perc = 1
        elif avg_yrd_separation_val == 50:
            avg_yrd_separation_score = 15
            avg_yrd_separation__perc = 0
        else:
            avg_yrd_separation_score = 0
            avg_yrd_separation__perc = 0
    else:
        avg_yrd_separation_score = 0
        avg_yrd_separation__perc = 0

    # Avg Transition Time Percentage
    if avgtranstime != None:
        if avgtranstime_val == 100:
            avgtranstime_score = 15
            avgtranstime_perc = 5
        elif avgtranstime_val == 90:
            avgtranstime_score = 13.5
            avgtranstime_perc = 4
        elif avgtranstime_val == 80:
            avgtranstime_score = 12
            avgtranstime_perc = 3
        elif avgtranstime_val == 70:
            avgtranstime_score = 10.5
            avgtranstime_perc = 2
        elif avgtranstime_val == 60:
            avgtranstime_score = 9
            avgtranstime_perc = 1
        elif avgtranstime_val == 50:
            avgtranstime_score = 7.5
            avgtranstime_perc = 0
        else:
            avgtranstime_score = 0
            avgtranstime_perc = 0
    else:
        avgtranstime_score = 0
        avgtranstime_perc = 0

    # Top Speed Percentage
    if topspeed != None:
        if topspeed_val == 100:
            topspeed_score = 20
            topspeed_perc = 5
        elif topspeed_val == 90:
            topspeed_score = 18
            topspeed_perc = 4
        elif topspeed_val == 80:
            topspeed_score = 16
            topspeed_perc = 3
        elif topspeed_val == 70:
            topspeed_score = 14
            topspeed_perc = 2
        elif topspeed_val == 60:
            topspeed_score = 12
            topspeed_perc = 1
        elif topspeed_val == 50:
            topspeed_score = 10
            topspeed_perc = 0
        else:
            topspeed_score = 0
            topspeed_perc = 0
    else:
        topspeed_score = 0
        topspeed_perc = 0

    # Avg Closing Speed Percentage
    if avgclospeed != None:
        if avgclospeed_val == 100:
            avgclospeed_score = 20
            avgclospeed_perc = 5
        elif avgclospeed_val == 90:
            avgclospeed_score = 18
            avgclospeed_perc = 4
        elif avgclospeed_val == 80:
            avgclospeed_score = 16
            avgclospeed_perc = 3
        elif avgclospeed_val == 70:
            avgclospeed_score = 14
            avgclospeed_perc = 2
        elif avgclospeed_val == 60:
            avgclospeed_score = 12
            avgclospeed_perc = 1
        elif avgclospeed_val == 50:
            avgclospeed_score = 10
            avgclospeed_perc = 0
        else:
            avgclospeed_score = 0
            avgclospeed_perc = 0
    else:
        avgclospeed_score = 0
        avgclospeed_perc = 0

    # Time To Top Speed Percentage
    if timetotopspeed != None:
        if timetotopspeed_val == 100:
            timetotopspeed_score = 15
            timetotopspeed_perc = 5
        elif timetotopspeed_val == 90:
            timetotopspeed_score = 13.5
            timetotopspeed_perc = 4
        elif timetotopspeed_val == 80:
            timetotopspeed_score = 12
            timetotopspeed_perc = 3
        elif timetotopspeed_val == 70:
            timetotopspeed_score = 10.5
            timetotopspeed_perc = 2
        elif timetotopspeed_val == 60:
            timetotopspeed_score = 9
            timetotopspeed_perc = 1
        elif timetotopspeed_val == 50:
            timetotopspeed_score = 7.5
            timetotopspeed_perc = 0
        else:
            timetotopspeed_score = 0
            timetotopspeed_perc = 0

    else:
        timetotopspeed_score = 0
        timetotopspeed_perc = 0

    athleticism_score = (avg_yrd_separation_score + avgtranstime_score +
                         topspeed_score + avgclospeed_score + timetotopspeed_score
                         )
    if athleticism_score >= 1:
        player.athleticism = athleticism_score
        player.save()
    else:
        player.athleticism = None
        player.save()
    return athleticism_score
