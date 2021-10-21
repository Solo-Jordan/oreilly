from django.shortcuts import render
import requests
from datetime import datetime, timedelta, date


def get_weeks():
    """
    This function simply returns the start/stop dates of each of the previous
    4 weeks. It is a list of tuples.
    """


    today = date.today()
    start_of_week = today - timedelta(days=(today.weekday() + 1))

    week_four_start = start_of_week - timedelta(days=7)
    week_four_end = week_four_start + timedelta(days=6)

    week_three_start = start_of_week - timedelta(days=14)
    week_three_end = week_three_start + timedelta(days=6)

    week_two_start = start_of_week - timedelta(days=21)
    week_two_end = week_two_start + timedelta(days=6)

    week_one_start =  start_of_week - timedelta(days=28)
    week_one_end = week_one_start + timedelta(days=6)

    weeks = [(week_one_start.strftime('%Y-%m-%d'), week_one_end.strftime('%Y-%m-%d')), \
    (week_two_start.strftime('%Y-%m-%d'), week_two_end.strftime('%Y-%m-%d')), \
    (week_three_start.strftime('%Y-%m-%d'), week_three_end.strftime('%Y-%m-%d')), \
    (week_four_start.strftime('%Y-%m-%d'), week_four_end.strftime('%Y-%m-%d'))]

    """
    The var weeks (list) should look something like this:

    [
     ('2021-09-19', '2021-09-25'),
     ('2021-09-26', '2021-10-02'),
     ('2021-10-03', '2021-10-09'),
     ('2021-10-10', '2021-10-16')
    ]
    """

    return weeks

def monitorView(request):
    """
    This view gets the current monitors setup for O'Reillys betteruptime
    automation group. It then grabs the availability for the last 4 weeks for each
    monitor and displays it in a table.
    """
    if request.method == 'POST':
        headers = {'Authorization': 'Bearer kQC4773J1v9364AT9ka5Krq8'}
        # Get all of the current monitors
        r = requests.get('https://betteruptime.com/api/v2/monitors', headers=headers)

        mons = r.json()['data'] # This is a list

        # Do dict comp instead of list comp because dict is easily searchable given key
        monitors = {mon['id']: mon['attributes']['pronounceable_name'] for mon in mons}

        """
        The var monitors (dict) should look something like this:

        {
         '386011': 'google.com',
         '386014': 'en.wikipedia.org',
         '386015': 'slashdot.org',
         '386017': 'amazon.com',
         '386018': 'yahoo.com'
         }
        """

        # This just gets a list of the previous 4 weeks start/stop dates
        weeks = get_weeks()

        monitors_data = {}
        # This for loop builds a dict of each monitor and it's availability
        # over the last 4 weeks.
        for id,name in monitors.items():
            week_num = 1
            for week in weeks:
                sla = requests.get('https://betteruptime.com/api/v2/monitors/' + id + \
                '/sla?from='+ week[0] +'&to='+ week[1], headers=headers)
                if name in monitors_data.keys():
                    monitors_data[name]['weeks'].append({'week_number':week_num,
                    'availability': sla.json()['data']['attributes']['availability']
                    })
                else:
                    monitors_data[name] = {'name': name,
                    'weeks': [
                    {
                    'week_number': week_num,
                    'availability': sla.json()['data']['attributes']['availability']
                    }
                    ]}
                week_num += 1
        """
        Next I take the tuples in weeks and turn them into strings to use for
        the table header.

        From: ('2021-09-19', '2021-09-25')
        To: '09/19 - 09/25'

        I use the replace method to convert the dash to a slash.
        """
        w1 = weeks[0][0][5:].replace('-', '/')+' - '+weeks[0][1][5:].replace('-', '/')
        w2 = weeks[1][0][5:].replace('-', '/')+' - '+weeks[1][1][5:].replace('-', '/')
        w3 = weeks[2][0][5:].replace('-', '/')+' - '+weeks[2][1][5:].replace('-', '/')
        w4 = weeks[3][0][5:].replace('-', '/')+' - '+weeks[3][1][5:].replace('-', '/')

        return render(request, 'results.html', {'monitors': monitors_data, 'w1': w1, 'w2': w2, 'w3': w3, 'w4': w4})
    else:
        return render(request, 'monitors.html')
