"""
Script to fetch TI schedule data from the same endpoint the DotA2 website uses.
"""
import datetime
import json
import http.client


# Comment whatever you don't want
TIME_ZONE = "IST"
# TIME_ZONE = "UTC"

def main():
    # Dict to map team_ID -> team_name
    teams = {}
    print(f"Selected time zone: {TIME_ZONE}\n")
    conn = http.client.HTTPSConnection("www.dota2.com")
    payload = ''
    headers = {}
    # Endpoint that populates the DotA2 website
    conn.request("GET", "/webapi/IDOTA2League/GetLeaguesData/v001?league_ids=13256,&delay_seconds=0", payload, headers)
    res = conn.getresponse()
    if res.status != 200:
        print(f"Response status not 200 ({res.status}). Exit code 2.\n")
        exit(2)
    print("Fetched data succesfully from DotA2 endpoint.\n")
    data = res.read()
    data = data.decode("utf-8")
    data = json.loads(data)

    # Final data to play around with
    data = data['leagues'][0]

    # Get all teams with their team IDs
    for _groups in data['node_groups']:
        for _standings in _groups['team_standings']:
            _team_id = _standings['team_id']
            _team_name = _standings['team_name']
            if _team_id not in teams.keys():
                teams[_team_id] = _team_name

    # Map matches with team IDs
    for _groups in data['node_groups']:
        for _stages in _groups['node_groups']:
            _stage_name = _stages['name']
            print(f"Stage name: {_stage_name}")
            for _matches in _stages['nodes']:
                _team_1_id = _matches['team_id_1']
                _team_2_id = _matches['team_id_2']
                if _team_1_id == 0 or _team_2_id == 0:
                    # Team ID will be zero if match not decided yet
                    print(f"TBD VS TBD AT {_match_time} {TIME_ZONE}")
                    continue
                _team_1_name = teams[_team_1_id]
                _team_2_name = teams[_team_2_id]
                _match_time = _matches['scheduled_time']
                _match_completed = _matches['is_completed']
                # Convert epoch time to datetime object (UTC)
                _match_time = datetime.datetime.utcfromtimestamp(_match_time)
                if TIME_ZONE == "IST":
                    # If time zone is IST: add 5h30m (330m) to datetime object
                    _match_time = _match_time + datetime.timedelta(minutes=330)
                elif TIME_ZONE == "UTC":
                    pass
                else:
                    print("Invalid time zone selection. Exit code 1.")
                    exit(1)
                _match_outcome = ""
                if _match_completed:
                    _team_1_wins = _matches['team_1_wins']
                    _team_2_wins = _matches['team_2_wins']
                    if _team_1_wins > _team_2_wins:
                        _match_outcome = f"|| {_team_1_name} ({_team_1_wins}-{_team_2_wins})"
                    else:
                        _match_outcome = f"|| {_team_2_name} ({_team_2_wins}-{_team_1_wins})"
                print(f"{_team_1_name} VS {_team_2_name} AT {_match_time} {TIME_ZONE} {_match_outcome}")
            print()

if __name__ == "__main__":
    main()
